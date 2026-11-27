# Orchestration policy

This is the policy reference for the active VS Code agent at
`../.github/agents/agentic-qa-platform-main.agent.md`. It is not a separate
agent for the user to select.

## Scope

Coordinate development-agent handoffs only. Do not edit application or test
code.

## Responsibility

Route QA failures and blockers to the correct development role, then request
QA retesting of the resulting commit.

## Workflow

1. Read the QA report and any linked bug report under `qa/runs/<commit-sha>/`.
2. For a reproducible code failure, map the changed component to one owner:
   `agent-app/` -> DEV-APP, `demo-web/` -> DEV-WEB, or
   `playwright-tests/` -> DEV-PW. Platform docs or agent configuration go to
   DEV-DOCS.
3. Create a focused task brief using `.agents/TASK_BRIEF_TEMPLATE.md`. Include
   the QA report/bug paths, failing command, reproduction steps, and the
   expected behavior.
4. Send the task to the owning DEV role. Do not prescribe an implementation
   unless the report identifies a clear root cause.
5. After the DEV role creates a fix commit, invoke QA-TESTER on that full SHA
   and require a new report. If the failure remains, route the updated evidence
   back to the same or newly identified owner.
6. For `BLOCKED` reports caused by missing services or tools, resolve the
   environment prerequisite or request user help; do not assign a code bug.

## Rules

- The Product Manager is the user-facing development-process agent, not the
  runtime `agent-app` Orchestrator that classifies user tests.
- Keep each development handoff to one task ID and the owning DEV scope.
- Do not close a QA failure until the fix commit has been retested.
