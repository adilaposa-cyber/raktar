from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app import models, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.PhaseDefOut])
def list_phases(db: Session = Depends(get_db)):
    return db.query(models.PhaseDefinition).options(
        joinedload(models.PhaseDefinition.from_article),
        joinedload(models.PhaseDefinition.to_article),
        joinedload(models.PhaseDefinition.destination_location),
    ).filter(models.PhaseDefinition.is_active == True).all()


@router.post("/", response_model=schemas.PhaseDefOut)
def create_phase(data: schemas.PhaseDefCreate, db: Session = Depends(get_db)):
    obj = models.PhaseDefinition(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{phase_id}", response_model=schemas.PhaseDefOut)
def get_phase(phase_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.PhaseDefinition).options(
        joinedload(models.PhaseDefinition.from_article),
        joinedload(models.PhaseDefinition.to_article),
        joinedload(models.PhaseDefinition.destination_location),
    ).filter(models.PhaseDefinition.id == phase_id).first()
    if not obj:
        raise HTTPException(404, "Fázis definíció nem található")
    return obj


@router.put("/{phase_id}", response_model=schemas.PhaseDefOut)
def update_phase(phase_id: int, data: schemas.PhaseDefCreate, db: Session = Depends(get_db)):
    obj = db.query(models.PhaseDefinition).filter(models.PhaseDefinition.id == phase_id).first()
    if not obj:
        raise HTTPException(404, "Fázis definíció nem található")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{phase_id}")
def delete_phase(phase_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.PhaseDefinition).filter(models.PhaseDefinition.id == phase_id).first()
    if not obj:
        raise HTTPException(404, "Fázis definíció nem található")
    obj.is_active = False
    db.commit()
    return {"ok": True}


@router.get("/for-article/{article_id}", response_model=List[schemas.PhaseDefOut])
def phases_for_article(article_id: int, db: Session = Depends(get_db)):
    return db.query(models.PhaseDefinition).options(
        joinedload(models.PhaseDefinition.from_article),
        joinedload(models.PhaseDefinition.to_article),
        joinedload(models.PhaseDefinition.destination_location),
    ).filter(
        models.PhaseDefinition.from_article_id == article_id,
        models.PhaseDefinition.is_active == True,
    ).all()
