from langchain_groq import ChatGroq
from app.core.config import settings
import random

# Support multiple API keys or environment variables
_raw_keys = [k.strip() for k in settings.GROQ_API_KEY.replace("\n", ",").split(",") if k.strip()]
_keys = _raw_keys if _raw_keys else [""]
_active_key = random.choice(_keys)

# Ensure an active supported Groq model is used
_model = settings.GROQ_MODEL
if "llama-3.3-70b-versatile" in _model or "llama-3.1" in _model or "llama3" in _model:
    _model = "qwen/qwen3.8-27b"

llm = ChatGroq(
    api_key=_active_key,
    model=_model,
    temperature=0
)


