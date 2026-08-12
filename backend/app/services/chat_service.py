import os
import json
import asyncio
from typing import AsyncGenerator
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.llm import llm
from app.core.config import settings
from app.agents.react_graph import react_agent
from app.schemas.chat import ChatRequest, ChatResponse, TraceStep
from app.services.memory_service import get_memory, save_memory
from app.schemas.memory import MemoryCreate
from app.services.document_service import list_user_documents


def is_nexus_fast_path(message: str) -> bool:
    """
    Returns True if the prompt is a simple greeting, conceptual theory query,
    or does not reference file modifications or github repositories.
    Bypasses supervisor/planner overhead for rapid responses.
    """
    msg_lower = message.lower()

    # If the message references github links or terms, it requires Octolyzer
    if "github.com/" in msg_lower or "repo" in msg_lower or "clone" in msg_lower:
        return False

    # If it references workspace code modifications, it requires Synthex
    if any(k in msg_lower for k in ["write", "fix", "modify", "edit", "refactor", "syntax", "ast"]):
        return False

    # Greetings
    greetings = ["hey", "hello", "hi", "yo", "sup", "greetings", "good morning", "good afternoon"]
    if any(msg_lower.strip() == g for g in greetings):
        return True

    # Conceptual/theory questions
    conceptual_keywords = ["explain", "how to", "what is", "difference between", "theory", "concept", "tutorial"]
    if any(k in msg_lower for k in conceptual_keywords):
        return True

    # Default: if it's very short, it's Nexus conversation
    if len(message.split()) < 5:
        return True

    return False


