# QA workflow

`QA-TESTER` verifies each project commit and creates a folder
at `qa/runs/<full-commit-sha>/`. Each folder contains `REPORT.md` with the
commands and test statuses; failures also get a `BUG-<number>.md` report.

On failure, hand the report and bug paths to `QA Platform Orchestrator`. It assigns the
bug to the scoped development role and requests a new commit. QA then tests the
fix commit and creates a separate report folder for its SHA.

Use the templates in `templates/`. Generated run folders are ignored by Git to
avoid recursive QA-only commits; preserve them as CI artifacts once CI is
configured. The handoff is an agent subtask, not an automatic Git hook or CI
trigger. See Section 7 of `PROJECT_PLAN.md` and the agent instructions in
`.agents/`.
