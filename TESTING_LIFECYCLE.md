# Testing Lifecycle with AI Agents

An end-to-end demonstration of AI-driven test automation. Claude agents drive every stage of the testing lifecycle — from reading JIRA requirements to generating BDD specs, Playwright bindings, and pytest API tests — with Allure reports published to GitHub Pages.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        JIRA Mock (port 8080)                                 │
│                   Flask API · realistic ticket JSON                          │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │  tickets JSON
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Stage 1 · RequirementsAgent                                                 │
│  Fetches JIRA tickets · Claude extracts testable requirements as JSON        │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │  requirements.json
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Stage 2 · BDDAgent                                                          │
│  Generates Gherkin .feature files grouped by component (Frontend / API)     │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │  *.feature files
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Stage 3 · StepDefinitionAgent                                               │
│  Reads .feature files · generates behave step definitions (Playwright)      │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │  *_steps.py
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Stage 4 · PlaywrightAgent                                                   │
│  Fetches live frontend HTML · generates Page Object Model class              │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │  todo_page.py (POM)
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Stage 5 · PytestAgent                                                       │
│  Reads OpenAPI YAML spec · generates comprehensive pytest test suite        │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │  test_todo_api_generated.py
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Test Execution                                                               │
│  behave (BDD) · pytest API · pytest E2E (Playwright)                        │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │  allure-results/
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Allure Report → GitHub Pages                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Target Stack

| Layer | Technology |
|---|---|
| Orchestration | n8n (Docker) |
| AI / LLM | Anthropic Claude (`claude-sonnet-4-6`) |
| BDD Testing | Python behave + Gherkin |
| E2E / UI Testing | Playwright (sync API) |
| API Testing | pytest + requests |
| Reporting | Allure 2 → GitHub Pages |
| Infrastructure | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Example App | FastAPI (backend) + Nginx/HTML (frontend) |

---

## Repository Structure

```
testing-lifecycle-with-agents-demo/
├── apps/
│   ├── example_app/              # Target application under test
│   │   ├── backend/              # FastAPI Todo REST API (port 8000)
│   │   │   ├── main.py
│   │   │   ├── requirements.txt
│   │   │   └── Dockerfile
│   │   ├── frontend/             # HTML/JS Todo UI (port 3000, via nginx)
│   │   │   ├── index.html        # data-testid attributes on all elements
│   │   │   ├── nginx.conf
│   │   │   └── Dockerfile
│   │   └── openapi.yaml          # OpenAPI 3.0 spec — fed to PytestAgent
│   │
│   ├── jira_mock/                # Mock JIRA REST API (port 8080)
│   │   ├── app.py                # Flask: /rest/api/3/search, /issue/{key}
│   │   ├── data/tickets.json     # 5 realistic Todo feature tickets
│   │   └── Dockerfile
│   │
│   ├── agents/                   # AI Agent pipeline
│   │   ├── base_agent.py         # BaseAgent: Anthropic SDK + retry + file helpers
│   │   ├── requirements_agent.py # Stage 1: JIRA → structured requirements JSON
│   │   ├── bdd_agent.py          # Stage 2: requirements → .feature files
│   │   ├── step_definition_agent.py # Stage 3: .feature → behave step defs
│   │   ├── playwright_agent.py   # Stage 4: HTML → Playwright POM class
│   │   ├── pytest_agent.py       # Stage 5: OpenAPI → pytest test file
│   │   └── orchestrator.py       # CLI: runs all stages in sequence
│   │
│   └── testing/                  # Test artifacts (baseline + AI-generated)
│       ├── features/
│       │   ├── environment.py    # behave hooks: Playwright browser lifecycle
│       │   ├── todo.feature      # Baseline BDD feature (overwritten by BDDAgent)
│       │   └── steps/
│       │       └── todo_steps.py # Baseline step defs (overwritten by StepDefinitionAgent)
│       ├── e2e/
│       │   ├── conftest.py       # Playwright pytest fixtures
│       │   ├── test_todo_e2e.py  # Baseline Playwright tests
│       │   └── pages/
│       │       └── todo_page.py  # Baseline POM (overwritten by PlaywrightAgent)
│       └── api/
│           ├── conftest.py       # requests.Session fixture
│           ├── test_todo_api.py  # Baseline API tests (hand-written)
│           └── test_todo_api_generated.py  # Generated by PytestAgent
│
├── docker-compose.yml            # Starts all services locally
├── pytest.ini                    # pytest config with allure + markers
├── requirements.txt              # harqis-core + allure-pytest + allure-behave
└── .github/workflows/
    ├── run_demo.yml              # Original harqis-core demo workflow
    └── testing-lifecycle.yml     # New: full lifecycle with allure reporting
```

