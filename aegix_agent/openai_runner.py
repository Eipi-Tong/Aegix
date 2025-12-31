"""Minimal example: user prompt -> LLM tool call -> Aegix exec -> final answer."""
from __future__ import annotations

import json
import os

from openai import OpenAI

class AegixRuntime:
    """Placeholder Aegix client; replace with real gateway calls."""

    def execute(self, command: str) -> dict:
        print(f"[aegix] executing: {command}")
        return {"stdout": f"ran: {command}", "stderr": "", "exit_code": 0}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "aegix_bash",
            "description": "Run a bash command inside Aegix sandbox",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to run, e.g. 'ls -la'",
                    }
                },
                "required": ["command"],
            },
        },
    }
]


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your_key_here"))
aegix = AegixRuntime()


def run_agent(prompt: str) -> str:
    messages = [{"role": "user", "content": prompt}]

    first = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    ).choices[0].message

    if not first.tool_calls:
        return first.content or ""

    messages.append(first)
    for call in first.tool_calls:
        args = json.loads(call.function.arguments)
        result = aegix.execute(args["command"])
        messages.append(
            {
                "role": "tool",
                "tool_call_id": call.id,
                "name": call.function.name,
                "content": json.dumps(result),
            }
        )

    follow_up = client.chat.completions.create(model="gpt-4o", messages=messages)
    return follow_up.choices[0].message.content or ""


if __name__ == "__main__":
    print(run_agent("帮我看看当前目录有哪些文件？"))
