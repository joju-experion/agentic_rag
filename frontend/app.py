import html
import os
from datetime import datetime

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
        max-height: 320px;
        overflow-y: auto;
        padding: 0.75rem;
        border: 1px solid #30363d;
        border-radius: 0.5rem;
        background: #0d1117;
        font-family: Consolas, "Courier New", monospace;
        font-size: 0.8rem;
        line-height: 1.5;
    }
    .log-line {
        white-space: pre-wrap;
        overflow-wrap: anywhere;
    }
    .log-info { color: #7ee787; }
    .log-warn { color: #d29922; }
    .log-error { color: #f85149; }
    .log-query { color: #58a6ff; font-weight: 600; }
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
                timestamp = datetime.now().astimezone().strftime("%H:%M:%S")
                st.session_state.logs.append(
                    f"{timestamp} | QUERY | USER       | {prompt}"
                )
                st.session_state.logs.extend(str(line) for line in request_logs)
                st.session_state.logs.append("")
            except (requests.exceptions.RequestException, KeyError, ValueError):
                answer = "I could not reach the backend. Please make sure the API is running."
                timestamp = datetime.now().astimezone().strftime("%H:%M:%S")
                st.session_state.logs.extend(
                    [
                        f"{timestamp} | QUERY | USER       | {prompt}",
                        f"{timestamp} | ERROR | FRONTEND   | {answer}",
                        "",
                    ]
                )

        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

with st.expander("Workflow terminal", expanded=False):
    terminal_lines = st.session_state.logs[-200:]
    if not terminal_lines:
        terminal_lines = ["Run a search to see workflow logs."]

    rendered_lines = []
    for line in terminal_lines:
        if "| ERROR |" in line:
            css_class = "log-error"
        elif "| WARN " in line:
            css_class = "log-warn"
        elif "| QUERY |" in line:
            css_class = "log-query"
        else:
            css_class = "log-info"

        content = html.escape(line) if line else "&nbsp;"
        rendered_lines.append(
            f'<div class="log-line {css_class}">{content}</div>'
        )

    st.markdown(
        f'<div class="log-terminal">{"".join(rendered_lines)}</div>',
        unsafe_allow_html=True,
    )
