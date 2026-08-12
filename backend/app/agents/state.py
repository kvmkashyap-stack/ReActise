from typing import Optional, TypedDict

from app.schemas.planner import PlannerResponse
from app.schemas.verifier import VerifierResponse


class AgentState(TypedDict):
    user_id: str
    question: str
    chat_history: Optional[str]
    active_repos: list[str]
    uploaded_files: Optional[str]
    plan: Optional[PlannerResponse]
    tool_output: str
    context: str
    draft_answer: str
    verifier_feedback: Optional[VerifierResponse]
    final_answer: str
    retry_count: int


def create_initial_state(question: str, user_id: str) -> AgentState:
    """Helper function to construct the initial AgentState payload."""
    return {
        "user_id": user_id,
        "question": question,
        "plan": None,
        "tool_output": "",
        "context": "",
        "draft_answer": "",
        "verifier_feedback": None,
        "final_answer": "",
        "retry_count": 0,
        "active_repos": [],
        "uploaded_files": None,
    }