# Agentic Test Generation Platform: Project Plan

An AI-agent platform that turns a URL and a plain-language test description into a working, reviewed and self-healing Playwright test, with reporting and a reusable knowledge store.

---

## 1. Goals

1. A user enters a **URL** and a **test description** (free text or a table).
2. An **Orchestrator** classifies the test type and routes it to a specialist agent.
3. The specialist and a **Generator** produce Python + Playwright + PyTest code.
4. A **Reviewer (QA gate)** checks the code before it runs.
5. The test runs; the user sees what happened (video, screenshots, trace) and an Allure report.
6. If it fails, a **Healer** reads the logs and fixes the test (bounded retries).
7. Facts observed on pages are stored in a **Knowledge Store** and reused by later tests.

**Guiding principle:** the LLM never guesses. It writes code from real page data (DOM / accessibility tree) collected by a Page Explorer.

---

## 2. Repository structure

The application, demo web, and Playwright project remain separate areas with the
contracts in Section 5. The existing `llm-client/` is a standalone Python
package used for APP-02; it stays at the repository root rather than being moved
into `agent-app/core/`. The tree below reflects the current layout; README files
mark current areas and folders reserved for later implementation.

```
agentic-qa-platform/
├─ README.md
├─ PROJECT_PLAN.md
├─ .gitignore
├─ .env.example
├─ docker-compose.yml
├─ .agents/                    # development and QA agent role files
│   ├─ README.md
│   ├─ DEV-APP.md
│   ├─ DEV-ORCHESTRATOR.md
│   ├─ DEV-PW.md
│   ├─ DEV-WEB.md
│   ├─ QA-APP.md
│   ├─ QA-TESTER.md
│   ├─ QA-WEB.md
│   └─ TASK_BRIEF_TEMPLATE.md
├─ llm-client/                 # standalone LLM package; implements APP-02
│   ├─ README.md
│   ├─ pyproject.toml
│   ├─ recordings/
│   ├─ src/llm_client/
│   │   ├─ __init__.py
│   │   ├─ __main__.py
│   │   ├─ cli.py
│   │   └─ client.py
│   └─ tests/
│       └─ test_replay.py
├─ agent-app/                  # FOLDER 1: the application we build
│   ├─ README.md
│   ├─ ui/README.md
│   ├─ agents/
│   │   ├─ README.md
│   │   └─ specialists/README.md
│   ├─ core/README.md
│   ├─ prompts/README.md
│   └─ tests/README.md
├─ demo-web/                   # FOLDER 2: the web app UNDER TEST
│   ├─ README.md
│   ├─ assets/README.md
│   ├─ pages/README.md
│   └─ tests/README.md
├─ playwright-tests/           # FOLDER 3: Playwright project
│   ├─ README.md
│   ├─ helpers/README.md
│   ├─ reports/README.md
│   ├─ test_data/README.md
│   └─ tests/
│       ├─ README.md
│       ├─ golden/README.md
│       └─ generated/README.md
├─ tests/
│   ├─ README.md
│   ├─ __init__.py
│   └─ test_mongodb_compose.py  # Compose config and MongoDB smoke checks
└─ qa/
    ├─ README.md
    ├─ templates/
    │   ├─ BUG_REPORT.md
    │   └─ COMMIT_REPORT.md
    └─ runs/
        ├─ README.md
        └─ <full-commit-sha>/
            ├─ REPORT.md
            └─ BUG-<number>.md  # created only when a test finds a defect
```

Generated `qa/runs/<full-commit-sha>/` folders are local/CI test artifacts and
are ignored by Git to avoid a QA report commit triggering another QA cycle.
CI should retain them as artifacts once the workflow is configured.

### Existing `llm-client/` package (APP-02)

This package provides one interface for Anthropic, OpenAI, Gemini, and Ollama,
with response recording and replay. From `llm-client/`, install it with
`python3 -m venv .venv`, activate the environment, then run
`pip install -e ".[dev]"`. Use the `llm "your prompt"` command or import
`LLMClient` from Python. `LLM_MODE` accepts `live` (always call the provider),
`record` (call and save the response), `replay` (use recordings only), or `auto`
(use a matching recording, otherwise call and save). Replay works without a
network call when a matching recording exists.

