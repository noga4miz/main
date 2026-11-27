# QA workflow

The Product Manager routes work by component: application changes go to QA-APP,
demo website changes to QA-WEB, and Playwright infrastructure or broader
cross-component checks to QA-TESTER. Every QA execution creates a unique folder:
`qa/runs/<full-commit-sha>/<UTC-run-id>/` for a commit, or
`qa/runs/working-tree/<UTC-run-id>/` for uncommitted work. Each folder contains
`REPORT.md` and, on failure, a `BUG-<number>.md`.

For application QA, QA-APP runs relevant pytest suites with `allure-pytest`,
generates the Allure HTML report using the Allure CLI, and records the result
and report path. A test failure does not prevent report generation. Missing
dependencies, no collected tests, or failed Allure generation are explicit
blockers. Other Python pytest suites also collect Allure data and generate HTML
reports.

On failure, return the report and bug paths to the Product Manager. The Product
Manager assigns the bug to the scoped development agent and requests a retest.
QA then creates a separate run folder for the retest.

Use the templates in `templates/`. Generated run folders are ignored by Git to
avoid recursive QA-only commits; preserve them as CI artifacts once CI is
configured. The handoff is an agent subtask, not an automatic Git hook or CI
trigger. See Section 7 of `PROJECT_PLAN.md` and the agent instructions in
`.agents/`.
