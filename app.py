import streamlit as st
from agent import run_agent, SYSTEM_PROMPT
from db import init_db
from tools import create_project, list_projects, create_task
from session_state import set_current_project
from timeline import get_timeline_data, build_gantt_figure
from extractor import extract_tasks_from_text
from extractor import extract_tasks_from_text

init_db()
st.set_page_config(page_title="PM AI Agent", page_icon="🗂️")

with st.sidebar:
    st.header("Projects")
    projects = list_projects()["projects"]
    project_names = {p["name"]: p["id"] for p in projects}

    selected_id = None
    if projects:
        selected_name = st.selectbox("Active project", list(project_names.keys()))
        selected_id = project_names[selected_name]
    else:
        st.info("No projects yet — create one below.")

    new_name = st.text_input("New project name")
    if st.button("Create project") and new_name:
        result = create_project(new_name)
        selected_id = result["project_id"]
        st.rerun()

if selected_id:
    set_current_project(selected_id)

st.title("🗂️ PM AI Agent")

tab_chat, tab_timeline, tab_import = st.tabs(["💬 Chat", "📅 Timeline", "📎 Import Notes"])

with tab_chat:
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    if "display_messages" not in st.session_state:
        st.session_state.display_messages = []

    for msg in st.session_state.display_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if selected_id:
        user_input = st.chat_input("What do you need help with?")
        if user_input:
            st.session_state.display_messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            reply = run_agent(user_input, conversation_history=st.session_state.conversation_history)

            st.session_state.display_messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)
    else:
        st.chat_input("Create a project first", disabled=True)

with tab_timeline:
    if selected_id:
        df = get_timeline_data()
        fig = build_gantt_figure(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No tasks with dates yet — create one in the Chat tab.")
    else:
        st.info("Select or create a project first.")
with tab_import:
    if selected_id:
        st.write("Paste meeting notes, emails, or any messy text — the agent will pull out actionable tasks.")
        notes_text = st.text_area("Notes", height=200)
        if st.button("Extract Tasks") and notes_text:
            with st.spinner("Extracting tasks..."):
                extracted = extract_tasks_from_text(notes_text)
            if not extracted:
                st.info("No actionable tasks found in that text.")
            else:
                st.success(f"Found {len(extracted)} task(s):")
                for t in extracted:
                    create_task(
                        title=t.get("title"),
                        due_date=t.get("due_date"),
                        estimated_effort_hours=t.get("estimated_effort_hours"),
                    )
                    st.write(f"✅ **{t.get('title')}** — due {t.get('due_date') or 'unspecified'}")
    else:
        st.info("Select or create a project first.")