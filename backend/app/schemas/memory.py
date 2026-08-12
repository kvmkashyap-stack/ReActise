from pydantic import BaseModel


class MemoryCreate(BaseModel):

    user_id: str

    role: str

    content: str