---

## 3. Technology choices

| Area | Choice | Notes |
|---|---|---|
| Language | Python 3.11+ | |
| Browser automation | Playwright (Python) + `pytest-playwright` | |
| Runner | PyTest | |
| Reporting | Allure + Playwright video/trace | Allure CLI requires Java |
| Database | **MongoDB** (PyMongo) | Local via Docker Compose; Atlas free tier is an option |
| LLM access | Direct API client behind one wrapper (`llm_client.py`) | Cost tracking, retries, record/replay mode |
| UI | Streamlit (MVP) | |
| Demo web | Static HTML/CSS/JS | Deployable to GitHub Pages or any static host |
| CI | GitHub Actions | One workflow per folder + one end-to-end workflow |
| DB in tests | `mongomock` for unit tests; real Mongo service container for e2e | |

**Model usage / cost:** a cheaper, faster model for classification and review; a stronger model for generation and healing. Set a monthly spend cap in the API console before the first call. Check current pricing before choosing.

---

## 4. Runtime architecture (inside `agent-app`)

```
 UI (URL + description)
        |
        v
  Orchestrator ---- classifies test type (+ confidence)
        |
   +----+-----------+--------------+
   v                v              v
 Form Agent     Table Agent    Compare Agent
   \                |              /
    +--------> Page Explorer <----+    (real DOM data, plain code)
                    |
                    v
               Generator ----> Reviewer (QA gate) --fail--> back to Generator (max N)
                                   | pass
                                   v
                                Runner (Playwright + PyTest + Allure)
                              +-----+------+
                           pass |          | fail
                                v          v
                    Knowledge Collector   Healer (max 3 attempts)
                                |          |
                                +----+-----+
                                     v
                       Result to user (video + report)
```

| Component | Type | Responsibility |
|---|---|---|
| Orchestrator | LLM | Classify test type, extract parameters, ask a clarifying question if confidence is low |
| Specialist agents | LLM | Know the patterns of one test type (forms, tables, cross-page comparison) and produce a structured test spec |
| Page Explorer | Plain code | Opens the page, returns interactive elements, locators, headings, tables |
| Generator | LLM | Turns the spec into code using the existing helpers; proposes new helpers instead of inlining logic |
| Reviewer | Code + LLM | Static rules first, then an LLM check that the test matches the description |
| Runner | Plain code | Runs PyTest via CLI, collects artifacts and results |
| Healer | LLM | Fixes a failing test from code + logs + screenshot + fresh DOM. May never weaken an assertion |
| Knowledge Collector | Plain code | Stores observed facts from passing runs |

### Design rules
1. **Data-driven:** test data lives in `test_data/` or MongoDB, never in test code.
2. **Shared helpers:** the Generator must use `helpers/`; missing helpers are proposed, not inlined.
3. **Real locators only:** prefer `get_by_role`, `get_by_label`, `get_by_test_id`.
4. **No sleeps:** use Playwright auto-wait and `expect`.
5. **Uniform test template:** Arrange / Act / Assert, with the original description in a docstring.
6. **Bounded loops:** Reviewer loop max 3, Healer max 3; then mark `needs_manual`.
7. **Prompts are versioned** in Git.

### MongoDB collections

| Collection | Purpose | Key fields |
|---|---|---|
| `tests` | Test definitions | `name`, `url`, `test_type`, `description`, `spec`, `data_ref`, `code_path`, `status`, timestamps |
| `runs` | Execution history | `test_id`, `result`, `attempts`, artifact paths, `duration`, `llm_cost_estimate`, `started_at` |
| `page_facts` | Knowledge Store | `page_url`, `element_key`, `fact_type`, `value`, `source_run_id`, `last_seen_at` |
| `llm_calls` | Cost and debugging log | `agent`, `model`, `tokens_in/out`, `cost_estimate`, `prompt_version`, `run_id` |

Suggested indexes: `tests.name` (unique), `runs.test_id + started_at`, `page_facts.page_url + element_key`.

---

## 5. Contracts between the folders

