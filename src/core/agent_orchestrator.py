"""
Chain Module - MentorIA Core
Responsible for orchestrating the execution graph using LangGraph.
"""

from src.core.graph.graph_builder import app
from src.core.graph.state import MentoriaState
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables.config import RunnableConfig


def generate_response(
    question: str,
    session_id: str,
    user_name: str,
    user_role: str,
) -> str:
    config = RunnableConfig(configurable={"thread_id": session_id})

    initial_state = MentoriaState(
        loop_count=0,
        question=question,
        user_name=user_name,
        user_role=user_role,
        messages=[HumanMessage(content=question)],
        context="",
    )

    final_state = app.invoke(initial_state, config=config)
    return final_state["messages"][-1].content


def generate_response_stream(
    question: str,
    session_id: str,
    user_name: str,
    user_role: str,
):
    config = RunnableConfig(configurable={"thread_id": session_id})

    initial_state = MentoriaState(
        loop_count=0,
        question=question,
        user_name=user_name,
        user_role=user_role,
        messages=[HumanMessage(content=question)],
        context="",
    )

    stream = app.stream(initial_state, config=config, stream_mode="messages")

    for message, metadata in stream:
        if metadata.get("langgraph_node") == "agent" and isinstance(message, AIMessage):
            content = message.content

            if isinstance(content, str):
                if content:
                    yield content

            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict):
                        if "text" in part:
                            yield part["text"]
                    elif isinstance(part, str):
                        yield part


def get_session_history(session_id: str):
    config = RunnableConfig(configurable={"thread_id": session_id})

    state = app.get_state(config)

    if state and state.values:
        return state.values.get("messages", [])
    return []
