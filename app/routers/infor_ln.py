from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app import models

router = APIRouter()


@router.get("/sync-log")
def sync_log(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(models.InforLNSync).order_by(
        models.InforLNSync.synced_at.desc()
    ).limit(limit).all()
    return [
        {
            "id": l.id,
            "sync_type": l.sync_type,
            "direction": l.direction,
            "infor_ln_ref": l.infor_ln_ref,
            "status": l.status,
            "error_message": l.error_message,
            "synced_at": l.synced_at.isoformat() if l.synced_at else None,
        }
        for l in logs
    ]


@router.post("/hu-mapping")
def map_hu_to_rfid(
    hu_number: str,
    rfid_epc: str,
    pallet_number: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Map an Infor LN Handling Unit to an RFID EPC tag."""
    tag = db.query(models.RFIDTag).filter(models.RFIDTag.epc == rfid_epc).first()
    if not tag:
        tag = models.RFIDTag(epc=rfid_epc, tag_type="pallet", description=f"HU: {hu_number}")
        db.add(tag)
        db.flush()

    pallet = db.query(models.Pallet).filter(models.Pallet.infor_ln_hu == hu_number).first()
    if not pallet and pallet_number:
        pallet = db.query(models.Pallet).filter(
            models.Pallet.pallet_number == pallet_number
        ).first()

    if pallet:
        pallet.infor_ln_hu = hu_number
        pallet.rfid_tag_id = tag.id
        pallet.updated_at = datetime.now()

    log = models.InforLNSync(
        sync_type="hu_mapping",
        direction="inbound",
        infor_ln_ref=hu_number,
        payload=f'{{"hu": "{hu_number}", "epc": "{rfid_epc}"}}',
        status="success",
    )
    db.add(log)
    db.commit()
    return {"ok": True, "hu": hu_number, "epc": rfid_epc}


@router.post("/import-receipt")
def import_receipt(payload: dict, db: Session = Depends(get_db)):
    """Import incoming goods receipt from Infor LN (placeholder for real integration)."""
    log = models.InforLNSync(
        sync_type="receipt",
        direction="inbound",
        infor_ln_ref=payload.get("order_number", "N/A"),
        payload=str(payload),
        status="success",
    )
    db.add(log)
    db.commit()
    return {"ok": True, "message": "Bevételezési adat importálva (teszt)"}


@router.post("/export-movement")
def export_movement(movement_id: int, db: Session = Depends(get_db)):
    """Push movement data to Infor LN (placeholder)."""
    mov = db.query(models.Movement).filter(models.Movement.id == movement_id).first()
    if not mov:
        raise HTTPException(404, "Mozgás nem található")

    log = models.InforLNSync(
        sync_type="movement",
        direction="outbound",
        infor_ln_ref=str(movement_id),
        payload=f'{{"movement_id": {movement_id}, "action": "{mov.action}"}}',
        status="pending",
    )
    db.add(log)
    db.commit()
    return {"ok": True, "message": "Mozgás exportálva (szimulált – valódi integráció szükséges)"}


@router.get("/status")
def integration_status():
    return {
        "connected": False,
        "message": "Infor LN integráció konfigurálás alatt – jelenleg szimulált üzemmód",
        "next_steps": [
            "Infor LN ION API hitelesítő adatok konfigurálása",
            "HU ↔ RFID leképezés szinkronizálása",
            "Mozgások automatikus exportálásának beállítása",
        ],
    }
