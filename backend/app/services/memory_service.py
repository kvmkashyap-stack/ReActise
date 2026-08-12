from fastapi import HTTPException

from app.core.supabase import supabase

from app.schemas.memory import MemoryCreate



def save_memory(
    memory: MemoryCreate,
):
    """
    Store conversation message.
    Silently fails if the table does not exist.
    """

    try:

        response = (
            supabase
            .table("conversation_memory")
            .insert(
                {
                    "user_id": memory.user_id,
                    "role": memory.role,
                    "content": memory.content,
                }
            )
            .execute()
        )


        return response.data


    except Exception as e:
        # Log but don't crash – table may not exist yet
        print(f"[memory] save_memory warning: {e}")
        return []



def get_memory(
    user_id: str,
    limit: int = 10,
):
    """
    Retrieve previous conversations.
    Returns empty list if the table does not exist.
    """

    try:

        response = (
            supabase
            .table("conversation_memory")
            .select("*")
            .eq(
                "user_id",
                user_id
            )
            .order(
                "created_at",
                desc=True
            )
            .limit(limit)
            .execute()
        )


        return response.data


    except Exception as e:
        # Log but don't crash – table may not exist yet
        print(f"[memory] get_memory warning: {e}")
        return []



def clear_memory(
    user_id: str,
):
    """
    Delete user conversation history.
    Returns success even if table does not exist.
    """

    try:

        response = (
            supabase
            .table("conversation_memory")
            .delete()
            .eq(
                "user_id",
                user_id
            )
            .execute()
        )


        return {
            "message":
            "Memory cleared successfully"
        }


    except Exception as e:
        print(f"[memory] clear_memory warning: {e}")
        return {
            "message":
            "Memory cleared (table may not exist)"
        }