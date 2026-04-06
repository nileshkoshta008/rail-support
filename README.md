# Customer Support Triage - Enhanced Edition

OpenEnv-compliant RL environment with RAG, multi-turn conversations, and enterprise infrastructure.

## Features

### 1. RAG-Enhanced Actions
- **Knowledge Base**: 6 default help articles
- **search_knowledge_base**: Search KB for solutions
- **draft_reply**: Respond using KB articles (+0.6 bonus)
- **escalate_to_human**: Escalate unsolvable issues

### 2. Data Engineering
- **Multi-turn conversations**: Back-and-forth message history
- **Attachments**: Images, logs, PDFs, screenshots
- **PII Detection**: Credit cards, SSNs with penalties

### 3. Enterprise Infrastructure
- **SQLite Database**: Persistent ticket/action storage
- **FastAPI**: REST API at localhost:8000
- **Streamlit Dashboard**: Real-time UI

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Edit config.py with your API key

# Run baseline (RAG version)
python baseline_support_rag.py
```

## Run with API + Dashboard

```bash
# Terminal 1: Start API
python api.py

# Terminal 2: Start Dashboard
streamlit run dashboard.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/start` | POST | Start task (easy/medium/hard) |
| `/state` | GET | Current observation |
| `/step` | POST | Execute action |
| `/reset` | POST | Reset environment |
| `/kb` | GET | Knowledge base articles |
| `/stats` | GET | Session statistics |

## Action Space

| Action | Parameters | Reward |
|--------|------------|--------|
| search_knowledge_base | ticket_id, query | +0.1 |
| draft_reply | ticket_id, message, article_id? | +0.3 to +0.6 |
| escalate_to_human | ticket_id, reason | +0.2 |
| route_ticket | ticket_id, department, priority | +0.2 to +0.7 |
| mark_spam | ticket_id | +0.5 |

## Files

```
.
├── env_support_rag.py        # RAG environment
├── tasks_support_rag.py     # Tasks with PII/multi-turn
├── baseline_support_rag.py  # OpenAI inference
├── database.py              # SQLite layer
├── api.py                   # FastAPI server
├── dashboard.py             # Streamlit UI
├── config.py                # API key config
├── Dockerfile               # Container
└── requirements.txt         # Dependencies
```
