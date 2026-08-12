import os
import shutil
from fastapi import UploadFile, HTTPException

from app.schemas.documents import DocumentUploadResponse
from app.tools.pdf_loader import process_pdf
from app.core.config import settings
from app.core.vector_store import vector_store


async def upload_document(
    file: UploadFile,
    user_id: str,
) -> DocumentUploadResponse:
    try:
        # Isolate uploaded files under user-specific subdirectories
        user_upload_dir = os.path.join(settings.UPLOAD_FOLDER, user_id)
        os.makedirs(user_upload_dir, exist_ok=True)
        file_path = os.path.join(user_upload_dir, file.filename)

        # Write uploaded file to disk
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Process PDF and split into chunks
        documents = process_pdf(file_path)

        # Index in vector store under the user's ID (falls back to FAISS)
        vector_store.add_documents(documents, user_id=user_id)

        return DocumentUploadResponse(
            filename=file.filename,
            status="success",
            message="Document processed and indexed successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


def list_user_documents(
    user_id: str,
) -> list[str]:
    """
    List all active uploaded document filenames for a user.
    """
    user_upload_dir = os.path.join(settings.UPLOAD_FOLDER, user_id)
    if not os.path.exists(user_upload_dir):
        return []
    return [
        f for f in os.listdir(user_upload_dir)
        if os.path.isfile(os.path.join(user_upload_dir, f))
    ]


def delete_user_document(
    user_id: str,
    filename: str,
) -> dict:
    """
    Delete a specific uploaded document file.
    """
    user_upload_dir = os.path.join(settings.UPLOAD_FOLDER, user_id)
    file_path = os.path.join(user_upload_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"status": "success", "message": f"Document '{filename}' deleted successfully"}
    raise HTTPException(status_code=404, detail="File not found")