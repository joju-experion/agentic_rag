import html
import os

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(page_title="Agentic RAG Chatbot", page_icon="🤖")
st.title("Agentic RAG Chatbot")
st.caption("Ask questions about prompt engineering, AI agents, or anything else.")

st.markdown(
    """
    <style>
    .log-terminal {
        max-height: 220px;
        overflow-y: auto;
        padding: 0.75rem;
        border: 1px solid #30363d;
        border-radius: 0.5rem;
        background: #0d1117;
        color: #39ff14;
        font-family: Consolas, "Courier New", monospace;
        font-size: 0.8rem;
    }
    .log-terminal pre {
        margin: 0;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "logs" not in st.session_state:
    st.session_state.logs = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"message": prompt},
                    timeout=120,
                )
                response.raise_for_status()
                result = response.json()
                answer = result["response"]
                request_logs = result.get("logs", [])
                st.session_state.logs.append(f"$ {prompt}")
                st.session_state.logs.extend(str(line) for line in request_logs)
                st.session_state.logs.append("")
            except (requests.exceptions.RequestException, KeyError, ValueError):
                answer = "I could not reach the backend. Please make sure the API is running."
                st.session_state.logs.extend([f"$ {prompt}", f"ERROR: {answer}", ""])

        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

with st.expander("Workflow terminal", expanded=False):
    terminal_output = "\n".join(st.session_state.logs[-200:])
    if not terminal_output:
        terminal_output = "Run a search to see workflow logs."

    st.markdown(
        f'<div class="log-terminal"><pre>{html.escape(terminal_output)}</pre></div>',
        unsafe_allow_html=True,
    )
