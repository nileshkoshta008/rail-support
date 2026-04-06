"""
Code Review Environment
OpenEnv-compliant reinforcement learning environment for PR triage
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


PRType = Literal["feature", "bugfix", "docs", "refactor", "hotfix"]
Priority = Literal["Low", "Medium", "High", "Critical"]
RiskLevel = Literal["low", "medium", "high"]


class PullRequest(BaseModel):
    """Represents a pull request to review"""
    pr_id: str
    title: str
    description: str
    files_changed: List[str]
    pr_type: PRType
    priority: Priority
    risk_level: RiskLevel
    is_spam: bool = False
    is_review_bomb: bool = False


class Action(BaseModel):
    """Action space for the environment"""
    action_type: Literal["classify_pr", "request_changes", "approve", "spam"] = Field(
        description="The type of action to take"
    )
    pr_id: str = Field(description="The ID of the PR to act on")
    pr_type: Optional[PRType] = Field(default=None, description="PR type classification")
    priority: Optional[Priority] = Field(default=None, description="Priority level")
    risk_level: Optional[RiskLevel] = Field(default=None, description="Risk assessment")


class Observation(BaseModel):
    """Observation space for the environment"""
    pull_requests: List[PullRequest] = Field(description="Active PRs awaiting review")
    completed_actions: List[str] = Field(description="Completed review actions")
    total_reward: float = Field(description="Cumulative reward received")


class CodeReviewEnv:
    """
    OpenEnv-compliant Code Review Triage environment.
    Agent acts as a first-pass reviewer classifying PRs.
    """
    
    def __init__(self, pull_requests: List[PullRequest]):
        self.original_prs = pull_requests
        self.prs = [p.model_copy() for p in pull_requests]
        self.completed_actions: List[str] = []
        self.total_reward = 0.0
    
    def state(self) -> Observation:
        return Observation(
            pull_requests=self.prs,
            completed_actions=self.completed_actions,
            total_reward=round(self.total_reward, 2)
        )
    
    def reset(self) -> Observation:
        self.prs = [p.model_copy() for p in self.original_prs]
        self.completed_actions = []
        self.total_reward = 0.0
        return self.state()
    
    def step(self, action: Action) -> tuple[Observation, float, bool, dict]:
        reward = 0.0
        done = False
        info = {}
        
        pr = next((p for p in self.prs if p.pr_id == action.pr_id), None)
        
        if pr is None:
            reward = -0.5
            info["error"] = f"PR ID '{action.pr_id}' does not exist"
            self.total_reward += reward
            return self.state(), reward, done, info
        
        reward += 0.2  # Valid PR ID
        
        if action.action_type == "spam":
            if pr.is_spam or pr.is_review_bomb:
                reward += 0.5
                action_desc = f"Marked {action.pr_id} as spam/review-bomb"
            else:
                reward = -1.0
                action_desc = f"ERROR: Incorrectly marked {action.pr_id} as spam"
                info["error"] = "Valid PR marked as spam"
            self.completed_actions.append(action_desc)
            self.prs = [p for p in self.prs if p.pr_id != action.pr_id]
        
        elif action.action_type in ("classify_pr", "request_changes", "approve"):
            if pr.is_spam or pr.is_review_bomb:
                reward = -1.0
                action_desc = f"ERROR: Routed spam/review-bomb PR {action.pr_id} to humans"
                info["error"] = "Spam/review-bomb routed to human reviewers"
            else:
                if action.pr_type == pr.pr_type:
                    reward += 0.25
                if action.priority == pr.priority:
                    reward += 0.25
                if action.risk_level == pr.risk_level:
                    reward += 0.3
                
                action_type_str = {
                    "classify_pr": "classified",
                    "request_changes": "requested changes for",
                    "approve": "approved"
                }
                action_desc = f"{action_type_str[action.action_type]} {action.pr_id} as {action.pr_type}/{action.priority}/{action.risk_level}"
            
            self.completed_actions.append(action_desc)
            self.prs = [p for p in self.prs if p.pr_id != action.pr_id]
        
        self.total_reward = round(self.total_reward + reward, 2)
        done = len(self.prs) == 0
        
        return self.state(), reward, done, info
