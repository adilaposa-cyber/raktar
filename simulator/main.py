"""
RFID ATR7000 Szoftver Szimulátor
- Virtuális raktár zónákkal
- Automatikus demo mód
- Valós idejű HTTP POST az fő alkalmazáshoz
- WebSocket UI frissítés

Indítás: python simulator/main.py
UI: http://localhost:8001
"""
import asyncio
import random
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import aiohttp

# ── Szerelde konfiguráció – valódi gyári alaprajz alapján ────────────────────
ZONES = [
    {"id": "HÁTRALÉKOS",  "name": "Hátralékos kocsik",         "color": "#3b82f6"},
    {"id": "1423",        "name": "JD 4270 – 1423 állás",      "color": "#2563eb"},
    {"id": "1424",        "name": "JD 4270 – 1424 állás",      "color": "#2563eb"},
    {"id": "1425",        "name": "JD 4270 – 1425 / Raktár",   "color": "#7c3aed"},
    {"id": "1426",        "name": "JD 4270 – 1426 állás",      "color": "#2563eb"},
    {"id": "1427",        "name": "JD 4270 – 1427 állás",      "color": "#2563eb"},
    {"id": "1428",        "name": "JD 4270 – 1428 állás",      "color": "#2563eb"},
    {"id": "1429",        "name": "JD 4270 – 1429 állás",      "color": "#2563eb"},
    {"id": "FOLYOSÓ",     "name": "Folyosó / tranzit",          "color": "#6b7280"},
    {"id": "1323",        "name": "KSR 4392 – 1323 állás",     "color": "#d97706"},
    {"id": "1324",        "name": "KSR 4392 – 1324 állás",     "color": "#d97706"},
    {"id": "1325",        "name": "KSR 4392 – 1325 állás",     "color": "#d97706"},
    {"id": "1326",        "name": "KSR 4392 – 1326 állás",     "color": "#d97706"},
    {"id": "1327",        "name": "KSR 4392 – 1327 állás",     "color": "#d97706"},
    {"id": "1328",        "name": "KSR 4392 – 1328 állás",     "color": "#d97706"},
    {"id": "1329",        "name": "KSR 4392 – 1329 állás",     "color": "#d97706"},
    {"id": "1330",        "name": "KSR 4392 – 1330 állás",     "color": "#d97706"},
    {"id": "KÉSZ",        "name": "Kész hidak",                 "color": "#22c55e"},
]

READERS = [
    {"id": "HK01", "name": "HK01 – KSR bal bejárat",    "zone": "1323"},
    {"id": "HK02", "name": "HK02 – JD 1424 bejárat",    "zone": "1424"},
    {"id": "HK03", "name": "HK03 – Szereldei raktár",   "zone": "1425"},
    {"id": "HK04", "name": "HK04 – JD 1426 bejárat",    "zone": "1426"},
    {"id": "HK05", "name": "HK05 – Középső folyosó",    "zone": "FOLYOSÓ"},
    {"id": "HK06", "name": "HK06 – JD 1428 bejárat",    "zone": "1428"},
    {"id": "HK07", "name": "HK07 – JD jobb kijárat",    "zone": "KÉSZ"},
    {"id": "HK08", "name": "HK08 – KSR 1327 bejárat",   "zone": "1327"},
    {"id": "HK09", "name": "HK09 – KSR 1326 bejárat",   "zone": "1326"},
    {"id": "HK10", "name": "HK10 – KSR 1324 bejárat",   "zone": "1324"},
]

# Demo forgatókönyv – komissiózó kocsi útja a szerelésen
DEMO_SCENARIO = [
    # (tag_epc, from_zone, to_zone, leírás, delay_mp)
    ("EPC-KOCSI001", "HÁTRALÉKOS", "1424",    "KOCSI-001 megérkezett JD 1424 álláshoz (HK02)", 3),
    ("EPC-KOCSI002", "HÁTRALÉKOS", "1323",    "KOCSI-002 megérkezett KSR 1323 álláshoz (HK01)", 2),
    ("EPC-KOCSI003", "HÁTRALÉKOS", "1425",    "KOCSI-003 szereldei raktárba megy (HK03)",       3),
    ("EPC-KOCSI001", "1424",       "1426",    "KOCSI-001 továbblép 1424 → 1426 (HK04)",         4),
    ("EPC-KOCSI002", "1323",       "1324",    "KOCSI-002 továbblép 1323 → 1324 (HK10)",         3),
    ("EPC-KOCSI004", "HÁTRALÉKOS", "1427",    "KOCSI-004 JD 1427 álláshoz",                      2),
    ("EPC-KOCSI001", "1426",       "FOLYOSÓ", "KOCSI-001 folyosón halad (HK05)",                 2),
    ("EPC-KOCSI001", "FOLYOSÓ",    "1326",    "KOCSI-001 KSR sorba kerül – 1326 (HK09)",         3),
    ("EPC-KOCSI003", "1425",       "1428",    "KOCSI-003 JD 1428 álláshoz (HK06)",               4),
    ("EPC-KOCSI002", "1324",       "1325",    "KOCSI-002 továbblép 1325 álláshoz",               3),
    ("EPC-KOCSI004", "1427",       "1429",    "KOCSI-004 JD 1429 kész területre",                4),
    ("EPC-KOCSI003", "1428",       "KÉSZ",    "KOCSI-003 kész hidak területére érkezett (HK07)", 3),
]

