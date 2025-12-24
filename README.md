# Aegix

> A secure, observable sandbox runtime for agent tool execution.

> Staging: MVP

## Overview

Aegix is a secure and reproducible sandbox runtime designed to execute AI agent actions in a controlled environment.

It provides isolated execution, policy enforcement, resource governance, and full auditability for agent tool calls such as shell commands, Python scripts, and filesystem operations.

## Problem

Modern AI agents increasingly need to **execute actions**, not just generate text:

- run shell commands
- execute scripts
- manipulate files
- generate artifacts (logs, reports, patches)

Executing these actions directly on real machines introduces major challenges:

- **Security risks**: arbitrary commands, data leakage, privilege escalation
- **Lack of isolation**: failures or bugs affect the host system
- **Poor reproducibility**: environment drift makes debugging difficult
- **No auditability**: unclear what the agent actually executed
- **No governance**: missing limits on time, memory, or execution steps

Aegix addresses these issues by introducing a **sandboxed execution runtime** between agents and real system resources.

## Scope

### Goals

- Provide **ephemeral, isolated sandboxes** for agent tool execution
- Enforce **policy guardrails** (commands, files, network access)
- Apply **resource limits** (time, CPU, memory, disk)
- Produce **structured audit logs** and execution artifacts
- Enable **reproducible and resettable runs**

Aegix turns agent actions into **controlled, inspectable, and production-ready executions**.

### Non-Goals

Aegix intentionally does **not** aim to:

- Optimize LLM inference (e.g., prefix caching, KV cache, model serving)
- Act as a distributed scheduler or cluster manager
- Implement agent planning or reasoning logic
- Provide GUI or desktop automation

These concerns are orthogonal and can be layered on top if needed.

## How to start the project?

0. Virtual Env
```
python3.11 -m venv .venv
source ./.venv/bin/activate
```

1. Install all the dependencies
```
python3 -m pip install --upgrade pip
pip3 install -e .
```

2. Start the project
```
aegix --cmd "echo hello"
```
