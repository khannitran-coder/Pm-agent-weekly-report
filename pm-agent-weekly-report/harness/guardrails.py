"""
harness/guardrails.py
----------------------
Harness Output Guardrails & Safety Gates for Advanced PM AI Agent Systems.
Implements 'Severity Conservation' to prevent LLM from softening critical risks (RED/YELLOW).

Architecture Metric: 90% Harness (Guardrails + Evals) / 10% Model
Course Alignment: 5-Days of AI Agents (Day 1: Harness, Day 4: Trajectory Evals & Trust Score)
"""

import re
import json
import logging
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("Guardrails")

# --- SEVERITY HIERARCHY ---
SEVERITY_LEVELS = {
    "RED": 3,
    "YELLOW": 2,
    "GREEN": 1,
    "UNKNOWN": 0
}

# Critical keywords that deterministically force RED or YELLOW status
CRITICAL_RED_INDICATORS = [
    r"\b(blocked|halting|halted|saturation|outage|failure|down|spanner|database migration failed|security breach|budget overrun > 20%)\b",
    r"\b(unrecoverable|data loss|critical path delayed > 2 weeks)\b"
]

CRITICAL_YELLOW_INDICATORS = [
    r"\b(delayed|behind schedule|resource constraint|at risk|testing delay|budget overrun > 5%)\b",
    r"\b(dependency block|approaching deadline)\b"
]


@dataclass
class GuardrailResult:
    is_passed: bool
    trust_score: float
    violations: List[str] = field(default_factory=list)
    sanitized_output: Optional[Dict[str, Any]] = None
    action_required: str = "APPROVE"  # APPROVE, RECTIFY_AND_REVIEW, ESCALATE_TO_HUMAN


class SeverityConservationGuardrail:
    """
    Guardrail enforcing 'Severity Conservation':
    Ensures LLM output NEVER dilutes/softens the severity of risks found in raw inputs or RAG context.
    If Raw Input indicates RED, the LLM output for that department MUST be RED.
    """

    def __init__(self, trust_penalty_per_violation: float = 40.0):
        self.trust_penalty = trust_penalty_per_violation

    def extract_raw_severity(self, raw_text: str) -> str:
        """Determines the ground-truth severity from raw text using deterministic regex rules."""
        text_lower = raw_text.lower()
        
        # Check explicit status tags first (e.g. STATUS: RED)
        explicit_match = re.search(r"status\s*:\s*(red|yellow|green)", text_lower)
        if explicit_match:
            return explicit_match.group(1).upper()

        # Check for RED indicators
        for pattern in CRITICAL_RED_INDICATORS:
            if re.search(pattern, text_lower):
                return "RED"

        # Check for YELLOW indicators
        for pattern in CRITICAL_YELLOW_INDICATORS:
            if re.search(pattern, text_lower):
                return "YELLOW"

        return "GREEN"

    def evaluate(
        self, 
        raw_inputs: List[Dict[str, str]], 
        llm_output_json: Dict[str, Any],
        rag_rules: Optional[List[str]] = None
    ) -> GuardrailResult:
        """
        Cross-validates raw department updates against LLM output report.
        
        :param raw_inputs: List of dicts with 'department' and 'content' (or 'raw_text')
        :param llm_output_json: The generated JSON draft report from LLM
        :param rag_rules: Optional list of strict RAG rule overrides
        :return: GuardrailResult with Trust Score and Actions
        """
        logger.info("🛡️ [GUARDRAIL] Executing Severity Conservation Check...")
        
        violations = []
        trust_score = 100.0
        rectified_output = json.loads(json.dumps(llm_output_json))  # Deep copy
        
        # Build map of raw severity per department
        raw_severity_map: Dict[str, str] = {}
        for item in raw_inputs:
            dept = item.get("department", "Unknown").upper()
            content = item.get("content", "")
            detected_sev = self.extract_raw_severity(content)
            raw_severity_map[dept] = detected_sev
            logger.info(f"🔍 Ground Truth Extracted - Dept: '{dept}' -> Raw Severity: {detected_sev}")

        # Check LLM output departments
        dept_summaries = rectified_output.get("department_summaries", [])
        
        for dept_data in dept_summaries:
            dept_name = dept_data.get("department", "").upper()
            output_status = dept_data.get("status", "GREEN").upper()
            
            # Match with raw input
            raw_status = "GREEN"
            for raw_dept, sev in raw_severity_map.items():
                if raw_dept in dept_name or dept_name in raw_dept:
                    raw_status = sev
                    break

            raw_val = SEVERITY_LEVELS.get(raw_status, 1)
            output_val = SEVERITY_LEVELS.get(output_status, 1)

            # --- SEVERITY CONSERVATION RULE ---
            # Output Severity cannot be less than Raw Severity!
            if output_val < raw_val:
                violation_msg = (
                    f"CRITICAL DRIFT: Department '{dept_name}' raw severity is {raw_status} "
                    f"but LLM softened it to {output_status}!"
                )
                logger.error(f"🚨 [VIOLATION] {violation_msg}")
                violations.append(violation_msg)
                trust_score -= self.trust_penalty
                
                # FORCE RECTIFICATION: Override LLM output back to Raw Severity
                dept_data["status"] = raw_status
                dept_data["severity_warning"] = (
                    f"AUTOCORRECTED BY HARNESS: Status restored to {raw_status} due to Severity Conservation Policy."
                )

        # Check overall project status consistency
        max_raw_sev_val = max([SEVERITY_LEVELS.get(ss, 1) for ss in raw_severity_map.values()] or [1])
        output_overall = rectified_output.get("overall_status", "GREEN").upper()
        output_overall_val = SEVERITY_LEVELS.get(output_overall, 1)

        if output_overall_val < max_raw_sev_val:
            expected_status = [k for k, v in SEVERITY_LEVELS.items() if v == max_raw_sev_val][0]
            violation_msg = (
                f"OVERALL STATUS DILUTION: Project overall status was '{output_overall}' "
                f"but highest department risk requires '{expected_status}'!"
            )
            logger.error(f"🚨 [VIOLATION] {violation_msg}")
            violations.append(violation_msg)
            trust_score -= 20.0
            rectified_output["overall_status"] = expected_status

        # Determine final action based on Trust Score
        trust_score = max(0.0, trust_score)
        if trust_score < 70.0:
            action = "ESCALATE_TO_HUMAN"
            logger.warning(f"⚠️ Trust Score ({trust_score}/100) below threshold (70). Triggering HUMAN_ESCALATION.")
        elif len(violations) > 0:
            action = "RECTIFY_AND_REVIEW"
            logger.info(f"🔧 Rectified output generated. Trust Score: {trust_score}/100.")
        else:
            action = "APPROVE"
            logger.info("✅ All Guardrails Passed. Trust Score: 100/100.")

        return GuardrailResult(
            is_passed=(len(violations) == 0),
            trust_score=trust_score,
            violations=violations,
            sanitized_output=rectified_output,
            action_required=action
        )


