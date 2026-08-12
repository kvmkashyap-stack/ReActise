from typing import Literal
from pydantic import BaseModel, Field, HttpUrl

class ReportRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        description="Report title.",
    )

    content: str = Field(
        ...,
        min_length=1,
        description="Content for the report.",
    )

    format: Literal[
        "pdf",
        "docx",
        "markdown",
    ] = Field(
        default="pdf",
        description="Output report format.",
    )


class ReportResponse(BaseModel):
    report_name: str = Field(
        ...,
        description="Generated report name.",
    )

    download_url: HttpUrl = Field(
        ...,
        description="Download link for the report.",
    )

    format: Literal["pdf", "docx", "markdown"] = Field(
        ...,
        description="Generated report format.",
    )

    message: str = Field(
        ...,
        description="Generation status.",
    )