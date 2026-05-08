---
name: run-pipeline
description: Primary entry point for generating tests. Brings the required services up (jira-mock, todo-backend, todo-frontend), waits for them to pass health checks, then runs all five agent stages. Requires Docker running locally and ANTHROPIC_API_KEY set in apps.env at the repo root.
disable-model-invocation: true
allowed-tools: Bash, Read
---

The main entry point for generating an end-to-end test suite. This skill is self-contained — it boots the services it needs before invoking the orchestrator, so callers don't have to remember `/services-up` first.

Steps performed:

1. Source `apps.env` (must contain `ANTHROPIC_API_KEY`)
2. `docker compose up -d todo-backend todo-frontend jira-mock` (idempotent — no-op if already running)
3. Poll each service's health endpoint until ready (max ~30s each)
4. Run `python -m agents.orchestrator --skip-playwright`

Pass an optional JQL string as `$ARGUMENTS` (default JQL: `status = 'Ready for Testing'`).

!`if [ -f apps.env ]; then set -a; . ./apps.env; set +a; fi; echo "── starting services ──"; docker compose up -d todo-backend todo-frontend jira-mock 2>&1 || { echo "docker compose failed — is Docker Desktop running?" >&2; exit 1; }; echo "── waiting for health ──"; for spec in "jira-mock|http://localhost:8080/health|30" "todo-backend|http://localhost:8000/health|30" "todo-frontend|http://localhost:3000|20"; do name=$(echo "$spec" | cut -d'|' -f1); url=$(echo "$spec" | cut -d'|' -f2); max=$(echo "$spec" | cut -d'|' -f3); ready=0; for i in $(seq 1 "$max"); do curl -sf "$url" >/dev/null 2>&1 && { echo "  $name ready"; ready=1; break; }; sleep 1; done; [ "$ready" = "1" ] || { echo "  $name not ready after ${max}s" >&2; exit 1; }; done; echo "── running pipeline ──"; PYTHONPATH=. python -m agents.orchestrator --skip-playwright 2>&1`

After the run, summarize:
- Whether all dependencies came up healthy (or which one timed out)
- Status of each agent stage (success / error / skipped)
- How many requirements were extracted in Stage 1
- Which feature files were generated in Stage 2
- Which step definition files were generated in Stage 3
- Which test files were generated in Stage 5
- Any errors and the likely cause (missing API key, Docker not running, JIRA unreachable, etc.)

If the user wants to run the generated tests next, suggest `/run-api-tests`, `/run-bdd-tests`, or `/run-e2e-tests` — all services are already up.
