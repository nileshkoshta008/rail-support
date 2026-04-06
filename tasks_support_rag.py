"""
Tasks for RAG-Enhanced Customer Support Environment
With multi-turn conversations, attachments, and PII
"""

from typing import List, Dict, Any
from pydantic import BaseModel


class TaskResult(BaseModel):
    task_name: str
    max_possible_reward: float
    achieved_reward: float
    score: float
    passed: bool


def create_task_1_easy() -> List[Dict[str, Any]]:
    """Task 1: Simple ticket with clear KB match"""
    return [
        {
            "ticket_id": "TKT-001",
            "subject": "Cannot export PDF",
            "messages": [
                {"sender": "customer", "content": "When I try to export my document as PDF, the application crashes. I need this fixed ASAP!", "timestamp": "2024-01-15T10:00:00Z"}
            ],
            "attachments": [{"filename": "error.png", "type": "screenshot", "description": "Error message showing crash"}],
            "department": "Tech Support",
            "priority": "High",
            "status": "open",
            "is_spam": False
        }
    ]


def create_task_2_medium() -> List[Dict[str, Any]]:
    """Task 2: 3 tickets requiring KB lookup"""
    return [
        {
            "ticket_id": "TKT-002",
            "subject": "Billed twice",
            "messages": [
                {"sender": "customer", "content": "I see two charges of $29.99 on my statement from Jan 1st. Please refund one!", "timestamp": "2024-01-15T11:00:00Z"}
            ],
            "attachments": [],
            "department": "Billing",
            "priority": "High",
            "status": "open",
            "is_spam": False
        },
        {
            "ticket_id": "TKT-003",
            "subject": "API returning 403",
            "messages": [
                {"sender": "customer", "content": "Getting 403 Forbidden when calling the API endpoint. My key should be valid.", "timestamp": "2024-01-15T12:00:00Z"}
            ],
            "attachments": [{"filename": "api_error.log", "type": "log", "description": "API response log"}],
            "department": "Tech Support",
            "priority": "High",
            "status": "open",
            "is_spam": False
        },
        {
            "ticket_id": "TKT-004",
            "subject": "Enterprise pricing",
            "messages": [
                {"sender": "customer", "content": "Interested in upgrading to Enterprise for 500+ users. What discounts do you offer?", "timestamp": "2024-01-15T13:00:00Z"}
            ],
            "attachments": [],
            "department": "Sales",
            "priority": "Medium",
            "status": "open",
            "is_spam": False
        }
    ]


def create_task_3_hard() -> List[Dict[str, Any]]:
    """Task 3: 5 tickets including multi-turn, PII, spam"""
    return [
        {
            "ticket_id": "TKT-005",
            "subject": "Password reset not working",
            "messages": [
                {"sender": "customer", "content": "I clicked reset password link but nothing happens.", "timestamp": "2024-01-15T14:00:00Z"},
                {"sender": "agent", "content": "Can you confirm which email address you used?", "timestamp": "2024-01-15T14:30:00Z"},
                {"sender": "customer", "content": "I used john.doe@company.com but never got any email. Help!", "timestamp": "2024-01-15T15:00:00Z"}
            ],
            "attachments": [],
            "department": "Tech Support",
            "priority": "High",
            "status": "open",
            "is_spam": False
        },
        {
            "ticket_id": "TKT-006",
            "subject": "SSN exposed in chat",
            "messages": [
                {"sender": "customer", "content": "My account shows my SSN: 123-45-6789. Please fix this!", "timestamp": "2024-01-15T16:00:00Z"}
            ],
            "attachments": [],
            "department": "Tech Support",
            "priority": "High",
            "status": "open",
            "is_spam": False,
            "pii_detected": True  # Ticket contains PII that should be redacted
        },
        {
            "ticket_id": "TKT-007",
            "subject": "Enterprise upgrade",
            "messages": [
                {"sender": "customer", "content": "Need quotes for 1000+ seats in healthcare. HIPAA compliant?", "timestamp": "2024-01-15T17:00:00Z"}
            ],
            "attachments": [],
            "department": "Sales",
            "priority": "Medium",
            "status": "open",
            "is_spam": False
        },
        {
            "ticket_id": "TKT-008",
            "subject": "FREE MONEY!!!",
            "messages": [
                {"sender": "customer", "content": "MAKE $10000/WEEK FROM HOME!!! CLICK HERE NOWWWW!!!! FREE BITCOIN!!!", "timestamp": "2024-01-15T18:00:00Z"}
            ],
            "attachments": [],
            "department": "Tech Support",
            "priority": "Low",
            "status": "open",
            "is_spam": True
        },
        {
            "ticket_id": "TKT-009",
            "subject": "Refund request",
            "messages": [
                {"sender": "customer", "content": "Accidentally charged for annual plan. Need to cancel and get refund. Card ending 4242.", "timestamp": "2024-01-15T19:00:00Z"}
            ],
            "attachments": [{"filename": "invoice.pdf", "type": "pdf", "description": "Invoice showing charge"}],
            "department": "Billing",
            "priority": "High",
            "status": "open",
            "is_spam": False,
            "pii_detected": True  # Contains credit card number
        }
    ]


def calculate_max_reward(task_tickets: List[dict]) -> float:
    max_reward = 0.0
    for ticket in task_tickets:
        if ticket.get("is_spam"):
            max_reward += 0.5
        elif ticket.get("pii_detected"):
            max_reward += 0.8  # PII requires special handling
        else:
            max_reward += 1.0
    return max_reward


def grade_task(task_name: str, tickets: List[dict], achieved_reward: float) -> TaskResult:
    max_reward = calculate_max_reward(tickets)
    score = achieved_reward / max_reward if max_reward > 0 else 0.0
    passed = score >= 0.8
    
    return TaskResult(
        task_name=task_name,
        max_possible_reward=round(max_reward, 2),
        achieved_reward=round(achieved_reward, 2),
        score=round(score, 2),
        passed=passed
    )


TASKS = {"easy": create_task_1_easy, "medium": create_task_2_medium, "hard": create_task_3_hard}


def get_task(task_level: str) -> List[dict]:
    return TASKS[task_level]()
