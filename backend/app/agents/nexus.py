from app.agents.state import AgentState
from app.tools.web_search import web_search
from app.tools.retriever import retrieve_context
from app.tools.report import generate_pdf_report


def nexus_node(state: AgentState) -> AgentState:
    """
    Nexus Node: Specialist for Knowledge, Search & Reasoning.
    """
    tool_name = state.get("selected_tool", "rag")
    question = state.get("question", "")
    user_id = state.get("user_id", "")

    observation = ""
    success = True

    try:
        if tool_name == "web_search":
            observation = str(web_search.invoke({"query": question}))
        elif tool_name == "report":
            draft = state.get("draft_answer", "Summary Report")
            observation = str(generate_pdf_report({"report_text": draft, "output_path": "reports/report.pdf"}))
        else:
            # Default to RAG
            observation = str(retrieve_context(query=question, user_id=user_id))
    except Exception as e:
        observation = f"Error in Nexus execution: {str(e)}"
        success = False

    state.get("observations", []).append(f"[Nexus - {tool_name}]: {observation[:1500]}")
    state.get("tool_results", []).append({"tool": tool_name, "result": observation[:1500], "success": success})

    # Update plan status for current step
    current_step = state.get("current_step", 1)
    plan = state.get("plan", [])
    for p in plan:
        if isinstance(p, dict) and p.get("step") == current_step:
            p["status"] = "completed" if success else "failed"

    if success:
        state.get("completed_steps", []).append(current_step)
    else:
        state.get("failed_steps", []).append(current_step)

    state.get("execution_log", []).append({
        "step": current_step,
        "agent": "nexus",
        "action": f"Executed {tool_name}",
        "observation": observation[:300],
        "result": "COMPLETED" if success else "FAILED"
    })

    return state
