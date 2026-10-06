# Model Configuration & Intelligent Routing Specification

## Model Allocation Matrix
- **Gemini 1.5 Pro / Ultra**: Complex reasoning, architecture planning, multi-scenario trade-off analysis (PP-15, PP-21).
- **Gemini 1.5 Flash / Gemma**: High-speed, deterministic tasks (Schema validation, PII masking, initial text parsing).

## Context Window Optimization
- Enforce Progressive Disclosure via Agent Skills metadata (~50 tokens initialization).
- Use RAG for dynamic context fetching from Vector Store instead of static system prompt bloat.
