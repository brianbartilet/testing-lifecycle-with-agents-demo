# Testing Lifecycle with AI Agents

## Project overview

A demo project that automates the full QA lifecycle using a 5-stage Claude agent pipeline:

1. **RequirementsAgent** — fetches JIRA tickets (mock) and extracts structured requirements JSON
2. **BDDAgent** — converts requirements into Gherkin `.feature` files
3. **StepDefinitionAgent** — generates Python `behave` step definitions from feature files
4. **PlaywrightAgent** — inspects live frontend HTML and generates a Playwright Page Object
5. **PytestAgent** — reads the OpenAPI spec and generates a pytest API test suite

## Key directories

| Path | Purpose |
|---|---|
| `apps/agents/` | The 5 AI agents + orchestrator |
| `apps/prompts/` | System prompts for each agent (`.md` files with `<!-- BEGIN_PROMPT -->` markers) |
| `apps/test_app/` | Example FastAPI backend + Nginx frontend under test |
| `apps/jira/` | Mock JIRA REST API (Flask) serving `apps/jira/data/tickets.json` |
| `apps/antropic/` | Thin Anthropic API client wrappers (harqis-core based) |
| `tests/` | All test suites — `api/` (pytest), `e2e/` (Playwright pytest), `features/` (behave BDD) |

## Running things locally

### Prerequisites

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### Start services

```bash
docker compose up -d todo-backend todo-frontend jira-mock
```

Or use `/services-up` skill.

### Run the agent pipeline

```bash
PYTHONPATH=. python -m apps.agents.orchestrator --skip-playwright
```

Or use `/run-pipeline` skill.

### Run tests

```bash
# API tests
PYTHONPATH=. python -m pytest tests/api/ -m "smoke or regression" -v

# BDD tests
PYTHONPATH=. behave tests/features/ --tags="@smoke or @regression"

# E2E tests
PYTHONPATH=. python -m pytest tests/e2e/ -v
```

Or use `/run-api-tests`, `/run-bdd-tests`, `/run-e2e-tests` skills.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | (required) | Claude API key for all agents |
| `JIRA_BASE_URL` | `http://localhost:8080` | JIRA mock URL |
| `API_BASE_URL` | `http://localhost:8000` | Todo backend URL |
| `FRONTEND_URL` | `http://localhost:3000` | Todo frontend URL |
| `ENV_APP_CONFIG_FILE` | (optional) | Path to harqis-core config YAML |
| `PYTHONPATH` | `.` | Must include project root |

## Available Claude Code skills

| Skill | Trigger | Purpose |
|---|---|---|
| `/run-pipeline` | Manual | Run all 5 agent stages |
| `/run-requirements` | Manual | Run Stage 1 only (fetch + parse JIRA tickets) |
| `/run-api-tests [marker]` | Manual | Run pytest API tests |
| `/run-bdd-tests [tag]` | Manual | Run behave BDD scenarios |
| `/run-e2e-tests [marker]` | Manual | Run Playwright E2E tests |
| `/services-up [names]` | Manual | Start Docker Compose services |
| `/services-down [names]` | Manual | Stop Docker Compose services |
| `/test-agents` | Manual | Run unit tests for the Anthropic client module |
| `agent-context` | Auto | Injects live pipeline state when editing agent/prompt files |

## Important conventions

- All agents extend `BaseAgent` in `apps/agents/base_agent.py`
- System prompts live in `apps/prompts/*.md`, loaded via `apps/prompts/loader.py` using `<!-- BEGIN_PROMPT -->` / `<!-- END_PROMPT -->` markers
- Generated test artifacts are gitignored: `tests/generated/*.json`, `tests/api/test_todo_api_generated.py`
- Python dependency is `harqis-core` (provides pytest, behave, playwright, anthropic, Flask, requests)
- Always set `PYTHONPATH=.` when running Python commands from the project root
