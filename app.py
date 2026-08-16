import streamlit as st
from agent import run_agent, SYSTEM_PROMPT
from db import init_db
from tools import create_project, list_projects
from session_state import set_current_project

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