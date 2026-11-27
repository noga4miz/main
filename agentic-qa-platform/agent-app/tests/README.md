# Application tests

Application tests use pytest and `allure-pytest`. Install the test dependencies
from the platform root:

```bash
python3 -m pip install -r agent-app/requirements-test.txt
```

Run the application suite and write Allure result data:

```bash
python3 -m pytest agent-app/tests \
  --alluredir=qa/runs/<sha-or-working-tree>/<UTC-run-id>/allure-results
```

Generate the browsable HTML report with the Allure command-line tool (requires
Java):

```bash
allure generate qa/runs/<sha-or-working-tree>/<UTC-run-id>/allure-results \
  --clean -o qa/runs/<sha-or-working-tree>/<UTC-run-id>/allure-report
```

The QA-APP agent creates a unique run directory, records both commands and
their outcomes in `REPORT.md`, and reports a blocker if tests cannot be
collected or the HTML report cannot be generated.