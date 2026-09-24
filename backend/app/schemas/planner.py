from typing import Literal, Optional, List
from pydantic import BaseModel, Field


class ExplicitPlanStep(BaseModel):
    step: int = Field(..., description="Step index starting from 1")
    task: str = Field(..., description="Description of the task to be performed")
    status: str = Field("pending", description="Current status of the step (pending, completed, failed)")
    tool: str = Field("answer", description="Suggested tool (answer, web_search, rag, github, list_files, read_file, write_file, check_syntax, execute_command, report)")
    file_path: Optional[str] = Field(None, description="Target file path if applicable")
    content: Optional[str] = Field(None, description="Content to write if applicable")


class ExplicitPlanResponse(BaseModel):
    thought: str = Field(..., description="Planner reasoning and dependency analysis")
    plan: List[ExplicitPlanStep] = Field(..., description="List of plan steps")
    active_specialist: str = Field("nexus", description="Assigned specialist ('nexus', 'octolyzer', or 'synthex')")


class ToolCall(BaseModel):
    action: Literal[
        "web_search",
        "rag",
        "github",
        "report",
        "list_files",
        "read_file",
        "write_file",
        "check_syntax",
        "execute_command",
        "final_answer",
    ] = Field(
        ...,
        description="The tool action to execute.",
    )
    file_path: Optional[str] = Field(
        default=None,
        description="Path to the file to read, write, or check.",
    )
    content: Optional[str] = Field(
        default=None,
        description="The text or code content to write (only required for 'write_file').",
    )
    reason: str = Field(
        ...,
        description="Why this step is necessary.",
    )


class PlannerResponse(BaseModel):
    """
    Structured output produced by the Planner, containing a sequence of steps.
    """

    thought: str = Field(
        ...,
        description="Planner's reasoning before choosing the steps, detailing task decomposition and dependency chains.",
    )

    steps: List[ToolCall] = Field(
        ...,
        description="The list of tool steps to execute sequentially to answer the query.",
    )

    active_specialist: Literal["nexus", "octolyzer", "synthex"] = Field(
        ...,
        description="The primary specialist agent assigned to resolve the query: 'nexus' (general), 'octolyzer' (github/files), or 'synthex' (code write/refactor).",
    )