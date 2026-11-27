# Agentic QA Platform

An agentic platform that turns a URL and a test description into reviewed,
executable Playwright tests.

## Project layout

- `agent-app/` — application and runtime agents
- `demo-web/` — the web application under test
- `playwright-tests/` — shared helpers and generated tests
- `llm-client/` — standalone multi-provider LLM client (APP-02)
- `.agents/` — development-process agent role files

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for architecture, contracts, and tasks.

## Configuration

Copy `.env.example` to `.env` and set values for your local environment.
`MONGO_URI` configures MongoDB, `DEFAULT_BASE_URL` points to the demo web,
`PLAYWRIGHT_PROJECT_PATH` locates the Playwright project, and `LLM_MODE`
selects the LLM client behavior. Never commit `.env` or API keys.