| Between | Contract |
|---|---|
| `agent-app` → `demo-web` | HTTP only. The app receives a URL; it never imports or reads web source files |
| `agent-app` → `playwright-tests` | (1) writes `tests/generated/<name>.py` and `test_data/<name>.yaml`; (2) runs `pytest` via subprocess with `--base-url` and an Allure dir; (3) reads `reports/` and the JUnit/JSON result. No Python imports across the boundary |
| `playwright-tests` → `demo-web` | HTTP only, via `BASE_URL` |

Paths are configured through `.env` (`PLAYWRIGHT_PROJECT_PATH`, `MONGO_URI`, `DEFAULT_BASE_URL`). Each folder has its own dependency file and its own CI workflow.

---

## 6. The demo web (`demo-web`)

A small self-contained site we fully control, so we can demonstrate both working tests and deliberate defects, and never get blocked or rate-limited.

**Pages**
1. **Registration form:** text fields, dropdowns, checkboxes, validation messages.
2. **Confirmation page:** shows submitted values (verify a result on another page).
3. **Products table:** filters, search, sorting, column chooser (add/remove columns), default values.
4. **Product details:** includes product description.
5. **Inventory/orders page:** repeats the same product descriptions (cross-page consistency).

**Controlled defects ("bug mode"):** enabled by a query parameter or an on-page panel, for example broken filter, wrong default column set, mismatching description between pages, validation that accepts bad input.

**UI drift mode:** changes labels/IDs/structure to demonstrate the Healer.

**Locator variety:** some elements have `data-testid`, some only roles/labels, to exercise locator strategy.

---

## 7. Development-process agents (how we build this project)

Separate from the runtime agents. These are role prompts in `.agents/` that we point at **one task ID at a time**.

| Agent | Scope (may edit) | Responsibility |
|---|---|---|
| **DEV-APP** | `agent-app/` | Implements the application and runtime agents |
| **DEV-WEB** | `demo-web/` | Implements the demo web |
| **DEV-PW** | `playwright-tests/` | Implements conftest, setup, helpers, golden tests |
| **DEV-ORCHESTRATOR** | Coordination only; no application code | Routes QA bug reports to the appropriate DEV role and requests retesting |
| **QA-APP** | `agent-app/tests/` | Tests our application (unit, agent behavior, e2e) |
| **QA-WEB** | `demo-web/tests/` | Verifies the web under test behaves as designed, including each bug mode |
| **QA-TESTER** | `qa/runs/<commit-sha>/` | Runs relevant tests for each commit, records results, and reports failures |

**Rules:** an agent edits only its scope; one task ID per session; each task ends with "Done when" satisfied; any cross-folder change goes through the contracts in Section 5.
After every change, run all existing tests relevant to the changed code and any
new regression tests. Run tests for each affected component when a change spans
components, and report the commands and results with the task outcome.

### Per-commit QA and bug handoff

For every project commit, invoke **QA-TESTER** with the full commit SHA.
QA-TESTER confirms that the workspace is at that commit, inspects the commit's
changed files, runs every relevant test suite, and creates
`qa/runs/<full-commit-sha>/REPORT.md` using the report template. Each suite is
recorded as `PASS`, `FAIL`, `BLOCKED`, or `NOT RUN`; skipped tests or missing
Docker/dependencies are never reported as a pass. For changes with no relevant
automated tests, the report records `NOT RUN` and explains why.

When a test fails, QA-TESTER creates a `BUG-<number>.md` in the same commit
folder with the failing command, expected and actual behavior, concise failure
output, and reproduction steps. It then hands the report and bug path to
**DEV-ORCHESTRATOR**. The orchestrator identifies the owning area, creates a
task brief for **DEV-APP**, **DEV-WEB**, or **DEV-PW**, and requests a new
commit. QA-TESTER reruns the relevant tests against that fix commit and records
the new result under its SHA. Environment/setup failures are marked `BLOCKED`
and returned to the orchestrator as blockers, not misreported as application
bugs.

The report and bug files are local/CI artifacts, not GitHub issues. The
orchestrator handoff is an explicit agent task; it is not automatically
triggered by Git hooks or CI yet.

