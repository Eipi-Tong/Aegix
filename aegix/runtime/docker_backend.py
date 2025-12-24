from __future__ import annotations

from dataclasses import dataclass
import docker

@dataclass(frozen=True)
class ExecResult:
    stdout: str
    stderr: str
    exit_code: int

class DockerBackend:
    def __init__(self) -> None:
        self.client = docker.from_env()
    
    def create(self, image: str) -> str:
        container = self.client.containers.run(
            image=image,
            command=["sh", "-lc", "tail -f /dev/null"],
            detach=True,
            tty=True,
        )
        return container.id
    
    def exec(self, container_id: str, cmd: str) -> ExecResult:
        container = self.client.containers.get(container_id)
        # demux=True => (stdout_bytes, stderr_bytes)
        res = container.exec_run(["sh", "-lc", cmd], demux=True)
        exit_code = int(res.exit_code)

        stdout_b, stderr_b = res.output if isinstance(res.output, tuple) else (res.output, b"")
        return ExecResult(
            stdout=(stdout_b or b"").decode("utf-8", errors="replace"),
            stderr=(stderr_b or b"").decode("utf-8", errors="replace"),
            exit_code=exit_code,
        )
    
    def destroy(self, container_id: str) -> None:
        container = self.client.containers.get(container_id)
        container.stop()
        container.remove(force=True)
