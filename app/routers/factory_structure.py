from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from datetime import datetime

from app.database import get_db
from app import models
from app.factory_config import ASSEMBLY_LINES, SPECIAL_ZONES, HK_READERS, HK_TO_POSITION, ALL_POSITIONS

router = APIRouter()


def _factory_dict(f: models.Factory) -> dict:
    return {
        "id": f.id, "code": f.code, "name": f.name,
        "address": f.address, "description": f.description, "is_active": f.is_active,
    }


def _hall_dict(h: models.Hall) -> dict:
    return {
        "id": h.id, "factory_id": h.factory_id, "code": h.code, "name": h.name,
        "description": h.description, "color": h.color, "is_active": h.is_active,
    }


def _ws_dict(w: models.WorkStation) -> dict:
    return {
        "id": w.id, "hall_id": w.hall_id, "code": w.code, "name": w.name,
        "assembly_line": w.assembly_line, "station_type": w.station_type,
        "svg_x": w.svg_x, "svg_y": w.svg_y, "svg_w": w.svg_w, "svg_h": w.svg_h,
        "color": w.color, "shim_required": w.shim_required,
        "shim_description": w.shim_description, "shim_quantity": w.shim_quantity,
        "notes": w.notes, "is_active": w.is_active, "sort_order": w.sort_order,
        "current_work_description": w.current_work_description,
        "current_work_article": w.current_work_article,
        "current_work_started_at": w.current_work_started_at.isoformat() if w.current_work_started_at else None,
        "current_work_operator": w.current_work_operator,
        "canvas_w": w.canvas_w, "canvas_h": w.canvas_h,
    }


def _reader_dict(r: models.RFIDReader) -> dict:
    return {
        "id": r.id, "reader_id": r.reader_id, "name": r.name,
        "ip_address": r.ip_address, "port": r.port, "zone": r.zone,
        "location_description": r.location_description,
        "status": r.status,
        "last_seen": r.last_seen.isoformat() if r.last_seen else None,
        "is_active": r.is_active,
        "hall_id": r.hall_id, "svg_x": r.svg_x, "svg_y": r.svg_y,
    }


# ── Factory CRUD ──────────────────────────────────────────────────────────────
@router.get("/factories")
def list_factories(db: Session = Depends(get_db)):
    return [_factory_dict(f) for f in db.query(models.Factory).filter(models.Factory.is_active == True).all()]


@router.post("/factories")
def create_factory(code: str, name: str, address: Optional[str] = None,
                   description: Optional[str] = None, db: Session = Depends(get_db)):
    if db.query(models.Factory).filter(models.Factory.code == code).first():
        raise HTTPException(400, "Ez a kód már létezik")
    f = models.Factory(code=code, name=name, address=address, description=description)
    db.add(f)
    db.commit()
    db.refresh(f)
    return _factory_dict(f)


@router.put("/factories/{fid}")
def update_factory(fid: int, name: Optional[str] = None, address: Optional[str] = None,
                   description: Optional[str] = None, db: Session = Depends(get_db)):
    f = db.query(models.Factory).filter(models.Factory.id == fid).first()
    if not f:
        raise HTTPException(404, "Üzem nem található")
    if name:
        f.name = name
    if address is not None:
        f.address = address
    if description is not None:
        f.description = description
    db.commit()
    return _factory_dict(f)


@router.delete("/factories/{fid}")
def delete_factory(fid: int, db: Session = Depends(get_db)):
    f = db.query(models.Factory).filter(models.Factory.id == fid).first()
    if not f:
        raise HTTPException(404, "Üzem nem található")
    f.is_active = False
    db.commit()
    return {"ok": True}