# --- ADDITIONAL HARNESS HELPER GUARDRAILS ---

def sanitize_pii(text: str) -> Tuple[str, int]:
    """Sanitizes PII such as SSN, Credit Cards, and API Keys."""
    count = 0
    # SSN pattern
    text, n1 = re.subn(r"\b\d{3}-\d{2}-\d{4}\b", "[PII_REDACTED_SSN]", text)
    # Credit card pattern
    text, n2 = re.subn(r"\b(?:\d{4}[- ]?){3}\d{4}\b", "[PII_REDACTED_CC]", text)
    # Generic API Key pattern
    text, n3 = re.subn(r"\b(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{20,})\b", "[CREDENTIAL_REDACTED]", text)
    return text, (n1 + n2 + n3)


def detect_prompt_injection(text: str) -> bool:
    """Detects common adversarial injection attempts."""
    patterns = [
        r"ignore\s+(all\s+)?(previous\s+)?instructions",
        r"bypass\s+(all\s+)?(rules|guardrails|safety)",
        r"system\s*:\s*you\s+are\s+now",
        r"bỏ\s+qua\s+mọi\s+quy\s+tắc",
        r"tự\s+động\s+phê\s+duyệt"
    ]
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False


# --- DEMO / STANDALONE UNIT TEST ---
if __name__ == "__main__":
    print("=" * 80)
    print("      HARNESS GUARDRAILS DEMO: SEVERITY CONSERVATION (PP-06 USE CASE)")
    print("=" * 80)

    # Raw inputs from department leads
    raw_updates = [
        {
            "department": "Infrastructure Team",
            "content": "CRITICAL: Spanner database migration halted due to SSD IOPS saturation and write latency spikes. Blocked."
        },
        {
            "department": "Frontend UI Team",
            "content": "Status: GREEN. Finished main navigation widgets. Testing proceeding smoothly."
        }
    ]

    # Simulated LLM Output attempting to 'soften' Infrastructure's RED to GREEN
    faulty_llm_output = {
        "project_name": "Phoenix Migration",
        "overall_status": "GREEN",
        "department_summaries": [
            {
                "department": "Infrastructure Team",
                "status": "GREEN",  # <-- SOFTENED! Should be RED!
                "summary_one_liner": "Minor database hiccups, infrastructure team is looking into it."
            },
            {
                "department": "Frontend UI Team",
                "status": "GREEN",
                "summary_one_liner": "UI components finished on time."
            }
        ]
    }

    guardrail = SeverityConservationGuardrail()
    result = guardrail.evaluate(raw_updates, faulty_llm_output)

    print("\n📊 EVALUATION RESULT:")
    print(f"Passed: {result.is_passed}")
    print(f"Trust Score: {result.trust_score}/100")
    print(f"Action Required: {result.action_required}")
    print("\n🚨 Violations Caught:")
    for v in result.violations:
        print(f"  - {v}")

    print("\n🔧 Rectified Output (Harness Enforcement):")
    print(json.dumps(result.sanitized_output, indent=2, ensure_ascii=False))
    print("=" * 80)
