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

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for architecture, contracts, and tasks.

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

## Commit-by-commit QA

After each commit, invoke `QA-TESTER` with its full SHA. It writes the test
status and commands to `qa/runs/<full-commit-sha>/REPORT.md`. On failure, it
creates a bug report there and hands it to `DEV-ORCHESTRATOR`, which assigns a
scoped development agent and requests a retest of the fix commit. See
`qa/README.md` and Section 7 of `PROJECT_PLAN.md`. This is an explicit
agent-driven handoff for now; Git hooks and CI do not invoke the agents yet.
