from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
from pathlib import Path
import asyncio
from app.data_loader import DataManager

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / 'sample_data.csv'

app = FastAPI(title="Dashboard Vendas & Estoque")

templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))
app.mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')), name='static')

data_manager = DataManager(CSV_PATH, refresh_interval=5.0)


class WSConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active.append(websocket)
        # Envia snapshot inicial
        await self.send_personal(websocket, data_manager.get_snapshot())

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active:
                self.active.remove(websocket)

    async def broadcast(self, data):
        dead = []
        for ws in list(self.active):
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                for d in dead:
                    if d in self.active:
                        self.active.remove(d)

    async def send_personal(self, websocket: WebSocket, data):
        await websocket.send_json(data)


ws_manager = WSConnectionManager()


@app.on_event("startup")
async def startup():
    data_manager.start()
    # Registrar callback para broadcast
    def push(snapshot):
        # Encapsular para loop async
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(ws_manager.broadcast({'type': 'snapshot', 'data': snapshot}))
        except RuntimeError:
            pass

    data_manager.subscribe(push)
    logger.info("Aplicação inicializada")


@app.on_event("shutdown")
async def shutdown():
    data_manager.stop()


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {"request": request, "title": "Dashboard"})


@app.get('/api/data')
async def api_data():
    return data_manager.get_snapshot()


@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Mantemos a conexão viva (ping/pong implícito)
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    except Exception:
        await ws_manager.disconnect(websocket)
