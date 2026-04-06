"""
Streamlit Dashboard for Customer Support Triage
Real-time visualization of agent performance
"""

import streamlit as st
import requests
import json
import time

st.set_page_config(page_title="Support Triage Dashboard", layout="wide")

API_BASE = "http://localhost:8000"

st.title("Customer Support Triage Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.header("Task Control")
    task_level = st.selectbox("Select Task", ["easy", "medium", "hard"])
    if st.button("Start Task"):
        resp = requests.post(f"{API_BASE}/start", json={"task_level": task_level})
        if resp.status_code == 200:
            st.success(resp.json()["message"])
        else:
            st.error(resp.text)

with col2:
    st.header("Current State")
    if st.button("Refresh State"):
        resp = requests.get(f"{API_BASE}/state")
        if resp.status_code == 200:
            data = resp.json()
            st.metric("Open Tickets", len(data["tickets"]))
            st.metric("Total Reward", data["total_reward"])
        else:
            st.error("Start a task first")

with col3:
    st.header("Statistics")
    if st.button("Load Stats"):
        resp = requests.get(f"{API_BASE}/stats")
        if resp.status_code == 200:
            stats = resp.json()
            st.metric("Total Sessions", stats["total_sessions"])
            st.metric("Avg Reward", f"{stats['avg_reward']:.2f}")
        else:
            st.error("No stats available")

st.divider()

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Active Tickets")
    try:
        resp = requests.get(f"{API_BASE}/state")
        if resp.status_code == 200:
            tickets = resp.json().get("tickets", [])
            for t in tickets:
                with st.expander(f"{t['ticket_id']}: {t['subject']}"):
                    st.write(f"**Department:** {t['department']}")
                    st.write(f"**Priority:** {t['priority']}")
                    st.write("**Messages:**")
                    for msg in t.get("messages", []):
                        st.write(f"  - {msg['sender']}: {msg['content'][:100]}...")
    except:
        st.info("Start a task to see tickets")

with col_right:
    st.subheader("Actions")
    action_type = st.selectbox("Action", ["search_knowledge_base", "draft_reply", "escalate_to_human", "route_ticket", "mark_spam"])
    ticket_id = st.text_input("Ticket ID", "TKT-001")
    
    if action_type == "search_knowledge_base":
        query = st.text_input("Search Query", "")
        if st.button("Execute"):
            resp = requests.post(f"{API_BASE}/step", json={
                "action_type": action_type,
                "ticket_id": ticket_id,
                "search_query": query
            })
            st.json(resp.json())
    
    elif action_type == "route_ticket":
        dept = st.selectbox("Department", ["Billing", "Tech Support", "Sales", "Spam"])
        prio = st.selectbox("Priority", ["Low", "Medium", "High"])
        if st.button("Execute"):
            resp = requests.post(f"{API_BASE}/step", json={
                "action_type": action_type,
                "ticket_id": ticket_id,
                "department": dept,
                "priority": prio
            })
            st.json(resp.json())
    
    elif action_type == "draft_reply":
        msg = st.text_area("Reply Message", "")
        article = st.text_input("Article ID (optional)", "")
        if st.button("Execute"):
            data = {"action_type": action_type, "ticket_id": ticket_id, "reply_message": msg}
            if article:
                data["article_id"] = article
            resp = requests.post(f"{API_BASE}/step", json=data)
            st.json(resp.json())
    
    else:
        if st.button("Execute"):
            resp = requests.post(f"{API_BASE}/step", json={
                "action_type": action_type,
                "ticket_id": ticket_id
            })
            st.json(resp.json())

st.divider()

st.subheader("Knowledge Base Articles")
try:
    resp = requests.get(f"{API_BASE}/kb")
    if resp.status_code == 200:
        articles = resp.json()
        for a in articles:
            st.write(f"**{a['article_id']}**: {a['title']} ({a['department']})")
except:
    st.info("Start a task to load KB")
