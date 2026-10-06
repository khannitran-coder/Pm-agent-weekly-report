# System Specification: PM AI Agent Architecture

## System Boundaries & Operational Rules
1. **Core Architecture**: 90% Harness, 10% Model.
2. **Execution Strategy**:
   - Automation: Administrative & repetitive tasks (PP-04, PP-25).
   - Assistance: Drafting with PM review (PP-09, PP-10).
   - Augmentation: Data analysis, scenario simulation with human decision checkpoint (PP-15, PP-21).
3. **Safety & Security**:
   - Deterministic Guardrails enforce strict rules (PII, Prompt Injections, Severity Conservation).
   - Human-in-the-loop triggers when Dynamic Trust Score < 80/100.
