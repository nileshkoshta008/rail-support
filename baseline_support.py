"""
Baseline Inference for Customer Support Triage
"""

import os
import sys
import json
from openai import OpenAI

from env_support import CustomerSupportEnv, Action, Observation, Ticket
from tasks_support import get_task, grade_task


def format_observation(obs: Observation) -> str:
    lines = ["=== TICKET QUEUE ==="]
    for t in obs.tickets:
        lines.append(f"\n[{t.ticket_id}] {t.content}")
    lines.append(f"\nReward: {obs.total_reward}")
    return "\n".join(lines)


def format_actions(env: CustomerSupportEnv) -> str:
    lines = ["Actions:"]
    for t in env.tickets:
        lines.append(f"- route_ticket('{t.ticket_id}', Dept, Priority)")
        lines.append(f"- mark_spam('{t.ticket_id}')")
    return "\n".join(lines)


SYSTEM_PROMPT = """You are a triage bot. Route tickets to: Billing, Tech Support, Sales, or Spam.
Priority: Low, Medium, High.

Respond JSON only:
{"action_type": "route_ticket", "ticket_id": "X", "department": "Y", "priority": "Z"}
{"action_type": "mark_spam", "ticket_id": "X"}"""


def parse_response(text: str) -> Action:
    data = json.loads(text[text.find("{"):text.rfind("}")+1])
    if data.get("action_type") == "route_ticket":
        return Action(**data)
    return Action(action_type=data["action_type"], ticket_id=data["ticket_id"])


def run_task(client: OpenAI, level: str) -> float:
    tickets = [Ticket(**t) for t in get_task(level)]
    env = CustomerSupportEnv(tickets)
    obs = env.reset()
    
    for _ in range(20):
        if not env.tickets:
            break
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": format_observation(obs) + "\n" + format_actions(env)}],
            temperature=0.1, max_tokens=256
        )
        action = parse_response(resp.choices[0].message.content)
        obs, reward, done, _ = env.step(action)
        if done:
            break
    
    result = grade_task(level, get_task(level), env.total_reward)
    print(f"{level.upper()}: Score={result.score} ({'PASS' if result.passed else 'FAIL'})")
    return env.total_reward


def get_api_key():
    # Check environment variable first
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return api_key
    # Fall back to config.py
    try:
        from config import OPENAI_API_KEY
        return OPENAI_API_KEY
    except:
        print("Error: OPENAI_API_KEY not found!")
        print("Set it in config.py or as environment variable")
        sys.exit(1)


def main():
    client = OpenAI(api_key=get_api_key())
    for level in ["easy", "medium", "hard"]:
        run_task(client, level)


if __name__ == "__main__":
    main()
