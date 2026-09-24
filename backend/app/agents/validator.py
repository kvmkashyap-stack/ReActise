import json
from app.agents.state import AgentState
from app.tools.code_workspace import execute_workspace_command


def call_tool_safe(tool_obj, args_dict):
    if hasattr(tool_obj, "invoke"):
        return tool_obj.invoke(args_dict)
    elif hasattr(tool_obj, "func") and callable(tool_obj.func):
        return tool_obj.func(**args_dict)
    else:
        return tool_obj(**args_dict)


def validator_node(state: AgentState) -> AgentState:
    """
    Validator Node: Specialist for Executing Tests & Commands to Validate Changes.
    """
    command = state.get("pending_command") or "pytest"
    user_id = state.get("user_id", "")
    repos = state.get("active_repos", [])
    repo_name = repos[0] if repos else ""

    success = False
    try:
        raw_res = call_tool_safe(execute_workspace_command, {"user_id": user_id, "repo_name": repo_name, "command": command})
        res_dict = json.loads(str(raw_res)) if isinstance(raw_res, str) else raw_res
        success = res_dict.get("success", False)
        stdout = res_dict.get("stdout", "")
        stderr = res_dict.get("stderr", "")
        exit_code = res_dict.get("exit_code", -1)
        
        observation = f"Command: '{command}' | Exit Code: {exit_code}\nSTDOUT:\n{stdout[:1000]}\nSTDERR:\n{stderr[:1000]}"
    except Exception as e:
        observation = f"Error running validation command '{command}': {str(e)}"

    state.get("observations", []).append(f"[Validator - execute_command]: {observation[:1500]}")
    state.get("tool_results", []).append({"tool": "execute_command", "result": observation[:1500], "success": success})

    current_step = state.get("current_step", 1)
    plan = state.get("plan", [])
    for p in plan:
        if isinstance(p, dict) and p.get("step") == current_step:
            p["status"] = "completed" if success else "failed"

    if success:
        state.get("completed_steps", []).append(current_step)
        state["verification_result"] = "PASSED"
    else:
        state.get("failed_steps", []).append(current_step)
        state["verification_result"] = "FAILED"
        state["retry_count"] = state.get("retry_count", 0) + 1

    state.get("execution_log", []).append({
        "step": current_step,
        "agent": "validator",
        "action": f"Executed command '{command}'",
        "observation": observation[:300],
        "result": "PASSED" if success else "FAILED"
    })

    return state
