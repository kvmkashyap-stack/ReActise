from app.agents.state import AgentState
from concurrent.futures import ThreadPoolExecutor

from app.tools.web_search import web_search
from app.tools.retriever import retrieve_context
from app.tools.github_loader import load_repository
from app.tools.report import generate_pdf_report
from app.tools.code_workspace import (
    list_workspace_files,
    read_workspace_file,
    write_workspace_file,
    check_code_syntax,
)


TOOLS = {
    "web_search": {
        "tool": web_search,
        "input": lambda state: {
            "query": state["question"]
        },
        "output": "tool_output",
    },

    "rag": {
        "tool": retrieve_context,
        "input": lambda state: {
            "query": state["question"],
            "user_id": state["user_id"]
        },
        "output": "context",
    },

    "github": {
        "tool": load_repository,
        "input": lambda state: state["question"],
        "output": "tool_output",
    },

    "report": {
        "tool": generate_pdf_report,
        "input": lambda state: {
            "report_text": state["draft_answer"],
            "output_path": "reports/report.pdf",
        },
        "output": "tool_output",
    },

    "list_files": {
        "tool": list_workspace_files,
        "input": lambda state: {
            "user_id": state["user_id"],
            "repo_name": state["active_repos"][0] if state.get("active_repos") else ""
        },
        "output": "tool_output",
    },

    "read_file": {
        "tool": read_workspace_file,
        "input": lambda state: {
            "user_id": state["user_id"],
            "repo_name": state["active_repos"][0] if state.get("active_repos") else "",
            "file_path": state["plan"].file_path if state["plan"] and hasattr(state["plan"], "file_path") and state["plan"].file_path else ""
        },
        "output": "tool_output",
    },

    "write_file": {
        "tool": write_workspace_file,
        "input": lambda state: {
            "user_id": state["user_id"],
            "repo_name": state["active_repos"][0] if state.get("active_repos") else ""
        },
        "output": "tool_output",
    },

    "check_syntax": {
        "tool": check_code_syntax,
        "input": lambda state: {
            "user_id": state["user_id"],
            "repo_name": state["active_repos"][0] if state.get("active_repos") else ""
        },
        "output": "tool_output",
    },
}


def executor_node(state: AgentState) -> AgentState:
    """
    Execute the sequence of tools selected by the planner.
    Runs independent gathering tools concurrently in a thread pool.
    """
    plan = state.get("plan")
    if not plan or not plan.steps:
        return state

    # Filter out non-tool steps
    steps_to_run = [step for step in plan.steps if step.action != "final_answer"]
    if not steps_to_run:
        return state

    accumulated_tool_output = []
    accumulated_context = []

    # Segregate independent gather steps and sequential workspace steps
    independent_steps = []
    sequential_steps = []
    for step in steps_to_run:
        if step.action in ["web_search", "rag", "github"]:
            independent_steps.append(step)
        else:
            sequential_steps.append(step)

    # 1. Execute independent gathering steps in parallel
    if independent_steps:
        def run_independent_step(step):
            action = step.action
            config = TOOLS.get(action)
            if not config:
                return action, "tool_output", f"Unknown action: {action}"

            tool = config["tool"]

            # Construct input parameters dynamically
            if action == "web_search":
                tool_input = {"query": state["question"]}
            elif action == "rag":
                tool_input = {
                    "query": state["question"],
                    "user_id": state["user_id"]
                }
            elif action == "github":
                tool_input = state["question"]
            else:
                tool_input = {}

            try:
                if hasattr(tool, "invoke"):
                    result = tool.invoke(tool_input)
                else:
                    result = tool(tool_input)
                return action, config["output"], result
            except Exception as e:
                return action, config["output"], f"Error: {str(e)}"

        with ThreadPoolExecutor() as executor:
            # Submit all independent tool calls concurrently
            futures = [executor.submit(run_independent_step, s) for s in independent_steps]
            for fut in futures:
                action, output_key, result = fut.result()
                if output_key == "context":
                    accumulated_context.append(f"--- Context from RAG Search ---\n{result}\n")
                else:
                    accumulated_tool_output.append(f"--- Tool Output of '{action}' ---\n{result}\n")

    # 2. Execute sequential editing steps in order (maintain dependency chain)
    for step in sequential_steps:
        action = step.action
        config = TOOLS.get(action)
        if not config:
            continue

        tool = config["tool"]
        tool_input = {}

        if action == "report":
            tool_input = {
                "report_text": state.get("draft_answer", ""),
                "output_path": "reports/report.pdf",
            }
        elif action == "list_files":
            tool_input = {
                "user_id": state["user_id"],
                "repo_name": state["active_repos"][0] if state.get("active_repos") else ""
            }
        elif action == "read_file":
            tool_input = {
                "user_id": state["user_id"],
                "repo_name": state["active_repos"][0] if state.get("active_repos") else "",
                "file_path": step.file_path or ""
            }
        elif action == "write_file":
            tool_input = {
                "user_id": state["user_id"],
                "repo_name": state["active_repos"][0] if state.get("active_repos") else "",
                "file_path": step.file_path or "",
                "content": step.content or ""
            }
        elif action == "check_syntax":
            tool_input = {
                "user_id": state["user_id"],
                "repo_name": state["active_repos"][0] if state.get("active_repos") else "",
                "file_path": step.file_path or ""
            }

        try:
            if hasattr(tool, "invoke"):
                result = tool.invoke(tool_input)
            else:
                result = tool(tool_input)
        except Exception as e:
            result = f"Error executing tool '{action}': {str(e)}"

        output_key = config["output"]
        if output_key == "context":
            accumulated_context.append(f"--- Context from RAG Search ---\n{result}\n")
        else:
            accumulated_tool_output.append(f"--- Tool Output of '{action}' ---\n{result}\n")

    # Save outputs back to state
    if accumulated_tool_output:
        state["tool_output"] = "\n".join(accumulated_tool_output)
    if accumulated_context:
        state["context"] = "\n".join(accumulated_context)

    return state