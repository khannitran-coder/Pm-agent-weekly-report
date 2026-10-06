import json
import re
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("RAG_PM_Harness")

# ==============================================================================
# 1. DATABASE & VECTOR STORE SIMULATION (DATA AUGMENTATION)
# ==============================================================================
# Grounding from "Developer's Guide to RAG": 
# Unstructured/semi-structured data is chunked and embedded into a Vector Store [7].
# We do NOT vectorize pure identifiers or aggregated numeric metrics directly [21].

HISTORICAL_VECTOR_STORE = [
    {
        "id": "chunk_001",
        "source": "PMBOK 8th Edition - Risk Management",
        "content": "Risk Severity Escalation Rule: Any blockages in technical infrastructure, particularly database io speed, network latency, or storage saturation, must be categorized as RED. Project Managers must escalate directly to the Sponsor within 24 hours.",
        "tags": ["risk", "infrastructure", "rules"]
    },
    {
        "id": "chunk_002",
        "source": "Project Phoenix Charter (V1.0)",
        "content": "Database Migration Strategy: The infrastructure team is transitioning legacy databases to Cloud Spanner. Critical paths rely on SSD provisioned IOPS to avoid write latency spikes.",
        "tags": ["database", "spanner", "infrastructure"]
    },
    {
        "id": "chunk_003",
        "source": "Lessons Learned - Q1 Retrospective",
        "content": "In Q1, we suffered a 48-hour outage because the team softened an 'Infrastructure write bottleneck' warning to 'Yellow' instead of 'Red' in the status report. Moving forward, strict status conservation is enforced: infrastructure blocks are always RED.",
        "tags": ["lessons-learned", "reporting", "severity"]
    }
]

def simulate_embedding(text):
    """
    Simulates generating a high-dimensional embedding [7].
    For this offline demo, we generate a mock semantic signature (term frequency overlap).
    """
    text_lower = text.lower()
    # Vocabulary of critical terms
    vocab = ["risk", "infrastructure", "database", "spanner", "severity", "lessons-learned", "red", "yellow", "latency", "reporting"]
    vector = [1.0 if word in text_lower else 0.0 for word in vocab]
    return vector

def cosine_similarity(v1, v2):
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude1 = sum(a * a for a in v1) ** 0.5
    magnitude2 = sum(b * b for b in v2) ** 0.5
    if magnitude1 * magnitude2 == 0:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)

def query_vector_store(query_text, top_k=2):
    """
    Executes semantic search against the mock Vector Store [6].
    """
    query_vector = simulate_embedding(query_text)
    scored_chunks = []
    
    for chunk in HISTORICAL_VECTOR_STORE:
        chunk_vector = simulate_embedding(chunk["content"])
        score = cosine_similarity(query_vector, chunk_vector)
        scored_chunks.append((score, chunk))
        
    # Sort by similarity score descending
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored_chunks[:top_k] if score > 0.0]

