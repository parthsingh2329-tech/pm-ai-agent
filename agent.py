import os
import json
from dotenv import load_dotenv
load_dotenv()
from groq import Groq
from tools import TOOL_SCHEMAS, TOOL_IMPL

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = (
    "You are a project management agent for a solo freelancer. You can create "
    "and update tasks, reschedule dependent tasks, and check the current project "
    "state. Use tools whenever the user's request requires reading or changing "
    "project data — don't guess at task IDs or dates, look them up first."
    " When calling any tool, omit optional parameters entirely if you don't have a value for them — "
    "never pass null explicitly."
)


def run_agent(user_message, conversation_history=None):
    messages = conversation_history or [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=MODEL, messages=messages, tools=TOOL_SCHEMAS, tool_choice="auto",
    )
    reply = response.choices[0].message
    messages.append(reply)

    while reply.tool_calls:
        for call in reply.tool_calls:
            fn_name = call.function.name
            fn_args = json.loads(call.function.arguments)
            result = TOOL_IMPL[fn_name](**fn_args)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result),
            })
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOL_SCHEMAS, tool_choice="auto",
        )
        reply = response.choices[0].message
        messages.append(reply)

    return reply.content


if __name__ == "__main__":
    print(run_agent("What color scheme did the client ask for?"))