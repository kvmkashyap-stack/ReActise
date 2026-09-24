from app.agents.state import AgentState
from app.core.llm import llm
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List


class CompletionEvaluation(BaseModel):
    all_completed: bool = Field(..., description="True if all user objectives are satisfied.")
    summary_checklist: List[str] = Field(..., description="Checklist items with [x] or [ ] status.")
    final_summary: str = Field(..., description="Comprehensive explanation of what was completed and verified.")


evaluator_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are the Task Completion Evaluator of ReActise.
Your job is to review the user's initial goal, the plan, all execution observations, and verification results.

Determine:
1. Were all requested objectives completed?
2. Create a checklist of tasks with [x] for completed and [ ] for uncompleted/failed.
3. Formulate the final structured answer.
""",
        ),
        (
            "human",
            """
User Goal: {user_goal}
Plan: {plan}
Completed Steps: {completed_steps}
Failed Steps: {failed_steps}
Observations: {observations}
Verification Result: {verification_result}
""",
        ),
    ]
)

evaluator_chain = evaluator_prompt | llm.with_structured_output(CompletionEvaluation)


def evaluator_node(state: AgentState) -> AgentState:
    """
    Evaluator Node: Formulates final structured response and task evaluation.
    """
    eval_res: CompletionEvaluation = evaluator_chain.invoke(
        {
            "user_goal": state.get("user_goal", state.get("question", "")),
            "plan": str(state.get("plan", [])),
            "completed_steps": str(state.get("completed_steps", [])),
            "failed_steps": str(state.get("failed_steps", [])),
            "observations": str(state.get("observations", [])[-5:]),
            "verification_result": state.get("verification_result", "UNKNOWN"),
        }
    )

    # Format structured response as requested by competition instructions
    status_header = "Task completed successfully." if eval_res.all_completed else "Task partially completed or failed."
    checklist_str = "\n".join(eval_res.summary_checklist)
    
    audit_log_lines = []
    for log in state.get("execution_log", []):
        audit_log_lines.append(
            f"STEP: Step {log.get('step')}\n"
            f"ACTION: [{log.get('agent')}] {log.get('action')}\n"
            f"OBSERVATION: {log.get('observation')}\n"
            f"DECISION: {log.get('result')}\n"
            f"VERIFICATION: {'SUCCESS' if log.get('result') in ['COMPLETED', 'PASSED'] else 'PENDING/FAILED'}\n"
        )
    audit_str = "\n---\n".join(audit_log_lines)

    formatted_final = (
        f"{status_header}\n\n"
        f"### Objectives Checklist:\n{checklist_str}\n\n"
        f"### Summary:\n{eval_res.final_summary}\n\n"
        f"### ReAct Verification Audit Log:\n{audit_str}"
    )

    state["final_response"] = formatted_final
    state["final_answer"] = formatted_final
    state["draft_answer"] = formatted_final
    state["active_agent"] = "end"

    return state