**Task brief template**
```
Task: <ID> - <title>
Role: <DEV-APP | DEV-WEB | DEV-PW | DEV-ORCHESTRATOR | QA-APP | QA-WEB | QA-TESTER>
Read: PROJECT_PLAN.md (sections: ...)
May edit: <folder>
Depends on: <IDs>
Done when: <acceptance criteria>
Tests to run: <relevant tests and commands>
QA report/bug: <path or N/A>
Out of scope: everything else
```

---

## 8. Task list

Status values: `todo`, `doing`, `done`. Work in order by phase. Within a phase, respect "Depends".

### Phase 0: Setup

| ID | Task | Agent | Depends | Done when | Status |
|---|---|---|---|---|---|
| REPO-01 | Create repo and folder structure (Section 2) | DEV-APP | - | Structure committed, empty READMEs in each folder | done |
| REPO-02 | `.gitignore`, `.env.example`, root README skeleton | DEV-APP | REPO-01 | No secrets tracked; env vars documented | done |
| REPO-03 | Create `.agents/` role files and task brief template | DEV-APP | REPO-01 | Five role files exist with scope and rules | done |
| REPO-04 | Set monthly API spend cap and store key locally | (manual) | - | Cap set; key in `.env` only | todo |
| DB-01 | `docker-compose.yml` with MongoDB | DEV-APP | REPO-01 | `docker compose up` gives a reachable Mongo; Compose smoke tests pass | doing |
| REPO-05 | Add QA agent and per-commit test reports | QA-TESTER | REPO-03 | QA report template and bug handoff flow are documented | done |
| REPO-06 | Add dev workflow orchestrator for QA bugs | DEV-ORCHESTRATOR | REPO-05 | Failed tests are assigned to a scoped DEV role and retested | done |

### Phase 1: Demo web

| ID | Task | Agent | Depends | Done when | Status |
|---|---|---|---|---|---|
| WEB-01 | Site skeleton: layout, navigation, shared styles | DEV-WEB | REPO-01 | All page links work | todo |
| WEB-02 | Registration form page with validation | DEV-WEB | WEB-01 | Valid and invalid inputs behave as specified | todo |
| WEB-03 | Confirmation page showing submitted data | DEV-WEB | WEB-02 | Values from the form appear correctly | todo |
| WEB-04 | Products table: filter, search, sort, column chooser, defaults | DEV-WEB | WEB-01 | Each table feature works and is documented | todo |
| WEB-05 | Product details page | DEV-WEB | WEB-04 | Details match table data | todo |
| WEB-06 | Inventory/orders page with repeated product descriptions | DEV-WEB | WEB-05 | Descriptions consistent in normal mode | todo |
| WEB-07 | Bug mode switches (list of defects documented) | DEV-WEB | WEB-02..06 | Each defect togglable and listed in README | todo |
| WEB-08 | UI drift mode (labels/IDs change) | DEV-WEB | WEB-02..06 | Toggle changes locators without breaking behavior | todo |
| WEB-09 | Locator variety (`data-testid` on some elements only) | DEV-WEB | WEB-02..06 | Documented which elements have test ids | todo |
| WEB-10 | Deploy (GitHub Pages or static host) and README | DEV-WEB | WEB-07 | Public URL works; instructions in README | todo |
| QW-01 | Smoke checks for every page in normal mode | QA-WEB | WEB-06 | Pass in `demo-web/tests/` | todo |
| QW-02 | Verify each bug mode produces its documented defect | QA-WEB | WEB-07 | One check per defect | todo |
| QW-03 | Verify UI drift mode | QA-WEB | WEB-08 | Locators change, behavior unchanged | todo |

### Phase 2: Playwright project