# ==============================================================================
# 2. THE HARNESS PLATFORM (SECURITY, ORCHESTRATION, VALIDATION)
# ==============================================================================
class RAGPMAgentHarness:
    def __init__(self):
        self.trajectory_log = []
        
    def log_trajectory(self, step_name, status, details=""):
        self.trajectory_log.append({"step": step_name, "status": status, "details": details})
        logger.info(f"📍 [TRAJECTORY] Step: {step_name} | Status: {status} {f'({details})' if details else ''}")

    # INPUT GUARDRAILS (Day 4 Security [204, 241])
    def scan_prompt_injection(self, raw_report):
        self.log_trajectory("Prompt_Injection_Scan", "RUNNING")
        injection_patterns = [
            r"bypass\s+(all\s+)?(rules|guardrails)",
            r"ignore\s+(previous\s+)?(instructions|rules)",
            r"override\s+status"
        ]
        for pattern in injection_patterns:
            if re.search(pattern, raw_report, re.IGNORECASE):
                self.log_trajectory("Prompt_Injection_Scan", "FAILED", "Malicious pattern matched.")
                return False
        self.log_trajectory("Prompt_Injection_Scan", "SUCCESS")
        return True

    def scan_and_mask_pii(self, raw_report):
        self.log_trajectory("PII_Scan", "RUNNING")
        # Mask social security numbers or credit card numbers [19, 241]
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        cc_pattern = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
        
        masked_report = re.sub(ssn_pattern, "[MASKED_SSN]", raw_report)
        masked_report = re.sub(cc_pattern, "[MASKED_CC]", masked_report)
        
        if "[MASKED_SSN]" in masked_report or "[MASKED_CC]" in masked_report:
            self.log_trajectory("PII_Scan", "PII_DETECTED_AND_MASKED")
        else:
            self.log_trajectory("PII_Scan", "CLEAN")
        return masked_report

    # RAG INFERENCE STEP (Day 3 & RAG Guide [15, 28, 335])
    def run_rag_augmentation(self, query_text):
        self.log_trajectory("RAG_Retrieval", "RUNNING", f"Query: '{query_text}'")
        retrieved_chunks = query_vector_store(query_text, top_k=2)
        
        if retrieved_chunks:
            context_payload = "\n\n=== RETRIEVED HISTORICAL CONTEXT (RAG) ===\n"
            for chunk in retrieved_chunks:
                context_payload += f"Source: {chunk['source']}\nContent: {chunk['content']}\n\n"
            self.log_trajectory("RAG_Retrieval", "SUCCESS", f"Retrieved {len(retrieved_chunks)} relevant chunk(s)")
            return context_payload
        else:
            self.log_trajectory("RAG_Retrieval", "NO_RESULTS", "No highly relevant context found.")
            return "\n\n=== NO RELEVANT HISTORICAL CONTEXT RETRIEVED ===\n"

    # OUTPUT GUARDRAILS (Day 4 & Day 5 [204, 261, 360])
    def validate_schema(self, output_text):
        self.log_trajectory("Schema_Validation", "RUNNING")
        try:
            data = json.loads(output_text)
            required_keys = ["project_name", "week_ending", "overall_status", "department_summaries"]
            for key in required_keys:
                if key not in data:
                    raise KeyError(f"Missing required key: {key}")
            self.log_trajectory("Schema_Validation", "SUCCESS")
            return True, data
        except Exception as e:
            self.log_trajectory("Schema_Validation", "FAILED", str(e))
            return False, None

    def verify_severity_conservation(self, original_inputs, aggregated_report):
        """
        Enforces PMBOK X3 / SOP Rule: AI must not soften Critical/Red status flags to appease management [438, 449].
        """
        self.log_trajectory("Severity_Conservation_Verify", "RUNNING")
        
        # Check original raw inputs for RED markers or known blocker words
        input_has_red = any("RED" in inp.upper() or "critical" in inp.upper() or "blocker" in inp.upper() for inp in original_inputs)
        
        # Check generated status
        overall_status = aggregated_report.get("overall_status", "GREEN").upper()
        
        if input_has_red and overall_status == "GREEN":
            # Violation: Red risk was suppressed to Green!
            self.log_trajectory("Severity_Conservation_Verify", "FAILED", "Critical risk softened from RED/YELLOW to GREEN.")
            return False
            
        self.log_trajectory("Severity_Conservation_Verify", "SUCCESS")
        return True

    # ORCHESTRATOR EXECUTION LOOP
    def execute_rag_pipeline(self, raw_reports):
        self.log_trajectory("Initialize_Agent", "SUCCESS")
        
        cleaned_inputs = []
        for i, report in enumerate(raw_reports):
            # 1. Security Scan: Prompt Injection
            if not self.scan_prompt_injection(report):
                self.log_trajectory("Human_Escalation", "TRIGGERED", "Security threat detected in input report.")
                return {
                    "status": "ESCALATED_TO_HUMAN",
                    "reason": "Security Threat: Prompt Injection Blocked",
                    "trajectory": self.trajectory_log
                }
            
            # 2. Security Scan: PII Scrubbing
            masked_report = self.scan_and_mask_pii(report)
            cleaned_inputs.append(masked_report)

        # 3. Dynamic RAG Search based on report topic
        # We query the vector store for any infrastructure or database rules since SSD issues are present.
        rag_context = self.run_rag_augmentation("database SSD latency infrastructure severity rules")

        # 4. Model Inference Simulation (Simulating LLM execution with the Augmented Prompt)
        # Grounding: The model represents only 10% of our logic, but we augment the prompt with RAG [7, 60]
        self.log_trajectory("Model_Inference", "RUNNING")
        
        # We simulate the LLM's output. 
        # In a real environment, we would pass cleaned_inputs + rag_context to Gemini.
        # Note: If the agent attempts to "soften" the report despite the RAG rules, our output guardrail catches it.
        
        # Simulating a compliant, highly grounded AI agent output:
        simulated_llm_output = json.dumps({
            "project_name": "Phoenix Enterprise Migration",
            "week_ending": "2026-09-04",
            "overall_status": "RED",  # Compliant with PMBOK / Historical Lessons Learned RAG chunk
            "department_summaries": [
                {
                    "department": "Infrastructure Team",
                    "status": "RED",
                    "summary_one_liner": "SSD storage latency spike during Cloud Spanner migration. Blocked.",
                    "critical_action_items": [
                        "Escalate storage provision increase request immediately as per PMBOK severity rules."
                    ]
                }
            ]
        }, indent=2)
        
        self.log_trajectory("Model_Inference", "SUCCESS")

        # 5. Output Validation
        valid_schema, parsed_data = self.validate_schema(simulated_llm_output)
        if not valid_schema:
            return {
                "status": "ESCALATED_TO_HUMAN",
                "reason": "Schema Validation Failure",
                "trajectory": self.trajectory_log
            }

        # 6. Severity Conservation Check (Crucial for Business Trust)
        if not self.verify_severity_conservation(raw_reports, parsed_data):
            return {
                "status": "ESCALATED_TO_HUMAN",
                "reason": "Safety Gate Violation: Softened Department Status",
                "trajectory": self.trajectory_log
            }

        self.log_trajectory("Human_Approval_Checkpoint", "APPROVED_BY_HARNESS")
        return {
            "status": "APPROVED_BY_HARNESS",
            "data": parsed_data,
            "trajectory": self.trajectory_log
        }

# ==============================================================================
# RUN SIMULATION
# ==============================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("      AI AGENT DEPLOYMENT DEMO - USE CASE: PP-06 WITH LIVE RAG INTEGRATION")
    print("      ARCHITECTURAL METRIC: 90% HARNESS (RAG + SECURITY), 10% MODEL")
    print("=" * 80)

    # Let's mock our incoming weekly report containing infrastructure blockages
    raw_weekly_updates = [
        "Infrastructure Team update: We hit a major write latency spike during the legacy database migration. The SSD storage IOPS saturated. Currently, the Spanner migration is completely blocked.",
    ]

    harness = RAGPMAgentHarness()
    result = harness.execute_rag_pipeline(raw_weekly_updates)

    print("\nReport Processing Result:")
    print(f"Status: {result['status']}")
    if result['status'] == "APPROVED_BY_HARNESS":
        print("\nGenerated Weekly Report Draft (RAG Context Infused & Approved):")
        print(json.dumps(result['data'], indent=2))
    else:
        print(f"Reason: {result['reason']}")

    print("=" * 80)
