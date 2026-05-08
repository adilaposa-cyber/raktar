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
from app.routers import articles, pallets, locations, rfid, tasks, receiving, phases, infor_ln


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
app.include_router(articles.router,  prefix="/api/articles",  tags=["Cikkek"])
app.include_router(pallets.router,   prefix="/api/pallets",   tags=["Raklapok"])
app.include_router(locations.router, prefix="/api/locations", tags=["Helyek"])
app.include_router(rfid.router,      prefix="/api/rfid",      tags=["RFID"])
app.include_router(tasks.router,     prefix="/api/tasks",     tags=["Feladatok"])
app.include_router(receiving.router, prefix="/api/receiving", tags=["Bevételezés"])
app.include_router(phases.router,    prefix="/api/phases",    tags=["Fázisok"])
app.include_router(infor_ln.router,  prefix="/api/infor-ln",  tags=["Infor LN"])


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

@app.get("/receiving")
async def page_receiving(request: Request):
    return templates.TemplateResponse("receiving.html", {"request": request, "page": "receiving"})

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
