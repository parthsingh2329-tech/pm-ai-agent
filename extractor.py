import os
import json
from dotenv import load_dotenv
load_dotenv()
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "openai/gpt-oss-120b"

EXTRACTION_PROMPT = """You are extracting actionable tasks from messy notes (meeting notes, emails, etc.)
Read the text and identify distinct, actionable tasks. For each task, extract:
- title: a short, clear task title
- due_date: an ISO date (YYYY-MM-DD) if a deadline is mentioned or can be reasonably inferred, otherwise null
- estimated_effort_hours: a number if effort/time is mentioned, otherwise null

Respond ONLY with valid JSON in this exact format, nothing else:
{"tasks": [{"title": "...", "due_date": "...", "estimated_effort_hours": ...}]}

If no actionable tasks are found, respond with {"tasks": []}.
Today's date is 2026-08-17, for resolving relative dates like "next Friday" or "in two weeks"."""


def extract_tasks_from_text(text):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return parsed.get("tasks", [])