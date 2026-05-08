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

# ── Raktár konfiguráció ───────────────────────────────────────────────────────
ZONES = [
    {"id": "BEVÉTELEZŐ",   "name": "Bevételező terület",  "color": "#3b82f6", "x": 0,  "y": 0},
    {"id": "A-TÁROLÓ",     "name": "A Tároló zóna",       "color": "#22c55e", "x": 1,  "y": 0},
    {"id": "B-TÁROLÓ",     "name": "B Tároló zóna",       "color": "#16a34a", "x": 2,  "y": 0},
    {"id": "GYÁRTÁS",      "name": "Gyártócsarnok",       "color": "#f59e0b", "x": 0,  "y": 1},
    {"id": "KOMISSIÓZÓ",   "name": "Komissiózó terület",  "color": "#8b5cf6", "x": 1,  "y": 1},
    {"id": "KISZÁLLÍTÁS",  "name": "Kiszállítási dok",    "color": "#ef4444", "x": 2,  "y": 1},
]

READERS = [
    {"id": "SIM-BEVET-01",  "name": "Bevételező kapu",     "zone": "BEVÉTELEZŐ"},
    {"id": "SIM-A-01",      "name": "A zóna bejárat",       "zone": "A-TÁROLÓ"},
    {"id": "SIM-B-01",      "name": "B zóna bejárat",       "zone": "B-TÁROLÓ"},
    {"id": "SIM-GYAR-01",   "name": "Gyártás bejárat",      "zone": "GYÁRTÁS"},
    {"id": "SIM-KOMM-01",   "name": "Komissiózó bejárat",   "zone": "KOMISSIÓZÓ"},
    {"id": "SIM-KISZALL-01","name": "Kiszállítási kapu",    "zone": "KISZÁLLÍTÁS"},
]

# Demo forgatókönyv – tipikus raktárfolyamat
DEMO_SCENARIO = [
    # (tag_epc, from_zone, to_zone, leírás, delay_mp)
    ("EPC-RAK001", None,           "BEVÉTELEZŐ",  "Raklap érkezik szállítótól",     2),
    ("EPC-RAK001", "BEVÉTELEZŐ",   "A-TÁROLÓ",    "Betárolás A zónába",             3),
    ("EPC-RAK002", None,           "BEVÉTELEZŐ",  "2. raklap érkezik",              2),
    ("EPC-RAK002", "BEVÉTELEZŐ",   "B-TÁROLÓ",    "Betárolás B zónába",             3),
    ("EPC-RAK001", "A-TÁROLÓ",     "GYÁRTÁS",     "Raklap kimegy gyártásba",        4),
    ("EPC-RAK003", None,           "BEVÉTELEZŐ",  "3. raklap érkezik",              2),
    ("EPC-RAK003", "BEVÉTELEZŐ",   "A-TÁROLÓ",    "Betárolás A zónába",             3),
    ("EPC-RAK001", "GYÁRTÁS",      "A-TÁROLÓ",    "Visszakerül tárolóba (fázis kész)", 5),
    ("EPC-RAK002", "B-TÁROLÓ",     "KOMISSIÓZÓ",  "Komissiózásra kivéve",           4),
    ("EPC-RAK002", "KOMISSIÓZÓ",   "KISZÁLLÍTÁS", "Kiszállításra előkészítve",      3),
    ("EPC-RAK001", "A-TÁROLÓ",     "KOMISSIÓZÓ",  "Komissiózásra kivéve",           4),
    ("EPC-RAK001", "KOMISSIÓZÓ",   "KISZÁLLÍTÁS", "Kiszállításra előkészítve",      3),
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
