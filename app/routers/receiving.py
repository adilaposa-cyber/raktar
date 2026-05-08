from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
import random

from app.database import get_db
from app import models, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.ReceivingOrderOut])
def list_orders(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.ReceivingOrder).options(joinedload(models.ReceivingOrder.article))
    if status:
        q = q.filter(models.ReceivingOrder.status == status)
    return q.order_by(models.ReceivingOrder.created_at.desc()).all()


@router.post("/", response_model=schemas.ReceivingOrderOut)
def create_order(data: schemas.ReceivingOrderCreate, db: Session = Depends(get_db)):
    existing = db.query(models.ReceivingOrder).filter(
        models.ReceivingOrder.order_number == data.order_number
    ).first()
    if existing:
        raise HTTPException(400, "Ez a rendelésszám már létezik")
    obj = models.ReceivingOrder(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{order_id}", response_model=schemas.ReceivingOrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.ReceivingOrder).options(
        joinedload(models.ReceivingOrder.article)
    ).filter(models.ReceivingOrder.id == order_id).first()
    if not obj:
        raise HTTPException(404, "Rendelés nem található")
    return obj


@router.post("/{order_id}/receive")
def receive_goods(order_id: int, data: schemas.ReceiveGoods, db: Session = Depends(get_db)):
    order = db.query(models.ReceivingOrder).options(
        joinedload(models.ReceivingOrder.article)
    ).filter(models.ReceivingOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "Rendelés nem található")
    if order.status == "complete":
        raise HTTPException(400, "Ez a rendelés már lezárva")

    order.received_quantity = (order.received_quantity or 0) + data.quantity
    order.received_date = datetime.now()

    if order.received_quantity >= order.expected_quantity:
        order.status = "complete"
    else:
        order.status = "partial"

    # Create pallet
    pallet_num = data.pallet_number or f"RAK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    pallet = models.Pallet(
        pallet_number=pallet_num,
        article_id=order.article_id,
        quantity=data.quantity,
        unit=order.unit or "db",
        status="at_receiving",
        notes=f"Bevételezve: {order.order_number}",
    )
    db.add(pallet)
    db.flush()

    # Assign RFID tag if EPC provided
    if data.rfid_epc:
        tag = db.query(models.RFIDTag).filter(models.RFIDTag.epc == data.rfid_epc).first()
        if not tag:
            tag = models.RFIDTag(epc=data.rfid_epc, tag_type="pallet")
            db.add(tag)
            db.flush()
        pallet.rfid_tag_id = tag.id

    # Find target location & create put-away task
    target_loc = None
    if order.target_zone:
        target_loc = db.query(models.Location).filter(
            models.Location.is_active == True,
            models.Location.zone_type == "storage",
            models.Location.zone == order.target_zone,
            models.Location.current_pallets < models.Location.max_pallets,
        ).first()

    task_num = f"TSK-{datetime.now().strftime('%Y%m%d%H%M')}-{random.randint(100,999)}"
    task = models.Task(
        task_number=task_num,
        task_type="storage_in",
        pallet_id=pallet.id,
        to_location_id=target_loc.id if target_loc else None,
        to_zone=order.target_zone,
        priority=4,
        assigned_to=data.operator,
        notes=f"Betárolás: {order.order_number} – {pallet_num}",
    )
    db.add(task)
    db.commit()

    return {
        "ok": True,
        "pallet_number": pallet_num,
        "task_number": task_num,
        "suggested_location": target_loc.code if target_loc else None,
        "order_status": order.status,
    }


@router.patch("/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.ReceivingOrder).filter(models.ReceivingOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "Rendelés nem található")
    order.status = "cancelled"
    db.commit()
    return {"ok": True}
