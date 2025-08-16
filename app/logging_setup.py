import logging
import os
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from pathlib import Path

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "json").lower()  # 'json' ou 'plain'
LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / 'app.log'


class PlainFormatter(logging.Formatter):
    default_fmt = "[%(asctime)s] %(levelname)s %(name)s %(message)s"
    def __init__(self):
        super().__init__(self.default_fmt)


def configure_logging():
    root = logging.getLogger()
    if getattr(root, '_configured', False):
        return
    root.setLevel(LOG_LEVEL)
    for h in list(root.handlers):
        root.removeHandler(h)

    if LOG_FORMAT == 'json':
        formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)s')
    else:
        formatter = PlainFormatter()

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root.addHandler(stream_handler)

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=2_000_000, backupCount=5, encoding='utf-8')
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    root._configured = True  # type: ignore
    root.info("logging configured", extra={"level": LOG_LEVEL, "format": LOG_FORMAT, "file": str(LOG_FILE)})
