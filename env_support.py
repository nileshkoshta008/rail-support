"""
Customer Support Ticket Triage Environment
OpenEnv-compliant reinforcement learning environment
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


Department = Literal["Billing", "Tech Support", "Sales", "Spam"]
Priority = Literal["Low", "Medium", "High"]


class Ticket(BaseModel):
    """Represents a customer support ticket"""
    ticket_id: str
    content: str
    department: Department
    priority: Priority
    is_spam: bool = False


class Action(BaseModel):
    """Action space for the environment"""
    action_type: Literal["route_ticket", "mark_spam"] = Field(
        description="The type of action to take"
    )
    ticket_id: str = Field(
        description="The ID of the ticket to act on"
    )
    department: Optional[Department] = Field(
        default=None,
        description="Department to route to (required for route_ticket)"
    )
    priority: Optional[Priority] = Field(
        default=None,
        description="Priority level (required for route_ticket)"
    )


class Observation(BaseModel):
    """Observation space for the environment"""
    tickets: List[Ticket] = Field(
        description="Currently active tickets in the queue"
    )
    completed_actions: List[str] = Field(
        description="List of completed action descriptions"
    )
    total_reward: float = Field(
        description="Cumulative reward received so far"
    )


class CustomerSupportEnv:
    """
    OpenEnv-compliant Customer Support Ticket Triage environment.
    """
    
    def __init__(self, tickets: List[Ticket]):
        self.original_tickets = tickets
        self.tickets = [t.model_copy() for t in tickets]
        self.completed_actions: List[str] = []
        self.total_reward = 0.0
    
    def state(self) -> Observation:
        return Observation(
            tickets=self.tickets,
            completed_actions=self.completed_actions,
            total_reward=round(self.total_reward, 2)
        )
    
    def reset(self) -> Observation:
        self.tickets = [t.model_copy() for t in self.original_tickets]
        self.completed_actions = []
        self.total_reward = 0.0
        return self.state()
    
    def step(self, action: Action) -> tuple[Observation, float, bool, dict]:
        reward = 0.0
        done = False
        info = {}
        
        ticket = next((t for t in self.tickets if t.ticket_id == action.ticket_id), None)
        
        if ticket is None:
            reward = -0.5
            info["error"] = f"Ticket ID '{action.ticket_id}' does not exist"
            self.total_reward += reward
            return self.state(), reward, done, info
        
        reward += 0.2  # Valid ticket ID
        
        if action.action_type == "mark_spam":
            if ticket.is_spam:
                reward += 0.5
                action_desc = f"Marked ticket {action.ticket_id} as spam"
            else:
                reward = -1.0
                action_desc = f"Incorrectly marked valid ticket {action.ticket_id} as spam"
                info["error"] = "Valid ticket incorrectly marked as spam"
            self.completed_actions.append(action_desc)
            self.tickets = [t for t in self.tickets if t.ticket_id != action.ticket_id]
        
        elif action.action_type == "route_ticket":
            if action.department is None or action.priority is None:
                reward = -0.5
                info["error"] = "route_ticket requires department and priority"
                self.total_reward += reward
                return self.state(), reward, done, info
            
            if ticket.is_spam:
                reward = -1.0
                action_desc = f"ERROR: Routed spam ticket {action.ticket_id} to {action.department}"
                info["error"] = "Spam ticket routed to human department"
            else:
                if action.department == ticket.department:
                    reward += 0.3
                if action.priority == ticket.priority:
                    reward += 0.5
                action_desc = f"Routed ticket {action.ticket_id} to {action.department} (priority: {action.priority})"
            
            self.completed_actions.append(action_desc)
            self.tickets = [t for t in self.tickets if t.ticket_id != action.ticket_id]
        
        self.total_reward = round(self.total_reward + reward, 2)
        done = len(self.tickets) == 0
        
        return self.state(), reward, done, info
