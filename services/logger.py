import logging
import asyncio
from datetime import datetime
from fastapi import WebSocket

class LogBuffer(logging.Handler):
    def __init__(self, max_lines=200):
        super().__init__()
        self.logs = []
        self.max_lines = max_lines
        self.clients: list[WebSocket] = []

    def emit(self, record):
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "level": record.levelname,
            "msg": self.format(record)
        }
        self.logs.append(entry)
        if len(self.logs) > self.max_lines:
            self.logs = self.logs[-self.max_lines:]
        # Notify WebSocket clients
        for ws in list(self.clients):
            try:
                # This depends on an event loop running, which FastAPI provides
                asyncio.get_event_loop().create_task(ws.send_json(entry))
            except:
                pass

log_buffer = LogBuffer()
log_buffer.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
logger = logging.getLogger("shio")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
logger.addHandler(log_buffer)
