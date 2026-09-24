from typing import Optional, TypedDict, Any, List, Dict


class AgentState(TypedDict):
    user_id: str
    question: str
    user_goal: str
    chat_history: Optional[str]
    active_repos: List[str]
    uploaded_files: Optional[str]
    
    # State-aware tracking fields
    plan: List[Dict[str, Any]]
    current_step: int
    active_agent: str
    selected_tool: str
    
    observations: List[str]
    tool_results: List[Dict[str, Any]]
    
    completed_steps: List[int]
    failed_steps: List[int]
    
    verification_result: str
    retry_count: int
    
    final_response: str
    execution_log: List[Dict[str, Any]]
    
    # Backward-compatibility fields
    tool_output: str
    context: str
    draft_answer: str
    verifier_feedback: Optional[Any]
    final_answer: str


def create_initial_state(question: str, user_id: str) -> AgentState:
    """Helper function to construct the initial AgentState payload."""
    return {
        "user_id": user_id,
        "question": question,
        "user_goal": question,
        "chat_history": None,
        "active_repos": [],
        "uploaded_files": None,
        "plan": [],
        "current_step": 1,
        "active_agent": "planner",
        "selected_tool": "none",
        "observations": [],
        "tool_results": [],
        "completed_steps": [],
        "failed_steps": [],
        "verification_result": "PENDING",
        "retry_count": 0,
        "final_response": "",
        "execution_log": [],
        "tool_output": "",
        "context": "",
        "draft_answer": "",
        "verifier_feedback": None,
        "final_answer": "",
    }