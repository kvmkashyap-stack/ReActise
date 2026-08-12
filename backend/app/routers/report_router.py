from fastapi import APIRouter
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

from app.schemas.report import (
    ReportRequest,
)

from app.services.report_service import (
    create_report,
)


router = APIRouter(
    prefix="/report",
    tags=["Reports"]
)



@router.post("/create")
def generate_report(
    request: ReportRequest,
    current_user=Depends(get_current_user),
):
    return create_report(request)