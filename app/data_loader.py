import threading
import time
from pathlib import Path
from typing import List, Dict, Any, Callable
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CSVChangeHandler(FileSystemEventHandler):
    def __init__(self, target_path: Path, on_change: Callable[[], None]):
        super().__init__()
        self._target = target_path.resolve()
        self._on_change = on_change

    def on_modified(self, event):  # type: ignore
        try:
            if Path(event.src_path).resolve() == self._target:
                logger.debug("Arquivo CSV modificado: %s", event.src_path)
                self._on_change()
        except Exception as e:
            logger.warning("Erro em on_modified: %s", e)

    # Alguns editores fazem operações de move/create
    def on_moved(self, event):  # type: ignore
        self.on_modified(event)


class DataManager:
    """Gerencia leitura do CSV e mantém snapshot em memória."""

    def __init__(self, csv_path: Path, refresh_interval: float = 5.0):
        self.csv_path = csv_path
        self.refresh_interval = refresh_interval
        self._last_mtime = 0.0
        self._lock = threading.RLock()
        self._data = {}
        self._subscribers = []  # type: list[Callable[[dict[str, Any]], None]]
        self._stop_event = threading.Event()
        self._thread = None  # type: ignore
        self._observer = None  # type: ignore

    def start(self):
        self._load_if_changed(force=True)
        # Thread de polling (fallback caso watchdog falhe)
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        # Watchdog
        if self.csv_path.exists():
            try:
                handler = CSVChangeHandler(self.csv_path, self._load_if_changed)
                self._observer = Observer()
                self._observer.schedule(handler, str(self.csv_path.parent), recursive=False)
                self._observer.start()
                logger.info("Watchdog iniciado para %s", self.csv_path)
            except Exception as e:
                # Em alguns ambientes (ex: Python 3.13 + sandbox) watchdog pode falhar; seguimos só com polling
                self._observer = None
                logger.warning("Watchdog desativado, usando apenas polling. Motivo: %s", e)
        else:
            logger.warning("CSV inicial não encontrado: %s", self.csv_path)

    def stop(self):
        self._stop_event.set()
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=2)

    def subscribe(self, cb: Callable[[Dict[str, Any]], None]):
        with self._lock:
            self._subscribers.append(cb)

    def get_snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._data)

    def _poll_loop(self):
        while not self._stop_event.is_set():
            try:
                self._load_if_changed()
            except Exception as e:
                logger.error("Erro no polling: %s", e)
            time.sleep(self.refresh_interval)

    def _notify(self):
        snapshot = self.get_snapshot()
        for cb in list(self._subscribers):
            try:
                cb(snapshot)
            except Exception as e:
                logger.warning("Subscriber falhou: %s", e)

    def _load_if_changed(self, force: bool = False):
        try:
            if not self.csv_path.exists():
                return
            mtime = self.csv_path.stat().st_mtime
            if not force and mtime <= self._last_mtime:
                return
            # Evitar leitura durante escrita: tentar múltiplas vezes
            for attempt in range(5):
                try:
                    df = pd.read_csv(self.csv_path)
                    break
                except Exception:
                    time.sleep(0.2)
            else:
                logger.error("Falha ao ler CSV após várias tentativas")
                return
            if df.empty:
                return
            # Normalizar colunas esperadas
            expected = {"timestamp", "produto", "vendas", "estoque"}
            missing = expected - set(df.columns)
            if missing:
                logger.warning("Colunas ausentes no CSV: %s", missing)
            # Conversões
            if 'timestamp' in df.columns:
                try:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                except Exception:
                    pass
            # Agregações simples
            total_vendas = df['vendas'].sum() if 'vendas' in df.columns else None
            estoque_por_produto = (
                df.groupby('produto')['estoque'].last().to_dict() if 'produto' in df.columns and 'estoque' in df.columns else {}
            )
            vendas_por_produto = (
                df.groupby('produto')['vendas'].sum().to_dict() if 'produto' in df.columns and 'vendas' in df.columns else {}
            )
            ultimo_timestamp = (
                df['timestamp'].max().isoformat() if 'timestamp' in df.columns and not df['timestamp'].isna().all() else None
            )
            snapshot = {
                'total_vendas': total_vendas,
                'estoque_por_produto': estoque_por_produto,
                'vendas_por_produto': vendas_por_produto,
                'linhas': len(df),
                'ultimo_timestamp': ultimo_timestamp,
                'atualizado_em': time.strftime('%Y-%m-%dT%H:%M:%S'),
            }
            with self._lock:
                self._data = snapshot
                self._last_mtime = mtime
            logger.info(
                "snapshot_update",
                extra={
                    "linhas": len(df),
                    "total_vendas": total_vendas,
                    "produtos": len(estoque_por_produto),
                    "ultimo_timestamp": ultimo_timestamp,
                },
            )
            self._notify()
        except Exception:
            logger.exception("csv_load_error")


__all__ = ["DataManager"]
