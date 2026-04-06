"""
Baseline Inference for Data Cleaning
"""

import os
import sys
import json
from openai import OpenAI

from env_data_cleaning import DataCleaningEnv, Action, Observation, DataRecord
from tasks_data_cleaning import get_task, grade_task


def get_api_key():
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return api_key
    try:
        from config import OPENAI_API_KEY
        return OPENAI_API_KEY
    except:
        print("Error: OPENAI_API_KEY not found!")
        print("Set it in config.py or as environment variable")
        sys.exit(1)


SYSTEM_PROMPT = """You are a data cleaning triage bot. Identify issues and apply corrections.
Issue types: missing, duplicate, format, outlier, inconsistent, valid
Corrections: drop, impute, flag, ignore

Respond JSON only:
{"action_type": "classify_issue", "record_id": "X", "issue_type": "Y", "correction": "Z"}
{"action_type": "apply_correction", "record_id": "X", "issue_type": "Y", "correction": "Z"}"""


def parse_response(text: str) -> Action:
    data = json.loads(text[text.find("{"):text.rfind("}")+1])
    return Action(**data)


def run_task(client: OpenAI, level: str) -> float:
    records = [DataRecord(**r) for r in get_task(level)]
    env = DataCleaningEnv(records)
    obs = env.reset()
    
    for _ in range(20):
        if not env.records:
            break
        obs_dict = obs.model_dump()
        prompt = f"Records: {obs_dict['records']}\nActions: {obs_dict['completed_actions']}"
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            temperature=0.1, max_tokens=256
        )
        action = parse_response(resp.choices[0].message.content)
        obs, reward, done, _ = env.step(action)
        if done:
            break
    
    result = grade_task(level, get_task(level), env.total_reward)
    print(f"{level.upper()}: Score={result.score} ({'PASS' if result.passed else 'FAIL'})")
    return env.total_reward


def main():
    client = OpenAI(api_key=get_api_key())
    for level in ["easy", "medium", "hard"]:
        run_task(client, level)


if __name__ == "__main__":
    main()