| ID | Task | Agent | Depends | Done when | Status |
|---|---|---|---|---|---|
| PW-01 | Project init: `requirements.txt`, `pytest.ini`, `setup.sh/.ps1` (installs browsers) | DEV-PW | REPO-01 | Fresh clone + setup script gives a working environment | todo |
| PW-02 | `conftest.py`: base URL option, context setup, video/trace/screenshot on failure, Allure hooks | DEV-PW | PW-01 | Failing test produces video, trace and screenshot | todo |
| PW-03 | `helpers/forms.py` | DEV-PW | PW-02 | Helpers cover fill, select, submit, read validation messages | todo |
| PW-04 | `helpers/tables.py` | DEV-PW | PW-02 | Helpers cover rows, filter, search, sort, columns, defaults | todo |
| PW-05 | `helpers/compare.py` | DEV-PW | PW-03, PW-04 | Compare values across pages | todo |
| PW-06 | Data loader for `test_data/` (YAML/JSON) | DEV-PW | PW-02 | Tests read data from files | todo |
| PW-07 | Golden test per type (form, table, compare) against `demo-web` | DEV-PW | PW-03..06, WEB-06 | Three passing tests used as few-shot examples | todo |
| PW-08 | Allure configuration and local report script | DEV-PW | PW-02 | One command produces a report | todo |

### Phase 3: Application core

| ID | Task | Agent | Depends | Done when | Status |
|---|---|---|---|---|---|
| APP-01 | App skeleton: config, logging, settings from `.env` | DEV-APP | REPO-02 | App starts and reads config | todo |
| APP-02 | `llm_client.py`: retries, token/cost logging, record/replay mode | DEV-APP | APP-01 | Calls logged; replay works without network | todo |
| APP-03 | MongoDB layer: models, repositories, indexes | DEV-APP | DB-01, APP-01 | CRUD for the four collections | todo |
| APP-04 | Page Explorer | DEV-APP | APP-01 | URL in, structured JSON of the page out | todo |
| APP-05 | Pydantic schemas: test spec, run result, page fact | DEV-APP | APP-01 | Schemas validated in tests | todo |
| APP-06 | Runner: pytest via subprocess, collect artifacts and result | DEV-APP | PW-02, APP-03 | Returns pass/fail plus artifact paths, stores in `runs` | todo |
| APP-07 | Knowledge Collector | DEV-APP | APP-03, APP-06 | Passing run stores facts in `page_facts` | todo |
| TST-01 | Unit tests for core (with `mongomock`) | QA-APP | APP-02..07 | Core modules covered; CI-ready | todo |

### Phase 4: Runtime agents

| ID | Task | Agent | Depends | Done when | Status |
|---|---|---|---|---|---|
| AGT-01 | Prompt structure and versioning | DEV-APP | APP-02 | Prompts loaded from files with version recorded | todo |
| AGT-02 | Form specialist + Generator | DEV-APP | APP-04, APP-05, PW-07, AGT-01 | A form description becomes passing code on `demo-web` | todo |
| AGT-03 | Reviewer: static rules | DEV-APP | AGT-02 | Rule list in Section 9 enforced in code | todo |
| AGT-04 | Reviewer: LLM check against the description | DEV-APP | AGT-03 | Catches at least one real mismatch in a test case | todo |
| AGT-05 | Generator/Reviewer loop with limits | DEV-APP | AGT-04 | Max attempts respected; `needs_manual` status | todo |
| AGT-06 | Orchestrator with confidence score | DEV-APP | AGT-02 | Returns type + confidence as structured output | todo |
| AGT-07 | Clarifying-question flow for low confidence | DEV-APP | AGT-06 | Low confidence yields a question, not a guess | todo |
| AGT-08 | Table specialist | DEV-APP | AGT-05, PW-04 | Filter/search/column/default descriptions produce passing tests | todo |
| AGT-09 | Compare specialist (uses `page_facts`) | DEV-APP | AGT-05, APP-07, PW-05 | Cross-page description produces a passing test | todo |
| AGT-10 | Healer with guardrails (no assertion weakening) | DEV-APP | APP-06, AGT-05 | A test broken by UI drift mode is repaired | todo |
| EVAL-01 | Classification benchmark: 20+ labeled descriptions | QA-APP | AGT-06 | Accuracy measured and recorded | todo |
| EVAL-02 | Healer benchmark on drift/bug scenarios | QA-APP | AGT-10, WEB-08 | Repair rate measured and recorded | todo |

### Phase 5: UI

