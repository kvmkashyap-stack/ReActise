from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class Message(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(
        ...,
        description="Role of the message sender.",
    )

    content: str = Field(
        ...,
        description="Message content.",
    )


class ChatRequest(BaseModel):
    session_id: str = Field(
        ...,
        description="Unique chat session ID.",
    )

    message: str = Field(
        ...,
        min_length=1,
        description="Latest user message.",
    )

    history: List[Message] = Field(
        default_factory=list,
        description="Conversation history.",
    )


class TraceStep(BaseModel):
    emoji: str = Field(..., description="Emoji representing the step.")
    label: str = Field(..., description="Human-readable step label.")
    details: Optional[str] = Field(None, description="Optional extra details about this execution step.")


class ChatResponse(BaseModel):
    answer: str = Field(
        ...,
        description="Final AI response.",
    )

    session_id: str = Field(
        ...,
        description="Conversation session ID.",
    )

    model_used: str = Field(
        ...,
        description="LLM used to generate the response.",
    )

    tools_used: List[str] = Field(
        default_factory=list,
        description="Tools used while generating the response.",
    )

    trace: List[TraceStep] = Field(
        default_factory=list,
        description="Agent execution trace steps.",
    )

    active_specialist: str = Field(
        ...,
        description="The primary specialist agent assigned to resolve the query: 'nexus', 'octolyzer', or 'synthex'.",
    )