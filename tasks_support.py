"""
Tasks and Graders for Customer Support Ticket Triage Environment
"""

from typing import List
from pydantic import BaseModel


class TaskResult(BaseModel):
    task_name: str
    max_possible_reward: float
    achieved_reward: float
    score: float
    passed: bool


def create_task_1_easy() -> List[dict]:
    return [
        {
            "ticket_id": "TKT-001",
            "content": "My application keeps crashing every time I try to export a PDF document. "
                       "I've tried restarting the software but the issue persists. "
                       "Error message shows: 'RuntimeError: Memory allocation failed'",
            "department": "Tech Support",
            "priority": "High",
            "is_spam": False
        }
    ]


def create_task_2_medium() -> List[dict]:
    return [
        {
            "ticket_id": "TKT-002",
            "content": "I was charged twice for my monthly subscription on March 1st. "
                       "Please refund the duplicate charge of $29.99 to my original payment method.",
            "department": "Billing",
            "priority": "High",
            "is_spam": False
        },
        {
            "ticket_id": "TKT-003",
            "content": "I'm interested in upgrading to the Enterprise plan. Can you provide "
                       "information about volume discounts for 500+ users? Also need to know "
                       "about SSO integration capabilities.",
            "department": "Sales",
            "priority": "Medium",
            "is_spam": False
        },
        {
            "ticket_id": "TKT-004",
            "content": "Cannot connect to the API endpoint at api.example.com/v2/users. "
                       "Getting 403 Forbidden error. Credentials are correct and API key is valid.",
            "department": "Tech Support",
            "priority": "High",
            "is_spam": False
        }
    ]


def create_task_3_hard() -> List[dict]:
    return [
        {
            "ticket_id": "TKT-005",
            "content": "The new update 3.2.1 broke our automated integration. All our cron jobs "
                       "that use the /schedule endpoint are failing with 500 errors since yesterday.",
            "department": "Tech Support",
            "priority": "High",
            "is_spam": False
        },
        {
            "ticket_id": "TKT-006",
            "content": "URGENT: My invoice shows $0.00 but I need to pay $1500 today for the annual plan. "
                       "How do I make a payment? The online portal shows balance due as $0.",
            "department": "Billing",
            "priority": "Medium",
            "is_spam": False
        },
        {
            "ticket_id": "TKT-007",
            "content": "We are a healthcare company looking for HIPAA-compliant solutions. "
                       "Need quotes for at least 1000 seats with dedicated support. What's your "
                       "healthcare pricing tier?",
            "department": "Sales",
            "priority": "Medium",
            "is_spam": False
        },
        {
            "ticket_id": "TKT-008",
            "content": "Hey buddy! Make $5000/week from home! Click here now!!! "
                       "FREE iPhone 14 for everyone! Act NOW! This is absolutely LEGIT!",
            "department": "Tech Support",
            "priority": "Low",
            "is_spam": True
        },
        {
            "ticket_id": "TKT-009",
            "content": "After the recent security update, I'm getting SSL certificate errors when "
                       "trying to access the admin panel. Browser: Chrome 120. OS: Windows 11.",
            "department": "Tech Support",
            "priority": "High",
            "is_spam": False
        }
    ]


def calculate_max_reward(task_tickets: List[dict]) -> float:
    max_reward = 0.0
    for ticket in task_tickets:
        if ticket["is_spam"]:
            max_reward += 0.7
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
