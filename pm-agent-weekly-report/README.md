# 🚀 PM Agent Weekly Report (`pm-agent-weekly-report`)

[![CI/CD Evals Gate](https://img.shields.io/badge/CI%2FCD-Passing-brightgreen?style=flat-square&logo=githubactions)](.github/workflows/ci-cd-evals.yml)
[![Architecture](https://img.shields.io/badge/Architecture-90%25%20Harness%20%7C%2010%25%20Model-blue?style=flat-square)](#-architectural-philosophy)
[![Spec-Driven](https://img.shields.io/badge/Spec-Gherkin%20BDD-orange?style=flat-square)](#-spec-driven-development-specs)
[![Python Version](https://img.shields.io/badge/Python-3.12%2B-green?style=flat-square&logo=python)](https://python.org)

**`pm-agent-weekly-report`** là hệ thống AI Agent cấp doanh nghiệp phục vụ tự động hóa và nâng cao năng lực Quản lý dự án (Project Management), giải quyết trực tiếp điểm nghẽn **PP-06 (Tổng hợp báo cáo tuần từ các Trưởng phòng)** trong SOP AI PM.

Dự án được xây dựng theo chuẩn **Agentic Engineering** từ khóa học *5-Days of AI Agents Intensive*, dịch chuyển từ việc "lập trình cảm tính" (Vibe Coding) sang thiết kế hệ thống bền vững, an toàn và có thể kiểm chứng.

---

## 📌 Kiếntrúc Cốt lõi: "90% Harness, 10% Model"

Trong hệ thống này, mô hình AI (LLM) chỉ đóng vai trò là "não bộ" xử lý suy luận (~10%), trong khi bộ khung **Harness** xung quanh quyết định 90% độ tin cậy và sự ổn định của hệ thống:

```text
[ Raw Department Updates ] (Slack, Jira, Email)
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    HARNESS INPUT GUARDRAILS                     │
│  • Prompt Injection Scanner   • PII Masking (SSN, Keys)         │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONTEXT AUGMENTATION (RAG)                   │
│  • Vector Store: PMBOK Rules, Lessons Learned, Risk Severity    │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MODEL INFERENCE (LLM - 10%)                  │
│  • Reasoning & JSON Draft Generation                            │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    HARNESS OUTPUT GUARDRAILS                    │
│  • JSON Schema Validation     • Severity Conservation Gate      │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│              TRAJECTORY EVALS & DYNAMIC TRUST SCORE             │
└─────────────────────────────────────────────────────────────────┘
          │
      ┌───┴─────────────────────────────┐
      ▼                                 ▼
[ Trust Score ≥ 80 ]            [ Trust Score < 80 ]
  Status: APPROVED                Status: ESCALATED_TO_HUMAN
  Auto-publish Draft              (Human-in-the-Loop Review)
```

---

## 📂 Cấu trúc Kho Mã Nguồn (Repository Structure)

```text
pm-agent-weekly-report/
├── .github/
│   └── workflows/
│       └── ci-cd-evals.yml         # GitHub Actions: 4 cổng kiểm duyệt tự động trước khi merge main
├── specs/                          # TIÊU CHUẨN ĐẶC TẢ (Day 5 - Spec-Driven Development)
│   ├── agents.md                   # Định nghĩa tổng thể hệ thống, ranh giới và stack
│   ├── gemini.md                   # Cấu hình mô hình & quy tắc định tuyến (Routing)
│   └── pp06_weekly_report.feature  # Bản đặc tả hành vi viết bằng Gherkin BDD (Given-When-Then)
├── skills/                         # KỸ NĂNG AGENT (Day 3 - Dynamic Context & Agent Skills)
│   └── weekly_report/
│       ├── skill.md                # Trigger, Luật bất biến & Checkpoint của kỹ năng PP-06
│       └── scripts/
│           └── clean_pii.py        # Script lập trình cứng ẩn danh dữ liệu nhạy cảm
├── harness/                        # BỘ KHUNG HARNESS (90% Sức mạnh hệ thống)
│   ├── core.py                     # Trình điều phối (Orchestrator) vòng lặp Agent
│   ├── guardrails.py               # Các "Hook" an toàn: Prompt Injection, Severity Conservation
│   └── mcp_connectors/             # KẾT NỐI NGOẠI VI (Day 2 - Giao thức MCP)
│       ├── jira_mcp.py             # MCP Server kéo trực tiếp dữ liệu từ Jira
│       └── slack_mcp.py            # MCP Server quét cập nhật từ kênh Slack
├── tests/                          # HỆ THỐNG KIỂM THỬ & ĐÁNH GIÁ (Day 4 - Security & Evals)
│   ├── unit/
│   │   └── test_guardrails.py      # Kiểm thử các rào chắn deterministic (Python code)
│   └── evals/
│       ├── eval_trajectory.py      # Đánh giá quỹ đạo (Trajectory-aware Evals) với OpenTelemetry
│       └── golden_dataset.json     # 5 kịch bản benchmark chuẩn hóa để tính Trust Score
├── README.md                       # Tài liệu hướng dẫn hệ thống
└── requirements.txt                # Các thư viện phụ thuộc (Python 3.12)
```

---

## ✨ Tính năng Nổi bật & Rào chắn An toàn

1. **Bảo toàn Mức độ Nghiêm trọng (Severity Conservation):**
   * Ngăn chặn triệt để hiện tượng AI "xoa dịu" hoặc làm mềm các rủi ro nguy cấp (tự ý đổi từ `RED` / `YELLOW` sang `GREEN` để báo cáo đẹp hơn).
   * Thuật toán trong `guardrails.py` sẽ tự động phát hiện vi phạm, hạ điểm tin cậy và khôi phục trạng thái đúng.

2. **Chống Thối rữa Ngữ cảnh (Context Rot & Progressive Disclosure):**
   * Áp dụng cơ chế **Agent Skills**. Khi khởi động, Agent chỉ nạp **Metadata siêu nhẹ (~50 tokens)**. Chi tiết kỹ năng trong `skill.md` chỉ được nạp vào ngữ cảnh khi nhiệm vụ thực sự khớp với Trigger.

3. **Giao thức Kết nối Tiêu chuẩn (MCP - Model Context Protocol):**
   * Chuẩn hóa kết nối với Jira, Slack qua MCP Servers, đóng vai trò như cổng "USB-C" giúp Agent thu thập dữ liệu tự động mà không cần copy-paste thủ công.

4. **Đánh giá Quỹ đạo & Điểm số Tin cậy Động (Dynamic Trust Score):**
   * Không chỉ kiểm tra đầu ra (Output), hệ thống theo dõi toàn bộ các bước trung gian của Agent (Tracing). Nếu Trust Score dưới **80/100**, hệ thống lập tức kích hoạt cơ chế **`ESCALATE_TO_HUMAN`**.

5. **Phát triển dựa trên Đặc tả (Spec-Driven Development):**
   * Coi *"Mã nguồn là đồ dùng một lần, Bản đặc tả là vĩnh viễn"*. Tất cả yêu cầu nghiệp vụ được viết bằng **Gherkin BDD (`specs/pp06_weekly_report.feature`)**.

---

## 🚀 Hướng dẫn Chạy Thử nghiệm (Quickstart)

### 1. Yêu cầu Tiền đề
* Python 3.12+
* Git

### 2. Cài đặt Môi trường
```bash
# Clone repository
git clone https://github.com/your-org/pm-agent-weekly-report.git
cd pm-agent-weekly-report

# Tạo môi trường ảo
python3 -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### 3. Thao tác Demo Kiểm thử trực tiếp

* **Chạy thử nghiệm Bộ khung Harness V2 (kèm RAG & Guardrails):**
  ```bash
  python harness/core.py
  ```

* **Chạy riêng Rào chắn An toàn (Guardrails Unit Demo):**
  ```bash
  python harness/guardrails.py
  ```

* **Chạy bộ kiểm thử tự động với Pytest:**
  ```bash
  pytest tests/unit/
  ```

---

## 🛡️ Quy trình CI/CD Kiểm duyệt Tự động (`ci-cd-evals.yml`)

Mỗi khi có Pull Request được tạo vào nhánh `main`, GitHub Actions sẽ tự động thực thi **4 Cổng Kiểm duyệt**:

1. **Gate 1 - Spec & Skill Syntax Check:** Dry-run bản đặc tả Gherkin BDD (`behave`) và kiểm tra cú pháp `skill.md`.
2. **Gate 2 - Unit Tests:** Chạy toàn bộ unit tests cho các guardrails trong `harness/guardrails.py`.
3. **Gate 3 - Trajectory Evals & Trust Score:** Chạy `eval_trajectory.py` trên `golden_dataset.json`. Nếu **Trust Score < 80**, PR sẽ tự động bị từ chối hợp nhất.
4. **Gate 4 - Red Team Automated Security Scan:** Bắn các kịch bản tấn công Prompt Injection đối nghịch để kiểm tra độ bền vững của bộ khung Harness.

---

## 📝 Mẫu Đặc tả BDD (`specs/pp06_weekly_report.feature`)

```gherkin
Feature: Tổng hợp báo cáo tuần từ các phòng ban (PP-06)
  Scenario: Chặn đứng hành vi làm dịu mức độ rủi ro (Severity Conservation Validation)
    When a department update is received with critical database failure
    And the LLM attempts to output the department status as "GREEN" to soften the issue
    Then the Harness "Severity Conservation" gate must catch the distortion
    And the Harness must downgrade the Trust Score below 80
    And the system must trigger an immediate escalation checkpoint for human PM review
```

---

## 📄 License & Attribution

Dự án được phát triển dựa trên các nguyên lý kiến trúc của **5-Days of AI Agents Intensive** (Google) và **SOP AI Quản lý Dự án Cá nhân**.

* Distributed under the MIT License. See `LICENSE` for more information.
