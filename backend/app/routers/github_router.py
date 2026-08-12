from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.github import GithubAnalyzeRequest
from app.services.github_service import analyze_repository

router = APIRouter(
    prefix="/github",
    tags=["Github"]
)


@router.post("/analyze")
def analyze_github(
    request: GithubAnalyzeRequest,
    current_user=Depends(get_current_user),
):
    return analyze_repository(request, current_user.id)


@router.post("/index")
def index_github(
    request: GithubAnalyzeRequest,
    current_user=Depends(get_current_user),
):
    return analyze_repository(request, current_user.id)