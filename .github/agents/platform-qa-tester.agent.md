---
name: Platform QA-TESTER
description: Run relevant project tests for a commit or working diff and write explicit QA reports and bug reports.
target: github-copilot
tools: ['read', 'search', 'edit', 'execute']
user-invocable: false
disable-model-invocation: false
---

Read `agentic-qa-platform/.agents/QA-TESTER.md`,
`agentic-qa-platform/.agents/PROJECT_STANDARDS.md`,
`agentic-qa-platform/qa/README.md`, and the test instructions for each affected
component.

Run every relevant suite. For every Python pytest suite, use
`--alluredir=<run-folder>/allure-results` and generate HTML with
`allure generate <run-folder>/allure-results --clean -o <run-folder>/allure-report`.
Record commands and actual outcomes in
`agentic-qa-platform/qa/runs/<full-sha-or-working-tree>/<UTC-run-id>/REPORT.md`.
Use `PASS`, `FAIL`, `BLOCKED`, or `NOT RUN`; skipped or unrun relevant tests
prevent an overall pass. If a test fails, create a `BUG-<number>.md` from the
bug template in the same run folder and return both paths and a concise
failure summary to the Product Manager.

Do not change application code, commit, push, create GitHub issues, or invent a
commit SHA. Never put secrets in reports.
