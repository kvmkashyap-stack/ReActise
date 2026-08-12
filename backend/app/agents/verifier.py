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

    # Always use the draft answer (which contains the actual code/content).
    # If rejected, the retry loop will go back to executor to improve it.
    # On final exit (max retries), the user still gets the best draft, not criticism.
    state["final_answer"] = state["draft_answer"]

    return state