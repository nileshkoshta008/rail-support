"""
FastAPI Server for Customer Support Environment
REST API wrapper for the RL environment
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json

from database import Database
from env_support_rag import CustomerSupportEnv, Action, Ticket, HelpArticle, Observation
from tasks_support_rag import get_task


app = FastAPI(title="Customer Support Triage API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()
current_env: Optional[CustomerSupportEnv] = None


class ActionRequest(BaseModel):
    action_type: str
    ticket_id: str
    search_query: Optional[str] = None
    reply_message: Optional[str] = None
    escalation_reason: Optional[str] = None
    department: Optional[str] = None
    priority: Optional[str] = None
    article_id: Optional[str] = None


class TaskStartRequest(BaseModel):
    task_level: str  # easy, medium, hard


@app.get("/")
def root():
    return {"message": "Customer Support Triage API", "endpoints": ["/start", "/state", "/step", "/reset", "/kb", "/stats"]}


@app.post("/start")
def start_task(req: TaskStartRequest):
    global current_env
    if req.task_level not in ["easy", "medium", "hard"]:
        raise HTTPException(status_code=400, detail="Invalid task level")
    
    tickets = [Ticket(**t) for t in get_task(req.task_level)]
    for t in tickets:
        db.insert_ticket(t.model_dump())
    
    kb_articles = [
        {"article_id": "KB-001", "title": "Password Reset", "content": "...", "tags": ["password"], "department": "Tech Support"},
        {"article_id": "KB-002", "title": "Billing FAQ", "content": "...", "tags": ["billing"], "department": "Billing"},
    ]
    for a in kb_articles:
        db.insert_kb_article(a)
    
    current_env = CustomerSupportEnv(tickets)
    return {"message": f"Task {req.task_level} started", "tickets": len(tickets)}


@app.get("/state")
def get_state() -> Dict[str, Any]:
    global current_env
    if current_env is None:
        raise HTTPException(status_code=400, detail="No active task")
    
    obs = current_env.state()
    return {
        "tickets": [t.model_dump() for t in obs.tickets],
        "completed_actions": obs.completed_actions,
        "total_reward": obs.total_reward,
        "search_results": [{"id": r.article_id, "title": r.title} for r in (obs.search_results or [])]
    }


@app.post("/step")
def take_step(action_req: ActionRequest) -> Dict[str, Any]:
    global current_env
    if current_env is None:
        raise HTTPException(status_code=400, detail="No active task")
    
    action = Action(**action_req.model_dump(exclude_none=False))
    obs, reward, done, info = current_env.step(action)
    
    db.insert_action(action_req.ticket_id, action_req.action_type, action_req.model_dump(), reward)
    
    if done:
        db.log_session("current", current_env.total_reward)
        db.update_ticket_status(action_req.ticket_id, "resolved")
    
    return {
        "reward": reward,
        "done": done,
        "info": info,
        "remaining_tickets": len(obs.tickets)
    }


@app.post("/reset")
def reset_task():
    global current_env
    if current_env is None:
        raise HTTPException(status_code=400, detail="No active task")
    obs = current_env.reset()
    return {"message": "Task reset", "tickets": len(obs.tickets)}


@app.get("/kb")
def get_knowledge_base() -> List[Dict[str, Any]]:
    articles = db.get_all_kb_articles()
    for a in articles:
        a["tags"] = json.loads(a["tags"])
    return articles


@app.get("/stats")
def get_stats() -> Dict[str, Any]:
    return db.get_session_stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
