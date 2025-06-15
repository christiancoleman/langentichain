import streamlit as st
from main import run_agent

st.set_page_config(page_title="Agentic Chat", layout="wide")
st.title("🧠 LangChain Agentic Chat")

if "history" not in st.session_state:
	st.session_state.history = []

user_input = st.chat_input("Ask your AI assistant...")
if user_input:
	with st.spinner("Thinking..."):
		response = run_agent(user_input)
	st.session_state.history.append((user_input, response))

for user_msg, agent_msg in reversed(st.session_state.history):
	st.chat_message("user").write(user_msg)
	st.chat_message("assistant").write(agent_msg)
