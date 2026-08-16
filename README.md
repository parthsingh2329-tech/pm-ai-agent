# PM AI Agent

A project management agent for solo freelancers, built to explore real agentic AI patterns — not just an LLM wrapper.

## What it does
- Creates and updates tasks through natural language
- Tracks dependencies and reschedules downstream tasks automatically when a deadline shifts
- Proactively checks in on stalled or at-risk tasks on a schedule, without being asked
- Remembers past notes and decisions via semantic search (RAG), so it can answer questions like "what did I decide about X?"
- Runs through a simple chat interface

## Architecture
- **LLM**: Groq (`openai/gpt-oss-120b` for reasoning, function/tool calling)
- **Orchestration**: a custom agent loop (no framework) — the model decides which tools to call, the code executes them, results feed back in
- **Structured data**: SQLite (`tasks`, `dependencies` tables) — dependency graph logic runs in code, not the LLM, for reliability
- **Memory**: ChromaDB for semantic search over notes
- **Proactive layer**: APScheduler runs a background check for stalled/at-risk tasks and triggers the agent to draft a nudge
- **Interface**: Streamlit

## Why this design
Most PM-tool clones are CRUD apps with a chatbot bolted on. This project tries to demonstrate actual agent behavior: the agent acts on its own initiative (the scheduler layer), reasons about state it looks up rather than guesses at (tool calling against a real DB), and recalls context across sessions (RAG memory) — rather than just answering one-off questions.

## Setup
1. `python -m venv venv` and activate it
2. `pip install groq fastapi uvicorn apscheduler chromadb python-dotenv streamlit`
3. Add a `.env` file with `GROQ_API_KEY=your-key-here`
4. `python db.py` to initialize the database
5. `streamlit run app.py`

## Tech stack
Python · Groq API · SQLite · ChromaDB · APScheduler · Streamlit