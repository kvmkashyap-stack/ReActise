from app.agents.state import AgentState
from app.core.llm import llm
from app.prompts.planner_prompt import planner_prompt
from app.schemas.planner import PlannerResponse

planner_chain = planner_prompt | llm.with_structured_output(PlannerResponse)


def planner_node(
    state: AgentState,
) -> AgentState:
    """
    Decide which action the agent should perform.
    """

    plan = planner_chain.invoke(
        {
            "question": state["question"],
            "chat_history": state.get("chat_history", ""),
            "uploaded_files": state.get("uploaded_files", "None"),
        }
    )

    state["plan"] = plan

    return state