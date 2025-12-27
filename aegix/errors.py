from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

ErrorType = Literal[
    "DENIED_POLICY",
    "INVALID_TOOL_CALL",
    "TIMEOUT",
    "NONZERO_EXIT",
    "BACKEND_ERROR",
]

@dataclass(frozen=True)
class AegixError:
    type: ErrorType
    message: str
    exit_code: Optional[int] = None
