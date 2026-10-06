---
name: weekly_report
description: Aggregates department updates into a consolidated weekly PM status report.
trigger: "aggregate weekly report", "pp-06", "tổng hợp báo cáo tuần"
---

# Skill: Weekly Report Aggregation (PP-06)

## Rules
1. Never soften status warnings (RED/YELLOW must be preserved).
2. Mask all PII elements before sending context to LLM.
3. Validate output against `WeeklyReportSchema`.
