from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func as sqlfunc
from typing import List, Optional
from datetime import datetime
import asyncio

from app.database import get_db
from app import models
from app.factory_config import HK_TO_POSITION, HK_BY_ID, ALL_POSITIONS, HK_READERS, CORRIDOR_POSITIONS

router = APIRouter()


# ── Séma helpers (inline – elkerüli a körkörös importot) ─────────────────────
def _cart_dict(c: models.Cart) -> dict:
    pos_changed = c.position_changed_at
    position_minutes = None
    if pos_changed:
        delta = datetime.now() - pos_changed.replace(tzinfo=None)
        position_minutes = round(delta.total_seconds() / 60, 1)
    in_corridor = c.current_position in CORRIDOR_POSITIONS
    kitarolt = in_corridor and position_minutes is not None and position_minutes >= 5
    return {
        "id": c.id,
        "cart_number": c.cart_number,
        "assembly_line": c.assembly_line,
        "current_position": c.current_position,
        "status": c.status,
        "last_hk_reader": c.last_hk_reader,
        "last_seen_at": c.last_seen_at.isoformat() if c.last_seen_at else None,
        "position_changed_at": pos_changed.isoformat() if pos_changed else None,
        "position_minutes": position_minutes,
        "corridor_minutes": position_minutes if in_corridor else None,
        "kitarolt": kitarolt,
        "assigned_operator": c.assigned_operator,
        "notes": c.notes,
        "rfid_epc": c.rfid_tag.epc if c.rfid_tag else None,
    }


# ── CRUD ──────────────────────────────────────────────────────────────────────
@router.get("/")
def list_carts(
    status: Optional[str] = None,
    assembly_line: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.Cart).options(joinedload(models.Cart.rfid_tag)).filter(
        models.Cart.is_active == True
    )
    if status:
        q = q.filter(models.Cart.status == status)
    if assembly_line:
        q = q.filter(models.Cart.assembly_line == assembly_line)
    return [_cart_dict(c) for c in q.all()]


@router.post("/")
def create_cart(
    cart_number: str,
    assembly_line: Optional[str] = None,
    rfid_epc: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
):
    existing = db.query(models.Cart).filter(models.Cart.cart_number == cart_number).first()
    if existing:
        raise HTTPException(400, "Ez a kocsi szám már létezik")

    tag_id = None
    if rfid_epc:
        tag = db.query(models.RFIDTag).filter(models.RFIDTag.epc == rfid_epc).first()
        if not tag:
            tag = models.RFIDTag(epc=rfid_epc, tag_type="cart", description=f"Kocsi: {cart_number}")
            db.add(tag)
            db.flush()
        tag_id = tag.id

    cart = models.Cart(
        cart_number=cart_number,
        assembly_line=assembly_line,
        current_position="HÁTRALÉKOS",
        status="hátralékos",
        rfid_tag_id=tag_id,
        notes=notes,
    )
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return _cart_dict(cart)


@router.get("/floor-plan")
def floor_plan_data(db: Session = Depends(get_db)):
    """Összes kocsi pozíciója a térképhez + olvasó státuszok."""
    carts = db.query(models.Cart).options(
        joinedload(models.Cart.rfid_tag)
    ).filter(models.Cart.is_active == True).all()

    position_map: dict[str, list] = {p: [] for p in ALL_POSITIONS}
    for c in carts:
        pos = c.current_position or "HÁTRALÉKOS"
        if pos in position_map:
            position_map[pos].append(_cart_dict(c))
        else:
            position_map["HÁTRALÉKOS"].append(_cart_dict(c))

    # Olvasók utolsó aktivitása
    readers_status = []
    for hk in HK_READERS:
        reader_db = db.query(models.RFIDReader).filter(
            models.RFIDReader.reader_id == hk["id"]
        ).first()
        readers_status.append({
            **hk,
            "status": reader_db.status if reader_db else "offline",
            "last_seen": reader_db.last_seen.isoformat() if (reader_db and reader_db.last_seen) else None,
        })

    corridor_carts = sum(
        len(position_map.get(p, [])) for p in CORRIDOR_POSITIONS
    )
    kitarolt_count = sum(
        1 for p in CORRIDOR_POSITIONS
        for c in position_map.get(p, [])
        if c.get("kitarolt")
    )
    return {
        "position_map": position_map,
        "readers": readers_status,
        "stats": {
            "hátralékos": len(position_map.get("HÁTRALÉKOS", [])),
            "aktív": sum(
                len(v) for k, v in position_map.items()
                if k not in {"HÁTRALÉKOS", "KÉSZ"} | CORRIDOR_POSITIONS
            ),
            "folyosó": corridor_carts,
            "kitarolt": kitarolt_count,
            "kész": len(position_map.get("KÉSZ", [])),
            "total": len(carts),
        },
    }


@router.get("/stats")
def cart_stats(db: Session = Depends(get_db)):
    rows = db.query(
        models.Cart.status, sqlfunc.count(models.Cart.id)
    ).filter(models.Cart.is_active == True).group_by(models.Cart.status).all()
    return {r[0]: r[1] for r in rows}


@router.get("/{cart_id}")
def get_cart(cart_id: int, db: Session = Depends(get_db)):
    cart = db.query(models.Cart).options(joinedload(models.Cart.rfid_tag)).filter(
        models.Cart.id == cart_id
    ).first()
    if not cart:
        raise HTTPException(404, "Kocsi nem található")
    history = db.query(models.CartMovement).filter(
        models.CartMovement.cart_id == cart_id
    ).order_by(models.CartMovement.moved_at.desc()).limit(30).all()
    d = _cart_dict(cart)
    d["history"] = [
        {
            "hk": m.hk_reader,
            "from": m.from_position,
            "to": m.to_position,
            "operator": m.operator,
            "moved_at": m.moved_at.isoformat() if m.moved_at else None,
        }
        for m in history
    ]
    return d


