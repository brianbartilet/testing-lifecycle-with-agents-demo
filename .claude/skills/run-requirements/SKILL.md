---
name: run-requirements
description: Run Stage 1 only — fetch JIRA tickets via mock and extract structured requirements JSON. Requires ANTHROPIC_API_KEY and jira-mock running on port 8080.
disable-model-invocation: true
allowed-tools: Bash, Read
---

Run the requirements agent (Stage 1):

!`PYTHONPATH=. python -c "from apps.agents.requirements_agent import RequirementsAgent; agent = RequirementsAgent(); reqs = agent.run(output_path='tests/generated/requirements.json'); print(f'Extracted {len(reqs)} requirements')" 2>&1`

Then read `tests/generated/requirements.json` and display a summary table with columns:

| Ticket | Title | Components | AC Count |
|--------|-------|------------|----------|

Flag any requirements that have no acceptance criteria or no components assigned.