async def chat_stream_generator(
    request: ChatRequest,
    user_id: str,
) -> AsyncGenerator[str, None]:
    """
    Asynchronously executes/streams trace steps and LLM tokens.
    """
    # 1. Yield initial planning trace log
    yield f"data: {json.dumps({'type': 'trace', 'emoji': '🤔', 'label': 'Planning...', 'details': 'Supervisor is analyzing your request...'})}\n\n"
    await asyncio.sleep(0.05)

    # 2. Get recent chat history (limit 4 for token and processing speed optimization!)
    history_data = get_memory(user_id, limit=4)
    history_data = reversed(history_data) if history_data else []

    history_lines = []
    for msg in history_data:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_lines.append(f"{role}: {msg['content']}")
    formatted_history = "\n".join(history_lines)

    # 3. Check if the message can bypass supervisor (Fast-Path)
    if is_nexus_fast_path(request.message):
        yield f"data: {json.dumps({'type': 'trace', 'emoji': '✨', 'label': 'Nexus Routing', 'details': 'Nexus is resolving your query directly.'})}\n\n"
        await asyncio.sleep(0.05)

        sys_content = f"""You are Nexus, the General AI Assistant of ReActise.
Your job is to answer the user's question directly and concisely.

Conversation History:
{formatted_history}
"""
        full_response = ""
        # Stream tokens from LLM directly
        async for chunk in llm.astream([
            SystemMessage(content=sys_content),
            HumanMessage(content=request.message)
        ]):
            token = chunk.content
            full_response += token
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

        # Save history in background (fail-safe)
        try:
            save_memory(MemoryCreate(user_id=user_id, role="user", content=request.message))
            save_memory(MemoryCreate(user_id=user_id, role="assistant", content=full_response))
        except Exception:
            pass

        yield f"data: {json.dumps({'type': 'done', 'active_specialist': 'nexus', 'tools_used': []})}\n\n"
        return

    # 4. Slow Path (Full ReAct Graph with Task Decomposer)
    # Find active workspaces on disk
    user_workspaces_dir = os.path.join("workspaces", user_id)
    active_repos = []
    if os.path.exists(user_workspaces_dir):
        active_repos = [
            d for d in os.listdir(user_workspaces_dir)
            if os.path.isdir(os.path.join(user_workspaces_dir, d))
        ]

    uploaded_files = list_user_documents(user_id)
    uploaded_files_str = ", ".join(uploaded_files) if uploaded_files else "None"

    initial_state = {
        "user_id": user_id,
        "question": request.message,
        "chat_history": formatted_history,
        "active_repos": active_repos,
        "uploaded_files": uploaded_files_str,
        "retry_count": 0,
        "context": "",
        "tool_output": "",
        "draft_answer": "",
        "final_answer": "",
        "verifier_feedback": None,
    }

    # Execute LangGraph and retrieve final result
    result = await asyncio.to_thread(react_agent.invoke, initial_state)

    final_answer = result.get("final_answer", "")
    verifier_feedback = result.get("verifier_feedback")

    # Map steps and tools used
    active_specialist = "nexus"
    tools_used = []
    if result.get("plan"):
        plan = result["plan"]
        active_specialist = plan.active_specialist
        spec_label = "Nexus" if active_specialist == "nexus" else "Octolyzer" if active_specialist == "octolyzer" else "Synthex"
        emoji = "✨" if active_specialist == "nexus" else "🌿" if active_specialist == "octolyzer" else "💻"

        yield f"data: {json.dumps({'type': 'trace', 'emoji': emoji, 'label': f'Routing to {spec_label}', 'details': plan.thought})}\n\n"
        await asyncio.sleep(0.05)

        for step in plan.steps:
            if step.action == "final_answer":
                continue
            tools_used.append(step.action)

            tool_emoji = "🔍" if step.action == "list_files" else "📄" if step.action == "read_file" else "💾" if step.action == "write_file" else "🧪" if step.action == "check_syntax" else "🔎" if step.action == "rag" else "🌐" if step.action == "web_search" else "📦" if step.action == "github" else "⚙️"
            tool_label = f"Executing {step.action}"

            yield f"data: {json.dumps({'type': 'trace', 'emoji': tool_emoji, 'label': tool_label, 'details': step.reason})}\n\n"
            await asyncio.sleep(0.05)

    if tools_used:
        yield f"data: {json.dumps({'type': 'trace', 'emoji': '🧠', 'label': 'Synthesizing output', 'details': 'Assembling final response.'})}\n\n"
        await asyncio.sleep(0.05)

    # Verifier Audits Check
    if verifier_feedback and tools_used:
        status = "passed" if verifier_feedback.approved else "failed"
        emoji = "✅" if verifier_feedback.approved else "⚠️"
        score_str = f" [Score: {verifier_feedback.confidence_score}/100]" if hasattr(verifier_feedback, "confidence_score") else ""
        reasons_list = verifier_feedback.reasons if hasattr(verifier_feedback, "reasons") and verifier_feedback.reasons else [verifier_feedback.feedback]
        reasons_str = "; ".join(reasons_list)

        yield f"data: {json.dumps({'type': 'trace', 'emoji': emoji, 'label': f'Verification {status}{score_str}', 'details': reasons_str})}\n\n"
        await asyncio.sleep(0.05)

        score_val = verifier_feedback.confidence_score if hasattr(verifier_feedback, "confidence_score") else 0
        actions_list = verifier_feedback.actions_taken if hasattr(verifier_feedback, "actions_taken") and verifier_feedback.actions_taken else tools_used
        actions_md = ", ".join([f"`{a}`" for a in actions_list]) if actions_list else "`None`"
        reasons_bullets = "\n".join([f"- {r}" for r in reasons_list])

        audit_footer = f"""

---
### 🛡️ ReAct Verification Audit
- **Confidence Score**: `{score_val}/100`
- **Actions Evaluated**: {actions_md}
- **Verification Reasoning**:
{reasons_bullets}
"""
        final_answer = final_answer + audit_footer

    # Smooth character chunk streaming of the final answer (typing simulation)
    chunk_size = 12
    for i in range(0, len(final_answer), chunk_size):
        chunk = final_answer[i:i+chunk_size]
        yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
        await asyncio.sleep(0.005)

    # Save memory
    try:
        save_memory(MemoryCreate(user_id=user_id, role="user", content=request.message))
        save_memory(MemoryCreate(user_id=user_id, role="assistant", content=final_answer))
    except Exception:
        pass

    yield f"data: {json.dumps({'type': 'done', 'active_specialist': active_specialist, 'tools_used': tools_used})}\n\n"


