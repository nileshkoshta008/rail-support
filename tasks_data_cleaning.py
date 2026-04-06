"""
Tasks and Graders for Data Cleaning Environment
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
    """Task 1 (Easy): Single clear dirty record"""
    return [
        {
            "record_id": "REC-001",
            "values": {"name": "John Doe", "email": "john@example.com", "age": "N/A"},
            "issues": ["missing"],
            "correct_issue_type": "missing",
            "correct_correction": "impute",
            "is_actually_valid": False
        }
    ]


def create_task_2_medium() -> List[dict]:
    """Task 2 (Medium): 3 mixed records"""
    return [
        {
            "record_id": "REC-002",
            "values": {"id": 1, "name": "Alice Smith", "email": "alice@email.com"},
            "issues": [],
            "correct_issue_type": "valid",
            "correct_correction": "ignore",
            "is_actually_valid": True
        },
        {
            "record_id": "REC-003",
            "values": {"id": 2, "name": "Bob Jones", "email": "bob@email.com", "age": 25},
            "issues": ["duplicate"],
            "correct_issue_type": "duplicate",
            "correct_correction": "drop",
            "is_actually_valid": False
        },
        {
            "record_id": "REC-004",
            "values": {"id": 3, "name": "Carol White", "email": "carol@email.com", "age": 999},
            "issues": ["outlier"],
            "correct_issue_type": "outlier",
            "correct_correction": "flag",
            "is_actually_valid": False
        }
    ]


def create_task_3_hard() -> List[dict]:
    """Task 3 (Hard): 5 records including valid ones"""
    return [
        {
            "record_id": "REC-005",
            "values": {"id": 5, "name": "Eve Black", "email": None, "phone": None},
            "issues": ["missing"],
            "correct_issue_type": "missing",
            "correct_correction": "impute",
            "is_actually_valid": False
        },
        {
            "record_id": "REC-006",
            "values": {"id": 6, "name": "Frank Green", "email": "frank@email.com"},
            "issues": [],
            "correct_issue_type": "valid",
            "correct_correction": "ignore",
            "is_actually_valid": True
        },
        {
            "record_id": "REC-007",
            "values": {"id": 7, "name": "Grace Lee", "email": "grace@email.com", "status": "active"},
            "issues": ["inconsistent"],
            "correct_issue_type": "inconsistent",
            "correct_correction": "flag",
            "is_actually_valid": False
        },
        {
            "record_id": "REC-008",
            "values": {"id": 8, "name": "Henry Brown", "email": "henry@email.com", "age": "-5"},
            "issues": ["format"],
            "correct_issue_type": "format",
            "correct_correction": "flag",
            "is_actually_valid": False
        },
        {
            "record_id": "REC-009",
            "values": {"id": 9, "name": "Ivy Wilson", "email": "ivy@email.com"},
            "issues": [],
            "correct_issue_type": "valid",
            "correct_correction": "ignore",
            "is_actually_valid": True
        }
    ]


def calculate_max_reward(task_records: List[dict]) -> float:
    max_reward = 0.0
    for record in task_records:
        if record["is_actually_valid"]:
            max_reward += 0.6
        else:
            max_reward += 0.8
    return max_reward


def grade_task(task_name: str, records: List[dict], achieved_reward: float) -> TaskResult:
    max_reward = calculate_max_reward(records)
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
