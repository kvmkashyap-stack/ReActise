from langgraph.graph import END, StateGraph

from app.agents.state import AgentState
from app.agents.planner import planner_node
from app.agents.supervisor import supervisor_node
from app.agents.octolyzer import octolyzer_node
from app.agents.synthex import synthex_node
from app.agents.validator import validator_node
from app.agents.nexus import nexus_node
from app.agents.evaluator import evaluator_node


def supervisor_router(state: AgentState) -> str:
    """
    Route execution based on active_agent selected by supervisor.
    """
    agent = state.get("active_agent", "evaluator")
    if agent in ["octolyzer", "synthex", "validator", "nexus", "planner", "evaluator"]:
        return agent
    return "evaluator"


# Create StateGraph
graph = StateGraph(AgentState)

# Register nodes
graph.add_node("planner", planner_node)
graph.add_node("supervisor", supervisor_node)
graph.add_node("octolyzer", octolyzer_node)
graph.add_node("synthex", synthex_node)
graph.add_node("validator", validator_node)
graph.add_node("nexus", nexus_node)
graph.add_node("evaluator", evaluator_node)

# Entry point starts at planner
graph.set_entry_point("planner")

# Planner hands off to supervisor
graph.add_edge("planner", "supervisor")

# Supervisor dynamically routes to specialists
graph.add_conditional_edges(
    "supervisor",
    supervisor_router,
    {
        "octolyzer": "octolyzer",
        "synthex": "synthex",
        "validator": "validator",
        "nexus": "nexus",
        "planner": "planner",
        "evaluator": "evaluator",
    },
)

# Specialist nodes return control to supervisor to evaluate next step
graph.add_edge("octolyzer", "supervisor")
graph.add_edge("synthex", "supervisor")
graph.add_edge("validator", "supervisor")
graph.add_edge("nexus", "supervisor")

# Evaluator finishes execution
graph.add_edge("evaluator", END)

# Compile final graph
react_agent = graph.compile()