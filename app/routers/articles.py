from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.ArticleOut])
def list_articles(db: Session = Depends(get_db)):
    return db.query(models.Article).filter(models.Article.is_active == True).all()


@router.post("/", response_model=schemas.ArticleOut)
def create_article(data: schemas.ArticleCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Article).filter(
        models.Article.article_number == data.article_number
    ).first()
    if existing:
        raise HTTPException(400, "Ez a cikkszám már létezik")
    obj = models.Article(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{article_id}", response_model=schemas.ArticleOut)
def get_article(article_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not obj:
        raise HTTPException(404, "Cikk nem található")
    return obj


@router.put("/{article_id}", response_model=schemas.ArticleOut)
def update_article(article_id: int, data: schemas.ArticleCreate, db: Session = Depends(get_db)):
    obj = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not obj:
        raise HTTPException(404, "Cikk nem található")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not obj:
        raise HTTPException(404, "Cikk nem található")
    obj.is_active = False
    db.commit()
    return {"ok": True}
