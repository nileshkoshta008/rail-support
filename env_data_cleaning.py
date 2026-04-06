"""
Data Cleaning Environment
OpenEnv-compliant reinforcement learning environment for data quality triage
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


IssueType = Literal["missing", "duplicate", "format", "outlier", "inconsistent", "valid"]
Correction = Literal["drop", "impute", "flag", "ignore"]


class DataRecord(BaseModel):
    """Represents a data record to clean"""
    record_id: str
    values: Dict[str, Any]
    issues: List[IssueType]
    correct_issue_type: IssueType
    correct_correction: Correction
    is_actually_valid: bool = False


class Action(BaseModel):
    """Action space for the environment"""
    action_type: Literal["classify_issue", "apply_correction"] = Field(
        description="Type of action"
    )
    record_id: str = Field(description="Record ID to act on")
    issue_type: Optional[IssueType] = Field(default=None, description="Classified issue type")
    correction: Optional[Correction] = Field(default=None, description="Correction to apply")


class Observation(BaseModel):
    """Observation space for the environment"""
    records: List[DataRecord] = Field(description="Records awaiting cleaning")
    completed_actions: List[str] = Field(description="Completed cleaning actions")
    total_reward: float = Field(description="Cumulative reward")


class DataCleaningEnv:
    """
    OpenEnv-compliant Data Cleaning triage environment.
    Agent identifies data quality issues and applies corrections.
    """
    
    def __init__(self, records: List[DataRecord]):
        self.original_records = records
        self.records = [r.model_copy() for r in records]
        self.completed_actions: List[str] = []
        self.total_reward = 0.0
    
    def state(self) -> Observation:
        return Observation(
            records=self.records,
            completed_actions=self.completed_actions,
            total_reward=round(self.total_reward, 2)
        )
    
    def reset(self) -> Observation:
        self.records = [r.model_copy() for r in self.original_records]
        self.completed_actions = []
        self.total_reward = 0.0
        return self.state()
    
    def step(self, action: Action) -> tuple[Observation, float, bool, dict]:
        reward = 0.0
        done = False
        info = {}
        
        record = next((r for r in self.records if r.record_id == action.record_id), None)
        
        if record is None:
            reward = -0.5
            info["error"] = f"Record ID '{action.record_id}' does not exist"
            self.total_reward += reward
            return self.state(), reward, done, info
        
        reward += 0.2  # Valid record ID
        
        if record.is_actually_valid:
            if action.action_type == "classify_issue" and action.issue_type == "valid":
                reward += 0.4
                action_desc = f"Correctly identified {action.record_id} as valid"
            else:
                reward = -1.0
                action_desc = f"ERROR: Incorrectly flagged valid record {action.record_id}"
                info["error"] = "Valid record incorrectly flagged"
            self.completed_actions.append(action_desc)
            self.records = [r for r in self.records if r.record_id != action.record_id]
        
        elif action.action_type == "classify_issue":
            if action.issue_type == record.correct_issue_type:
                reward += 0.4
                issue_correct = True
            else:
                issue_correct = False
            
            if action.correction == record.correct_correction:
                reward += 0.4
                action_desc = f"Classified {action.record_id}: {action.issue_type}, will {action.correction}"
            else:
                action_desc = f"Partially correct: {action.record_id} issue={issue_correct}"
            
            self.completed_actions.append(action_desc)
            self.records = [r for r in self.records if r.record_id != action.record_id]
        
        self.total_reward = round(self.total_reward + reward, 2)
        done = len(self.records) == 0
        
        return self.state(), reward, done, info
