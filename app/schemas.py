from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ── Articles ──────────────────────────────────────────────────────────────────
class ArticleBase(BaseModel):
    article_number: str
    name: str
    description: Optional[str] = None
    unit: str = "db"
    weight_kg: Optional[float] = None
    preferred_zone: Optional[str] = None

class ArticleCreate(ArticleBase):
    pass

class ArticleOut(ArticleBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ── Locations ─────────────────────────────────────────────────────────────────
class LocationBase(BaseModel):
    code: str
    zone: str
    zone_type: str = "storage"
    row: Optional[int] = None
    col: Optional[int] = None
    level: int = 1
    max_pallets: int = 1
    notes: Optional[str] = None
    rfid_reader_zone: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class LocationOut(LocationBase):
    id: int
    is_occupied: bool
    current_pallets: int
    is_active: bool
    model_config = {"from_attributes": True}


# ── RFID Tags ─────────────────────────────────────────────────────────────────
class RFIDTagBase(BaseModel):
    epc: str
    tag_type: str = "pallet"
    description: Optional[str] = None

class RFIDTagCreate(RFIDTagBase):
    pass

class RFIDTagOut(RFIDTagBase):
    id: int
    is_active: bool
    last_seen: Optional[datetime] = None
    last_seen_zone: Optional[str] = None
    last_rssi: Optional[float] = None
    model_config = {"from_attributes": True}


# ── Pallets ───────────────────────────────────────────────────────────────────
class PalletCreate(BaseModel):
    pallet_number: str
    article_id: Optional[int] = None
    quantity: float = 0
    unit: str = "db"
    rfid_tag_id: Optional[int] = None
    infor_ln_hu: Optional[str] = None
    batch_number: Optional[str] = None
    notes: Optional[str] = None

class PalletUpdate(BaseModel):
    article_id: Optional[int] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    status: Optional[str] = None
    rfid_tag_id: Optional[int] = None
    infor_ln_hu: Optional[str] = None
    batch_number: Optional[str] = None
    notes: Optional[str] = None

class PalletList(BaseModel):
    id: int
    pallet_number: str
    status: str
    quantity: float
    unit: str
    infor_ln_hu: Optional[str] = None
    article: Optional[ArticleOut] = None
    current_location: Optional[LocationOut] = None
    rfid_tag: Optional[RFIDTagOut] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

class MovementOut(BaseModel):
    id: int
    action: str
    from_zone: Optional[str] = None
    to_zone: Optional[str] = None
    notes: Optional[str] = None
    moved_at: Optional[datetime] = None
    operator: Optional[str] = None
    from_location: Optional[LocationOut] = None
    to_location: Optional[LocationOut] = None
    model_config = {"from_attributes": True}

class TaskOut(BaseModel):
    id: int
    task_number: str
    task_type: str
    status: str
    priority: int
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    from_location: Optional[LocationOut] = None
    to_location: Optional[LocationOut] = None
    model_config = {"from_attributes": True}

class PalletDetail(PalletList):
    movements: List[MovementOut] = []
    tasks: List[TaskOut] = []

class PalletMove(BaseModel):
    to_location_id: Optional[int] = None
    to_zone: Optional[str] = None
    notes: Optional[str] = None
    operator: Optional[str] = "rendszer"

class PhaseChange(BaseModel):
    phase_definition_id: int
    operator: Optional[str] = "rendszer"


# ── Tasks ─────────────────────────────────────────────────────────────────────
class TaskCreate(BaseModel):
    task_type: str
    pallet_id: Optional[int] = None
    from_location_id: Optional[int] = None
    to_location_id: Optional[int] = None
    from_zone: Optional[str] = None
    to_zone: Optional[str] = None
    priority: int = 5
    notes: Optional[str] = None
    assigned_to: Optional[str] = None
    infor_ln_ref: Optional[str] = None

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


# ── Phase Definitions ─────────────────────────────────────────────────────────
class PhaseDefCreate(BaseModel):
    name: str
    from_article_id: Optional[int] = None
    to_article_id: Optional[int] = None
    destination_zone: Optional[str] = None
    destination_location_id: Optional[int] = None
    process_description: Optional[str] = None
    auto_task_create: bool = True

class PhaseDefOut(PhaseDefCreate):
    id: int
    is_active: bool
    from_article: Optional[ArticleOut] = None
    to_article: Optional[ArticleOut] = None
    destination_location: Optional[LocationOut] = None
    model_config = {"from_attributes": True}


# ── Receiving Orders ──────────────────────────────────────────────────────────
class ReceivingOrderCreate(BaseModel):
    order_number: str
    infor_ln_ref: Optional[str] = None
    supplier: Optional[str] = None
    article_id: Optional[int] = None
    expected_quantity: float = 0
    unit: str = "db"
    target_zone: Optional[str] = None
    notes: Optional[str] = None

class ReceivingOrderOut(ReceivingOrderCreate):
    id: int
    received_quantity: float
    status: str
    created_at: Optional[datetime] = None
    received_date: Optional[datetime] = None
    article: Optional[ArticleOut] = None
    model_config = {"from_attributes": True}

class ReceiveGoods(BaseModel):
    quantity: float
    pallet_number: Optional[str] = None
    rfid_epc: Optional[str] = None
    operator: Optional[str] = "rendszer"


# ── RFID Readers ──────────────────────────────────────────────────────────────
class RFIDReaderCreate(BaseModel):
    reader_id: str
    name: str
    ip_address: Optional[str] = None
    port: int = 5084
    zone: Optional[str] = None
    location_description: Optional[str] = None

class RFIDReaderOut(RFIDReaderCreate):
    id: int
    status: str
    last_seen: Optional[datetime] = None
    firmware_version: Optional[str] = None
    is_active: bool
    model_config = {"from_attributes": True}


# ── RFID Events (webhook from ATR7000) ────────────────────────────────────────
class RFIDWebhookEvent(BaseModel):
    reader_id: str
    tag_epc: str
    rssi: Optional[float] = None
    zone: Optional[str] = None
    event_type: str = "read"
    timestamp: Optional[datetime] = None


# ── Stats ─────────────────────────────────────────────────────────────────────
class DashboardStats(BaseModel):
    total_pallets: int
    in_storage: int
    in_transit: int
    total_locations: int
    occupied_locations: int
    utilization_pct: float
    pending_tasks: int
    active_readers: int
