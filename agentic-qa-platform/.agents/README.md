# Development and QA agents

These files define project role policies; runnable VS Code Copilot agent
definitions live in the parent repository's `.github/agents/`. The only
user-facing project agent is **QA Platform Orchestrator**; it invokes the hidden
DEV and QA subagents and returns results in the same chat. These are separate
from the runtime agents in `agent-app/`.

- `DEV-APP.md`, `DEV-WEB.md`, `DEV-PW.md`, and `DEV-DOCS.md` define scoped
  development tasks.
- `QA-APP.md` and `QA-WEB.md` own component-specific test work.
- `QA-TESTER.md` runs tests for a commit and writes its report under `qa/runs/`.
- `DEV-ORCHESTRATOR.md` provides the routing policy followed by the main agent;
  it is not another agent to select.
- `TASK_BRIEF_TEMPLATE.md` defines the handoff fields.

See Section 7 of `PROJECT_PLAN.md` for the routing and per-commit QA workflow.