from app.agents.state import AgentState
from app.tools.code_workspace import write_workspace_file, check_code_syntax


def call_tool_safe(tool_obj, args_dict):
    if hasattr(tool_obj, "invoke"):
        return tool_obj.invoke(args_dict)
    elif hasattr(tool_obj, "func") and callable(tool_obj.func):
        return tool_obj.func(**args_dict)
    else:
        return tool_obj(**args_dict)


def synthex_node(state: AgentState) -> AgentState:
    """
    Synthex Node: Specialist for Code Modification & Editing.
    """
    tool_name = str(state.get("selected_tool", "write_file")).lower()
    user_id = state.get("user_id", "")
    repos = state.get("active_repos", [])
    repo_name = repos[0] if repos else ""
    file_path = state.get("pending_file_path", "")
    content = state.get("pending_content", "")

    # Fail-safe auto-extraction if pending_file_path is missing or empty
    if not file_path:
        import re
        goal_text = f"{state.get('user_goal', '')} {state.get('question', '')}"
        m = re.search(r'[\w\-]+\.(?:py|json|md|ts|js|txt|html|css)', goal_text, re.IGNORECASE)
        if m:
            file_path = m.group(0)
        else:
            file_path = "workspace_script.py"

    if not content or content == "print('hello world')\n":
        from app.core.llm import llm
        from langchain_core.messages import SystemMessage, HumanMessage

        sys_prompt = """
You are Synthex, the Code Intelligence Specialist of ReActise.
Your job is to produce 100% valid, error-free, properly-indented code based on the user's request and observations.

Rules:
1. Ensure proper 4-space indentation for Python code blocks.
2. Fix any syntax errors, missing indentation, or logical bugs present in the prompt.
3. Return ONLY raw executable code (no introductory text or prose).
"""
        code_res = llm.invoke([
            SystemMessage(content=sys_prompt),
            HumanMessage(content=f"User Goal: {state.get('user_goal', state.get('question', ''))}\nTask Context: {state.get('question')}\nRecent Observations: {state.get('observations', [])}")
        ])

        raw_code = str(code_res.content).strip()
        if raw_code.startswith("```"):
            lines = raw_code.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_code = "\n".join(lines)

        content = raw_code

    observation = ""
    success = True

    try:
        if tool_name == "check_syntax":
            observation = str(call_tool_safe(check_code_syntax, {"user_id": user_id, "repo_name": repo_name, "file_path": file_path}))
            if "Syntax Error" in observation or "Format Error" in observation:
                success = False
        else:
            if not file_path:
                observation = "Error: Cannot write file without specifying file_path."
                success = False
            else:
                observation = str(call_tool_safe(write_workspace_file, {
                    "user_id": user_id,
                    "repo_name": repo_name,
                    "file_path": file_path,
                    "content": content
                }))
    except Exception as e:
        observation = f"Error in Synthex execution: {str(e)}"
        success = False

    state.get("observations", []).append(f"[Synthex - {tool_name}]: {observation[:1500]}")
    state.get("tool_results", []).append({"tool": tool_name, "result": observation[:1500], "success": success})

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
