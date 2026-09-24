from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from app.agents.state import AgentState
from app.core.llm import llm


class SupervisorRouting(BaseModel):
    thought: str = Field(..., description="Reasoning for selecting the next agent/action based on the current step, plan, and prior observations.")
    next_node: Literal["octolyzer", "synthex", "nexus", "validator", "planner", "evaluator"] = Field(
        ...,
        description="The next node/agent to invoke."
    )
    target_tool: str = Field(..., description="The specific tool to invoke in the target node (e.g. list_files, read_file, write_file, execute_command, web_search, rag, report, answer).")
    file_path: str = Field("", description="File path argument if applicable.")
    content: str = Field("", description="Content argument if applicable (for write_file).")
    command: str = Field("", description="Command argument if applicable (for execute_command).")


supervisor_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are the State-Aware Supervisor of ReActise. You dynamically coordinate execution across specialist agents.

Given:
1. User Goal
2. Current Plan & Status
3. Current Step
4. Recent Observations & Tool Results

Your job is to select the NEXT node and the target tool to execute for the current step.

Available Nodes & Their Specialties:
- 'octolyzer': GitHub & Workspace Repository Investigation (tools: list_files, read_file, github)
- 'synthex': Code Modification & Editing (tools: write_file, check_syntax)
- 'validator': Code Execution & Validation (tools: execute_command)
- 'nexus': Knowledge, Web Search & Explanation (tools: web_search, rag, report, reasoning)
- 'planner': Re-planning (Choose this if the previous step failed and the plan needs to be revised)
- 'evaluator': Final Task Evaluation (Choose this if all pending steps are completed)

Rules:
- Inspect the pending steps in the plan. Choose the next node/tool to fulfill the uncompleted step.
- If a step failed and retries remain, route to 'planner' to adjust the plan or 'nexus' to analyze the error.
- If all steps are completed, route to 'evaluator'.
""",
        ),
        (
            "human",
            """
User Goal: {user_goal}
Plan: {plan}
Current Step: {current_step}
Recent Observations: {observations}
Retry Count: {retry_count}
""",
        ),
    ]
)

supervisor_chain = supervisor_prompt | llm.with_structured_output(SupervisorRouting)


def supervisor_node(state: AgentState) -> AgentState:
    """
    State-aware Supervisor Node.
    """
    # Check max retries
    if state.get("retry_count", 0) >= 3:
        state["active_agent"] = "evaluator"
        state["verification_result"] = "FAILED_MAX_RETRIES"
        return state

    plan = state.get("plan", [])
    
    # If no plan exists, route to planner
    if not plan:
        state["active_agent"] = "planner"
        return state

    # Check if all steps are completed
    pending_steps = [p for p in plan if isinstance(p, dict) and p.get("status") == "pending"]
    if not pending_steps:
        state["active_agent"] = "evaluator"
        return state

    # Current step is the first pending step
    current_p = pending_steps[0]
    step_num = current_p.get("step", state.get("current_step", 1))
    state["current_step"] = step_num

    observations = state.get("observations", [])

    routing: SupervisorRouting = supervisor_chain.invoke(
        {
            "user_goal": state.get("user_goal", state.get("question", "")),
            "plan": str(plan),
            "current_step": f"Step {step_num}: {current_p.get('task')}",
            "observations": str(observations[-3:]) if observations else "None",
            "retry_count": state.get("retry_count", 0),
        }
    )

    state["active_agent"] = routing.next_node
    state["selected_tool"] = routing.target_tool

    # Store tool parameters for execution
    state["pending_file_path"] = routing.file_path
    state["pending_content"] = routing.content
    state["pending_command"] = routing.command

    # Log supervisor decision
    state.get("execution_log", []).append({
        "step": step_num,
        "agent": "supervisor",
        "action": f"Routed to {routing.next_node} using {routing.target_tool}",
        "observation": f"Reason: {routing.thought}",
        "result": "PENDING"
    })

    return state
