from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import asyncio

from app.database import get_db
from app import models

router = APIRouter()


def _op_dict(op: models.ForkliftOperator) -> dict:
    return {
        "id": op.id, "name": op.name, "employee_id": op.employee_id,
        "rfid_epc": op.rfid_epc, "forklift_number": op.forklift_number,
        "is_active": op.is_active,
    }


def _session_dict(s: models.ForkliftSession) -> dict:
    return {
        "id": s.id,
        "operator_id": s.operator_id,
        "operator_name": s.operator.name if s.operator else "–",
        "forklift_number": s.forklift_number,
        "started_at": s.started_at.isoformat() if s.started_at else None,
        "ended_at": s.ended_at.isoformat() if s.ended_at else None,
        "last_activity": s.last_activity.isoformat() if s.last_activity else None,
        "active": s.ended_at is None,
    }


# ── Kezelők CRUD ──────────────────────────────────────────────────────────────
@router.get("/operators")
def list_operators(db: Session = Depends(get_db)):
    return [_op_dict(op) for op in
            db.query(models.ForkliftOperator).filter(models.ForkliftOperator.is_active == True).all()]


@router.post("/operators")
def create_operator(
    name: str,
    employee_id: str,
    rfid_epc: Optional[str] = None,
    pin_code: Optional[str] = None,
    forklift_number: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if db.query(models.ForkliftOperator).filter(models.ForkliftOperator.employee_id == employee_id).first():
        raise HTTPException(400, "Ez az alkalmazotti szám már létezik")
    if rfid_epc and db.query(models.ForkliftOperator).filter(models.ForkliftOperator.rfid_epc == rfid_epc).first():
        raise HTTPException(400, "Ez az RFID EPC már hozzá van rendelve")
    op = models.ForkliftOperator(
        name=name, employee_id=employee_id, rfid_epc=rfid_epc,
        pin_code=pin_code, forklift_number=forklift_number,
    )
    db.add(op)
    db.commit()
    db.refresh(op)
    return _op_dict(op)


@router.put("/operators/{oid}")
def update_operator(
    oid: int,
    name: Optional[str] = None,
    rfid_epc: Optional[str] = None,
    pin_code: Optional[str] = None,
    forklift_number: Optional[str] = None,
    db: Session = Depends(get_db),
):
    op = db.query(models.ForkliftOperator).filter(models.ForkliftOperator.id == oid).first()
    if not op:
        raise HTTPException(404, "Kezelő nem található")
    if name:
        op.name = name
    if rfid_epc is not None:
        op.rfid_epc = rfid_epc
    if pin_code is not None:
        op.pin_code = pin_code
    if forklift_number is not None:
        op.forklift_number = forklift_number
    db.commit()
    return _op_dict(op)


@router.delete("/operators/{oid}")
def delete_operator(oid: int, db: Session = Depends(get_db)):
    op = db.query(models.ForkliftOperator).filter(models.ForkliftOperator.id == oid).first()
    if not op:
        raise HTTPException(404, "Kezelő nem található")
    op.is_active = False
    db.commit()
    return {"ok": True}


# ── Bejelentkezés ─────────────────────────────────────────────────────────────
@router.post("/login")
async def login(
    request: Request,
    rfid_epc: Optional[str] = None,
    pin_code: Optional[str] = None,
    forklift_number: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """RFID kártyával vagy PIN-nel belépés."""
    op = None
    if rfid_epc:
        op = db.query(models.ForkliftOperator).filter(
            models.ForkliftOperator.rfid_epc == rfid_epc,
            models.ForkliftOperator.is_active == True,
        ).first()
    elif pin_code:
        op = db.query(models.ForkliftOperator).filter(
            models.ForkliftOperator.pin_code == pin_code,
            models.ForkliftOperator.is_active == True,
        ).first()

    if not op:
        raise HTTPException(401, "Ismeretlen RFID vagy helytelen PIN")

    # Korábbi aktív szekció lezárása
    old = db.query(models.ForkliftSession).filter(
        models.ForkliftSession.operator_id == op.id,
        models.ForkliftSession.ended_at == None,
    ).first()
    if old:
        old.ended_at = datetime.now()

    # Új szekció
    sess = models.ForkliftSession(
        operator_id=op.id,
        forklift_number=forklift_number or op.forklift_number,
        last_activity=datetime.now(),
    )
    db.add(sess)
    db.commit()
    db.refresh(sess)

    ws_manager = request.app.state.ws_manager
    asyncio.create_task(ws_manager.broadcast({
        "type": "forklift_login",
        "operator": op.name,
        "forklift": sess.forklift_number,
    }))

    return {
        "ok": True,
        "session_id": sess.id,
        "operator": _op_dict(op),
        "forklift_number": sess.forklift_number,
    }


@router.post("/logout/{session_id}")
async def logout(session_id: int, request: Request, db: Session = Depends(get_db)):
    sess = db.query(models.ForkliftSession).filter(models.ForkliftSession.id == session_id).first()
    if not sess:
        raise HTTPException(404, "Szekció nem található")
    sess.ended_at = datetime.now()
    db.commit()

    ws_manager = request.app.state.ws_manager
    asyncio.create_task(ws_manager.broadcast({
        "type": "forklift_logout",
        "operator": sess.operator.name if sess.operator else "–",
    }))
    return {"ok": True}


@router.get("/sessions/active")
def active_sessions(db: Session = Depends(get_db)):
    sessions = db.query(models.ForkliftSession).filter(
        models.ForkliftSession.ended_at == None
    ).all()
    return [_session_dict(s) for s in sessions]


@router.get("/sessions/history")
def session_history(limit: int = 50, db: Session = Depends(get_db)):
    sessions = db.query(models.ForkliftSession).order_by(
        models.ForkliftSession.started_at.desc()
    ).limit(limit).all()
    return [_session_dict(s) for s in sessions]


# ── Feladatok targoncásnak ────────────────────────────────────────────────────
@router.get("/tasks/{session_id}")
def get_forklift_tasks(session_id: int, db: Session = Depends(get_db)):
    sess = db.query(models.ForkliftSession).filter(models.ForkliftSession.id == session_id).first()
    if not sess:
        raise HTTPException(404, "Szekció nem található")

    tasks = db.query(models.Task).filter(
        models.Task.status.in_(["pending", "in_progress"]),
        models.Task.task_type == "move",
    ).order_by(models.Task.priority.asc(), models.Task.created_at.asc()).limit(20).all()

    return [
        {
            "id": t.id,
            "task_number": t.task_number,
            "task_type": t.task_type,
            "from_zone": t.from_zone,
            "to_zone": t.to_zone,
            "priority": t.priority,
            "status": t.status,
            "notes": t.notes,
            "pallet_number": t.pallet.pallet_number if t.pallet else None,
        }
        for t in tasks
    ]


@router.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: int, session_id: int, request: Request,
    db: Session = Depends(get_db),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Feladat nem található")
    sess = db.query(models.ForkliftSession).filter(models.ForkliftSession.id == session_id).first()
    if not sess:
        raise HTTPException(404, "Szekció nem található")

    task.status = "completed"
    task.completed_at = datetime.now()
    task.assigned_to = sess.operator.name if sess.operator else "targoncás"
    sess.last_activity = datetime.now()
    db.commit()

    ws_manager = request.app.state.ws_manager
    asyncio.create_task(ws_manager.broadcast({
        "type": "task_completed",
        "task_id": task_id,
        "operator": sess.operator.name if sess.operator else "–",
    }))
    return {"ok": True}
