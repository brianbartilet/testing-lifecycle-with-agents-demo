"""
Mock JIRA API server.

Provides realistic JIRA REST API v3 responses for the testing lifecycle demo.
Replaces a real JIRA instance so the requirements agent can be tested without credentials.
"""
import json
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "tickets.json")

with open(DATA_FILE) as f:
    TICKETS_DATA = json.load(f)

ISSUES = {issue["key"]: issue for issue in TICKETS_DATA["issues"]}


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "jira-mock"})


@app.get("/rest/api/3/search")
def search_issues():
    """Mock JIRA JQL search endpoint."""
    jql = request.args.get("jql", "")
    start_at = int(request.args.get("startAt", 0))
    max_results = int(request.args.get("maxResults", 50))

    issues = list(ISSUES.values())

    # Basic JQL status filter support
    if "status = 'Ready for Testing'" in jql or 'status = "Ready for Testing"' in jql:
        issues = [i for i in issues if i["fields"]["status"]["name"] == "Ready for Testing"]
    elif "status = 'In Progress'" in jql:
        issues = [i for i in issues if i["fields"]["status"]["name"] == "In Progress"]

    paginated = issues[start_at: start_at + max_results]
    return jsonify({
        "expand": "schema,names",
        "startAt": start_at,
        "maxResults": max_results,
        "total": len(issues),
        "issues": paginated,
    })


@app.get("/rest/api/3/issue/<key>")
def get_issue(key: str):
    """Mock JIRA issue detail endpoint."""
    if key not in ISSUES:
        return jsonify({"errorMessages": [f"Issue '{key}' not found."], "errors": {}}), 404
    return jsonify(ISSUES[key])


@app.get("/rest/api/3/project")
def list_projects():
    return jsonify([{
        "id": "10000",
        "key": "TODO",
        "name": "Todo Application",
        "projectTypeKey": "software",
        "self": "http://localhost:8080/rest/api/3/project/10000",
    }])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
