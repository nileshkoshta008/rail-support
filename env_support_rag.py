"""
Customer Support Ticket Triage Environment - RAG Enhanced
With Knowledge Base, Draft Reply, and Escalation Actions
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
import json


Department = Literal["Billing", "Tech Support", "Sales", "Spam"]
Priority = Literal["Low", "Medium", "High"]
TicketStatus = Literal["open", "investigating", "awaiting_response", "resolved", "escalated"]


class Message(BaseModel):
    """A message in the conversation history"""
    sender: Literal["customer", "agent"]
    content: str
    timestamp: str


class Attachment(BaseModel):
    """Simulated attachment"""
    filename: str
    type: Literal["image", "log", "pdf", "screenshot"]
    description: str


class HelpArticle(BaseModel):
    """Knowledge base article"""
    article_id: str
    title: str
    content: str
    tags: List[str]
    department: Department


class Ticket(BaseModel):
    """Represents a customer support ticket"""
    ticket_id: str
    subject: str
    messages: List[Message]
    attachments: List[Attachment] = Field(default_factory=list)
    department: Department
    priority: Priority
    status: TicketStatus = "open"
    is_spam: bool = False
    pii_detected: bool = False


class Action(BaseModel):
    """Enhanced action space with RAG capabilities"""
    action_type: Literal[
        "search_knowledge_base",
        "draft_reply",
        "escalate_to_human",
        "route_ticket",
        "mark_spam"
    ] = Field(description="The type of action to take")
    
    ticket_id: str = Field(description="The ID of the ticket to act on")
    
    # For search_knowledge_base
    search_query: Optional[str] = Field(default=None, description="Search query for KB")
    
    # For draft_reply
    reply_message: Optional[str] = Field(default=None, description="Draft response to customer")
    
    # For escalate_to_human
    escalation_reason: Optional[str] = Field(default=None, description="Why escalate")
    
    # For route_ticket
    department: Optional[Department] = Field(default=None)
    priority: Optional[Priority] = Field(default=None)
    
    # KB article to use for draft
    article_id: Optional[str] = Field(default=None)


class Observation(BaseModel):
    """Observation space for the environment"""
    tickets: List[Ticket] = Field(description="Currently active tickets")
    knowledge_base: List[HelpArticle] = Field(description="Available help articles")
    completed_actions: List[Dict[str, Any]] = Field(description="Log of actions taken")
    total_reward: float = Field(description="Cumulative reward")
    search_results: Optional[List[HelpArticle]] = Field(default=None, description="Last KB search results")


class CustomerSupportEnv:
    """
    Enhanced OpenEnv-compliant Customer Support Ticket Triage environment.
    
    Agent capabilities:
    - Route tickets to departments
    - Search knowledge base for solutions
    - Draft replies using help articles
    - Escalate complex issues to humans
    - Mark spam
    """
    
    def __init__(self, tickets: List[Ticket], knowledge_base: List[HelpArticle] = None):
        self.original_tickets = tickets
        self.tickets = [t.model_copy() for t in tickets]
        self.knowledge_base = knowledge_base or self._default_kb()
        self.completed_actions: List[Dict[str, Any]] = []
        self.total_reward = 0.0
        self.last_search_results: List[HelpArticle] = []
    
    def _default_kb(self) -> List[HelpArticle]:
        """Default knowledge base with help articles"""
        return [
            HelpArticle(
                article_id="KB-001",
                title="How to reset your password",
                content="Go to Settings > Security > Reset Password. Enter your email and follow the link sent to your inbox.",
                tags=["password", "reset", "login", "account"],
                department="Tech Support"
            ),
            HelpArticle(
                article_id="KB-002",
                title="Billing cycle explained",
                content="Your billing cycle starts on the 1st of each month. Charges are processed within 24 hours. Contact billing@company.com for disputes.",
                tags=["billing", "charge", "invoice", "payment"],
                department="Billing"
            ),
            HelpArticle(
                article_id="KB-003",
                title="Export PDF document",
                content="Click File > Export > PDF. Select destination and click Save. For large documents, use the batch export feature.",
                tags=["export", "pdf", "document", "save"],
                department="Tech Support"
            ),
            HelpArticle(
                article_id="KB-004",
                title="API authentication error",
                content="Ensure your API key is valid. Check the authorization header: 'Bearer YOUR_API_KEY'. Regenerate keys in developer settings.",
                tags=["api", "error", "authentication", "403"],
                department="Tech Support"
            ),
            HelpArticle(
                article_id="KB-005",
                title="Enterprise plan upgrade",
                content="Contact sales@company.com for enterprise quotes. We offer volume discounts for 100+ seats and custom SLA terms.",
                tags=["enterprise", "upgrade", "sales", "pricing"],
                department="Sales"
            ),
            HelpArticle(
                article_id="KB-006",
                title="Duplicate charge refund",
                content="Submit a refund request through the billing portal. Include the transaction ID and date. Refunds process within 5-7 business days.",
                tags=["refund", "duplicate", "charge", "billing"],
                department="Billing"
            ),
        ]
    
    def search_knowledge_base(self, query: str) -> List[HelpArticle]:
        """Search the knowledge base for relevant articles"""
        query_lower = query.lower()
        results = []
        
        for article in self.knowledge_base:
            score = 0
            # Check title
            if any(word in article.title.lower() for word in query_lower.split()):
                score += 2
            # Check tags
            if any(word in article.tags for word in query_lower.split()):
                score += 1
            # Check content keywords
            if any(word in article.content.lower() for word in query_lower.split()):
                score += 1
            
            if score > 0:
                results.append(article)
        
        # Sort by relevance score
        results.sort(key=lambda a: sum(1 for w in query_lower.split() if w in a.title.lower()), reverse=True)
        self.last_search_results = results[:3]  # Top 3 results
        return self.last_search_results
    
    def state(self) -> Observation:
        return Observation(
            tickets=self.tickets,
            knowledge_base=self.knowledge_base,
            completed_actions=self.completed_actions,
            total_reward=round(self.total_reward, 2),
            search_results=self.last_search_results if self.last_search_results else None
        )
    
    def reset(self) -> Observation:
        self.tickets = [t.model_copy() for t in self.original_tickets]
        self.completed_actions = []
        self.total_reward = 0.0
        self.last_search_results = []
        return self.state()
    
    def step(self, action: Action) -> tuple[Observation, float, bool, dict]:
        reward = 0.0
        done = False
        info = {}
        
        # Find ticket
        ticket = next((t for t in self.tickets if t.ticket_id == action.ticket_id), None)
        
        if ticket is None and action.action_type != "search_knowledge_base":
            reward = -0.3
            info["error"] = f"Ticket ID '{action.ticket_id}' not found"
            self.total_reward += reward
            return self.state(), reward, done, info
        
        # Handle different action types
        if action.action_type == "search_knowledge_base":
            reward = 0.1  # Searching is always okay
            if action.search_query:
                results = self.search_knowledge_base(action.search_query)
                info["results"] = [{"id": r.article_id, "title": r.title} for r in results]
                if results:
                    reward += 0.1  # Bonus for finding results
            action_desc = f"Searched KB: '{action.search_query}'"
        
        elif action.action_type == "draft_reply":
            if not ticket:
                reward = -0.3
                info["error"] = "No ticket to reply to"
            elif ticket.is_spam:
                reward = -0.5
                action_desc = "ERROR: Attempted to reply to spam"
                info["error"] = "Cannot reply to spam"
            else:
                # Check if using KB article
                if action.article_id:
                    article = next((a for a in self.knowledge_base if a.article_id == action.article_id), None)
                    if article:
                        reward = 0.6  # Great: used KB to solve
                        action_desc = f"Solved ticket {action.ticket_id} using {article.article_id}: {article.title}"
                    else:
                        reward = 0.3
                        action_desc = f"Drafted reply to {action.ticket_id} (no KB reference)"
                else:
                    reward = 0.3  # Good: drafted a reply
                    action_desc = f"Drafted reply to {action.ticket_id}"
                
                # Remove ticket from queue (resolved)
                self.tickets = [t for t in self.tickets if t.ticket_id != action.ticket_id]
        
        elif action.action_type == "escalate_to_human":
            if not ticket:
                reward = -0.3
            elif ticket.is_spam:
                reward = -0.5
                info["error"] = "Cannot escalate spam"
            else:
                reward = 0.2  # Appropriate escalation
                action_desc = f"Escalated {action.ticket_id} to human: {action.escalation_reason}"
                self.tickets = [t for t in self.tickets if t.ticket_id != action.ticket_id]
        
        elif action.action_type == "mark_spam":
            if ticket and ticket.is_spam:
                reward = 0.5
                action_desc = f"Marked {action.ticket_id} as spam"
            else:
                reward = -1.0
                action_desc = f"ERROR: Incorrectly marked {action.ticket_id} as spam"
                info["error"] = "Valid ticket marked as spam"
            self.tickets = [t for t in self.tickets if t.ticket_id != action.ticket_id]
        
        elif action.action_type == "route_ticket":
            if ticket and ticket.is_spam:
                reward = -1.0
                action_desc = f"ERROR: Routed spam {action.ticket_id} to {action.department}"
                info["error"] = "Spam routed to humans"
            elif action.department == ticket.department and action.priority == ticket.priority:
                reward = 0.7
                action_desc = f"Correctly routed {action.ticket_id} to {action.department} ({action.priority})"
            else:
                reward = 0.2
                action_desc = f"Partially correct routing for {action.ticket_id}"
            
            self.tickets = [t for t in self.tickets if t.ticket_id != action.ticket_id]
        
        else:
            reward = -0.3
            action_desc = "Unknown action"
        
        self.completed_actions.append({"action": action_desc, "reward": reward})
        self.total_reward = round(self.total_reward + reward, 2)
        done = len(self.tickets) == 0
        
        return self.state(), reward, done, info
