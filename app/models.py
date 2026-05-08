from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, ForeignKey, Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    article_number = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    unit = Column(String(20), default="db")
    weight_kg = Column(Float)
    preferred_zone = Column(String(10))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    pallets = relationship("Pallet", back_populates="article")


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    zone = Column(String(20), nullable=False)
    zone_type = Column(String(20), default="storage")
    row = Column(Integer)
    col = Column(Integer)
    level = Column(Integer, default=1)
    is_occupied = Column(Boolean, default=False)
    max_pallets = Column(Integer, default=1)
    current_pallets = Column(Integer, default=0)
    notes = Column(Text)
    rfid_reader_zone = Column(String(50))
    is_active = Column(Boolean, default=True)

    pallets = relationship("Pallet", back_populates="current_location")


class RFIDTag(Base):
    __tablename__ = "rfid_tags"

    id = Column(Integer, primary_key=True, index=True)
    epc = Column(String(100), unique=True, index=True, nullable=False)
    tag_type = Column(String(20), default="pallet")
    description = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True))
    last_seen_zone = Column(String(50))
    last_rssi = Column(Float)

    pallet = relationship("Pallet", back_populates="rfid_tag", uselist=False)


class Pallet(Base):
    __tablename__ = "pallets"

    id = Column(Integer, primary_key=True, index=True)
    pallet_number = Column(String(50), unique=True, index=True, nullable=False)
    rfid_tag_id = Column(Integer, ForeignKey("rfid_tags.id"), nullable=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=True)
    quantity = Column(Float, default=0)
    unit = Column(String(20), default="db")
    status = Column(String(30), default="unknown")
    current_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    infor_ln_hu = Column(String(50))
    batch_number = Column(String(50))
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    rfid_tag = relationship("RFIDTag", back_populates="pallet")
    article = relationship("Article", back_populates="pallets")
    current_location = relationship("Location", back_populates="pallets")
    movements = relationship("Movement", back_populates="pallet", order_by="Movement.moved_at.desc()")
    tasks = relationship("Task", back_populates="pallet", order_by="Task.created_at.desc()")


class Movement(Base):
    __tablename__ = "movements"

    id = Column(Integer, primary_key=True, index=True)
    pallet_id = Column(Integer, ForeignKey("pallets.id"))
    rfid_tag_epc = Column(String(100))
    from_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    to_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    from_zone = Column(String(50))
    to_zone = Column(String(50))
    action = Column(String(30))
    notes = Column(Text)
    moved_at = Column(DateTime(timezone=True), server_default=func.now())
    operator = Column(String(100))

    pallet = relationship("Pallet", back_populates="movements")
    from_location = relationship("Location", foreign_keys=[from_location_id])
    to_location = relationship("Location", foreign_keys=[to_location_id])


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_number = Column(String(30), unique=True, index=True)
    task_type = Column(String(30), nullable=False)
    pallet_id = Column(Integer, ForeignKey("pallets.id"), nullable=True)
    from_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    to_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    from_zone = Column(String(50))
    to_zone = Column(String(50))
    priority = Column(Integer, default=5)
    status = Column(String(20), default="pending")
    assigned_to = Column(String(100))
    notes = Column(Text)
    infor_ln_ref = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    pallet = relationship("Pallet", back_populates="tasks")
    from_location = relationship("Location", foreign_keys=[from_location_id])
    to_location = relationship("Location", foreign_keys=[to_location_id])


class PhaseDefinition(Base):
    __tablename__ = "phase_definitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    from_article_id = Column(Integer, ForeignKey("articles.id"))
    to_article_id = Column(Integer, ForeignKey("articles.id"))
    destination_zone = Column(String(20))
    destination_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    process_description = Column(Text)
    auto_task_create = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    from_article = relationship("Article", foreign_keys=[from_article_id])
    to_article = relationship("Article", foreign_keys=[to_article_id])
    destination_location = relationship("Location")


class ReceivingOrder(Base):
    __tablename__ = "receiving_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True)
    infor_ln_ref = Column(String(50))
    supplier = Column(String(200))
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=True)
    expected_quantity = Column(Float)
    received_quantity = Column(Float, default=0)
    unit = Column(String(20), default="db")
    status = Column(String(20), default="pending")
    expected_date = Column(DateTime(timezone=True))
    received_date = Column(DateTime(timezone=True))
    target_zone = Column(String(20))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    article = relationship("Article")


class RFIDReader(Base):
    __tablename__ = "rfid_readers"

    id = Column(Integer, primary_key=True, index=True)
    reader_id = Column(String(50), unique=True, index=True)
    name = Column(String(100), nullable=False)
    ip_address = Column(String(50))
    port = Column(Integer, default=5084)
    zone = Column(String(50))
    location_description = Column(String(200))
    status = Column(String(20), default="offline")
    last_seen = Column(DateTime(timezone=True))
    firmware_version = Column(String(50))
    is_active = Column(Boolean, default=True)


