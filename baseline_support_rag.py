"""
Baseline Inference for RAG-Enhanced Customer Support
Uses Knowledge Base, Draft Reply, and Escalation Actions
"""

import os
import sys
import json
from openai import OpenAI

from env_support_rag import CustomerSupportEnv, Action, Observation, Ticket, HelpArticle
from tasks_support_rag import get_task, grade_task


def get_api_key():
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return api_key
    try:
        from config import OPENAI_API_KEY
        return OPENAI_API_KEY
    except:
        print("Error: OPENAI_API_KEY not found!")
        sys.exit(1)


def format_observation(obs: Observation) -> str:
    lines = ["=== TICKET QUEUE ==="]
    for t in obs.tickets:
        lines.append(f"\n[{t.ticket_id}] {t.subject}")
        for msg in t.messages:
            lines.append(f"  {msg.sender}: {msg.content[:100]}...")
        if t.attachments:
            lines.append(f"  Attachments: {[a.filename for a in t.attachments]}")
    lines.append(f"\nTotal Reward: {obs.total_reward}")
    
    if obs.search_results:
        lines.append("\n=== LAST KB SEARCH ===")
        for r in obs.search_results:
            lines.append(f"  - {r.article_id}: {r.title}")
    
    return "\n".join(lines)


def format_actions(env: CustomerSupportEnv) -> str:
    lines = ["\n=== AVAILABLE ACTIONS ==="]
    for t in env.tickets:
        lines.append(f"- search_knowledge_base('{t.ticket_id}', query='<search terms>')")
        lines.append(f"- draft_reply('{t.ticket_id}', message='<reply>', article_id='<KB-XXX>')")
        lines.append(f"- escalate_to_human('{t.ticket_id}', reason='<why>')")
        lines.append(f"- route_ticket('{t.ticket_id}', department='X', priority='Y')")
        lines.append(f"- mark_spam('{t.ticket_id}')")
    return "\n".join(lines)


SYSTEM_PROMPT = """You are a Level 1 Customer Support Agent with access to a Knowledge Base (KB).

AVAILABLE ACTIONS:
1. search_knowledge_base(ticket_id, query) - Search KB for solutions
2. draft_reply(ticket_id, message, article_id?) - Reply using KB article
3. escalate_to_human(ticket_id, reason) - Escalate complex issues
4. route_ticket(ticket_id, department, priority) - Route if can't solve
5. mark_spam(ticket_id) - Mark obvious spam

GUIDELINES:
- ALWAYS search KB first before responding
- Use KB article_id in draft_reply for +0.6 reward bonus
- Only escalate if truly unsolvable
- PII in tickets: Route to Tech Support with "PII" flag

Respond JSON only:
{"action_type": "search_knowledge_base", "ticket_id": "X", "search_query": "terms"}
{"action_type": "draft_reply", "ticket_id": "X", "reply_message": "text", "article_id": "KB-XXX"}
{"action_type": "escalate_to_human", "ticket_id": "X", "escalation_reason": "why"}
{"action_type": "route_ticket", "ticket_id": "X", "department": "Y", "priority": "Z"}
{"action_type": "mark_spam", "ticket_id": "X"}"""


def parse_response(text: str) -> Action:
    try:
        data = json.loads(text[text.find("{"):text.rfind("}")+1])
        return Action(**data)
    except:
        # Default fallback
        return Action(action_type="route_ticket", ticket_id="TKT-001", department="Tech Support", priority="Medium")


def run_task(client: OpenAI, level: str) -> float:
    tickets = [Ticket(**t) for t in get_task(level)]
    env = CustomerSupportEnv(tickets)
    obs = env.reset()
    
    print(f"\n{'='*50}")
    print(f"Running Task: {level.upper()}")
    print(f"{'='*50}")
    
    for step in range(30):
        if not env.tickets:
            print("All tickets resolved!")
            break
        
        prompt = format_observation(obs) + format_actions(env)
        
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=512
        )
        
        llm_text = resp.choices[0].message.content
        print(f"\nStep {step+1}: {llm_text[:150]}...")
        
        try:
            action = parse_response(llm_text)
            obs, reward, done, info = env.step(action)
            print(f"  Reward: {reward:.2f}")
            if info.get("error"):
                print(f"  Error: {info['error']}")
            if done:
                break
        except Exception as e:
            print(f"  Action error: {e}")
    
    result = grade_task(level, get_task(level), env.total_reward)
    print(f"\n{level.upper()}: Score={result.score} ({'PASS' if result.passed else 'FAIL'})")
    print(f"Max: {result.max_possible_reward}, Got: {result.achieved_reward}")
    return env.total_reward


def main():
    client = OpenAI(api_key=get_api_key())
    
    for level in ["easy", "medium", "hard"]:
        run_task(client, level)


if __name__ == "__main__":
    main()
