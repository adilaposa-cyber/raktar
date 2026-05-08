from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
import random

from app.database import get_db
from app import models, schemas

router = APIRouter()


@router.get("/stats/summary")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(models.Pallet).filter(models.Pallet.is_active == True).count()
    in_storage = db.query(models.Pallet).filter(
        models.Pallet.is_active == True, models.Pallet.status == "in_storage"
    ).count()
    in_transit = db.query(models.Pallet).filter(
        models.Pallet.is_active == True, models.Pallet.status == "in_transit"
    ).count()
    total_locs = db.query(models.Location).filter(
        models.Location.is_active == True, models.Location.zone_type == "storage"
    ).count()
    occupied_locs = db.query(models.Location).filter(
        models.Location.is_active == True, models.Location.is_occupied == True
    ).count()
    pending_tasks = db.query(models.Task).filter(
        models.Task.status.in_(["pending", "assigned", "in_progress"])
    ).count()
    active_readers = db.query(models.RFIDReader).filter(
        models.RFIDReader.status == "online"
    ).count()
    return {
        "total_pallets": total,
        "in_storage": in_storage,
        "in_transit": in_transit,
        "total_locations": total_locs,
        "occupied_locations": occupied_locs,
        "utilization_pct": round(occupied_locs / total_locs * 100, 1) if total_locs > 0 else 0,
        "pending_tasks": pending_tasks,
        "active_readers": active_readers,
    }


@router.get("/recent-movements")
def recent_movements(limit: int = 20, db: Session = Depends(get_db)):
    movs = db.query(models.Movement).options(
        joinedload(models.Movement.pallet),
        joinedload(models.Movement.from_location),
        joinedload(models.Movement.to_location),
    ).order_by(models.Movement.moved_at.desc()).limit(limit).all()
    return [
        {
            "id": m.id,
            "pallet_number": m.pallet.pallet_number if m.pallet else "–",
            "action": m.action,
            "from": m.from_location.code if m.from_location else m.from_zone or "–",
            "to": m.to_location.code if m.to_location else m.to_zone or "–",
            "operator": m.operator or "–",
            "moved_at": m.moved_at.isoformat() if m.moved_at else None,
        }
        for m in movs
    ]


@router.get("/", response_model=List[schemas.PalletList])
def list_pallets(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.Pallet).options(
        joinedload(models.Pallet.article),
        joinedload(models.Pallet.current_location),
        joinedload(models.Pallet.rfid_tag),
    ).filter(models.Pallet.is_active == True)

    if search:
        q = q.filter(
            or_(
                models.Pallet.pallet_number.ilike(f"%{search}%"),
                models.Pallet.infor_ln_hu.ilike(f"%{search}%"),
                models.Pallet.batch_number.ilike(f"%{search}%"),
            )
        )
    if status:
        q = q.filter(models.Pallet.status == status)

    return q.order_by(models.Pallet.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=schemas.PalletDetail)
def create_pallet(data: schemas.PalletCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Pallet).filter(
        models.Pallet.pallet_number == data.pallet_number
    ).first()
    if existing:
        raise HTTPException(400, "Ez a raklap szám már létezik")
    pallet = models.Pallet(**data.model_dump())
    db.add(pallet)
    db.commit()
    db.refresh(pallet)
    return pallet


@router.get("/{pallet_id}", response_model=schemas.PalletDetail)
def get_pallet(pallet_id: int, db: Session = Depends(get_db)):
    pallet = db.query(models.Pallet).options(
        joinedload(models.Pallet.article),
        joinedload(models.Pallet.current_location),
        joinedload(models.Pallet.rfid_tag),
        joinedload(models.Pallet.movements).joinedload(models.Movement.from_location),
        joinedload(models.Pallet.movements).joinedload(models.Movement.to_location),
        joinedload(models.Pallet.tasks).joinedload(models.Task.from_location),
        joinedload(models.Pallet.tasks).joinedload(models.Task.to_location),
    ).filter(models.Pallet.id == pallet_id).first()
    if not pallet:
        raise HTTPException(404, "Raklap nem található")
    return pallet


@router.put("/{pallet_id}", response_model=schemas.PalletDetail)
def update_pallet(pallet_id: int, data: schemas.PalletUpdate, db: Session = Depends(get_db)):
    pallet = db.query(models.Pallet).filter(models.Pallet.id == pallet_id).first()
    if not pallet:
        raise HTTPException(404, "Raklap nem található")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(pallet, k, v)
    pallet.updated_at = datetime.now()
    db.commit()
    db.refresh(pallet)
    return pallet


@router.delete("/{pallet_id}")
def delete_pallet(pallet_id: int, db: Session = Depends(get_db)):
    pallet = db.query(models.Pallet).filter(models.Pallet.id == pallet_id).first()
    if not pallet:
        raise HTTPException(404, "Raklap nem található")
    pallet.is_active = False
    db.commit()
    return {"ok": True}