| ID | Task | Agent | Depends | Done when | Status |
|---|---|---|---|---|---|
| UI-01 | Streamlit skeleton | DEV-APP | APP-01 | Page loads | todo |
| UI-02 | Input form: URL + free text or table | DEV-APP | UI-01 | Input validated and passed to Orchestrator | todo |
| UI-03 | Display detected type, generated code, Reviewer verdict | DEV-APP | UI-02, AGT-05 | Visible in UI | todo |
| UI-04 | Run button and playback of video/screenshots | DEV-APP | UI-03, APP-06 | User sees the run | todo |
| UI-05 | Test history from MongoDB | DEV-APP | UI-04, APP-03 | Past tests and runs listed | todo |
| UI-06 | Link to Allure report | DEV-APP | UI-04, PW-08 | Report opens from the UI | todo |

### Phase 6: Application quality

| ID | Task | Agent | Depends | Done when | Status |
|---|---|---|---|---|---|
| TST-02 | Agent tests with recorded LLM responses | QA-APP | AGT-05 | Deterministic tests, no network | todo |
| TST-03 | End-to-end: description to passing run on `demo-web` | QA-APP | UI-04, AGT-09 | Automated e2e passes | todo |
| TST-04 | End-to-end: Healer scenario | QA-APP | AGT-10 | Drift mode repaired automatically | todo |

### Phase 7: CI, docs, presentation

| ID | Task | Agent | Depends | Done when | Status |
|---|---|---|---|---|---|
| CI-01 | Separate workflows per folder | DEV-APP | TST-01, QW-01, PW-07 | Each folder builds and tests independently | todo |
| CI-02 | End-to-end workflow with Mongo service container | DEV-APP | TST-03 | E2E runs on push or manually | todo |
| CI-03 | Publish Allure report from CI | DEV-APP | CI-01 | Report available as artifact or page | todo |
| DOC-01 | README with architecture diagram, run instructions, known limits | DEV-APP | CI-01 | A new person can run it from the README | todo |
| DOC-02 | Demo recording (1-2 minutes) | (manual) | TST-03 | Video exists | todo |
| DOC-03 | Publish the repo with a short project write-up | (manual) | DOC-01 | Published | todo |
| OBS-01 | (Optional) Grafana dashboard: success rate, healing attempts, cost per test | DEV-APP | APP-03, TST-03 | Dashboard shows data from MongoDB | todo |

**Core scope:** Phases 0-5 plus TST-03. Phases 6-7 extras and `OBS-01` can follow.

---

## 9. Reviewer rules (AGT-03 / AGT-04)

**Static (plain code):**
- At least one assertion.
- No `sleep`.
- No hardcoded URLs, credentials or expected values.
- Interactions go through helpers where a helper exists.
- Locators are role/label/test-id based.
- Docstring contains the original description.
- Linting passes (`ruff`).

**LLM check:**
- The test checks what the user asked, and nothing else.
- No redundant steps.
- The expected result is explicit and correct.

**Healer guardrail check (AGT-10):** the diff must not remove or weaken assertions.

---

## 10. Success metrics

| Metric | Initial target |
|---|---|
| Tests generated and passing without intervention | 60%+ |
| Tests passing after Healer | 80%+ |
| Orchestrator classification accuracy (EVAL-01) | 90%+ |
| Time from URL to a running test | under 2 minutes |
| Average cost per test | measured and documented |

---

## 11. Risks

| Risk | Mitigation |
|---|---|
| Invented locators | Mandatory Page Explorer data |
| API cost overruns | Spend cap, cheap model for classification/review, replay mode, bounded loops |
| Healer weakens tests | Explicit rule plus diff check |
| Flaky tests | Re-run once before invoking the Healer |
| Scope creep | Work by task ID; core scope defined in Section 8 |
| Hidden coupling between folders | Contracts in Section 5; separate dependency files and CI |

---

## 12. Open questions

1. Streamlit for the MVP UI, or a custom frontend later?
2. Which LLM provider and models, within what budget?
3. Test description as a table: which columns (step, action, data, expected result)?
4. What identifies "the same product" for cross-page comparison (name, SKU)?
5. Confirm the interpretation of Section 7: dev-process agents (DEV/QA roles) used to build the project, separate from runtime agents.

---

## 13. Starting point

1. REPO-01, REPO-02, REPO-03.
2. DB-01.
3. WEB-01 to begin the demo web, in parallel with PW-01.