def chat_with_agent(
    request: ChatRequest,
    user_id: str,
) -> ChatResponse:
    """
    Standard synchronous fallback request handler.
    """
    # 1. Retrieve previous conversation memory (limit 4 for token optimization)
    history_data = get_memory(user_id, limit=4)
    history_data = reversed(history_data) if history_data else []

    history_lines = []
    for msg in history_data:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_lines.append(f"{role}: {msg['content']}")
    formatted_history = "\n".join(history_lines)

    user_workspaces_dir = os.path.join("workspaces", user_id)
    active_repos = []
    if os.path.exists(user_workspaces_dir):
        active_repos = [
            d for d in os.listdir(user_workspaces_dir)
            if os.path.isdir(os.path.join(user_workspaces_dir, d))
        ]

    uploaded_files = list_user_documents(user_id)
    uploaded_files_str = ", ".join(uploaded_files) if uploaded_files else "None"

    result = react_agent.invoke(
        {
            "user_id": user_id,
            "question": request.message,
            "chat_history": formatted_history,
            "active_repos": active_repos,
            "uploaded_files": uploaded_files_str,
            "retry_count": 0,
            "context": "",
            "tool_output": "",
            "draft_answer": "",
            "final_answer": "",
            "verifier_feedback": None,
        }
    )

    final_answer = result["final_answer"]

    try:
        save_memory(MemoryCreate(user_id=user_id, role="user", content=request.message))
        save_memory(MemoryCreate(user_id=user_id, role="assistant", content=final_answer))
    except Exception:
        pass

    trace = [
        TraceStep(
            emoji="🤔",
            label="Planning...",
            details=result["plan"].thought if result.get("plan") else "Analyzing task request structure."
        )
    ]

    tools_used = []
    if result.get("plan") and result["plan"].steps:
        for step in result["plan"].steps:
            if step.action == "final_answer":
                continue
            tools_used.append(step.action)

            emoji = "🔍" if step.action == "list_files" else "📄" if step.action == "read_file" else "💾" if step.action == "write_file" else "🧪" if step.action == "check_syntax" else "🔎" if step.action == "rag" else "🌐" if step.action == "web_search" else "📦" if step.action == "github" else "⚙️"
            label = f"Executing {step.action}"
            trace.append(TraceStep(emoji=emoji, label=label, details=step.reason))

    if tools_used:
        trace.append(TraceStep(emoji="🧠", label="Analyzing results", details="Synthesizing tool data into response."))

    vf = result.get("verifier_feedback")
    if vf and tools_used:
        status = "passed" if vf.approved else "failed"
        emoji = "✅" if vf.approved else "⚠️"
        score_str = f" [Score: {vf.confidence_score}/100]" if hasattr(vf, "confidence_score") else ""
        reasons_list = vf.reasons if hasattr(vf, "reasons") and vf.reasons else [vf.feedback]
        reasons_str = "; ".join(reasons_list)
        trace.append(TraceStep(emoji=emoji, label=f"Verification {status}{score_str}", details=reasons_str))

        score_val = vf.confidence_score if hasattr(vf, "confidence_score") else 0
        actions_list = vf.actions_taken if hasattr(vf, "actions_taken") and vf.actions_taken else tools_used
        actions_md = ", ".join([f"`{a}`" for a in actions_list]) if actions_list else "`None`"
        reasons_bullets = "\n".join([f"- {r}" for r in reasons_list])

        audit_footer = f"""

---
### 🛡️ ReAct Verification Audit
- **Confidence Score**: `{score_val}/100`
- **Actions Evaluated**: {actions_md}
- **Verification Reasoning**:
{reasons_bullets}
"""
        final_answer = final_answer + audit_footer

    trace.append(TraceStep(emoji="💬", label="Final response", details="Rendering final answer response."))

    spec = "nexus"
    if result.get("plan") and hasattr(result["plan"], "active_specialist") and result["plan"].active_specialist:
        spec = result["plan"].active_specialist

    return ChatResponse(
        answer=final_answer,
        session_id=request.session_id,
        model_used=settings.GROQ_MODEL,
        tools_used=tools_used,
        trace=trace,
        active_specialist=spec
    )