from contextlib import asynccontextmanager
from typing import List
import json
import asyncio

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app import models  # noqa: F401 – registers all models
from app.routers import (
    articles, pallets, locations, rfid, tasks,
    receiving, phases, infor_ln, carts, factory_structure, forklift,
)


class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


ws_manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    from app.migrate import run_migrations
    run_migrations()
    yield


app = FastAPI(
    title="Raktar RFID – Raklap Nyomonkövető Rendszer",
    description="ATR7000 RTLS alapú raktárkezelő és raklap nyomonkövető",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Share ws_manager with routers via app state
app.state.ws_manager = ws_manager

# ── API routers ────────────────────────────────────────────────────────────────
app.include_router(articles.router,           prefix="/api/articles",         tags=["Cikkek"])
app.include_router(pallets.router,            prefix="/api/pallets",          tags=["Raklapok"])
app.include_router(locations.router,          prefix="/api/locations",        tags=["Helyek"])
app.include_router(rfid.router,               prefix="/api/rfid",             tags=["RFID"])
app.include_router(tasks.router,              prefix="/api/tasks",            tags=["Feladatok"])
app.include_router(receiving.router,          prefix="/api/receiving",        tags=["Bevételezés"])
app.include_router(phases.router,             prefix="/api/phases",           tags=["Fázisok"])
app.include_router(infor_ln.router,           prefix="/api/infor-ln",         tags=["Infor LN"])
app.include_router(carts.router,              prefix="/api/carts",            tags=["Kocsik"])
app.include_router(factory_structure.router,  prefix="/api/factory",          tags=["Üzem struktúra"])
app.include_router(forklift.router,           prefix="/api/forklift",         tags=["Targoncás"])


# ── WebSocket ──────────────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# ── HTML pages ─────────────────────────────────────────────────────────────────
@app.get("/")
async def page_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "page": "dashboard"})

@app.get("/pallets")
async def page_pallets(request: Request):
    return templates.TemplateResponse("pallets.html", {"request": request, "page": "pallets"})

@app.get("/pallets/{pallet_id}")
async def page_pallet_detail(request: Request, pallet_id: int):
    return templates.TemplateResponse("pallet_detail.html", {"request": request, "page": "pallets", "pallet_id": pallet_id})

@app.get("/locations")
async def page_locations(request: Request):
    return templates.TemplateResponse("locations.html", {"request": request, "page": "locations"})

@app.get("/tasks")
async def page_tasks(request: Request):
    return templates.TemplateResponse("tasks.html", {"request": request, "page": "tasks"})

@app.get("/phases")
async def page_phases(request: Request):
    return templates.TemplateResponse("phases.html", {"request": request, "page": "phases"})

@app.get("/rfid")
async def page_rfid(request: Request):
    return templates.TemplateResponse("rfid.html", {"request": request, "page": "rfid"})

@app.get("/articles")
async def page_articles(request: Request):
    return templates.TemplateResponse("articles.html", {"request": request, "page": "articles"})

@app.get("/infor-ln")
async def page_infor_ln(request: Request):
    return templates.TemplateResponse("infor_ln.html", {"request": request, "page": "infor_ln"})

@app.get("/szerelde")
async def page_szerelde(request: Request):
    return templates.TemplateResponse("szerelde.html", {"request": request, "page": "szerelde"})

@app.get("/targonca")
async def page_targonca(request: Request):
    return templates.TemplateResponse("targonca.html", {"request": request, "page": "targonca"})

@app.get("/factory-admin")
async def page_factory_admin(request: Request):
    return templates.TemplateResponse("factory_admin.html", {"request": request, "page": "factory_admin"})

@app.get("/hall-map/{hall_id}")
async def page_hall_map(request: Request, hall_id: int):
    return templates.TemplateResponse("hall_map.html", {"request": request, "page": "factory_admin", "hall_id": hall_id})

@app.get("/rtls-planner")
async def page_rtls_planner(request: Request):
    return templates.TemplateResponse("rtls_planner.html", {"request": request, "page": "rtls_planner"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
