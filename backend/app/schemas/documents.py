from datetime import datetime
from pydantic import BaseModel, Field

class DocumentUploadResponse(BaseModel):
    document_id: str = Field(
        ...,
        description="Unique document identifier.",
    )

    filename: str = Field(
        ...,
        description="Uploaded file name.",
    )

    message: str = Field(
        ...,
        description="Upload status.",
    )


class DocumentMetadata(BaseModel):
    document_id: str = Field(
        ...,
        description="Document ID.",
    )

    filename: str = Field(
        ...,
        description="Stored file name.",
    )

    content_type: str = Field(
        ...,
        description="MIME type.",
    )

    uploaded_at: datetime = Field(
        ...,
        description="Upload timestamp.",
    )


class DocumentDeleteResponse(BaseModel):
    message: str = Field(
        ...,
        description="Delete confirmation.",
    )