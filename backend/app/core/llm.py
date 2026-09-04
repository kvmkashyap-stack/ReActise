from langchain_groq import ChatGroq
from app.core.config import settings
import random

# Support comma-separated list of keys to round-robin on serverless boot
_keys = [k.strip() for k in settings.GROQ_API_KEY.split(",")] if settings.GROQ_API_KEY else [""]
_active_key = random.choice(_keys) if _keys else ""

llm = ChatGroq(
    api_key=_active_key,
    model=settings.GROQ_MODEL,
    temperature=0
)

