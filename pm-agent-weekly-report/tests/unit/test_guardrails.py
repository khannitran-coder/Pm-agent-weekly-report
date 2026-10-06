import pytest
from harness.guardrails import HarnessGuardrails, SecurityViolationError

def test_severity_conservation_pass():
    guardrail = HarnessGuardrails()
    raw_updates = [{"department": "QA", "content": "All tests passed on schedule."}]
    llm_output = {"overall_status": "GREEN", "department_summaries": [{"department": "QA", "status": "GREEN"}]}
    res = guardrail.evaluate(raw_updates, llm_output)
    assert res["passed"] is True

def test_severity_conservation_fail():
    guardrail = HarnessGuardrails()
    raw_updates = [{"department": "Infrastructure", "content": "Database migration failure! System blocked."}]
    llm_output = {"overall_status": "GREEN", "department_summaries": [{"department": "Infrastructure", "status": "GREEN"}]}
    res = guardrail.evaluate(raw_updates, llm_output)
    assert res["passed"] is False
    assert res["trust_score"] < 70
