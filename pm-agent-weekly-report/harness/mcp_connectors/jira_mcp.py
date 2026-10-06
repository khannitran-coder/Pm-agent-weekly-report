# Mock MCP Server for Jira Integration
import json

class JiraMCPConnector:
    def fetch_active_sprint_issues(self, project_key: str):
        return [
            {"id": "INFRA-101", "summary": "Spanner SSD IOPS saturation", "status": "BLOCKED", "severity": "RED"},
            {"id": "FE-202", "summary": "Dashboard navigation widgets", "status": "IN_PROGRESS", "severity": "GREEN"}
        ]
