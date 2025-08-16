from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import time
from pathlib import Path
import asyncio
from app.data_loader import DataManager
from app.logging_setup import configure_logging
import pandas as pd

configure_logging()
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
        logging.getLogger("ws").info("ws_connected", extra={"total_active": len(self.active), "client": str(websocket.client)})
        # Envia snapshot inicial
        await self.send_personal(websocket, data_manager.get_snapshot())

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active:
                self.active.remove(websocket)
        logging.getLogger("ws").info("ws_disconnected", extra={"total_active": len(self.active), "client": str(websocket.client)})

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
    snapshot = data_manager.get_snapshot()
    logging.getLogger("api").debug("snapshot_served", extra={"linhas": snapshot.get('linhas'), "total_vendas": snapshot.get('total_vendas')})
    return snapshot


@app.get('/api/historico')
async def api_historico(limit: int = Query(100, ge=1, le=1000)):
    """Retorna as últimas linhas (raw) do CSV para gráficos históricos."""
    if not CSV_PATH.exists():
        return []
    try:
        df = pd.read_csv(CSV_PATH)
        if df.empty:
            return []
        if 'timestamp' in df.columns:
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
            except Exception:
                pass
        df = df.tail(limit)
        return JSONResponse(df.to_dict(orient='records'))
    except Exception as e:
        logger.error("Erro ao ler historico: %s", e)
        return JSONResponse([], status_code=500)


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

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        logging.getLogger("http").info(
            "request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query)[:200],
                "status_code": getattr(response, 'status_code', None),
                "duration_ms": round(duration_ms, 2),
                "client": request.client.host if request.client else None,
            },
        )