class RFIDEvent(Base):
    __tablename__ = "rfid_events"

    id = Column(Integer, primary_key=True, index=True)
    reader_id = Column(String(50))
    reader_name = Column(String(100))
    tag_epc = Column(String(100), index=True)
    rssi = Column(Float)
    zone = Column(String(50))
    event_type = Column(String(20), default="read")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)


class Cart(Base):
    """Komissiózó kocsi – szereldei nyomonkövetés."""
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    cart_number = Column(String(50), unique=True, index=True, nullable=False)
    rfid_tag_id = Column(Integer, ForeignKey("rfid_tags.id"), nullable=True)
    assembly_line = Column(String(10))          # "4270" | "4392"
    current_position = Column(String(30))       # "HÁTRALÉKOS" | "1423" | "RAKTÁR" ...
    status = Column(String(20), default="hátralékos")  # hátralékos | aktív | kész | hiányzik
    last_hk_reader = Column(String(10))         # HK01..HK10
    last_seen_at = Column(DateTime(timezone=True))
    assigned_operator = Column(String(100))
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    rfid_tag = relationship("RFIDTag")


class CartMovement(Base):
    """Kocsi mozgástörténet."""
    __tablename__ = "cart_movements"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"))
    hk_reader = Column(String(10))
    from_position = Column(String(30))
    to_position = Column(String(30))
    moved_at = Column(DateTime(timezone=True), server_default=func.now())
    operator = Column(String(100))
    notes = Column(Text)

    cart = relationship("Cart")


class Factory(Base):
    """Üzem / gyár."""
    __tablename__ = "factories"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    address = Column(String(300))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    halls = relationship("Hall", back_populates="factory")


class Hall(Base):
    """Csarnok / üzemrész."""
    __tablename__ = "halls"

    id = Column(Integer, primary_key=True, index=True)
    factory_id = Column(Integer, ForeignKey("factories.id"))
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    color = Column(String(20), default="#3b82f6")
    floor_plan_url = Column(String(500))
    is_active = Column(Boolean, default=True)

    factory = relationship("Factory", back_populates="halls")
    workstations = relationship("WorkStation", back_populates="hall")


class WorkStation(Base):
    """Munkaállomás – testreszabható, adatbázisban tárolt pozíció."""
    __tablename__ = "workstations"

    id = Column(Integer, primary_key=True, index=True)
    hall_id = Column(Integer, ForeignKey("halls.id"), nullable=True)
    code = Column(String(30), unique=True, index=True, nullable=False)   # pl. "1423"
    name = Column(String(200))                                            # pl. "JD 1423 – Hajtómű szerelés"
    assembly_line = Column(String(20))                                    # "4270" | "4392"
    station_type = Column(String(30), default="assembly")                 # assembly | storage | transit | finished
    # SVG pozíció a térképen
    svg_x = Column(Integer)
    svg_y = Column(Integer)
    svg_w = Column(Integer, default=118)
    svg_h = Column(Integer, default=140)
    color = Column(String(20))
    # Hézagoló lemez igény
    shim_required = Column(Boolean, default=False)
    shim_description = Column(Text)                                       # milyen hézagoló lemez kell
    shim_quantity = Column(Integer, default=0)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    hall = relationship("Hall", back_populates="workstations")


class ForkliftOperator(Base):
    """Targoncás kezelő."""
    __tablename__ = "forklift_operators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    employee_id = Column(String(50), unique=True, index=True)
    rfid_epc = Column(String(100), unique=True, index=True)   # belépő kártya EPC
    pin_code = Column(String(10))                              # PIN alternatív bejelentkezés
    forklift_number = Column(String(30))                      # melyik targoncához rendelt
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sessions = relationship("ForkliftSession", back_populates="operator")


class ForkliftSession(Base):
    """Aktív targoncás szekció – bejelentkezési rekord."""
    __tablename__ = "forklift_sessions"

    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("forklift_operators.id"))
    forklift_number = Column(String(30))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    last_activity = Column(DateTime(timezone=True))
    notes = Column(Text)

    operator = relationship("ForkliftOperator", back_populates="sessions")


class InforCSVImport(Base):
    """Infor LN CSV import napló."""
    __tablename__ = "infor_csv_imports"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(200))
    import_type = Column(String(50))        # inventory | articles | orders
    rows_total = Column(Integer, default=0)
    rows_imported = Column(Integer, default=0)
    rows_error = Column(Integer, default=0)
    status = Column(String(20), default="pending")
    error_log = Column(Text)
    imported_at = Column(DateTime(timezone=True), server_default=func.now())


class InforLNSync(Base):
    __tablename__ = "infor_ln_sync"

    id = Column(Integer, primary_key=True, index=True)
    sync_type = Column(String(50))
    direction = Column(String(10))
    infor_ln_ref = Column(String(100))
    payload = Column(Text)
    status = Column(String(20), default="pending")
    error_message = Column(Text)
    synced_at = Column(DateTime(timezone=True), server_default=func.now())
