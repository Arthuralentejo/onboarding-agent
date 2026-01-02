from langgraph.prebuilt import ToolNode

from src.config import get_llm_model, get_tavily_search_tool
from src.core.graph.state import MentoriaState
from src.core.graph.prompts import get_mentoria_prompt
from src.core.graph.retrieval import retrieve_context
from src.core.utils import format_context

tavily_tool = get_tavily_search_tool()
tools = [tavily_tool]
tool_node = ToolNode(tools)


def retrieve_node(state: MentoriaState):
    print("--- RETRIEVING CONTEXT ---")
    question = state["question"]

    chunks = retrieve_context(question=question, k=5)
    formatted_context = format_context(chunks)

    if not formatted_context:
        formatted_context = "No internal context found."

    return {"context": formatted_context}


def agent_node(state: MentoriaState):
    print("--- AGENT THINKING ---")
    llm = get_llm_model(temperature=0.3)
    llm_with_tools = llm.bind_tools(tools)

    prompt_template = get_mentoria_prompt()

    chain = prompt_template | llm_with_tools

    response = chain.invoke(
        {
            "user_name": state["user_name"],
            "user_role": state["user_role"],
            "context": state["context"],
            "chat_history": state["messages"],
            "question": state["question"],
        }
    )

    return {"messages": [response], "loop_count": 1}
