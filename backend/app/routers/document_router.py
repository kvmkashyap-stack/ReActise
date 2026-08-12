from fastapi import APIRouter, UploadFile, File, Depends
from app.core.security import get_current_user

from app.services.document_service import (
    upload_document,
    list_user_documents,
    delete_user_document,
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    return await upload_document(file, current_user.id)


@router.get("/")
def get_documents(
    current_user=Depends(get_current_user),
):
    return list_user_documents(current_user.id)


@router.delete("/{filename}")
def delete_document(
    filename: str,
    current_user=Depends(get_current_user),
):
    return delete_user_document(current_user.id, filename)