# ── Hall CRUD ─────────────────────────────────────────────────────────────────
@router.get("/halls")
def list_halls(factory_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(models.Hall).filter(models.Hall.is_active == True)
    if factory_id:
        q = q.filter(models.Hall.factory_id == factory_id)
    return [_hall_dict(h) for h in q.all()]


@router.post("/halls")
def create_hall(code: str, name: str, factory_id: Optional[int] = None,
                color: str = "#3b82f6", description: Optional[str] = None,
                db: Session = Depends(get_db)):
    if db.query(models.Hall).filter(models.Hall.code == code).first():
        raise HTTPException(400, "Ez a kód már létezik")
    h = models.Hall(code=code, name=name, factory_id=factory_id, color=color, description=description)
    db.add(h)
    db.commit()
    db.refresh(h)
    return _hall_dict(h)


@router.put("/halls/{hid}")
def update_hall(hid: int, name: Optional[str] = None, color: Optional[str] = None,
                description: Optional[str] = None, db: Session = Depends(get_db)):
    h = db.query(models.Hall).filter(models.Hall.id == hid).first()
    if not h:
        raise HTTPException(404, "Csarnok nem található")
    if name:
        h.name = name
    if color:
        h.color = color
    if description is not None:
        h.description = description
    db.commit()
    return _hall_dict(h)


@router.delete("/halls/{hid}")
def delete_hall(hid: int, db: Session = Depends(get_db)):
    h = db.query(models.Hall).filter(models.Hall.id == hid).first()
    if not h:
        raise HTTPException(404, "Csarnok nem található")
    h.is_active = False
    db.commit()
    return {"ok": True}


# ── WorkStation CRUD ──────────────────────────────────────────────────────────
@router.get("/workstations")
def list_workstations(hall_id: Optional[int] = None, assembly_line: Optional[str] = None,
                      db: Session = Depends(get_db)):
    q = db.query(models.WorkStation).filter(models.WorkStation.is_active == True)
    if hall_id:
        q = q.filter(models.WorkStation.hall_id == hall_id)
    if assembly_line:
        q = q.filter(models.WorkStation.assembly_line == assembly_line)
    return [_ws_dict(w) for w in q.order_by(models.WorkStation.sort_order, models.WorkStation.code).all()]


@router.post("/workstations")
def create_workstation(
    code: str, name: str,
    assembly_line: Optional[str] = None,
    station_type: str = "assembly",
    hall_id: Optional[int] = None,
    svg_x: Optional[int] = None, svg_y: Optional[int] = None,
    svg_w: int = 118, svg_h: int = 140,
    color: Optional[str] = None,
    shim_required: bool = False,
    shim_description: Optional[str] = None,
    shim_quantity: int = 0,
    notes: Optional[str] = None,
    sort_order: int = 0,
    db: Session = Depends(get_db),
):
    if db.query(models.WorkStation).filter(models.WorkStation.code == code).first():
        raise HTTPException(400, "Ez a kód már létezik")
    ws = models.WorkStation(
        code=code, name=name, assembly_line=assembly_line, station_type=station_type,
        hall_id=hall_id, svg_x=svg_x, svg_y=svg_y, svg_w=svg_w, svg_h=svg_h,
        color=color, shim_required=shim_required, shim_description=shim_description,
        shim_quantity=shim_quantity, notes=notes, sort_order=sort_order,
    )
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return _ws_dict(ws)


@router.put("/workstations/{wid}")
def update_workstation(
    wid: int,
    name: Optional[str] = None,
    assembly_line: Optional[str] = None,
    station_type: Optional[str] = None,
    hall_id: Optional[int] = None,
    svg_x: Optional[int] = None, svg_y: Optional[int] = None,
    svg_w: Optional[int] = None, svg_h: Optional[int] = None,
    color: Optional[str] = None,
    shim_required: Optional[bool] = None,
    shim_description: Optional[str] = None,
    shim_quantity: Optional[int] = None,
    notes: Optional[str] = None,
    sort_order: Optional[int] = None,
    db: Session = Depends(get_db),
):
    ws = db.query(models.WorkStation).filter(models.WorkStation.id == wid).first()
    if not ws:
        raise HTTPException(404, "Munkaállomás nem található")
    for field, val in [
        ("name", name), ("assembly_line", assembly_line), ("station_type", station_type),
        ("hall_id", hall_id), ("svg_x", svg_x), ("svg_y", svg_y),
        ("svg_w", svg_w), ("svg_h", svg_h), ("color", color),
        ("shim_required", shim_required), ("shim_description", shim_description),
        ("shim_quantity", shim_quantity), ("notes", notes), ("sort_order", sort_order),
    ]:
        if val is not None:
            setattr(ws, field, val)
    db.commit()
    return _ws_dict(ws)


@router.delete("/workstations/{wid}")
def delete_workstation(wid: int, db: Session = Depends(get_db)):
    ws = db.query(models.WorkStation).filter(models.WorkStation.id == wid).first()
    if not ws:
        raise HTTPException(404, "Munkaállomás nem található")
    ws.is_active = False
    db.commit()
    return {"ok": True}


# ── Seed: default szerelde adatok betöltése ───────────────────────────────────
@router.post("/seed-default")
def seed_default_layout(db: Session = Depends(get_db)):
    """Betölti a valódi gyári alaprajz alapján a szerelde állásokat."""
    created = 0

    # Alapértelmezett gyár
    factory = db.query(models.Factory).filter(models.Factory.code == "SZERELDE").first()
    if not factory:
        factory = models.Factory(
            code="SZERELDE", name="Szerelde Csarnok",
            description="JD 4270 és KSR 4392 összeszerelő sorok"
        )
        db.add(factory)
        db.flush()

    # JD 4270 csarnok
    hall_jd = db.query(models.Hall).filter(models.Hall.code == "JD4270").first()
    if not hall_jd:
        hall_jd = models.Hall(
            factory_id=factory.id, code="JD4270",
            name="4270 John Deere futómű szerelde", color="#2563eb"
        )
        db.add(hall_jd)
        db.flush()

    # KSR 4392 csarnok
    hall_ksr = db.query(models.Hall).filter(models.Hall.code == "KSR4392").first()
    if not hall_ksr:
        hall_ksr = models.Hall(
            factory_id=factory.id, code="KSR4392",
            name="4392 Középsorozatú futómű szerelde", color="#d97706"
        )
        db.add(hall_ksr)
        db.flush()

    # JD állások SVG koordinátái
    jd_stations = [
        {"code": "1423", "svg_x": 92,  "svg_y": 82, "sort_order": 1},
        {"code": "1424", "svg_x": 213, "svg_y": 82, "sort_order": 2},
        {"code": "1425", "svg_x": 334, "svg_y": 82, "sort_order": 3, "station_type": "storage"},
        {"code": "1426", "svg_x": 455, "svg_y": 82, "sort_order": 4},
        {"code": "1427", "svg_x": 576, "svg_y": 82, "sort_order": 5},
        {"code": "1428", "svg_x": 697, "svg_y": 82, "sort_order": 6},
        {"code": "1429", "svg_x": 818, "svg_y": 82, "sort_order": 7, "svg_w": 140},
    ]
    for s in jd_stations:
        if not db.query(models.WorkStation).filter(models.WorkStation.code == s["code"]).first():
            db.add(models.WorkStation(
                hall_id=hall_jd.id, code=s["code"],
                name=f"JD 4270 – {s['code']} állás",
                assembly_line="4270",
                station_type=s.get("station_type", "assembly"),
                svg_x=s["svg_x"], svg_y=s["svg_y"],
                svg_w=s.get("svg_w", 118), svg_h=140,
                color="#2563eb", shim_required=True,
                sort_order=s["sort_order"],
            ))
            created += 1

    # KSR állások SVG koordinátái
    ksr_stations = [
        {"code": "1323", "svg_x": 92,  "svg_y": 308, "sort_order": 1, "svg_w": 105},
        {"code": "1324", "svg_x": 200, "svg_y": 308, "sort_order": 2, "svg_w": 105},
        {"code": "1325", "svg_x": 308, "svg_y": 308, "sort_order": 3, "svg_w": 105},
        {"code": "1326", "svg_x": 416, "svg_y": 308, "sort_order": 4, "svg_w": 105},
        {"code": "1327", "svg_x": 524, "svg_y": 308, "sort_order": 5, "svg_w": 105},
        {"code": "1328", "svg_x": 632, "svg_y": 308, "sort_order": 6, "svg_w": 105},
        {"code": "1329", "svg_x": 740, "svg_y": 308, "sort_order": 7, "svg_w": 105},
        {"code": "1330", "svg_x": 848, "svg_y": 308, "sort_order": 8, "svg_w": 110},
    ]
    for s in ksr_stations:
        if not db.query(models.WorkStation).filter(models.WorkStation.code == s["code"]).first():
            db.add(models.WorkStation(
                hall_id=hall_ksr.id, code=s["code"],
                name=f"KSR 4392 – {s['code']} állás",
                assembly_line="4392",
                station_type="assembly",
                svg_x=s["svg_x"], svg_y=s["svg_y"],
                svg_w=s["svg_w"], svg_h=140,
                color="#d97706", shim_required=True,
                sort_order=s["sort_order"],
            ))
            created += 1

    # Speciális zónák
    special = [
        {"code": "HÁTRALÉKOS", "name": "Hátralékos kocsik", "type": "transit", "color": "#3b82f6"},
        {"code": "FOLYOSÓ",    "name": "Folyosó / tranzit",  "type": "transit", "color": "#6b7280"},
        {"code": "KÉSZ",       "name": "Kész hidak",         "type": "finished","color": "#22c55e"},
        {"code": "RAKTÁR",     "name": "Szereldei raktár",   "type": "storage", "color": "#8b5cf6"},
    ]
    for s in special:
        if not db.query(models.WorkStation).filter(models.WorkStation.code == s["code"]).first():
            db.add(models.WorkStation(
                code=s["code"], name=s["name"], station_type=s["type"],
                color=s["color"], sort_order=99,
            ))
            created += 1

    db.commit()
    return {"ok": True, "created": created}


# ── Összefoglaló nézet ────────────────────────────────────────────────────────
@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    factories = db.query(models.Factory).options(
        joinedload(models.Factory.halls).joinedload(models.Hall.workstations)
    ).filter(models.Factory.is_active == True).all()

    result = []
    for f in factories:
        halls = []
        for h in f.halls:
            if not h.is_active:
                continue
            halls.append({
                **_hall_dict(h),
                "workstations": [_ws_dict(w) for w in h.workstations if w.is_active],
            })
        result.append({**_factory_dict(f), "halls": halls})

    # Önálló munkaállomások (nincs csarnokuk)
    standalone = db.query(models.WorkStation).filter(
        models.WorkStation.hall_id == None,
        models.WorkStation.is_active == True,
    ).all()

    return {"factories": result, "standalone_workstations": [_ws_dict(w) for w in standalone]}


# ══════════════════════════════════════════════════════════════════════════════
# HALL TÉRKÉP API-K
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/halls/{hid}/map")
def get_hall_map(hid: int, db: Session = Depends(get_db)):
    """Egy csarnok teljes térkép adatai: munkaállomások + RFID olvasók."""
    hall = db.query(models.Hall).filter(models.Hall.id == hid).first()
    if not hall:
        raise HTTPException(404, "Csarnok nem található")

    workstations = db.query(models.WorkStation).filter(
        models.WorkStation.hall_id == hid,
        models.WorkStation.is_active == True,
    ).order_by(models.WorkStation.sort_order, models.WorkStation.code).all()

    readers = db.query(models.RFIDReader).filter(
        models.RFIDReader.hall_id == hid,
        models.RFIDReader.is_active == True,
    ).all()

    # Vászon mérete a hall-on tárolt értékekből, vagy default
    canvas_w = 1200
    canvas_h = 700
    if workstations:
        canvas_w = workstations[0].canvas_w or 1200
        canvas_h = workstations[0].canvas_h or 700

    return {
        "hall": _hall_dict(hall),
        "canvas_w": canvas_w,
        "canvas_h": canvas_h,
        "workstations": [_ws_dict(w) for w in workstations],
        "readers": [_reader_dict(r) for r in readers],
    }


@router.post("/halls/{hid}/save-layout")
def save_hall_layout(hid: int, layout: dict, db: Session = Depends(get_db)):
    """
    Térkép elrendezés mentése – munkaállomások és olvasók SVG pozíciói.
    Body: {
      canvas_w, canvas_h,
      workstations: [{id, svg_x, svg_y, svg_w, svg_h}],
      readers: [{id, svg_x, svg_y}]
    }
    """
    hall = db.query(models.Hall).filter(models.Hall.id == hid).first()
    if not hall:
        raise HTTPException(404, "Csarnok nem található")

    canvas_w = layout.get("canvas_w", 1200)
    canvas_h = layout.get("canvas_h", 700)

    for ws_data in layout.get("workstations", []):
        ws = db.query(models.WorkStation).filter(models.WorkStation.id == ws_data["id"]).first()
        if ws and ws.hall_id == hid:
            ws.svg_x = ws_data.get("svg_x", ws.svg_x)
            ws.svg_y = ws_data.get("svg_y", ws.svg_y)
            ws.svg_w = ws_data.get("svg_w", ws.svg_w)
            ws.svg_h = ws_data.get("svg_h", ws.svg_h)
            ws.canvas_w = canvas_w
            ws.canvas_h = canvas_h

    for rd_data in layout.get("readers", []):
        rd = db.query(models.RFIDReader).filter(models.RFIDReader.id == rd_data["id"]).first()
        if rd:
            rd.svg_x = rd_data.get("svg_x", rd.svg_x)
            rd.svg_y = rd_data.get("svg_y", rd.svg_y)

    db.commit()
    return {"ok": True}


@router.post("/workstations/{wid}/current-work")
def update_current_work(
    wid: int,
    description: Optional[str] = None,
    article: Optional[str] = None,
    operator: Optional[str] = None,
    clear: bool = False,
    db: Session = Depends(get_db),
):
    """Megadja, hogy éppen mit szerelnek az adott állomáson."""
    ws = db.query(models.WorkStation).filter(models.WorkStation.id == wid).first()
    if not ws:
        raise HTTPException(404, "Munkaállomás nem található")
    if clear:
        ws.current_work_description = None
        ws.current_work_article = None
        ws.current_work_started_at = None
        ws.current_work_operator = None
    else:
        if description is not None:
            ws.current_work_description = description
        if article is not None:
            ws.current_work_article = article
        if operator is not None:
            ws.current_work_operator = operator
        if description or article:
            ws.current_work_started_at = datetime.now()
    db.commit()
    return _ws_dict(ws)


# ══════════════════════════════════════════════════════════════════════════════
# RFID OLVASÓ TÉRKÉP CRUD
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/readers")
def list_map_readers(hall_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(models.RFIDReader).filter(models.RFIDReader.is_active == True)
    if hall_id:
        q = q.filter(models.RFIDReader.hall_id == hall_id)
    return [_reader_dict(r) for r in q.all()]


@router.post("/readers")
def create_map_reader(
    reader_id: str,
    name: str,
    hall_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    zone: Optional[str] = None,
    location_description: Optional[str] = None,
    svg_x: int = 200,
    svg_y: int = 200,
    db: Session = Depends(get_db),
):
    existing = db.query(models.RFIDReader).filter(models.RFIDReader.reader_id == reader_id).first()
    if existing:
        raise HTTPException(400, f"'{reader_id}' olvasó ID már létezik")
    r = models.RFIDReader(
        reader_id=reader_id, name=name, hall_id=hall_id,
        ip_address=ip_address, zone=zone,
        location_description=location_description,
        svg_x=svg_x, svg_y=svg_y,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return _reader_dict(r)


@router.put("/readers/{rid}")
def update_map_reader(
    rid: int,
    name: Optional[str] = None,
    hall_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    zone: Optional[str] = None,
    location_description: Optional[str] = None,
    svg_x: Optional[int] = None,
    svg_y: Optional[int] = None,
    db: Session = Depends(get_db),
):
    r = db.query(models.RFIDReader).filter(models.RFIDReader.id == rid).first()
    if not r:
        raise HTTPException(404, "Olvasó nem található")
    for field, val in [
        ("name", name), ("hall_id", hall_id), ("ip_address", ip_address),
        ("zone", zone), ("location_description", location_description),
        ("svg_x", svg_x), ("svg_y", svg_y),
    ]:
        if val is not None:
            setattr(r, field, val)
    db.commit()
    return _reader_dict(r)


@router.delete("/readers/{rid}")
def delete_map_reader(rid: int, db: Session = Depends(get_db)):
    r = db.query(models.RFIDReader).filter(models.RFIDReader.id == rid).first()
    if not r:
        raise HTTPException(404, "Olvasó nem található")
    r.is_active = False
    db.commit()
    return {"ok": True}


@router.post("/halls/{hid}/seed-readers")
def seed_hall_readers(hid: int, db: Session = Depends(get_db)):
    """HK01-HK10 RFID olvasók betöltése a csarnokhoz az alaprajz alapján."""
    from app.factory_config import HK_READERS as CONFIG_READERS
    hall = db.query(models.Hall).filter(models.Hall.id == hid).first()
    if not hall:
        raise HTTPException(404, "Csarnok nem található")

    created = 0
    for hk in CONFIG_READERS:
        existing = db.query(models.RFIDReader).filter(
            models.RFIDReader.reader_id == hk["id"]
        ).first()
        if existing:
            existing.hall_id = hid
            existing.svg_x = hk["svg_x"]
            existing.svg_y = hk["svg_y"]
        else:
            db.add(models.RFIDReader(
                reader_id=hk["id"],
                name=hk["name"],
                zone=hk["zone"],
                location_description=hk.get("description", ""),
                hall_id=hid,
                svg_x=hk["svg_x"],
                svg_y=hk["svg_y"],
            ))
            created += 1
    db.commit()
    return {"ok": True, "created": created}
