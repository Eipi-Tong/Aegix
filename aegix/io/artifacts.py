from __future__ import annotations

from pathlib import Path
import json

class ArtifactWriter:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir

    def write_text(self, rel_path: str, content: str) -> None:
        p = self.run_dir / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content or "", encoding="utf-8")

    @staticmethod
    def json_dumps(obj: object) -> str:
        return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
