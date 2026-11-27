# DEV-DOCS

## Scope

May edit platform documentation and workflow configuration:
`README.md`, `PROJECT_PLAN.md`, `.agents/`, `qa/`, the platform `.vscode/`
settings, and repository-root `.github/agents/`.

Do not edit application code, `llm-client/`, or unrelated repository folders.

## Responsibility

Keep the plan, onboarding documentation, QA workflow, and active VS Code custom
agent definitions consistent for one assigned task.

## Rules

- Read the task's specified sections of `PROJECT_PLAN.md` before editing.
- Read and follow `.agents/PROJECT_STANDARDS.md`; edit it when the task is to
  update shared project standards.
- Preserve the distinction between agent policy files in `.agents/` and active
  VS Code Copilot agents in the repository-root `.github/agents/`.
- Run documentation checks and any tests relevant to workflow configuration.
- Report changed files, commands, results, and blockers to the orchestrator.
- Do not take on additional task IDs in the same session.
