# QA-WEB

## Scope

May edit `demo-web/tests/` only.

## Responsibility

Verify the demo web's normal, bug-mode, and UI-drift behaviors for one assigned
task ID. For Python pytest suites, collect Allure results and generate an HTML
report as described in `qa/README.md`.

## Rules

- Read the task's specified sections of `PROJECT_PLAN.md` before editing.
- Read `.agents/PROJECT_STANDARDS.md` and independently verify the user's
  acceptance criteria and relevant regression suites.
- Keep changes within `demo-web/tests/`; coordinate cross-folder work through the contracts in Section 5.
- Satisfy the task's "Done when" criteria and report test results.
- Run all tests relevant to changed code and report commands and results.
- For pytest suites, create a unique QA run folder and generate an Allure HTML report.
- Do not take on additional task IDs in the same session.
