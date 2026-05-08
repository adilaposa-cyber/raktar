from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
import random

from app.database import get_db
from app import models, schemas

router = APIRouter()


def _gen_task_number():
    return f"TSK-{datetime.now().strftime('%Y%m%d%H%M')}-{random.randint(100,999)}"


@router.get("/", response_model=List[schemas.TaskOut])
def list_tasks(
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    assigned_to: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.Task).options(
        joinedload(models.Task.pallet),
        joinedload(models.Task.from_location),
        joinedload(models.Task.to_location),
    )
    if status:
        q = q.filter(models.Task.status == status)
    if task_type:
        q = q.filter(models.Task.task_type == task_type)
    if assigned_to:
        q = q.filter(models.Task.assigned_to == assigned_to)
    return q.order_by(models.Task.priority, models.Task.created_at).all()


@router.post("/", response_model=schemas.TaskOut)
def create_task(data: schemas.TaskCreate, db: Session = Depends(get_db)):
    task = models.Task(**data.model_dump(), task_number=_gen_task_number())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Feladat nem található")
    return task


@router.patch("/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, data: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Feladat nem található")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/start")
def start_task(task_id: int, operator: str = "targoncás", db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Feladat nem található")
    task.status = "in_progress"
    task.assigned_to = operator
    task.started_at = datetime.now()
    db.commit()
    return {"ok": True, "task_number": task.task_number}


@router.post("/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Feladat nem található")

    task.status = "completed"
    task.completed_at = datetime.now()

    if task.pallet_id and task.to_location_id:
        pallet = db.query(models.Pallet).filter(models.Pallet.id == task.pallet_id).first()
        if pallet:
            if pallet.current_location_id:
                old_loc = db.query(models.Location).filter(
                    models.Location.id == pallet.current_location_id
                ).first()
                if old_loc:
                    old_loc.current_pallets = max(0, old_loc.current_pallets - 1)
                    old_loc.is_occupied = old_loc.current_pallets > 0

            new_loc = db.query(models.Location).filter(
                models.Location.id == task.to_location_id
            ).first()
            if new_loc:
                new_loc.current_pallets += 1
                new_loc.is_occupied = True

            pallet.current_location_id = task.to_location_id
            pallet.status = "in_storage"
            pallet.updated_at = datetime.now()

            mov = models.Movement(
                pallet_id=pallet.id,
                from_location_id=task.from_location_id,
                to_location_id=task.to_location_id,
                action=task.task_type,
                notes=f"Feladat teljesítve: {task.task_number}",
                operator=task.assigned_to,
            )
            db.add(mov)

    db.commit()
    return {"ok": True}


@router.post("/{task_id}/cancel")
def cancel_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Feladat nem található")
    task.status = "cancelled"
    db.commit()
    return {"ok": True}


@router.get("/suggest/storage-in/{pallet_id}")
def suggest_storage_in(pallet_id: int, db: Session = Depends(get_db)):
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
        preferred = q.filter(
            models.Location.zone == pallet.article.preferred_zone
        ).first()
        if preferred:
            return {"location": schemas.LocationOut.model_validate(preferred)}

    loc = q.first()
    if not loc:
        raise HTTPException(404, "Nincs szabad tárolóhely")
    return {"location": schemas.LocationOut.model_validate(loc)}
