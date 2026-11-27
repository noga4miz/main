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
- `../.github/agents/` — VS Code custom agents, including the user-facing orchestrator

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for architecture, contracts, and tasks.

## Use the orchestrator in VS Code

Open the repository in VS Code and select **QA Platform Orchestrator** in the
Chat agent picker. This is the only user-facing project agent. It delegates
implementation to hidden DEV agents and verification to the hidden QA-TESTER
agent, then reports results back in the same chat. If you open only this
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

## Commit-by-commit QA

Keep **QA Platform Orchestrator** selected in the Chat agent picker. After a
change or commit, it invokes the hidden QA-TESTER subagent, which writes the
status and commands to `qa/runs/<full-commit-sha>/REPORT.md`. On failure, the
orchestrator delegates a fix to a scoped DEV agent and asks QA to retest.
See `qa/README.md` and Section 7 of `PROJECT_PLAN.md`. Git hooks and CI do not
start the orchestrator automatically yet.
