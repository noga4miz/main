# Development and QA agents

These role files define the project workflow; they are separate from the
runtime agents in `agent-app/`.

- `DEV-APP.md`, `DEV-WEB.md`, and `DEV-PW.md` implement scoped development tasks.
- `QA-APP.md` and `QA-WEB.md` own component-specific test work.
- `QA-TESTER.md` runs tests for a commit and writes its report under `qa/runs/`.
- `DEV-ORCHESTRATOR.md` routes QA bug reports to the appropriate development role.
- `TASK_BRIEF_TEMPLATE.md` defines the handoff fields.

See Section 7 of `PROJECT_PLAN.md` for the per-commit QA and failure handoff
workflow.