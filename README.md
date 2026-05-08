# Testing Lifecycle with AI Agents

[![Testing Lifecycle CI](https://github.com/brianbartilet/testing-lifecycle-with-agents-demo/actions/workflows/testing-lifecycle.yml/badge.svg)](https://github.com/brianbartilet/testing-lifecycle-with-agents-demo/actions/workflows/testing-lifecycle.yml)

End-to-end demo of AI-driven test automation. Five Claude agents drive every stage of the QA lifecycle — from JIRA tickets to Gherkin specs, Playwright bindings, and pytest API tests — with Allure reports published to GitHub Pages.

- **Batteries included.** Mock JIRA, FastAPI app under test, nginx UI, the five agents, system prompts, baseline + generated test suites, Allure reporting — all wired up out of the box. `docker compose up`, fill in `apps.env`, run `/run-pipeline`. That's the whole local loop.
- **Scales to real systems.** The mock JIRA implements the real JIRA REST API v3 contract, so pointing `JIRA_BASE_URL` at a live instance keeps `RequirementsAgent` working unchanged. Swap in your OpenAPI spec or `data-testid`-tagged HTML and the rest of the pipeline adapts. Add stages by extending `BaseAgent`.
- **CI/CD ready.** A full GitHub Actions workflow ships in the box — pre-flight import smoke → docker services → API / BDD / E2E in parallel → Allure published to GitHub Pages — on every push. Browse [recent CI/CD runs](https://github.com/brianbartilet/testing-lifecycle-with-agents-demo/actions). Set `ANTHROPIC_API_KEY` as a repo secret and you're done.

---

## 1. Testing Lifecycle

### Pipeline architecture

The pipeline is driven by the **`/run-pipeline`** Claude Code skill — call it from any Claude Code session and the five agents run in sequence to (re)generate the entire test suite. Internally it sources `apps.env`, then invokes `agents.orchestrator`, which calls each stage and writes outputs into `tests/`.

```
┌──────────────────────────────────────────────────────────────────┐
│  /run-pipeline    (Claude Code skill — primary entrypoint)       │
│  .claude/skills/run-pipeline/SKILL.md                            │
│  ↳ source apps.env  →  python -m agents.orchestrator             │
└────────────────────────────────┬─────────────────────────────────┘
                                 │ orchestrator.run_pipeline()
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  JIRA Mock (Flask, port 8080)  ·  realistic ticket JSON          │
└────────────────────────────────┬─────────────────────────────────┘
                                 │ tickets
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  Stage 1 · RequirementsAgent                                     │
│  JIRA tickets → structured requirements JSON                     │
└────────────────────────────────┬─────────────────────────────────┘
                                 │ tests/generated/requirements.json
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  Stage 2 · BDDAgent                                              │
│  requirements → Gherkin .feature files (grouped by component)    │
└────────────────────────────────┬─────────────────────────────────┘
                                 │ tests/features/*.feature
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  Stage 3 · StepDefinitionAgent                                   │
│  .feature → Python `behave` step definitions (Playwright)        │
└────────────────────────────────┬─────────────────────────────────┘
                                 │ tests/features/steps/*_steps.py
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  Stage 4 · PlaywrightAgent                                       │
│  live frontend HTML → Page Object Model                          │
└────────────────────────────────┬─────────────────────────────────┘
                                 │ tests/e2e/pages/todo_page.py
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  Stage 5 · PytestAgent                                           │
│  OpenAPI spec → pytest API test suite                            │
└────────────────────────────────┬─────────────────────────────────┘
                                 │ tests/api/test_todo_api_generated.py
                                 ▼
   Test Execution (separate skills, not part of /run-pipeline):
     /run-bdd-tests · /run-api-tests · /run-e2e-tests
                                 │ allure-results/
                                 ▼
                  Allure Report → GitHub Pages
```

### How `/run-pipeline` maps to the code

| Layer | Lives in | What it does |
|---|---|---|
| Skill | `.claude/skills/run-pipeline/SKILL.md` | One-line bash that sources `apps.env` (so `ANTHROPIC_API_KEY` is in scope) and shells out to the orchestrator |
| Orchestrator | `agents/orchestrator.py · run_pipeline()` | Calls `RequirementsAgent → BDDAgent → StepDefinitionAgent → PlaywrightAgent → PytestAgent` in order, captures status of each stage, prints a JSON summary |
| Each agent | `agents/<name>_agent.py` (extends `BaseAgent`) | Loads its system prompt from `integrations/prompts/`, calls Anthropic, writes the artifact to disk |
| Generated artifacts | `tests/features/`, `tests/features/steps/`, `tests/e2e/pages/`, `tests/api/test_todo_api_generated.py`, `tests/generated/requirements.json` | Gitignored; safe to delete and regenerate |

Skipping a stage:

```bash
/run-pipeline                                # all 5 stages
python -m agents.orchestrator --skip-playwright          # skip Stage 4 (no frontend needed)
python -m agents.orchestrator --jql "project = TODO"     # custom JIRA filter
```

The skill is the supported entrypoint for humans; the raw `python -m agents.orchestrator` form is what CI uses (see `.github/workflows/testing-lifecycle.yml`).

### The five agents

| Stage | Agent | Input | Output |
|---|---|---|---|
| 1 | `RequirementsAgent` | JIRA `/rest/api/3/search` JSON (summary, ADF description, comments) | `tests/generated/requirements.json` — `business_requirement`, `acceptance_criteria`, `test_scenarios`, `components`, `priority` |
| 2 | `BDDAgent` | `requirements.json` | `tests/features/*.feature` — Gherkin grouped by component, tagged `@smoke` / `@regression` / `@ui` / `@api` |
| 3 | `StepDefinitionAgent` | `.feature` files | `tests/features/steps/*_steps.py` — `behave` step defs using Playwright sync API |
| 4 | `PlaywrightAgent` | live HTML at `http://localhost:3000` | `tests/e2e/pages/todo_page.py` — POM keyed off `data-testid` |
| 5 | `PytestAgent` | `apps/test_app/openapi.yaml` | `tests/api/test_todo_api_generated.py` — happy-path + 404 + 422 tests with `@pytest.mark.parametrize` and `@allure.feature` |

All agents extend `BaseAgent` (`agents/base_agent.py`): direct Anthropic SDK access, exponential-backoff retries, structured-output writers, large `max_tokens` budget. Default model: `claude-sonnet-4-6`.

### Application under test

Backend — FastAPI Todo API (`apps/test_app/backend/`):

| Method | Path | Status |
|---|---|---|
| GET | `/health` | 200 |
| GET | `/todos` | 200 |
| POST | `/todos` | 201 / 422 |
| GET | `/todos/{id}` | 200 / 404 |
| PUT | `/todos/{id}` | 200 / 404 / 422 |
| DELETE | `/todos/{id}` | 204 / 404 |

Frontend — static HTML + nginx (`apps/test_app/frontend/`). Every interactive element carries a `data-testid` attribute (`todo-input`, `add-todo-btn`, `todo-item`, `delete-todo-btn`, etc.) so PlaywrightAgent picks stable selectors.

JIRA mock — Flask app (`integrations/jira/`) serving five pre-loaded TODO-* tickets that exercise create / complete / delete / filter / status-code scenarios.

### Quick start

```bash
# 1. Install
pip install -r requirements.txt
python -m playwright install chromium

# 2. Configure local env (gitignored)
cp apps.env.example apps.env
#   then edit apps.env and set ANTHROPIC_API_KEY

# 3. Start services
docker compose up -d

# 4. Run the agent pipeline
PYTHONPATH=. python -m agents.orchestrator --skip-playwright

# 4. Run the tests
PYTHONPATH=. pytest tests/api/ -m "smoke or regression" --alluredir=allure-results/api -v
PYTHONPATH=. behave tests/features/ -f allure_behave.formatter:AllureFormatter -o allure-results/bdd
PYTHONPATH=. pytest tests/e2e/ --alluredir=allure-results/e2e -v

# 5. View report (requires Allure CLI)
allure serve allure-results/api
```

| Service | URL |
|---|---|
| Todo API | http://localhost:8000 (Swagger: `/docs`) |
| Todo UI  | http://localhost:3000 |
| JIRA mock | http://localhost:8080 |

Orchestrator flags:

```bash
python -m agents.orchestrator                   # all 5 stages
python -m agents.orchestrator --skip-playwright # skip Stage 4 (no frontend needed)
python -m agents.orchestrator --jql "project = TODO AND status = 'Ready for Testing'"
```

### CI/CD

Workflow: [`.github/workflows/testing-lifecycle.yml`](.github/workflows/testing-lifecycle.yml).

```
push / PR / workflow_dispatch
        │
        ▼
   pre-flight (import smoke)        ─ catches broken imports in seconds
        │
        ▼
   services-check (build + start)
        │
        ├──► api-tests   (pytest + allure)   ┐
        ├──► bdd-tests   (behave + allure)   ├── parallel
        ├──► e2e-tests   (Playwright)        ┘
        ├──► agent-pipeline (optional, run_agents=true)
        ▼
   allure-report → GitHub Pages (main branch only)
```

| Secret | Required | Purpose |
|---|---|---|
| `GITHUB_TOKEN` | auto | publish to `gh-pages` |
| `ANTHROPIC_API_KEY` | optional | only when `workflow_dispatch` is run with `run_agents=true` |

Allure report is published at `https://<owner>.github.io/<repo>/` after a successful `main` build. The downloaded artifact ships a `serve_report.py` helper because Allure assets need HTTP, not `file://`.

---

## 2. Claude Code

The repo is configured for [Claude Code](https://claude.ai/code). Skills live under `.claude/skills/` and are invoked as slash commands.

### Available skills

| Skill | Trigger | Purpose |
|---|---|---|
| `/run-pipeline [jql]` | manual | run all 5 agent stages |
| `/run-requirements` | manual | Stage 1 only — fetch JIRA + extract requirements |
| `/run-api-tests [marker]` | manual | `pytest tests/api/` |
| `/run-bdd-tests [tag]` | manual | `behave tests/features/` |
| `/run-e2e-tests [marker]` | manual | `pytest tests/e2e/` (Playwright) |
| `/services-up [names]` | manual | `docker compose up -d` |
| `/services-down [names]` | manual | `docker compose down` |
| `/test-agents` | manual | unit tests for the Anthropic client wrappers |
| `/commit` | manual | draft a Conventional Commits message from `git diff --cached` |
| `agent-context` | auto (path-scoped) | injects live pipeline state when editing files in `agents/**` or `integrations/prompts/**` |

### Prompts as code

System prompts for each agent are version-controlled markdown files at `integrations/prompts/`. Each file embeds the literal prompt between markers:

```markdown
<!-- BEGIN_PROMPT -->
You are a senior QA engineer...
<!-- END_PROMPT -->
```

`integrations/prompts/loader.py` reads the section between markers; everything outside is human-readable documentation that the runtime ignores. This lets prompt files double as design docs.

Files: `requirements_analysis.md`, `bdd_feature_generation.md`, `step_definition_generation.md`, `playwright_page_object.md`, `pytest_api_tests.md`.

### MCP server (optional)

`mcp/server.py` exposes Anthropic usage and cost-tracking tools as an MCP server (`harqis-work`). Configure your client with `mcp/claude_desktop_config.json.template`. Useful for monitoring spend during heavy pipeline runs; not required to use the agents.

> Note: the MCP scaffold currently registers a long list of optional integrations; only `Anthropic` is wired up in this repo. The rest fail registration gracefully (logged as warnings).

### Claude Code conventions

- All agents extend `BaseAgent` in `agents/base_agent.py`.
- Always set `PYTHONPATH=.` when running Python from the project root.
- Generated test artifacts are gitignored: `tests/generated/*.json`, `tests/api/test_todo_api_generated.py`. Hand-written baselines in `tests/` provide a working CI floor that doesn't depend on a successful agent run.
- Agents are stateless and re-runnable; rerunning the orchestrator overwrites previously generated files for iterative refinement.
- `data-testid` attributes are first-class — PlaywrightAgent is instructed to prefer them over fragile CSS or position selectors.

---

## 3. Project Composition

### Directory tree

```
testing-lifecycle-with-agents-demo/
├── agents/                          # Stages 1–5 + orchestrator (BaseAgent → 5 subclasses)
│   ├── base_agent.py
│   ├── requirements_agent.py
│   ├── bdd_agent.py
│   ├── step_definition_agent.py
│   ├── playwright_agent.py
│   ├── pytest_agent.py
│   └── orchestrator.py
│
├── integrations/                    # External services + shared assets
│   ├── antropic/                    # Anthropic SDK config + usage/cost API
│   ├── jira/                        # Mock JIRA Flask app + Dockerfile + tickets.json
│   └── prompts/                     # Versioned system prompts + loader
│       ├── loader.py
│       └── *.md                     # one per agent stage, BEGIN_PROMPT / END_PROMPT markers
│
├── apps/
│   ├── apps_config.py               # harqis-core ConfigLoaderService entry point
│   └── test_app/                    # Application under test
│       ├── backend/                 # FastAPI Todo API (port 8000) + Dockerfile
│       ├── frontend/                # HTML + nginx (port 3000) + Dockerfile
│       └── openapi.yaml             # OpenAPI 3.0 spec — input to PytestAgent
│
├── mcp/                             # MCP server (Anthropic usage + cost tools)
│   ├── server.py
│   └── claude_desktop_config.json.template
│
├── tests/
│   ├── api/                         # pytest API tests (baseline + generated)
│   ├── e2e/                         # Playwright pytest tests (POM under pages/)
│   ├── features/                    # behave Gherkin (.feature + steps/)
│   └── generated/                   # requirements.json (gitignored)
│
├── .claude/
│   ├── settings.local.json          # tool permissions
│   └── skills/                      # slash-command skills (run-pipeline, commit, …)
│
├── .github/workflows/
│   └── testing-lifecycle.yml        # CI: pre-flight → services → 3-way parallel tests → allure
│
├── docker-compose.yml               # todo-backend, todo-frontend, jira-mock
├── pytest.ini                       # markers + testpaths
├── requirements.txt                 # harqis-core + allure-pytest + allure-behave
└── README.md                        # this file
```

### Component map

| Component | Path | Role |
|---|---|---|
| Agent pipeline | `agents/` | Generates test artifacts; runs against Anthropic SDK |
| System prompts | `integrations/prompts/` | One markdown file per agent stage; loaded at runtime |
| Anthropic client | `integrations/antropic/` | SDK config (`config.py`) + usage/cost reporting |
| JIRA mock | `integrations/jira/` | Flask app, Docker-built, serves canned tickets |
| App under test | `apps/test_app/` | FastAPI backend + nginx frontend, Docker-built |
| App config | `apps/apps_config.py` | `harqis-core` `ConfigLoaderService` + `AppConfigManager` |
| MCP server | `mcp/` | Optional — exposes Anthropic usage tools to MCP clients |
| Tests | `tests/` | Baseline (hand-written) + generated artifacts |
| CI | `.github/workflows/` | Pre-flight import smoke → services → parallel tests → Allure |

### Configuration

| Variable | Default | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | (required for agents) | Claude API key |
| `JIRA_BASE_URL` | `http://localhost:8080` | mock JIRA |
| `API_BASE_URL`  | `http://localhost:8000` | Todo backend |
| `FRONTEND_URL`  | `http://localhost:3000` | Todo frontend |
| `PYTHONPATH`    | `.` | must include project root |
| `ENV_APP_CONFIG_FILE` | (optional) | path to harqis-core config YAML |
| `ANTHROPIC_ADMIN_KEY` | (optional, MCP only) | enables usage/cost tools |
| `MCP_ENABLED_APPS`    | (optional) | comma-separated filter for MCP registrations |

Local values live in **`apps.env`** at the repo root (gitignored; template at `apps.env.example`). Every `/run-*` skill sources it before running, so any keys you set there override the defaults above.

### Design decisions

- **Baseline + generated coexist.** Hand-written tests give CI a working floor before any agent runs. Generated files augment coverage — they don't replace the baseline.
- **OpenAPI is source of truth for API tests.** PytestAgent reads `apps/test_app/openapi.yaml` directly, so generated tests always reflect the current contract.
- **`data-testid` over CSS selectors.** Frontend HTML carries `data-testid` on every interactive element; PlaywrightAgent prefers them.
- **Prompts are versioned files, not constants.** Markdown with `<!-- BEGIN_PROMPT -->` markers — diffable, reviewable, and the surrounding documentation rots less than inline strings.
- **Single CI pre-flight job.** A 30-second import smoke test gates the expensive docker builds and avoids burning Actions minutes on broken imports.

---

## License

[MIT](LICENSE).
