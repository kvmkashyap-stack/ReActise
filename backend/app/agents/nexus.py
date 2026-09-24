from app.agents.state import AgentState
from app.core.llm import llm
from app.tools.web_search import web_search
from app.tools.retriever import retrieve_context
from app.tools.report import generate_pdf_report
from langchain_core.messages import SystemMessage, HumanMessage


def call_tool_safe(tool_obj, args_dict):
    """Safely invoke a LangChain StructuredTool or standard function."""
    if hasattr(tool_obj, "invoke"):
        return tool_obj.invoke(args_dict)
    elif hasattr(tool_obj, "func") and callable(tool_obj.func):
        return tool_obj.func(**args_dict)
    else:
        return tool_obj(**args_dict)


def nexus_node(state: AgentState) -> AgentState:
    """
    Nexus Node: Specialist for Knowledge, Search & Reasoning.
    """
    tool_name = str(state.get("selected_tool", "rag")).lower()
    question = state.get("question", "")
    user_id = state.get("user_id", "")

    observation = ""
    success = True

    try:
        if tool_name in ["answer", "conversational", "reasoning", "greeting", "none"]:
            # Direct LLM conversational response
            res = llm.invoke([
                SystemMessage(content="You are Nexus, the friendly AI assistant of ReActise. Respond warmly and concisely to the user."),
                HumanMessage(content=question)
            ])
            observation = res.content
        elif tool_name == "web_search":
            observation = str(call_tool_safe(web_search, {"query": question}))
        elif tool_name == "report":
            draft = state.get("draft_answer", "Summary Report")
            observation = str(call_tool_safe(generate_pdf_report, {"report_text": draft, "output_path": "reports/report.pdf"}))
        elif tool_name == "rag":
            observation = str(call_tool_safe(retrieve_context, {"query": question, "user_id": user_id}))
        else:
            # Fallback to direct conversational answer
            res = llm.invoke([
                SystemMessage(content="You are Nexus, the AI assistant of ReActise. Provide a helpful response to the user's inquiry."),
                HumanMessage(content=question)
            ])
            observation = res.content
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
