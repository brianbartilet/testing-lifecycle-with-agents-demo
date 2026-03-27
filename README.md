# HARQIS Demo Generic Framework

## Introduction

- This is a demo project for [HARQIS-core](https://github.com/brianbartilet/harqis-core). 
- This can be used as a template for creating new projects and provide knowledge of basic operations of fixtures and templates.
- Please see the generated [README.md](demo/README.md) for detailed documentation of features and operations.

## Getting Started
**Setup and Installation**:
   - Runs on Python 3.12
   - Clone the repository
      ```sh
      git https://github.com/brianbartilet/harqis-core.git
      ```
   - Set up and activate the virtual environment.
      ```sh
      python -m venv venv
      source venv/bin/activate
      ```
   - Install the required packages using the requirements file for [HARQIS-core](https://github.com/brianbartilet/harqis-core) package.
      ```sh
      python -m pip install --upgrade pip
      pip install -r requirements.txt
      ```

**Generate The Demo**:     
- Run the `get_started.py` script, this will add the `demo` directory along with templates and docs.
     ```sh
     python get_started.py
     ```
- The `demo` directory is added in the `.gitignore` file.

- Run all available tests.
     ```sh
     pytest
     ```
## Testing Lifecycle with AI Agents

This project includes an end-to-end AI-driven testing lifecycle. See [TESTING_LIFECYCLE.md](TESTING_LIFECYCLE.md) for the full walkthrough.

### Quick start (with Docker)

```bash
docker compose up -d todo-backend todo-frontend jira-mock
PYTHONPATH=. python -m apps.agents.orchestrator --skip-playwright
```

### Claude Code skills

If you use [Claude Code](https://claude.ai/code), the following slash commands are available:

| Skill | Purpose |
|---|---|
| `/run-pipeline` | Run the full 5-stage agent pipeline |
| `/run-api-tests` | Run pytest API tests |
| `/run-bdd-tests` | Run behave BDD scenarios |
| `/run-e2e-tests` | Run Playwright E2E tests |
| `/services-up` | Start Docker services |
| `/services-down` | Stop Docker services |

## Full Documentation
- After successfully running `get_started.py` please see the generated [README.md](demo/README.md) for detailed documentation of features and operations.

## Getting Updates

- If you need to update the `harqis-core` package, run the following commands:
   ```bash
   pip uninstall harqis-core
   pip install -r requirements.txt --force-reinstall
   ```
## Contact

For questions or feedback, please contact [brian.bartilet@gmail.com](mailto:brian.bartilet@gmail.com).

## License

**HARQIS-demo-generic-framework** is distributed under the [MIT License](LICENSE).
