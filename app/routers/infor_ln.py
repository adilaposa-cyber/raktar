from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import csv
import io

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


# ── CSV Import ────────────────────────────────────────────────────────────────
@router.post("/import-csv")
async def import_csv(
    import_type: str = "inventory",
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    CSV fájl importálása az Infor LN-ből.

    Támogatott típusok:
    - inventory : Cikkszám, Megnevezés, Mennyiség, Egység, Telephely, Helyszín
    - articles  : Cikkszám, Megnevezés, Egység, Megjegyzés
    - orders    : Rendelésszám, Cikkszám, Mennyiség, Határidő, Szállító
    """
    content = await file.read()
    text = content.decode("utf-8-sig", errors="replace")

    log = models.InforCSVImport(
        filename=file.filename,
        import_type=import_type,
        status="running",
    )
    db.add(log)
    db.flush()

    errors = []
    imported = 0
    total = 0

    try:
        reader = csv.DictReader(io.StringIO(text), delimiter=";")
        # Ha pontosvessző nem működik, próbáld vesszővel
        rows = list(reader)
        if len(rows) == 0 or (len(rows[0]) == 1):
            reader = csv.DictReader(io.StringIO(text), delimiter=",")
            rows = list(reader)

        # Mezőnév normalizálás (kis-nagybetű, szóközök)
        def norm(row: dict) -> dict:
            return {k.strip().lower(): v.strip() if v else "" for k, v in row.items()}

        for i, raw_row in enumerate(rows):
            total += 1
            row = norm(raw_row)
            try:
                if import_type == "articles":
                    _import_article_row(row, db)
                elif import_type == "inventory":
                    _import_inventory_row(row, db)
                elif import_type == "orders":
                    _import_order_row(row, db)
                imported += 1
            except Exception as e:
                errors.append(f"Sor {i+2}: {e}")

        db.flush()

        # LN sync napló
        db.add(models.InforLNSync(
            sync_type=f"csv_{import_type}",
            direction="inbound",
            infor_ln_ref=file.filename,
            payload=f"total={total}, imported={imported}, errors={len(errors)}",
            status="success" if not errors else "partial",
        ))

        log.rows_total = total
        log.rows_imported = imported
        log.rows_error = len(errors)
        log.status = "success" if not errors else "partial"
        log.error_log = "\n".join(errors[:50]) if errors else None
        db.commit()

    except Exception as e:
        log.status = "error"
        log.error_log = str(e)
        db.commit()
        raise HTTPException(500, f"CSV feldolgozási hiba: {e}")

    return {
        "ok": True,
        "filename": file.filename,
        "import_type": import_type,
        "total": total,
        "imported": imported,
        "errors": len(errors),
        "error_samples": errors[:10],
    }


def _import_article_row(row: dict, db: Session):
    """articles típus: cikkszám, megnevezés, egység"""
    # Lehetséges fejléc nevek Infor LN exportból
    num = row.get("cikkszám") or row.get("item") or row.get("article") or row.get("cikk")
    name = row.get("megnevezés") or row.get("description") or row.get("name") or row.get("leiras")
    unit = row.get("egység") or row.get("unit") or row.get("me") or "db"

    if not num:
        raise ValueError("Hiányzó cikkszám")

    existing = db.query(models.Article).filter(models.Article.article_number == num).first()
    if existing:
        if name:
            existing.name = name
        if unit:
            existing.unit = unit
    else:
        db.add(models.Article(
            article_number=num,
            name=name or num,
            unit=unit,
        ))


def _import_inventory_row(row: dict, db: Session):
    """inventory típus: cikkszám, megnevezés, mennyiség, egység, helyszín"""
    num = row.get("cikkszám") or row.get("item") or row.get("article") or row.get("cikk")
    name = row.get("megnevezés") or row.get("description") or row.get("leiras") or num
    qty_str = row.get("mennyiség") or row.get("quantity") or row.get("qty") or "0"
    unit = row.get("egység") or row.get("unit") or row.get("me") or "db"
    location_code = row.get("helyszín") or row.get("location") or row.get("hely") or ""
    hu_number = row.get("hu") or row.get("handling unit") or row.get("raklap") or ""

    if not num:
        raise ValueError("Hiányzó cikkszám")

    try:
        qty = float(qty_str.replace(",", "."))
    except ValueError:
        qty = 0.0

    # Cikk létrehozása/frissítése
    article = db.query(models.Article).filter(models.Article.article_number == num).first()
    if not article:
        article = models.Article(article_number=num, name=name or num, unit=unit)
        db.add(article)
        db.flush()

    # Helyszín keresése
    loc = None
    if location_code:
        loc = db.query(models.Location).filter(models.Location.code == location_code).first()

    # Ha van HU szám, raklap frissítése
    if hu_number:
        pallet = db.query(models.Pallet).filter(models.Pallet.infor_ln_hu == hu_number).first()
        if pallet:
            pallet.article_id = article.id
            pallet.quantity = qty
            pallet.unit = unit
            if loc:
                pallet.current_location_id = loc.id
        else:
            import uuid
            pallet = models.Pallet(
                pallet_number=f"HU-{hu_number}",
                infor_ln_hu=hu_number,
                article_id=article.id,
                quantity=qty,
                unit=unit,
                current_location_id=loc.id if loc else None,
                status="in_storage",
            )
            db.add(pallet)


def _import_order_row(row: dict, db: Session):
    """orders típus: rendelésszám, cikkszám, mennyiség, határidő, szállító"""
    order_num = row.get("rendelésszám") or row.get("order") or row.get("rendeles")
    item_num = row.get("cikkszám") or row.get("item") or row.get("cikk")
    qty_str = row.get("mennyiség") or row.get("quantity") or row.get("qty") or "0"
    supplier = row.get("szállító") or row.get("supplier") or row.get("szallito") or ""

    if not order_num:
        raise ValueError("Hiányzó rendelésszám")

    try:
        qty = float(qty_str.replace(",", "."))
    except ValueError:
        qty = 0.0

    article = None
    if item_num:
        article = db.query(models.Article).filter(models.Article.article_number == item_num).first()

    existing = db.query(models.ReceivingOrder).filter(
        models.ReceivingOrder.order_number == order_num
    ).first()
    if not existing:
        db.add(models.ReceivingOrder(
            order_number=order_num,
            infor_ln_ref=order_num,
            supplier=supplier,
            article_id=article.id if article else None,
            expected_quantity=qty,
            status="pending",
        ))


@router.get("/import-history")
def import_history(limit: int = 30, db: Session = Depends(get_db)):
    rows = db.query(models.InforCSVImport).order_by(
        models.InforCSVImport.imported_at.desc()
    ).limit(limit).all()
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "import_type": r.import_type,
            "rows_total": r.rows_total,
            "rows_imported": r.rows_imported,
            "rows_error": r.rows_error,
            "status": r.status,
            "error_log": r.error_log,
            "imported_at": r.imported_at.isoformat() if r.imported_at else None,
        }
        for r in rows
    ]
