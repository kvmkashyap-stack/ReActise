from app.core.llm import llm
from app.agents.state import AgentState
from langchain_core.messages import HumanMessage, SystemMessage


def responder_node(
    state: AgentState,
) -> AgentState:
    """
    Generate final answer using gathered information, verifier audits, and conversation history.
    """

    history_str = state.get("chat_history", "")
    verifier_feedback = state.get("verifier_feedback")

    feedback_guideline = ""
    if verifier_feedback and not verifier_feedback.approved:
        reasons_list = verifier_feedback.reasons if hasattr(verifier_feedback, "reasons") and verifier_feedback.reasons else []
        reasons_str = "\n".join([f"- {r}" for r in reasons_list])
        feedback_guideline = f"""
### CRITICAL: Previous response rejected!
The Verifier evaluated your previous draft response and flagged issues:
- Confidence Score: {verifier_feedback.confidence_score if hasattr(verifier_feedback, 'confidence_score') else 0}/100
- Evaluation Reasons:
{reasons_str or '- Answer is incomplete.'}
- Verifier Feedback/Directions: {verifier_feedback.feedback}

You must refine, correct, and optimize your solution to address these issues.
You MUST explicitly begin your response with:
"Analyzing verifier feedback and refining my previous solution... I can provide a better version than this:"
"""

    sys_content = f"""
You are an Enterprise AI Assistant.

Your responsibilities are:
- Be accurate.
- Be truthful.
- Never hallucinate facts.
- Use available tools whenever external knowledge is required.
- If uploaded documents are relevant, prefer document retrieval.
- If recent information is required, use web search.
- Explain technical concepts clearly.
- Produce professional responses.
- If you are uncertain, clearly state your uncertainty instead of inventing information.
- Do your job properly and professionally and don't hardcode any responses.

{feedback_guideline}

Conversation History:
{history_str}
"""

    response = llm.invoke(
        [
            SystemMessage(
                content=sys_content
            ),

            HumanMessage(
                content=f"""
                User Question:

                {state["question"]}


                Available Context:

                {state.get("context","")}


                Tool Output:

                {state.get("tool_output","")}


                Generate a clear and accurate answer.
                """
            ),
        ]
    )

    state["draft_answer"] = response.content

    return state