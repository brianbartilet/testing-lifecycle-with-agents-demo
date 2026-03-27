# JIRA Mock

A lightweight Flask server that mimics the JIRA REST API v3. It exists purely to stand in for a real JIRA instance so the `RequirementsAgent` can be developed and tested locally without credentials, network access, or a paid subscription.

---

## Why a mock?

Real JIRA requires OAuth/API token auth, a cloud or server URL, and a live internet connection. The mock lets you:

- Run the full agent pipeline offline or in CI with no secrets
- Control exactly what ticket data the agent receives
- Test edge cases (e.g. tickets with no description, missing components) by editing one JSON file
- Keep the demo self-contained — `docker-compose up` is all that is needed

The mock is **not** a full JIRA replacement. It only implements the three endpoints the `RequirementsAgent` calls.

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check — returns `{"status": "ok"}` |
| `GET` | `/rest/api/3/search` | Search issues by JQL query string |
| `GET` | `/rest/api/3/issue/{key}` | Fetch a single issue by key (e.g. `TODO-1`) |
| `GET` | `/rest/api/3/project` | List projects |

### JQL support

The `/search` endpoint supports basic status filtering via the `jql` query parameter:

```
jql=status = 'Ready for Testing'   →  returns only Ready for Testing tickets
jql=status = 'In Progress'         →  returns only In Progress tickets
(any other value)                  →  returns all tickets
```

---

## Running locally

```bash
# Standalone
cd apps/jira
pip install flask
python app.py
# Listening on http://localhost:8080

# Via Docker Compose (recommended)
docker-compose up jira-mock
```

---

## Ticket data — `data/tickets.json`

Five pre-loaded stories covering the Todo application feature set. Each ticket follows the real JIRA REST API v3 response shape, including:

- Atlassian Document Format (ADF) description with a `paragraph` intro and an `orderedList` of enumerated acceptance criteria
- `status`, `priority`, `issuetype`, `components`, `labels`, `fixVersions`
- `comment.comments` array with QA/developer notes referencing specific AC numbers

### Ticket summary

| Key | Summary | Components | Priority | ACs |
|---|---|---|---|---|
| `TODO-1` | User can create a new todo item | Frontend, Backend API | High | 8 |
| `TODO-2` | User can mark a todo as complete | Frontend | High | 6 |
| `TODO-3` | User can delete a todo item | Frontend, Backend API | Medium | 6 |
| `TODO-4` | User can filter todos by status | Frontend | Medium | 7 |
| `TODO-5` | API returns correct HTTP status codes | Backend API | High | 11 |

---

## Acceptance criteria format

Each ticket's description is structured as ADF with an enumerated `orderedList` so the `RequirementsAgent` parser extracts them as discrete, numbered items. Example for **TODO-1**:

```
AC-1: The todo input field is visible on the page on load
AC-2: User can type a todo title between 1 and 200 characters inclusive
AC-3: Clicking the 'Add' button submits the form and creates the todo
AC-4: Pressing the Enter key inside the input field also creates the todo
AC-5: Submitting an empty input is rejected — no todo is created and an error is shown
AC-6: The newly created todo appears at the top of the todo list immediately
AC-7: The input field is cleared after a todo is successfully added
AC-8: The todo is persisted via POST /todos and survives a page refresh
```

**TODO-2** — Mark todo as complete (6 ACs):
```
AC-1: Every todo item displays a checkbox on the left side
AC-2: Clicking the checkbox on an active todo marks it as completed
AC-3: Completed todos display their title with strikethrough text
AC-4: Completed todos are visually dimmed (reduced opacity)
AC-5: Clicking the checkbox on a completed todo toggles it back to active
AC-6: The completion state is persisted via PUT /todos/{id}
```

**TODO-3** — Delete a todo (6 ACs):
```
AC-1: Every todo item displays a Delete button
AC-2: Clicking Delete removes the todo from the visible list immediately
AC-3: The deletion is sent to the API via DELETE /todos/{id} and returns HTTP 204
AC-4: After deletion, a GET /todos/{id} for the same ID returns HTTP 404
AC-5: Deleting a todo does not affect any other todo items in the list
AC-6: Both active and completed todos can be deleted
```

**TODO-4** — Filter todos by status (7 ACs):
```
AC-1: Three filter buttons are visible: 'All', 'Active', and 'Completed'
AC-2: 'All' is the default selected filter and shows every todo
AC-3: Selecting 'Active' shows only todos where completed = false
AC-4: Selecting 'Completed' shows only todos where completed = true
AC-5: The currently active filter button is visually highlighted
AC-6: Adding a new todo while a filter is active does not reset the filter
AC-7: When a filtered view is empty, the empty-state message is displayed
```

**TODO-5** — API HTTP status codes (11 ACs):
```
AC-1:  GET /todos                     → 200 OK, JSON array
AC-2:  POST /todos (valid body)       → 201 Created, new todo object
AC-3:  GET /todos/{id} (exists)       → 200 OK, todo object
AC-4:  GET /todos/{id} (missing)      → 404 Not Found
AC-5:  PUT /todos/{id} (valid body)   → 200 OK, updated todo object
AC-6:  PUT /todos/{id} (missing)      → 404 Not Found
AC-7:  DELETE /todos/{id} (exists)    → 204 No Content
AC-8:  DELETE /todos/{id} (missing)   → 404 Not Found
AC-9:  POST /todos (empty title)      → 422 Unprocessable Entity
AC-10: POST /todos (title > 200 chars)→ 422 Unprocessable Entity
AC-11: GET /health                    → 200 OK, {status: 'ok'}
```

---

## Adding or editing tickets

Edit `data/tickets.json` directly. The ADF description structure to follow:

```json
"description": {
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [{"type": "text", "text": "User story / context sentence."}]
    },
    {
      "type": "paragraph",
      "content": [{"type": "text", "text": "Acceptance Criteria:", "marks": [{"type": "strong"}]}]
    },
    {
      "type": "orderedList",
      "content": [
        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "AC-1: first criterion"}]}]},
        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "AC-2: second criterion"}]}]}
      ]
    }
  ]
}
```

No server restart is needed — the file is read at startup. Restart the container to pick up changes:

```bash
docker-compose restart jira-mock
```

---

## Pointing at a real JIRA instance

Set the `JIRA_BASE_URL` environment variable before running the orchestrator:

```bash
export JIRA_BASE_URL="https://your-company.atlassian.net"
export JIRA_TOKEN="Basic <base64(email:api_token)>"
python -m apps.agents.orchestrator --jql "project = MYPROJ AND sprint in openSprints()"
```

Then update `RequirementsAgent.fetch_tickets()` in `apps/agents/requirements_agent.py` to pass the `Authorization` header from `JIRA_TOKEN`.
