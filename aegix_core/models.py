from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

NetworkMode = Literal["none", "bridge", "host", "allowlist"]

@dataclass(frozen=True)
class Limits:
    timeout_s: int = 30
    cpu: float = 1.0
    mem_mb: int = 512
    pids: int = 256
    
    def merged(self, override: Optional[Dict[str, Any]]) -> Limits:
        if not override:
            return self
        return Limits(
            timeout_s=int(override.get("timeout_s", self.timeout_s)),
            cpu=float(override.get("cpu", self.cpu)),
            mem_mb=int(override.get("mem_mb", self.mem_mb)),
            pids=int(override.get("pids", self.pids)),
        )

@dataclass(frozen=True)
class FSRule:
    write_paths: List[str] = field(default_factory=lambda: ["/workspace"])
    read_only_paths: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class ToolCall:
    """Structural call made from LLM/Orchestrator"""
    tool_name: str    # e.g., "bash", "python"
    cmd: str          # raw command string (bash) or snippet
    image: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)
    cwd: str = "/workspace"

@dataclass(frozen=True)
class ToolContext:
    run_id: str
    actor: str = "cli"   # "agent" / "cli" / "service"
    metadate: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class AdjustedPolicy:
    limits: Limits
    network_mode: NetworkMode
    env_allowlist: Optional[List[str]]
    fs_rules: FSRule

@dataclass(frozen=True)
class PolicyDecision:
    allow: bool
    reason: str
    adjusted: AdjustedPolicy
    redactions: Dict[str, Any] = field(default_factory=dict)
