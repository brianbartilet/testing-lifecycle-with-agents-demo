"""
Requirements Analysis Agent.

Fetches JIRA tickets and extracts structured, testable requirements
that downstream agents (BDD, pytest) can act on.
"""
import json
from typing import Optional
import requests

from apps.agents.base_agent import BaseAgent
from apps.prompts.loader import load as load_prompt
from core.utilities.logging.custom_logger import logger as log


SYSTEM_PROMPT = load_prompt("requirements_analysis.md")


class RequirementsAgent(BaseAgent):
    """
    Fetches JIRA tickets and uses Claude to extract structured requirements.
    Each ticket is analyzed individually; results are returned as a list.
    """

    def __init__(self, jira_base_url: str = "http://localhost:8080", api_key: Optional[str] = None):
        super().__init__(api_key=api_key)
        self.jira_base_url = jira_base_url.rstrip("/")

    def fetch_tickets(self, jql: str = "status = 'Ready for Testing'") -> list[dict]:
        """Fetch issues from the JIRA mock (or real JIRA) using a JQL query."""
        url = f"{self.jira_base_url}/rest/api/3/search"
        params = {"jql": jql, "maxResults": 50}
        log.info(f"[RequirementsAgent] Fetching tickets: GET {url} jql={jql!r}")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        issues = data.get("issues", [])
        log.info(f"[RequirementsAgent] Fetched {len(issues)} tickets")
        return issues

    def analyze_ticket(self, ticket: dict) -> dict:
        """Use Claude to extract structured requirements from a single ticket."""
        key = ticket.get("key", "UNKNOWN")
        fields = ticket.get("fields", {})
        summary = fields.get("summary", "")
        description = self._extract_description(fields.get("description"))
        components = [c["name"] for c in fields.get("components", [])]
        comments = [
            c["body"] for c in fields.get("comment", {}).get("comments", [])
            if isinstance(c.get("body"), str)
        ]

        prompt = f"""Analyze this JIRA ticket and extract structured requirements.

Ticket Key: {key}
Summary: {summary}
Components: {', '.join(components) or 'Not specified'}
Description:
{description}

Additional Comments:
{chr(10).join(comments) if comments else 'None'}
"""
        log.info(f"[RequirementsAgent] Analyzing ticket {key}")
        raw = self._ask(prompt, system=SYSTEM_PROMPT)
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            # Claude sometimes wraps in ```json ... ```
            cleaned = self._extract_code_block(raw, "json")
            result = json.loads(cleaned)
        return result

    def run(
        self,
        jql: str = "status = 'Ready for Testing'",
        output_path: Optional[str] = None,
    ) -> list[dict]:
        """
        Fetch all tickets matching JQL, analyze each, and optionally save results.

        Args:
            jql: JIRA Query Language string to filter tickets.
            output_path: If set, writes the requirements JSON to this file.

        Returns:
            List of structured requirement dicts, one per ticket.
        """
        tickets = self.fetch_tickets(jql)
        requirements = []
        for ticket in tickets:
            try:
                req = self.analyze_ticket(ticket)
                requirements.append(req)
            except Exception as exc:
                log.error(f"[RequirementsAgent] Failed to analyze {ticket.get('key')}: {exc}")

        if output_path:
            self.write_file(output_path, json.dumps(requirements, indent=2))
            log.info(f"[RequirementsAgent] Saved {len(requirements)} requirements → {output_path}")

        return requirements

    @staticmethod
    def _extract_description(description_field) -> str:
        """
        Extract plain text from JIRA's Atlassian Document Format (ADF) description.

        Handles:
        - Plain strings (legacy)
        - ADF paragraph blocks
        - ADF orderedList / bulletList blocks — items are rendered as "N. <text>"
        """
        if not description_field:
            return "No description provided."
        if isinstance(description_field, str):
            return description_field

        lines = []
        for block in description_field.get("content", []):
            block_type = block.get("type")

            if block_type == "paragraph":
                text_parts = []
                for inline in block.get("content", []):
                    if inline.get("type") == "text":
                        text_parts.append(inline.get("text", ""))
                if text_parts:
                    lines.append("".join(text_parts))

            elif block_type in ("orderedList", "bulletList"):
                prefix = "ordered" if block_type == "orderedList" else "bullet"
                for idx, item in enumerate(block.get("content", []), start=1):
                    item_text_parts = []
                    for para in item.get("content", []):
                        for inline in para.get("content", []):
                            if inline.get("type") == "text":
                                item_text_parts.append(inline.get("text", ""))
                    item_text = "".join(item_text_parts).strip()
                    if item_text:
                        marker = f"{idx}." if prefix == "ordered" else "-"
                        lines.append(f"  {marker} {item_text}")

        return "\n".join(lines) or "No description provided."
