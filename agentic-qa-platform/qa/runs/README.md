# Per-commit QA runs

QA-TESTER creates one ignored folder per tested commit:
`<full-commit-sha>/REPORT.md`, plus `BUG-<number>.md` files for failures.
These are local or CI artifacts, not source files. Keep this README tracked and
retain generated folders as CI artifacts when that workflow is added.
