import streamlit as st
from agent import run_agent, SYSTEM_PROMPT
from db import init_db

init_db()

st.set_page_config(page_title="PM AI Agent", page_icon="🗂️")
st.title("🗂️ PM AI Agent")

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]
if "display_messages" not in st.session_state:
    st.session_state.display_messages = []

for msg in st.session_state.display_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("What do you need help with?")
if user_input:
    st.session_state.display_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    reply = run_agent(user_input, conversation_history=st.session_state.conversation_history)

    st.session_state.display_messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)