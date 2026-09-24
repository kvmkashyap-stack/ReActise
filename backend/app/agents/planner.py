from langchain_core.prompts import ChatPromptTemplate
from app.agents.state import AgentState
from app.core.llm import llm
from app.schemas.planner import ExplicitPlanResponse, PlannerResponse, ToolCall

explicit_planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are the Master Planner of ReActise. Your job is to analyze the user's task and generate a structured step-by-step plan.

Your plan must be a list of steps, where each step has:
- step: Integer index starting from 1.
- task: Concise description of what needs to be done.
- status: Always 'pending' initially.
- depends_on: List of step numbers that must be completed before this step can run.
- tool: Optional suggested tool (web_search, rag, github, list_files, read_file, write_file, check_syntax, execute_command, report).

Guidelines:
1. Decompose the request logically into clear steps.
2. For code/bug tasks: Step 1 (Inspect/locate), Step 2 (Analyze), Step 3 (Modify/Fix), Step 4 (Validate/Test).
3. If this is a RE-PLANNING request (previous steps failed), inspect the failure observations and add new steps to fix dependencies or rectify errors.
""",
        ),
        (
            "human",
            """
User Goal: {user_goal}
Current Plan: {current_plan}
Observations/Failures: {observations}
Uploaded Files: {uploaded_files}
""",
        ),
    ]
)

planner_chain = explicit_planner_prompt | llm.with_structured_output(ExplicitPlanResponse)


def planner_node(state: AgentState) -> AgentState:
    """
    Generate or update the dynamic plan.
    """
    user_goal = state.get("user_goal") or state.get("question", "")
    current_plan = state.get("plan", [])
    observations = state.get("observations", [])

    try:
        response = planner_chain.invoke(
            {
                "user_goal": user_goal,
                "current_plan": str(current_plan),
                "observations": str(observations[-3:]) if observations else "None",
                "uploaded_files": state.get("uploaded_files", "None"),
            }
        )
        plan_dicts = [step.dict() for step in response.plan]
        thought_str = response.thought
        active_spec = response.active_specialist
    except Exception as e:
        print(f"[planner_node] Structured output failed: {e}. Falling back to default plan.")
        plan_dicts = [{"step": 1, "task": f"Process request: {user_goal}", "status": "pending", "tool": "answer"}]
        thought_str = "Generated default execution plan."
        active_spec = "nexus"

    # Preserve completed statuses if re-planning
    if current_plan and isinstance(current_plan, list):
        completed_map = {p["step"]: p["status"] for p in current_plan if isinstance(p, dict) and p.get("status") == "completed"}
        for p in plan_dicts:
            if p["step"] in completed_map:
                p["status"] = completed_map[p["step"]]

    state["plan"] = plan_dicts
    state["active_agent"] = "supervisor"

    # Log plan creation
    state.get("execution_log", []).append({
        "step": state.get("current_step", 1),
        "agent": "planner",
        "action": "Generated Plan",
        "observation": f"Created {len(plan_dicts)} plan steps.",
        "result": "SUCCESS"
    })

    # Backward compatibility for legacy PlannerResponse expected by existing legacy handlers
    legacy_tool_calls = []
    for p in plan_dicts:
        action = p.get("tool") or "rag"
        if action not in ["web_search", "rag", "github", "report", "list_files", "read_file", "write_file", "check_syntax", "execute_command", "final_answer"]:
            action = "rag"
        legacy_tool_calls.append(
            ToolCall(
                action=action,
                file_path=p.get("file_path"),
                content=p.get("content"),
                reason=p.get("task", "Step task")
            )
        )
    
    # Store legacy plan object alongside state dict plan if needed
    state["legacy_plan"] = PlannerResponse(
        thought=thought_str,
        steps=legacy_tool_calls,
        active_specialist=active_spec if active_spec in ["nexus", "octolyzer", "synthex"] else "nexus"
    )

    return state