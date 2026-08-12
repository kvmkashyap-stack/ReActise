from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    auth_router,
    chat_router,
    github_router,
    document_router,
    memory_router,
    report_router,
)

app = FastAPI(
    title="ReAct Agent",
    description="Industry level ReAct AI Agent API",
    version="1.0.0"
)

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(chat_router.router)
app.include_router(github_router.router)
app.include_router(document_router.router)
app.include_router(memory_router.router)
app.include_router(report_router.router)

@app.get("/")
def root():
    return {
        "message":
        "ReAct Agent Backend Running"
    }



@app.get("/health")
def health_check():

    return {
        "status":
        "healthy"
    }