from app.agents.state import AgentState
from app.tools.code_workspace import list_workspace_files, read_workspace_file
from app.tools.github_loader import load_repository


def octolyzer_node(state: AgentState) -> AgentState:
    """
    Octolyzer Node: Specialist for Repository Investigation & Inspection.
    """
    tool_name = state.get("selected_tool", "list_files")
    user_id = state.get("user_id", "")
    repos = state.get("active_repos", [])
    repo_name = repos[0] if repos else ""
    file_path = state.get("pending_file_path", "")

    observation = ""
    success = True

    try:
        if tool_name == "github":
            question = state.get("question", "")
            observation = str(load_repository(question))
        elif tool_name == "read_file" and file_path:
            observation = read_workspace_file(user_id=user_id, repo_name=repo_name, file_path=file_path)
        else:
            # Default to listing workspace files
            file_list = list_workspace_files(user_id=user_id, repo_name=repo_name)
            observation = f"Files in workspace:\n" + "\n".join(file_list[:50])
    except Exception as e:
        observation = f"Error in Octolyzer execution: {str(e)}"
        success = False

    state.get("observations", []).append(f"[Octolyzer - {tool_name}]: {observation[:1500]}")
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
        "agent": "octolyzer",
        "action": f"Executed {tool_name}",
        "observation": observation[:300],
        "result": "COMPLETED" if success else "FAILED"
    })

    return state
