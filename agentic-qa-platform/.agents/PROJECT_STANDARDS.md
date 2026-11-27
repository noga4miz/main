# Project development and QA standards

This is the shared source of truth for code and test quality. The Product
Manager asks the user before changing a project-wide standard when the desired
behavior is ambiguous, then coordinates an update to this file. Every DEV and
QA agent must read and apply it for each task.

## Code standards

- Make the smallest change that fully meets the accepted task criteria.
- Follow the language and framework conventions already used by the component.
- Prefer clear names, small cohesive functions, explicit error handling, and
  type-safe interfaces where supported.
- Keep secrets, local environments, generated test output, and credentials out
  of source control.
- Update directly affected docs and callers; do not broaden scope to unrelated
  refactors.

## Test standards

- Every behavior change must have focused automated coverage that would fail
  before the fix or feature, when the project has a testable implementation.
- QA verifies the user's accepted criteria, relevant existing tests, and
  regression suites for the affected component; report what was run and what
  was not.
- Never describe skipped, uncollected, blocked, or unrun tests as passing.
- Application QA uses pytest, captures Allure results with `--alluredir`, and
  generates an Allure HTML report for every run, even if a test fails.
- A QA pass requires all relevant required tests to pass and the required
  reports to be generated. Missing tooling or no collected tests is `BLOCKED`,
  not `PASS`.
- On a product failure, QA records reproduction steps and expected/actual
  behavior in a bug report and returns it to the Product Manager for routing to
  the owning DEV agent.

## Task completion and handoff

- The Product Manager writes acceptance criteria and identifies the owning
  component; the user should not have to choose an agent.
- DEV reports the changes and test commands/results to the Product Manager.
- QA independently checks accepted criteria and regressions after DEV reports
  completion. A failed check returns to Product Manager -> owning DEV -> QA
  retest.
- Do not commit or push unless the user asks.

The Product Manager may add project-specific standards here as the user
defines them. New standards apply to subsequent development and QA tasks.
