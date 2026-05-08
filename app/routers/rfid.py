from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import asyncio

from app.database import get_db
from app import models, schemas

router = APIRouter()


# ── Readers ────────────────────────────────────────────────────────────────────
@router.get("/readers", response_model=List[schemas.RFIDReaderOut])
def list_readers(db: Session = Depends(get_db)):
    return db.query(models.RFIDReader).filter(models.RFIDReader.is_active == True).all()


@router.post("/readers", response_model=schemas.RFIDReaderOut)
def create_reader(data: schemas.RFIDReaderCreate, db: Session = Depends(get_db)):
    existing = db.query(models.RFIDReader).filter(
        models.RFIDReader.reader_id == data.reader_id
    ).first()
    if existing:
        raise HTTPException(400, "Ez az olvasó ID már létezik")
    obj = models.RFIDReader(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/readers/{reader_id}/status")
def update_reader_status(reader_id: str, status: str, db: Session = Depends(get_db)):
    reader = db.query(models.RFIDReader).filter(
        models.RFIDReader.reader_id == reader_id
    ).first()
    if not reader:
        raise HTTPException(404, "Olvasó nem található")
    reader.status = status
    reader.last_seen = datetime.now()
    db.commit()
    return {"ok": True}


@router.delete("/readers/{reader_id}")
def delete_reader(reader_id: str, db: Session = Depends(get_db)):
    reader = db.query(models.RFIDReader).filter(
        models.RFIDReader.reader_id == reader_id
    ).first()
    if not reader:
        raise HTTPException(404, "Olvasó nem található")
    reader.is_active = False
    db.commit()
    return {"ok": True}


# ── Tags ───────────────────────────────────────────────────────────────────────
@router.get("/tags", response_model=List[schemas.RFIDTagOut])
def list_tags(db: Session = Depends(get_db)):
    return db.query(models.RFIDTag).filter(models.RFIDTag.is_active == True).all()


@router.post("/tags", response_model=schemas.RFIDTagOut)
def create_tag(data: schemas.RFIDTagCreate, db: Session = Depends(get_db)):
    existing = db.query(models.RFIDTag).filter(models.RFIDTag.epc == data.epc).first()
    if existing:
        raise HTTPException(400, "Ez az EPC már létezik")
    obj = models.RFIDTag(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/tags/{tag_id}/assign/{pallet_id}")
def assign_tag_to_pallet(tag_id: int, pallet_id: int, db: Session = Depends(get_db)):
    tag = db.query(models.RFIDTag).filter(models.RFIDTag.id == tag_id).first()
    if not tag:
        raise HTTPException(404, "Tag nem található")
    pallet = db.query(models.Pallet).filter(models.Pallet.id == pallet_id).first()
    if not pallet:
        raise HTTPException(404, "Raklap nem található")
    if tag.pallet and tag.pallet.id != pallet_id:
        raise HTTPException(400, "Ez a tag már hozzá van rendelve egy másik raklaphoz")
    pallet.rfid_tag_id = tag.id
    db.commit()
    return {"ok": True}


@router.post("/tags/{tag_id}/unassign")
def unassign_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(models.RFIDTag).filter(models.RFIDTag.id == tag_id).first()
    if not tag:
        raise HTTPException(404, "Tag nem található")
    if tag.pallet:
        tag.pallet.rfid_tag_id = None
        db.commit()
    return {"ok": True}


# ── Webhook from ATR7000 ───────────────────────────────────────────────────────
@router.post("/event")
async def rfid_event(request: Request, data: schemas.RFIDWebhookEvent, db: Session = Depends(get_db)):
    """ATR7000 reader HTTP webhook endpoint – called when tag is detected."""
    now = datetime.now()

    # Update or mark reader as online
    reader = db.query(models.RFIDReader).filter(
        models.RFIDReader.reader_id == data.reader_id
    ).first()
    reader_name = data.reader_id
    if reader:
        reader.status = "online"
        reader.last_seen = now
        reader_name = reader.name

    # Store event
    event = models.RFIDEvent(
        reader_id=data.reader_id,
        reader_name=reader_name,
        tag_epc=data.tag_epc,
        rssi=data.rssi,
        zone=data.zone or (reader.zone if reader else None),
        event_type=data.event_type,
        timestamp=data.timestamp or now,
    )
    db.add(event)

    # Update tag
    tag = db.query(models.RFIDTag).filter(models.RFIDTag.epc == data.tag_epc).first()
    zone = data.zone or (reader.zone if reader else None)
    if tag:
        tag.last_seen = now
        tag.last_seen_zone = zone
        tag.last_rssi = data.rssi

        # Update pallet status
        if tag.pallet:
            pallet = tag.pallet
            if pallet.status != "in_storage":
                pallet.status = "in_transit"
                pallet.updated_at = now

            # Log movement if zone changed
            if pallet.status == "in_transit":
                mov = models.Movement(
                    pallet_id=pallet.id,
                    rfid_tag_epc=data.tag_epc,
                    to_zone=zone,
                    action="rfid_scan",
                    notes=f"RFID detektálva – olvasó: {reader_name}, RSSI: {data.rssi}",
                )
                db.add(mov)

    db.commit()

    # Broadcast to WebSocket clients
    ws_manager = request.app.state.ws_manager
    payload = {
        "type": "rfid_event",
        "reader_id": data.reader_id,
        "reader_name": reader_name,
        "tag_epc": data.tag_epc,
        "zone": zone,
        "rssi": data.rssi,
        "pallet_number": tag.pallet.pallet_number if (tag and tag.pallet) else None,
        "timestamp": now.isoformat(),
    }
    asyncio.create_task(ws_manager.broadcast(payload))

    return {"ok": True, "processed": tag is not None}


# ── Recent events ──────────────────────────────────────────────────────────────
@router.get("/events")
def list_events(limit: int = 50, db: Session = Depends(get_db)):
    events = db.query(models.RFIDEvent).order_by(
        models.RFIDEvent.timestamp.desc()
    ).limit(limit).all()
    return [
        {
            "id": e.id,
            "reader_id": e.reader_id,
            "reader_name": e.reader_name,
            "tag_epc": e.tag_epc,
            "zone": e.zone,
            "rssi": e.rssi,
            "event_type": e.event_type,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        }
        for e in events
    ]


# ── Simulate event (dev/test) ─────────────────────────────────────────────────
@router.post("/simulate")
async def simulate_event(
    request: Request,
    tag_epc: str,
    zone: str = "A",
    rssi: float = -65.0,
    reader_id: str = "SIM-001",
    db: Session = Depends(get_db),
):
    fake = schemas.RFIDWebhookEvent(
        reader_id=reader_id,
        tag_epc=tag_epc,
        rssi=rssi,
        zone=zone,
        event_type="read",
    )
    return await rfid_event(request, fake, db)