@router.post("/{pallet_id}/move")
def move_pallet(pallet_id: int, data: schemas.PalletMove, db: Session = Depends(get_db)):
    pallet = db.query(models.Pallet).options(
        joinedload(models.Pallet.rfid_tag)
    ).filter(models.Pallet.id == pallet_id).first()
    if not pallet:
        raise HTTPException(404, "Raklap nem található")

    old_loc_id = pallet.current_location_id
    if old_loc_id:
        old_loc = db.query(models.Location).filter(models.Location.id == old_loc_id).first()
        if old_loc:
            old_loc.current_pallets = max(0, old_loc.current_pallets - 1)
            old_loc.is_occupied = old_loc.current_pallets > 0

    if data.to_location_id:
        new_loc = db.query(models.Location).filter(models.Location.id == data.to_location_id).first()
        if new_loc:
            new_loc.current_pallets += 1
            new_loc.is_occupied = True
            pallet.status = "in_storage"
    else:
        pallet.status = "in_transit"

    pallet.current_location_id = data.to_location_id
    pallet.updated_at = datetime.now()

    mov = models.Movement(
        pallet_id=pallet_id,
        rfid_tag_epc=pallet.rfid_tag.epc if pallet.rfid_tag else None,
        from_location_id=old_loc_id,
        to_location_id=data.to_location_id,
        to_zone=data.to_zone,
        action="transfer",
        notes=data.notes,
        operator=data.operator,
    )
    db.add(mov)
    db.commit()
    return {"ok": True}


@router.post("/{pallet_id}/phase-change")
def phase_change(pallet_id: int, data: schemas.PhaseChange, db: Session = Depends(get_db)):
    pallet = db.query(models.Pallet).filter(models.Pallet.id == pallet_id).first()
    if not pallet:
        raise HTTPException(404, "Raklap nem található")

    phase = db.query(models.PhaseDefinition).filter(
        models.PhaseDefinition.id == data.phase_definition_id,
        models.PhaseDefinition.is_active == True,
    ).first()
    if not phase:
        raise HTTPException(404, "Fázis definíció nem található")

    old_article_id = pallet.article_id
    pallet.article_id = phase.to_article_id
    pallet.updated_at = datetime.now()

    mov = models.Movement(
        pallet_id=pallet_id,
        action="phase_change",
        notes=f"Fázisváltás: {phase.name} ({old_article_id} → {phase.to_article_id})",
        operator=data.operator,
    )
    db.add(mov)

    if phase.auto_task_create and phase.destination_location_id:
        task_num = f"TSK-{datetime.now().strftime('%Y%m%d%H%M')}-{random.randint(100,999)}"
        task = models.Task(
            task_number=task_num,
            task_type="phase_change",
            pallet_id=pallet_id,
            from_location_id=pallet.current_location_id,
            to_location_id=phase.destination_location_id,
            to_zone=phase.destination_zone,
            priority=3,
            notes=f"Automatikus feladat – {phase.name}",
        )
        db.add(task)

    db.commit()
    return {"ok": True, "message": "Fázisváltás sikeres"}


@router.post("/{pallet_id}/auto-storage-in")
def auto_storage_in(pallet_id: int, operator: str = "rendszer", db: Session = Depends(get_db)):
    pallet = db.query(models.Pallet).options(
        joinedload(models.Pallet.article)
    ).filter(models.Pallet.id == pallet_id).first()
    if not pallet:
        raise HTTPException(404, "Raklap nem található")

    q = db.query(models.Location).filter(
        models.Location.is_active == True,
        models.Location.zone_type == "storage",
        models.Location.current_pallets < models.Location.max_pallets,
    )
    if pallet.article and pallet.article.preferred_zone:
        preferred = q.filter(models.Location.zone == pallet.article.preferred_zone).first()
        loc = preferred or q.first()
    else:
        loc = q.first()

    if not loc:
        raise HTTPException(404, "Nincs szabad tárolóhely")

    task_num = f"TSK-{datetime.now().strftime('%Y%m%d%H%M')}-{random.randint(100,999)}"
    task = models.Task(
        task_number=task_num,
        task_type="storage_in",
        pallet_id=pallet_id,
        from_location_id=pallet.current_location_id,
        to_location_id=loc.id,
        to_zone=loc.zone,
        priority=4,
        assigned_to=operator,
        notes=f"Automatikus betárolás – javasolt hely: {loc.code}",
    )
    db.add(task)
    pallet.status = "in_transit"
    pallet.updated_at = datetime.now()
    db.commit()
    db.refresh(task)
    return {"ok": True, "task_number": task.task_number, "suggested_location": loc.code}
