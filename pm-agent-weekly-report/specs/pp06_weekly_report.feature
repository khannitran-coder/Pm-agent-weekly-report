Feature: Weekly Report Aggregation (PP-06)
  As a Project Manager
  I want an AI Agent with a secure Harness to aggregate weekly status updates
  So that I can have a trustworthy, validated weekly draft report without manual copy-paste.

  Background:
    Given the static context is loaded with the Project Charter and RAID Log
    And the Harness security gates (PII Masking and Prompt Injection Filter) are active

  Scenario: Successful Report Aggregation (Happy Path)
    When raw weekly updates are received from department leads
    And all updates pass security and PII screening
    Then the Agent generates a draft weekly report in JSON format
    And the status of "Infrastructure" remains "RED"
    And the generated draft includes recommendations retrieved from RAG

  Scenario: Prevent Status Softening (Severity Conservation)
    When a department update is received with critical database failure
    And the LLM attempts to output the department status as "GREEN"
    Then the Harness "Severity Conservation" gate catches the distortion
    And the Harness downgrades the Trust Score below 80
    And the system triggers an immediate escalation checkpoint for human PM review
