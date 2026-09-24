# ⚡ ReActise

> **A State-Aware ReAct Multi-Agent Platform for Autonomous Software Engineering, Dynamic Planning, Real Code Execution, and Self-Correction.**

---

## 📌 Executive Summary

**ReActise** is an enterprise-grade agentic AI platform built on top of **LangGraph**, **LangChain**, and **FastAPI**. Moving beyond simple prompt-response loops, ReActise implements a **State-Aware Supervisor Paradigm** that dynamically decomposes user requests into explicit execution plans, delegates subtasks to specialist agents, executes real workspace test commands, observes runtime outputs, and autonomously **re-plans and self-corrects** upon failure.

---

## 🧠 Core Architecture: State-Aware Supervisor Pattern

Instead of static sequential routing, ReActise operates on a cyclic **StateGraph** coordinated by an LLM-driven Supervisor.

```text
                               ┌───────────────────────────┐
                               │       User Request        │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │       Master Planner      │
                               │  (Generates Explicit Plan)│
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                        ┌─────►│  State-Aware Supervisor   │◄────┐
                        │      │  (Inspects State & Steps) │     │
                        │      └─────────────┬─────────────┘     │
                        │                    │                   │
                        │      Dynamic Routing Decision          │
                        │                    │                   │
         ┌──────────────┼──────────────┬─────┴────────┬──────────┼──────────────┐
         ▼              ▼              ▼              ▼          ▼              ▼
   ✨ Nexus       🌿 Octolyzer   💻 Synthex     🧪 Validator  🔄 Re-Planner 🎯 Evaluator
 (Knowledge)      (GitHub/RAG)   (Code Edit)   (Exec Cmd)    (Update Plan) (Checklist)
         │              │              │              │          │              │
         └──────────────┴──────────────┴──────────────┴──────────┴──────────────┘
                                             │
                                   Return Control to State
```

---

## 🚀 Key Architectural Features & Upgrades

### 1. 📋 Explicit Dynamic Planner Node
- Decomposes the user's task into a structured plan consisting of numbered steps, task descriptions, initial `"pending"` status, step dependencies (`depends_on`), and suggested tools.
- Generated dynamically from the user's prompt rather than hardcoded rules.

### 2. 🗂️ Upgraded Shared LangGraph State (`AgentState`)
The system maintains a rich, persistent state across the entire trajectory:
```python
class AgentState(TypedDict):
    user_goal: str
    plan: List[Dict[str, Any]]
    current_step: int
    active_agent: str
    selected_tool: str
    observations: List[str]
    tool_results: List[Dict[str, Any]]
    completed_steps: List[int]
    failed_steps: List[int]
    verification_result: str
    retry_count: int
    final_response: str
    execution_log: List[Dict[str, Any]]
```

### 3. 🎯 State-Aware Supervisor Routing
- Evaluates `current_step`, `plan`, `observations`, and `retry_count` on every cycle.
- Dynamically selects which specialist node (`nexus`, `octolyzer`, `synthex`, `validator`, `planner`, `evaluator`) and tool parameters (`file_path`, `content`, `command`) to invoke.

### 4. 🧰 Dynamic Tool Selection
- Agents select tools dynamically based on goal requirements:
  - **Octolyzer:** `github`, `list_files`, `read_file`
  - **Synthex:** `write_file`, `check_syntax`
  - **Validator:** `execute_command` (real command execution)
  - **Nexus:** `web_search`, `rag`, `report`, `answer`

### 5. 💻 Real Code & Test Execution
- Implements `execute_workspace_command` using `subprocess.run`.
- Executes test commands (`pytest`, `python -m unittest`, `npm test`) inside isolated workspace directories.
- Captures `stdout`, `stderr`, `exit_code`, and `success` status as structured JSON for agent inspection.

### 6. 🔄 Executable Re-Plan & Self-Correction Loop
- If code execution or validation fails, the Supervisor routes control back to the **Planner**.
- The Planner inspects the failure traceback in `observations` and modifies/appends new steps to fix dependencies, modify code, and re-run tests until success is achieved.

### 7. 🛡️ Retry Guards & Safety Limits
- Built-in `MAX_RETRIES = 3` counter prevents infinite execution loops.
- If retries exceed the limit, execution safely terminates and routes to the Evaluator with a detailed failure report.

### 8. 📊 Task Completion Evaluator
- Prior to final output, the **Evaluator Node** inspects all completed and failed steps.
- Generates a structured response containing a completed objectives checklist `[x]`, summary, and verification status.

### 9. 📝 Comprehensive ReAct Verification Audit Log
- Formats every step in the trajectory showing:
  - **STEP:** Step index & task
  - **ACTION:** Agent & tool invoked
  - **OBSERVATION:** Output/Traceback returned
  - **DECISION:** State decision (PENDING/COMPLETED/FAILED)
  - **VERIFICATION:** SUCCESS / FAILED status

---

## 🤖 Multi-Agent Specialist Roles

| Agent | Icon | Role & Specialty | Tools |
| :--- | :---: | :--- | :--- |
| **Nexus** | ✨ | General Reasoning, Search & Q&A | `web_search`, `rag`, `report`, `answer` |
| **Octolyzer** | 🌿 | GitHub Intelligence & File Inspection | `github`, `list_files`, `read_file` |
| **Synthex** | 💻 | Code Synthesis & AST Validation | `write_file`, `check_syntax` |
| **Validator** | 🧪 | Runtime Command & Test Execution | `execute_workspace_command` |
| **Planner** | 📋 | Step Decomposition & Re-Planning | `ExplicitPlanResponse` |
| **Evaluator** | 🎯 | Completion Verification & Audit | `CompletionEvaluation` |

---

## 🛠️ Technology Stack

- **Frontend:** Next.js 16 (React 19), Tailwind CSS, Lucide Icons, Server-Sent Events (SSE)
- **Backend:** FastAPI, Python 3.12, Pydantic v2
- **Agent Framework:** LangGraph, LangChain
- **LLM Engine:** Groq API (`qwen/qwen3.8-27b`)
- **Vector DB / Storage:** Supabase (pgvector), FAISS (Local Fallback)
- **Code Workspace:** Subprocess Execution Engine, AST Parser

---

## 🏃 Quickstart Guide

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the application.

---

## 📄 License
Distributed under the MIT License.
