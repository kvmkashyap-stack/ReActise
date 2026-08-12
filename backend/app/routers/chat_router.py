from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.security import get_current_user
from app.schemas.chat import ChatRequest
from app.services.chat_service import (
    chat_with_agent,
    chat_stream_generator,
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/")
def chat(
    request: ChatRequest,
    current_user=Depends(get_current_user),
):
    return chat_with_agent(request, current_user.id)


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user=Depends(get_current_user),
):
    """
    Server-Sent Events (SSE) streaming endpoint.
    """
    generator = chat_stream_generator(request, current_user.id)
    return StreamingResponse(generator, media_type="text/event-stream")