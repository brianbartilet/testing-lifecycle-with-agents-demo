---
name: agent-context
description: Load current agent pipeline state — generated requirements, features, step definitions, and API test files — for development assistance
user-invocable: false
paths: apps/agents/**/*.py,apps/prompts/**/*.md
---

## Current pipeline output state

### Generated requirements
!`cat tests/generated/requirements.json 2>/dev/null | python -c "import sys,json; data=json.load(sys.stdin); [print(f'  [{r[\"ticket_id\"]}] {r[\"title\"]} ({len(r.get(\"acceptance_criteria\",[]))} ACs)') for r in data]" 2>/dev/null || echo "  Not yet generated — run /run-requirements"`

### Generated feature files
!`ls tests/features/*.feature 2>/dev/null && wc -l tests/features/*.feature || echo "  None yet — run /run-pipeline"`

### Generated step definitions
!`ls tests/features/steps/*_steps.py 2>/dev/null || echo "  None yet"`

### Generated API test file
!`ls tests/api/test_todo_api_generated.py 2>/dev/null && echo "  Present" || echo "  Not yet generated"`

### OpenAPI endpoints available
!`PYTHONPATH=. python -c "import yaml; s=yaml.safe_load(open('apps/test_app/openapi.yaml')); [print(f'  {m.upper()} {p}') for p,ms in s['paths'].items() for m in ms]" 2>/dev/null || echo "  Could not load spec"`

Use this state when assisting with agent development, prompt tuning, or debugging pipeline failures.