# ── App state ─────────────────────────────────────────────────────────────────
class SimState:
    def __init__(self):
        self.pallet_locations: Dict[str, Optional[str]] = {}  # epc → zone
        self.events: List[dict] = []
        self.demo_running = False
        self.main_app_url = "http://localhost:8000"
        self.ws_clients: List[WebSocket] = []
        self.send_to_main = True

    def get_zone_pallets(self) -> Dict[str, List[str]]:
        result = {z["id"]: [] for z in ZONES}
        for epc, zone in self.pallet_locations.items():
            if zone and zone in result:
                result[zone].append(epc)
        return result

state = SimState()

# ── Pre-populate demo pallets ─────────────────────────────────────────────────
for i in range(1, 8):
    state.pallet_locations[f"EPC-RAK{i:03d}"] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="RFID Szimulátor", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="simulator/static"), name="sim_static")
templates = Jinja2Templates(directory="simulator/templates")

# ── WebSocket broadcast ───────────────────────────────────────────────────────
async def broadcast(data: dict):
    dead = []
    for ws in state.ws_clients:
        try:
            await ws.send_json(data)
        except Exception:
            dead.append(ws)
    for ws in dead:
        state.ws_clients.remove(ws)

# ── RFID event küldés főalkalmazásba ─────────────────────────────────────────
async def fire_rfid_event(reader: dict, tag_epc: str, rssi: float = None) -> bool:
    rssi = rssi or round(random.uniform(-75, -50), 1)
    payload = {
        "reader_id": reader["id"],
        "tag_epc": tag_epc,
        "rssi": rssi,
        "zone": reader["zone"],
        "event_type": "read",
    }
    event = {
        "ts": datetime.now().isoformat(),
        "reader": reader["name"],
        "zone": reader["zone"],
        "epc": tag_epc,
        "rssi": rssi,
        "sent_to_main": False,
    }

    if state.send_to_main:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{state.main_app_url}/api/rfid/event",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=3),
                ) as resp:
                    event["sent_to_main"] = resp.status == 200
        except Exception as e:
            event["error"] = str(e)

    state.events.insert(0, event)
    state.events = state.events[:100]
    await broadcast({"type": "event", "event": event})
    return event["sent_to_main"]


def zone_to_reader(zone_id: str) -> Optional[dict]:
    for r in READERS:
        if r["zone"] == zone_id:
            return r
    return None

# ── API ───────────────────────────────────────────────────────────────────────
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("simulator.html", {"request": request})

@app.get("/api/state")
def get_state():
    return {
        "zones": ZONES,
        "readers": READERS,
        "zone_pallets": state.get_zone_pallets(),
        "all_pallets": list(state.pallet_locations.keys()),
        "events": state.events[:30],
        "demo_running": state.demo_running,
        "send_to_main": state.send_to_main,
        "main_app_url": state.main_app_url,
    }

@app.post("/api/move")
async def move_pallet(epc: str, to_zone: str):
    """Raklap manuális áthelyezése – RFID esemény kiváltása."""
    if epc not in state.pallet_locations:
        return JSONResponse({"ok": False, "error": "Ismeretlen EPC"}, 400)

    old_zone = state.pallet_locations[epc]
    state.pallet_locations[epc] = to_zone

    reader = zone_to_reader(to_zone)
    if reader:
        ok = await fire_rfid_event(reader, epc)
    else:
        ok = False

    await broadcast({"type": "move", "epc": epc, "from": old_zone, "to": to_zone})
    return {"ok": True, "sent_to_main": ok, "from": old_zone, "to": to_zone}

@app.post("/api/add-pallet")
async def add_pallet(epc: str):
    if epc in state.pallet_locations:
        return JSONResponse({"ok": False, "error": "EPC már létezik"}, 400)
    state.pallet_locations[epc] = None
    await broadcast({"type": "add_pallet", "epc": epc})
    return {"ok": True}

@app.post("/api/settings")
async def update_settings(main_app_url: str = "http://localhost:8000", send_to_main: bool = True):
    state.main_app_url = main_app_url.rstrip("/")
    state.send_to_main = send_to_main
    return {"ok": True}

@app.post("/api/demo/start")
async def start_demo():
    if state.demo_running:
        return {"ok": False, "error": "Demo már fut"}
    state.demo_running = True
    asyncio.create_task(_run_demo())
    return {"ok": True}

@app.post("/api/demo/stop")
async def stop_demo():
    state.demo_running = False
    return {"ok": True}

@app.post("/api/reset")
async def reset_state():
    state.demo_running = False
    for epc in state.pallet_locations:
        state.pallet_locations[epc] = None
    state.events.clear()
    await broadcast({"type": "reset"})
    return {"ok": True}

async def _run_demo():
    """Lejátssza a teljes demo forgatókönyvet."""
    await broadcast({"type": "demo_start"})
    for tag_epc, from_zone, to_zone, description, delay in DEMO_SCENARIO:
        if not state.demo_running:
            break
        await broadcast({"type": "demo_step", "description": description, "epc": tag_epc})
        state.pallet_locations[tag_epc] = to_zone
        reader = zone_to_reader(to_zone)
        if reader:
            await fire_rfid_event(reader, tag_epc)
        await broadcast({"type": "move", "epc": tag_epc, "from": from_zone, "to": to_zone})
        await asyncio.sleep(delay)
    state.demo_running = False
    await broadcast({"type": "demo_end"})

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    state.ws_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in state.ws_clients:
            state.ws_clients.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("simulator.main:app", host="0.0.0.0", port=8001, reload=True)
