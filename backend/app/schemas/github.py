from pydantic import BaseModel, Field
from typing import Optional


class GithubIndexRequest(BaseModel):
    """
    Schema for GitHub repository indexing requests.
    """
    repo_url: str = Field(
        ...,
        description="The GitHub repository URL to clone and index.",
    )
    branch: Optional[str] = Field(
        default="main",
        description="The branch of the repository.",
    )


class GithubIndexResponse(BaseModel):
    """
    Schema for GitHub repository indexing responses.
    """
    repository: str = Field(
        ...,
        description="The repository URL.",
    )
    status: str = Field(
        ...,
        description="Status of the operation.",
    )
    message: str = Field(
        ...,
        description="User-friendly status message.",
    )


# Keep the aliases for compatibility with routers and services
GitHubRequest = GithubIndexRequest
GithubAnalyzeRequest = GithubIndexRequest
GitHubResponse = GithubIndexResponse
GithubAnalyzeResponse = GithubIndexResponse