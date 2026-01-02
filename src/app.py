"""
Streamlit Web Interface - MentorIA
Provides a clean and reactive web chat interface for MentorIA.
This component contains no business logic or AI logic.
"""

import sys
import os
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.utils import extract_response_text


import streamlit as st  # noqa: E402
from streamlit_extras.add_vertical_space import add_vertical_space  # noqa: E402
from src.core.agent_orchestrator import (
    generate_response_stream,
    get_session_history,
)
from src.core.graph.graph_builder import initialize_conversation

st.set_page_config(
    page_title="MentorIA - Onboarding Assistant",
    layout="wide",
)

st.title("🤖 MentorIA - Onboarding Assistant")

with st.sidebar:
    st.title("About MentorIA")
    st.markdown("""
    **MentorIA** is a virtual assistant designed to facilitate the onboarding
    process for new employees. It uses advanced **Retrieval-Augmented
    Generation (RAG)** techniques to provide accurate and contextual answers
    to user questions, helping them integrate quickly into the company.
    """)
    add_vertical_space(1)
    st.text_input("Name", key="user_name", placeholder="Enter your name")
    st.text_input("Role", key="user_role", placeholder="Enter your role")
    add_vertical_space(2)
    if st.button("Start new session"):
        st.session_state.conversation_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.history_loaded = False
        st.rerun()
    st.divider()

    st.markdown("### 🛠️ Admin")

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

user_name = st.session_state.get("user_name", "Employee")

initialize_conversation(st.session_state.conversation_id, user_name)

if "messages" not in st.session_state:
    st.session_state.messages = []

history = get_session_history(st.session_state.conversation_id)
st.session_state.messages = history

for msg in st.session_state.messages:
    role = "user" if msg.type == "human" else "assistant"
    with st.chat_message(role):
        clean_content = extract_response_text(msg)
        st.markdown(clean_content)

prompt = st.chat_input("Type your question here...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            stream_generator = generate_response_stream(
                question=prompt,
                session_id=st.session_state.conversation_id,
                user_name=st.session_state.get("user_name", "Employee"),
                user_role=st.session_state.get("user_role", "New Role"),
            )

            response_text = st.write_stream(stream_generator)

        except Exception as error:
            st.error(f"Error: {error}")
            response_text = None

    if response_text:
        st.session_state.messages = get_session_history(
            st.session_state.conversation_id
        )
