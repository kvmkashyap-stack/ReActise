from fastapi import HTTPException

from app.schemas.github import (
    GithubAnalyzeRequest,
    GithubAnalyzeResponse,
)
from app.tools.github_loader import load_repository
from app.core.vector_store import vector_store


from app.core.config import settings
import os
from urllib.parse import urlparse

def analyze_repository(
    request: GithubAnalyzeRequest,
    user_id: str,
) -> GithubAnalyzeResponse:
    """
    Analyze GitHub repository and prepare data
    for AI processing.
    """

    try:
        repo_url = str(request.repo_url)

        # Parse repository name from GitHub URL
        parsed_url = urlparse(repo_url)
        path_parts = parsed_url.path.strip("/").split("/")
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub repository URL")
        repo_name = path_parts[-1].replace(".git", "")

        # Target local workspace directory
        workspace_dir = os.path.join(settings.WORKSPACES_FOLDER, user_id, repo_name)

        # Clone and load code files as LangChain Documents
        result = load_repository(repo_url, clone_to_dir=workspace_dir)

        # Attach repo name metadata to documents
        for doc in result:
            doc.metadata["repo_name"] = repo_name

        # Index in vector store under the user's ID
        vector_store.add_documents(result, user_id=user_id)

        return GithubAnalyzeResponse(
            repository=repo_url,
            status="success",
            message=f"Repository '{repo_name}' processed and indexed successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Repository processing failed: {str(e)}"
        )