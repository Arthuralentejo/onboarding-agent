import operator
from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class MentoriaState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    loop_count: Annotated[int, operator.add]
    user_name: str
    user_role: str
    context: str
    question: str
