from dataclasses import dataclass


@dataclass
class ToolInvocation:
    tool_name: str
    args: dict
    policy_profile: str
    metadata: dict
    workspace: str
