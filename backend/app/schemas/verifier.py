from pydantic import BaseModel, Field


class VerifierResponse(BaseModel):
    """
    Structured output produced by the Verifier.
    """

    approved: bool = Field(
        ...,
        description="True if the draft answer is accurate and complete, False otherwise.",
    )

    confidence_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Evaluation confidence rating of the answer quality from 0 to 100.",
    )

    reasons: list[str] = Field(
        default_factory=list,
        description="Specific reasoning points supporting the approval status and confidence score.",
    )

    actions_taken: list[str] = Field(
        default_factory=list,
        description="List of tool actions evaluated or verified during the check.",
    )

    feedback: str = Field(
        default="",
        description="Constructive feedback or corrections if not approved.",
    )