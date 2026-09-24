from app.agents.state import AgentState
from app.tools.code_workspace import write_workspace_file, check_code_syntax


def synthex_node(state: AgentState) -> AgentState:
    """
    Synthex Node: Specialist for Code Modification & Editing.
    """
    tool_name = state.get("selected_tool", "write_file")
    user_id = state.get("user_id", "")
    repos = state.get("active_repos", [])
    repo_name = repos[0] if repos else ""
    file_path = state.get("pending_file_path", "")
    content = state.get("pending_content", "")

    observation = ""
    success = True

    try:
        if tool_name == "check_syntax":
            observation = check_code_syntax(user_id=user_id, repo_name=repo_name, file_path=file_path)
            if "Syntax Error" in observation or "Format Error" in observation:
                success = False
        else:
            if not file_path:
                observation = "Error: Cannot write file without specifying file_path."
                success = False
            else:
                observation = write_workspace_file(
                    user_id=user_id,
                    repo_name=repo_name,
                    file_path=file_path,
                    content=content
                )
    except Exception as e:
        observation = f"Error in Synthex execution: {str(e)}"
        success = False

    state.get("observations", []).append(f"[Synthex - {tool_name}]: {observation[:1500]}")
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
        "agent": "synthex",
        "action": f"Executed {tool_name} on {file_path}",
        "observation": observation[:300],
        "result": "COMPLETED" if success else "FAILED"
    })

    return state
