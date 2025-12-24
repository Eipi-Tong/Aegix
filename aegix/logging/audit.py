from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import time

class AuditLogger:
    def __init__(self, events_path: Path) -> None:
        self.events_path = events_path
        self.events_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event_type: str, data: Dict[str, Any]) -> None:
        event = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "type": event_type,
            "data": data or {},
        }
        with self.events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
