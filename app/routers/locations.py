from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import models, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.LocationOut])
def list_locations(
    zone: Optional[str] = None,
    zone_type: Optional[str] = None,
    free_only: bool = False,
    db: Session = Depends(get_db),
):
    q = db.query(models.Location).filter(models.Location.is_active == True)
    if zone:
        q = q.filter(models.Location.zone == zone)
    if zone_type:
        q = q.filter(models.Location.zone_type == zone_type)
    if free_only:
        q = q.filter(models.Location.current_pallets < models.Location.max_pallets)
    return q.order_by(models.Location.zone, models.Location.row, models.Location.col).all()


@router.post("/", response_model=schemas.LocationOut)
def create_location(data: schemas.LocationCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Location).filter(models.Location.code == data.code).first()
    if existing:
        raise HTTPException(400, "Ez a helykód már létezik")
    obj = models.Location(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/bulk-create")
def bulk_create_locations(
    zone: str,
    zone_type: str = "storage",
    rows: int = 10,
    cols: int = 5,
    levels: int = 1,
    rfid_reader_zone: Optional[str] = None,
    db: Session = Depends(get_db),
):
    created = 0
    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            for lv in range(1, levels + 1):
                code = f"{zone}-{r:02d}-{c:02d}" if levels == 1 else f"{zone}-{r:02d}-{c:02d}-{lv}"
                existing = db.query(models.Location).filter(models.Location.code == code).first()
                if not existing:
                    loc = models.Location(
                        code=code,
                        zone=zone,
                        zone_type=zone_type,
                        row=r,
                        col=c,
                        level=lv,
                        rfid_reader_zone=rfid_reader_zone,
                    )
                    db.add(loc)
                    created += 1
    db.commit()
    return {"created": created}


@router.get("/{location_id}", response_model=schemas.LocationOut)
def get_location(location_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Location).filter(models.Location.id == location_id).first()
    if not obj:
        raise HTTPException(404, "Hely nem található")
    return obj


@router.put("/{location_id}", response_model=schemas.LocationOut)
def update_location(location_id: int, data: schemas.LocationCreate, db: Session = Depends(get_db)):
    obj = db.query(models.Location).filter(models.Location.id == location_id).first()
    if not obj:
        raise HTTPException(404, "Hely nem található")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{location_id}/pallets")
def get_location_pallets(location_id: int, db: Session = Depends(get_db)):
    pallets = db.query(models.Pallet).filter(
        models.Pallet.current_location_id == location_id,
        models.Pallet.is_active == True,
    ).all()
    return pallets


@router.get("/map/grid")
def get_map_grid(db: Session = Depends(get_db)):
    locations = db.query(models.Location).filter(models.Location.is_active == True).all()
    result = []
    for loc in locations:
        result.append({
            "id": loc.id,
            "code": loc.code,
            "zone": loc.zone,
            "zone_type": loc.zone_type,
            "row": loc.row,
            "col": loc.col,
            "level": loc.level,
            "is_occupied": loc.is_occupied,
            "current_pallets": loc.current_pallets,
            "max_pallets": loc.max_pallets,
        })
    return result