---

## Prerequisites

- **Docker** and **Docker Compose**
- **Python 3.12**
- **ANTHROPIC_API_KEY** environment variable

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## Quick Start

### 1. Start all services

```bash
docker-compose up -d
```

| Service | URL |
|---|---|
| Todo API (backend) | http://localhost:8000 |
| Todo UI (frontend) | http://localhost:3000 |
| JIRA Mock | http://localhost:8080 |
| n8n Orchestration | http://localhost:5678 |
| Swagger UI | http://localhost:8000/docs |

### 2. Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
python get_started.py
```

### 3. Run the AI agent pipeline

```bash
python -m apps.agents.orchestrator
```

Runs all 5 stages, writes generated files to `apps/testing/`.

```bash
# Skip Playwright stage if frontend is not running
python -m apps.agents.orchestrator --skip-playwright

# Custom JQL filter
python -m apps.agents.orchestrator --jql "project = TODO AND status = 'Ready for Testing'"
```

### 4. Run the tests

**API tests:**
```bash
pytest apps/testing/api/ -m "smoke or regression" --alluredir=allure-results/api -v
```

**BDD tests:**
```bash
behave apps/testing/features/ \
  -f allure_behave.formatter:AllureFormatter \
  -o allure-results/bdd
```

**E2E Playwright tests:**
```bash
pytest apps/testing/e2e/ --alluredir=allure-results/e2e -v
```

### 5. View Allure report locally

```bash
allure serve allure-results/api
```

---

## Agent Pipeline Detail

### Stage 1 — RequirementsAgent

**Input:** JIRA ticket JSON (`/rest/api/3/search`)
**Output:** `apps/testing/generated/requirements.json`

Claude analyzes each ticket's `summary`, `description` (Atlassian Document Format), and `comments` to produce structured JSON:
- `business_requirement` — what must be built
- `acceptance_criteria` — verifiable conditions
- `test_scenarios` — `[{given, when, then, type}]`
- `components` — Frontend / Backend API (groups feature file output)
- `priority` — high / medium / low

### Stage 2 — BDDAgent

**Input:** `requirements.json`
**Output:** `apps/testing/features/*.feature`

Groups requirements by component, generates one `.feature` file per group. Claude uses proper Gherkin: `Feature`, `Background`, `Scenario`, `Scenario Outline`, with `@smoke`, `@regression`, `@ui`, `@api` tags.

### Stage 3 — StepDefinitionAgent

**Input:** `.feature` files
**Output:** `apps/testing/features/steps/*_steps.py`

Claude generates behave step definitions using Playwright sync API (`context.page`) and the `TodoPage` page object.

### Stage 4 — PlaywrightAgent

**Input:** Live HTML from `http://localhost:3000`
**Output:** `apps/testing/e2e/pages/todo_page.py`

Fetches running frontend HTML, identifies `data-testid` attributes, generates a complete Page Object Model class.

### Stage 5 — PytestAgent

**Input:** `apps/example_app/openapi.yaml`
**Output:** `apps/testing/api/test_todo_api_generated.py`

Reads every endpoint from the OpenAPI spec, generates pytest tests covering happy paths, 404s, 422 validation errors, with `@pytest.mark.parametrize` and `@allure.feature()` annotations.

---

## Example Application

### Backend — FastAPI Todo API

| Method | Path | Status |
|---|---|---|
| GET | `/health` | 200 |
| GET | `/todos` | 200 |
| POST | `/todos` | 201 / 422 |
| GET | `/todos/{id}` | 200 / 404 |
| PUT | `/todos/{id}` | 200 / 404 / 422 |
| DELETE | `/todos/{id}` | 204 / 404 |

Swagger UI: http://localhost:8000/docs

### Frontend — HTML Todo UI

All interactive elements carry `data-testid` attributes:

| data-testid | Element |
|---|---|
| `app-title` | Page heading |
| `todo-input` | Text input |
| `add-todo-btn` | Add button |
| `filter-all / filter-active / filter-completed` | Filter buttons |
| `todo-item` | List item (has `data-completed` attribute) |
| `todo-checkbox` | Completion toggle |
| `todo-title` | Title text |
| `delete-todo-btn` | Delete button |

### Mock JIRA API

Five pre-loaded tickets (TODO-1 to TODO-5) covering: create todo, mark complete, delete, filter, and API status codes.

---

## CI/CD — GitHub Actions

Workflow: `.github/workflows/testing-lifecycle.yml`

```
Push to main
    │
    ├─► Build & Start Services
    │
    ├─► API Tests (pytest + allure)        ─┐
    ├─► BDD Tests (behave + allure)         ├── parallel
    ├─► E2E Tests (Playwright + allure)    ─┘
    │
    └─► Generate Allure Report → GitHub Pages
```

### Enabling GitHub Pages

1. **Settings → Pages → Source:** branch `gh-pages`, folder `/`
2. Report available at `https://<username>.github.io/<repo>/`

### Secrets

| Secret | Required | Purpose |
|---|---|---|
| `GITHUB_TOKEN` | Auto | gh-pages deployment |
| `ANTHROPIC_API_KEY` | Optional | Agent pipeline (`run_agents=true`) |

### Running Agents in CI

```
Actions → Testing Lifecycle with AI Agents → Run workflow → run_agents: true
```

---

## n8n Orchestration

n8n calls `apps/n8n/utilities/command_runner.py` (Flask on port 5252) to execute the pipeline:

```json
POST http://host.docker.internal:5252/run
Authorization: Bearer {RUNNER_TOKEN}
{ "command": "python -m apps.agents.orchestrator --skip-playwright" }
```

Recommended n8n workflow sequence:
1. Cron / JIRA webhook trigger
2. HTTP node → run orchestrator
3. Wait node
4. HTTP node → `pytest apps/testing/api/`
5. HTTP node → `behave apps/testing/features/`
6. HTTP node → `allure generate`
7. Notification node

---

## Allure Reporting

Annotations used throughout the test code:

```python
@allure.feature("Todo API")
@allure.story("Create Todo")
@allure.title("POST /todos returns 201 with created todo")
@pytest.mark.smoke
def test_create_returns_201(self, client, new_todo): ...
```

Generate and open locally (requires Allure CLI):
```bash
allure generate allure-results -o allure-report --clean
allure open allure-report
```

---

## Key Design Decisions

**Baseline + generated tests coexist.** Hand-written tests provide a working CI baseline before any agent runs. Agent-generated files augment coverage without replacing the baseline.

**Agents are stateless and re-runnable.** Each agent reads fresh input on every run. Rerrunning the orchestrator overwrites previously generated files for iterative refinement.

**`data-testid` attributes are first-class.** The frontend HTML uses `data-testid` on every interactive element. PlaywrightAgent is instructed to prefer these over fragile CSS or position selectors.

**OpenAPI spec is the API test source of truth.** Versioned alongside backend code, the spec is read directly by PytestAgent so generated tests always reflect the current API contract.
