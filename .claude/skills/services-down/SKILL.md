---
name: services-down
description: Stop and remove Docker Compose services. Pass service names as arguments to stop specific services, or leave blank to stop all.
disable-model-invocation: true
allowed-tools: Bash
---

Stop services. If `$ARGUMENTS` is provided, stop only those services; otherwise stop all.

!`docker compose down ${ARGUMENTS} 2>&1`

Report:
- Which containers were stopped and removed
- Any errors during shutdown
