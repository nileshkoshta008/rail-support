"""
Database layer for Customer Support Environment
SQLite persistence for tickets, actions, and knowledge base
"""

import os
import sqlite3
import json
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

# Get the absolute path to the directory containing this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = os.path.join(BASE_DIR, "support.db")
        else:
            self.db_path = db_path
        self.init_db()
    
    @contextmanager
    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
    
    def init_db(self):
        with self.get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id TEXT PRIMARY KEY,
                    subject TEXT,
                    messages TEXT,
                    attachments TEXT,
                    department TEXT,
                    priority TEXT,
                    status TEXT,
                    is_spam INTEGER,
                    pii_detected INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    article_id TEXT PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    tags TEXT,
                    department TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id TEXT,
                    action_type TEXT,
                    details TEXT,
                    reward REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_level TEXT,
                    total_reward REAL,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def insert_ticket(self, ticket: Dict[str, Any]):
        with self.get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tickets 
                (ticket_id, subject, messages, attachments, department, priority, status, is_spam, pii_detected)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket["ticket_id"],
                ticket["subject"],
                json.dumps(ticket["messages"]),
                json.dumps(ticket.get("attachments", [])),
                ticket["department"],
                ticket["priority"],
                ticket.get("status", "open"),
                1 if ticket.get("is_spam") else 0,
                1 if ticket.get("pii_detected") else 0
            ))
    
    def get_all_tickets(self) -> List[Dict[str, Any]]:
        with self.get_conn() as conn:
            rows = conn.execute("SELECT * FROM tickets WHERE status != 'resolved'").fetchall()
            return [dict(row) for row in rows]
    
    def update_ticket_status(self, ticket_id: str, status: str):
        with self.get_conn() as conn:
            conn.execute("UPDATE tickets SET status = ? WHERE ticket_id = ?", (status, ticket_id))
    
    def insert_action(self, ticket_id: str, action_type: str, details: Dict[str, Any], reward: float):
        with self.get_conn() as conn:
            conn.execute("""
                INSERT INTO actions (ticket_id, action_type, details, reward)
                VALUES (?, ?, ?, ?)
            """, (ticket_id, action_type, json.dumps(details), reward))
    
    def insert_kb_article(self, article: Dict[str, Any]):
        with self.get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO knowledge_base
                (article_id, title, content, tags, department)
                VALUES (?, ?, ?, ?, ?)
            """, (
                article["article_id"],
                article["title"],
                article["content"],
                json.dumps(article["tags"]),
                article["department"]
            ))
    
    def get_all_kb_articles(self) -> List[Dict[str, Any]]:
        with self.get_conn() as conn:
            rows = conn.execute("SELECT * FROM knowledge_base").fetchall()
            return [dict(row) for row in rows]
    
    def log_session(self, task_level: str, total_reward: float):
        with self.get_conn() as conn:
            conn.execute("""
                INSERT INTO sessions (task_level, total_reward)
                VALUES (?, ?)
            """, (task_level, total_reward))
    
    def get_session_stats(self) -> Dict[str, Any]:
        with self.get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
            avg_reward = conn.execute("SELECT AVG(total_reward) FROM sessions").fetchone()[0] or 0
            by_level = conn.execute("""
                SELECT task_level, COUNT(*) as count, AVG(total_reward) as avg 
                FROM sessions GROUP BY task_level
            """).fetchall()
            return {"total_sessions": total, "avg_reward": avg_reward, "by_level": [dict(r) for r in by_level]}
