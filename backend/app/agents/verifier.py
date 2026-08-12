from app.agents.state import AgentState
from app.core.llm import llm
from app.prompts.verifier_prompt import verifier_prompt
from app.schemas.verifier import VerifierResponse

verifier_chain = verifier_prompt | llm.with_structured_output(VerifierResponse)


def verifier_node(state: AgentState) -> AgentState:
    """
    Verify the generated answer.
    """
    result: VerifierResponse = verifier_chain.invoke(
        {
            "question": state["question"],
            "plan": str(state["plan"]) if state.get("plan") else "",
            "tool_output": state.get("tool_output", ""),
            "draft_answer": state.get("draft_answer", ""),
        }
    )

    # Store structured output in state
    state["verifier_feedback"] = result

    if result.approved:
        state["final_answer"] = state["draft_answer"]
    else:
        state["final_answer"] = result.feedback

    return state