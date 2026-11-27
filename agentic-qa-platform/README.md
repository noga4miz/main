# Agentic QA Platform

An agentic platform that turns a URL and a test description into reviewed,
executable Playwright tests.

## Project layout

- `agent-app/` — application and runtime agents
- `demo-web/` — the web application under test
- `playwright-tests/` — shared helpers and generated tests
- `llm-client/` — standalone multi-provider LLM client (APP-02)
- `.agents/` — development-process agent role files
- `qa/` — per-commit QA reports, bug reports, and templates
- `../.github/agents/` — VS Code custom agents, including the Product Manager

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for architecture, contracts, and tasks.

## Use the Product Manager in VS Code

Open the repository in VS Code and select **Agentic QA Platform Product
Manager** in the Chat agent picker. Select it once; after that, just describe
the feature or fix you want. The Product Manager chooses the matching DEV and
QA agents without asking you to name them, then reports results in the same
chat. App changes go to DEV-APP and then QA-APP; demo website changes go to
DEV-WEB and then QA-WEB; Playwright
infrastructure changes go to DEV-PW and then QA-TESTER. If you open only this
subfolder and the agent is not listed, the workspace setting enables discovery
from the parent repository; reload the window or run **Chat: Open
Customizations** to verify the agent files were discovered.

## Configuration

Copy `.env.example` to `.env` and set values for your local environment.
`MONGO_URI` configures MongoDB, `DEFAULT_BASE_URL` points to the demo web,
`PLAYWRIGHT_PROJECT_PATH` locates the Playwright project, and `LLM_MODE`
selects the LLM client behavior. Never commit `.env` or API keys.

## Verification

After each change, run all existing tests relevant to the changed code and any
new regression tests. Include the commands run and their results in the task
handoff. For changes affecting multiple components, run the relevant suites for
each affected component.

To check the MongoDB Compose setup, start the service and run the project checks
from this directory:

```bash
docker compose up -d --wait
python3 -m unittest discover -s tests -v
```

The checks validate the Compose configuration, ping MongoDB, and check its
localhost port. Docker Compose must be installed, and the MongoDB service must
be running. Stop it afterward with `docker compose down` (do not use `-v` if you
want to keep the database volume).

To run the existing LLM client tests, use `python -m pytest` from `llm-client/`
after installing its development dependencies.

## Pytest and Allure QA

For each application task, the Product Manager invokes QA-APP after DEV-APP.
QA-APP runs relevant tests using pytest, saves Allure results, generates an
Allure HTML report, and writes a run report under
`qa/runs/<full-commit-sha>/<UTC-run-id>/` (or
`qa/runs/working-tree/<UTC-run-id>/` before a commit). The report records test
status and links to the Allure report. If a test fails, QA-APP writes a bug
report; the Product Manager routes the fix to the responsible DEV agent and asks
QA to retest.
Install `agent-app/requirements-test.txt` and the Allure CLI (Java required).
See `qa/README.md` and Section 7 of `PROJECT_PLAN.md`.

## Shared engineering standards

All DEV and QA agents follow `.agents/PROJECT_STANDARDS.md` for code quality,
test coverage, regression checks, reports, and handoffs. You can ask the
Product Manager to add or change a shared standard; it will be recorded there
and included in later development and QA tasks.
