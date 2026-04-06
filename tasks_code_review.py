"""
Tasks and Graders for Code Review Environment
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
    """Task 1 (Easy): Single clear feature PR"""
    return [
        {
            "pr_id": "PR-001",
            "title": "Add user authentication module",
            "description": "Implements JWT-based authentication with refresh tokens. "
                           "Includes login, logout, and token refresh endpoints.",
            "files_changed": ["auth.py", "models.py", "routes.py"],
            "pr_type": "feature",
            "priority": "Medium",
            "risk_level": "medium",
            "is_spam": False,
            "is_review_bomb": False
        }
    ]


def create_task_2_medium() -> List[dict]:
    """Task 2 (Medium): 3 mixed PRs"""
    return [
        {
            "pr_id": "PR-002",
            "title": "Fix memory leak in image processor",
            "description": "Found and fixed a memory leak in the image processing pipeline. "
                           "The buffer was not being released after processing.",
            "files_changed": ["image_processor.py"],
            "pr_type": "bugfix",
            "priority": "High",
            "risk_level": "high",
            "is_spam": False,
            "is_review_bomb": False
        },
        {
            "pr_id": "PR-003",
            "title": "Update API documentation",
            "description": "Updated REST API docs to reflect v2 endpoints. Added examples "
                           "for new authentication flow.",
            "files_changed": ["docs/api.md", "docs/examples.md"],
            "pr_type": "docs",
            "priority": "Low",
            "risk_level": "low",
            "is_spam": False,
            "is_review_bomb": False
        },
        {
            "pr_id": "PR-004",
            "title": "Refactor database connection pool",
            "description": "Extracted database connection management into separate module. "
                           "Improved connection reuse and error handling.",
            "files_changed": ["db_pool.py", "db_connection.py", "__init__.py"],
            "pr_type": "refactor",
            "priority": "Medium",
            "risk_level": "medium",
            "is_spam": False,
            "is_review_bomb": False
        }
    ]


def create_task_3_hard() -> List[dict]:
    """Task 3 (Hard): 5 PRs including spam/review bomb"""
    return [
        {
            "pr_id": "PR-005",
            "title": "CRITICAL: Security patch for auth bypass",
            "description": "Urgent fix for CVE-2024-XXXX. Bypasses proper authentication "
                           "when certain headers are present. Hotfix required immediately.",
            "files_changed": ["auth.py", "middleware.py"],
            "pr_type": "hotfix",
            "priority": "Critical",
            "risk_level": "high",
            "is_spam": False,
            "is_review_bomb": False
        },
        {
            "pr_id": "PR-006",
            "title": "Fix typo in comment",
            "description": "Fixed typo in comment from 'functoin' to 'function'",
            "files_changed": ["utils.py"],
            "pr_type": "docs",
            "priority": "Low",
            "risk_level": "low",
            "is_spam": False,
            "is_review_bomb": False
        },
        {
            "pr_id": "PR-007",
            "title": "Add dark mode support",
            "description": "Implements dark mode toggle in settings. Persists preference "
                           "in local storage. Theme switcher component added.",
            "files_changed": ["theme.py", "settings.js", "styles.css"],
            "pr_type": "feature",
            "priority": "Medium",
            "risk_level": "low",
            "is_spam": False,
            "is_review_bomb": False
        },
        {
            "pr_id": "PR-008",
            "title": "MAKE MONEY FAST!!! BEST PR!! $$$",
            "description": "CLICK HERE FOR FREE BITCOIN!!! This PR will make you rich!!! "
                           "100x returns guaranteed!!! BUY NOW!!!",
            "files_changed": ["SCAM.py", "FRAUD.js"],
            "pr_type": "feature",
            "priority": "High",
            "risk_level": "low",
            "is_spam": True,
            "is_review_bomb": False
        },
        {
            "pr_id": "PR-009",
            "title": "Fix null pointer in payment processor",
            "description": "Added null check for payment intent before processing. "
                           "Prevents crash when payment intent is None.",
            "files_changed": ["payment.py"],
            "pr_type": "bugfix",
            "priority": "High",
            "risk_level": "medium",
            "is_spam": False,
            "is_review_bomb": False
        }
    ]


def calculate_max_reward(task_prs: List[dict]) -> float:
    max_reward = 0.0
    for pr in task_prs:
        if pr["is_spam"] or pr["is_review_bomb"]:
            max_reward += 0.7
        else:
            max_reward += 0.8
    return max_reward


def grade_task(task_name: str, prs: List[dict], achieved_reward: float) -> TaskResult:
    max_reward = calculate_max_reward(prs)
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
