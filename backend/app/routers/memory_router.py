from fastapi import APIRouter, Depends
from app.core.security import get_current_user

from app.schemas.memory import (
    MemoryCreate,
)

from app.services.memory_service import (
    save_memory,
    get_memory,
    clear_memory,
)


router = APIRouter(
    prefix="/memory",
    tags=["Memory"]
)



@router.post("/save")
def create_memory(
    request: MemoryCreate,
    current_user=Depends(get_current_user),
):
    request.user_id = current_user.id
    return save_memory(request)


@router.get("/")
def retrieve_memory(
    current_user=Depends(get_current_user),
):
    return get_memory(current_user.id)


@router.delete("/")
def delete_memory(
    current_user=Depends(get_current_user),
):
    return clear_memory(current_user.id)