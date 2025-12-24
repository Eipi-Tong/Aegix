from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import time
import uuid

from aegix.io.artifacts import ArtifactWriter
from aegix.logging.audit import AuditLogger
from aegix.runtime.docker_backend import DockerBackend, ExecResult

@dataclass(frozen=True)
class RunConfig:
    cmd: str
    image: str = "python:3.11-slim"

@dataclass(frozen=True)
class RunResult:
    run_id: str
    run_dir: str
    exit_code: int
    stderr_tail: str

class ToolRouter:
    def __init__(self, run_dir: Path = Path("runs")) -> None:
        self.run_dir = run_dir
        self.backend = DockerBackend()

    def _new_run_id(self) -> str:
        ts = time.strftime("%Y%m%d_%H%M%S")
        short = uuid.uuid4().hex[:8]
        return f"{ts}_{short}"

    def handle(self, cfg: RunConfig) -> RunResult:
        run_id = self._new_run_id()
        run_dir = self.run_dir / run_id
        artifacts_dir = run_dir / "artifacts"
        run_dir.mkdir(parents=True, exist_ok=True)
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        writer = ArtifactWriter(run_dir=run_dir)
        audit = AuditLogger(events_path=run_dir / "events.jsonl")

        # ---- Run Start ----
        audit.log("RUN_START", {"cmd": cfg.cmd, "image": cfg.image})

        # ---- Validation ----
        cmd = (cfg.cmd or "").strip()
        if not cmd:
            audit.log("RUN_ERROR", {"status": "error", "reason": "empty command"})
            writer.write_text("artifacts/stderr.txt", "Error: Empty command\n")
            writer.write_text("artifacts/exit_code.txt", "2\n")
            return RunResult(
                run_id=run_id,
                run_dir=str(run_dir),
                exit_code=2,
                stderr_tail="Error: Empty command"
            )
        
        # ---- Policy Check ----
        # In this MVP, we allow all commands in this example.
        audit.log("POLICY_ALLOW", {"reason": "default allow all"})

        # ---- Execution ----
        container_id: Optional[str] = None
        start = time.time()
        try:
            container_id = self.backend.create(image=cfg.image)
            audit.log("EXEC_START", {"container_id": container_id})

            exec_res: ExecResult = self.backend.exec(
                container_id=container_id,
                cmd=cmd,
            )
            dur_ms = int((time.time() - start) * 1000)
            audit.log("EXEC_END", {
                "container_id": container_id, 
                "exit_code": exec_res.exit_code,
                "dur_ms": dur_ms,
            })

            # ---- Persist Artifacts ----
            writer.write_text("meta.json", writer.json_dumps({
                "run_id": run_id,
                "cmd": cmd,
                "image": cfg.image,
            }))
            writer.write_text("artifacts/stdout.txt", exec_res.stdout)
            writer.write_text("artifacts/stderr.txt", exec_res.stderr)
            writer.write_text("artifacts/exit_code.txt", f"{exec_res.exit_code}\n")
            audit.log("RUN_END", {"status": "ok", "exit_code": exec_res.exit_code})

            stderr_tail = (exec_res.stderr or "").splitlines()[-10:]  # last 10 lines
            return RunResult(
                run_id=run_id,
                run_dir=str(run_dir),
                exit_code=exec_res.exit_code,
                stderr_tail="\n".join(stderr_tail),
            )
        
        except Exception as e:
            audit.log("RUN_END", {"status": "error", "reason": str(e)})
            writer.write_text("artifacts/stderr.txt", f"{type(e).__name__}: {str(e)}\n")
            writer.write_text("artifacts/exit_code.txt", "1\n") 
            return RunResult(
                run_id=run_id,
                run_dir=str(run_dir),
                exit_code=1,
                stderr_tail=f"Error during execution: {str(e)}"
            )
        
        finally:
            if container_id:
                try:
                    self.backend.destroy(container_id)
                except Exception:
                    # best effort cleanup
                    pass