@router.post("/{cart_id}/move")
async def manual_move(
    request: Request,
    cart_id: int,
    to_position: str,
    operator: str = "kezelő",
    db: Session = Depends(get_db),
):
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(404, "Kocsi nem található")

    old_pos = cart.current_position
    now = datetime.now()
    cart.current_position = to_position
    cart.last_seen_at = now
    cart.updated_at = now
    if old_pos != to_position:
        cart.position_changed_at = now

    if to_position == "HÁTRALÉKOS":
        cart.status = "hátralékos"
    elif to_position == "KÉSZ":
        cart.status = "kész"
    else:
        cart.status = "aktív"

    mov = models.CartMovement(
        cart_id=cart_id,
        from_position=old_pos,
        to_position=to_position,
        operator=operator,
        notes="Kézi áthelyezés",
    )
    db.add(mov)
    db.commit()

    ws_manager = request.app.state.ws_manager
    asyncio.create_task(ws_manager.broadcast({
        "type": "cart_move",
        "cart_number": cart.cart_number,
        "from": old_pos,
        "to": to_position,
        "operator": operator,
    }))
    return {"ok": True, "from": old_pos, "to": to_position}


@router.post("/{cart_id}/assign-rfid")
def assign_rfid(cart_id: int, rfid_epc: str, db: Session = Depends(get_db)):
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(404, "Kocsi nem található")
    tag = db.query(models.RFIDTag).filter(models.RFIDTag.epc == rfid_epc).first()
    if not tag:
        tag = models.RFIDTag(epc=rfid_epc, tag_type="cart")
        db.add(tag)
        db.flush()
    cart.rfid_tag_id = tag.id
    db.commit()
    return {"ok": True}


@router.delete("/{cart_id}")
def delete_cart(cart_id: int, db: Session = Depends(get_db)):
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(404, "Kocsi nem található")
    cart.is_active = False
    db.commit()
    return {"ok": True}


# ── RFID esemény feldolgozása (HK01-HK10 webhook) ────────────────────────────
@router.post("/rfid-event")
async def process_rfid_event(
    request: Request,
    reader_id: str,
    tag_epc: str,
    rssi: float = -65.0,
    db: Session = Depends(get_db),
):
    """HK01-HK10 RFID olvasóktól jövő esemény feldolgozása."""
    now = datetime.now()

    # Olvasó státusz frissítése
    reader = db.query(models.RFIDReader).filter(
        models.RFIDReader.reader_id == reader_id
    ).first()
    if reader:
        reader.status = "online"
        reader.last_seen = now

    # Kocsi keresése RFID tag alapján
    tag = db.query(models.RFIDTag).filter(models.RFIDTag.epc == tag_epc).first()
    if not tag:
        db.commit()
        return {"ok": True, "processed": False, "reason": "Ismeretlen RFID tag"}

    cart = db.query(models.Cart).filter(
        models.Cart.rfid_tag_id == tag.id,
        models.Cart.is_active == True,
    ).first()

    if not cart:
        db.commit()
        return {"ok": True, "processed": False, "reason": "Nincs kocsi ehhez a taghoz rendelve"}

    old_position = cart.current_position
    new_position = HK_TO_POSITION.get(reader_id, old_position)

    cart.current_position = new_position
    cart.last_hk_reader = reader_id
    cart.last_seen_at = now
    cart.updated_at = now
    if old_position != new_position:
        cart.position_changed_at = now

    if new_position == "HÁTRALÉKOS":
        cart.status = "hátralékos"
    elif new_position == "KÉSZ":
        cart.status = "kész"
    else:
        cart.status = "aktív"

    mov = models.CartMovement(
        cart_id=cart.id,
        hk_reader=reader_id,
        from_position=old_position,
        to_position=new_position,
        notes=f"RFID: {reader_id} | RSSI: {rssi}",
    )
    db.add(mov)

    # RFIDEvent loggolás
    hk_info = HK_BY_ID.get(reader_id, {})
    db.add(models.RFIDEvent(
        reader_id=reader_id,
        reader_name=hk_info.get("name", reader_id),
        tag_epc=tag_epc,
        rssi=rssi,
        zone=hk_info.get("zone", ""),
        event_type="cart_move",
        processed=True,
    ))
    db.commit()

    ws_manager = request.app.state.ws_manager
    asyncio.create_task(ws_manager.broadcast({
        "type": "cart_move",
        "cart_number": cart.cart_number,
        "hk_reader": reader_id,
        "from": old_position,
        "to": new_position,
        "rssi": rssi,
    }))

    return {
        "ok": True,
        "processed": True,
        "cart_number": cart.cart_number,
        "from": old_position,
        "to": new_position,
    }


@router.get("/movements")
def list_movements(limit: int = 60, db: Session = Depends(get_db)):
    """Legutóbbi mozgások listája."""
    movements = db.query(models.CartMovement).options(
        joinedload(models.CartMovement.cart)
    ).order_by(models.CartMovement.moved_at.desc()).limit(limit).all()
    return [
        {
            "id": m.id,
            "cart_number": m.cart.cart_number if m.cart else "?",
            "from": m.from_position,
            "to": m.to_position,
            "operator": m.operator,
            "hk_reader": m.hk_reader,
            "moved_at": m.moved_at.isoformat() if m.moved_at else None,
        }
        for m in movements
    ]
