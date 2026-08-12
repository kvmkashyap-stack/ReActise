from langgraph.graph import END, StateGraph

from app.agents.executor import executor_node
from app.agents.planner import planner_node
from app.agents.responder import responder_node
from app.agents.state import AgentState
from app.agents.verifier import verifier_node


def verifier_router(state: AgentState) -> str:
    verification = state.get("verifier_feedback")

    # Exit if approved or feedback missing
    if not verification or verification.approved:
        return "end"

    # Prevent infinite loops (max 2 retries)
    if state.get("retry_count", 0) >= 2:
        return "end"

    # Increment retry counter on loop back
    state["retry_count"] = state.get("retry_count", 0) + 1
    return "retry"


# Create LangGraph workflow
graph = StateGraph(AgentState)

# Register nodes
graph.add_node("planner", planner_node)
graph.add_node("executor", executor_node)
graph.add_node("responder", responder_node)
graph.add_node("verifier", verifier_node)

# Starting point
graph.set_entry_point("planner")

# Normal execution path
graph.add_edge("planner", "executor")
graph.add_edge("executor", "responder")
graph.add_edge("responder", "verifier")

# Conditional path after verification
graph.add_conditional_edges(
    "verifier",
    verifier_router,
    {
        "end": END,
        "retry": "responder",
    },
)

# Compile final agent graph
react_agent = graph.compile()