from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import tools_condition
from langchain_core.messages import AIMessage
from src.config import get_mongodb_client
from src.core.graph.nodes import agent_node, retrieve_node, tool_node
from src.core.graph.state import MentoriaState
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_core.runnables.config import RunnableConfig


def limited_tools_condition(state):
    MAX_LOOPS = 3

    current_loops = state.get("loop_count", 0)

    if current_loops > MAX_LOOPS:
        return END

    return tools_condition(state)


client = get_mongodb_client()
checkpointer = MongoDBSaver(client=client)

workflow = StateGraph(MentoriaState)

workflow.add_node("retrieve", retrieve_node)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)


workflow.add_edge(START, "retrieve")

workflow.add_edge("retrieve", "agent")

workflow.add_conditional_edges(
    "agent", limited_tools_condition, {"tools": "tools", END: END}
)

workflow.add_edge("tools", "agent")

app = workflow.compile(checkpointer=checkpointer)


def initialize_conversation(session_id: str, user_name: str) -> None:
    """
    Verifica se a sessão é nova e injeta a mensagem de boas-vindas no banco.
    """
    config = RunnableConfig(configurable={"thread_id": session_id})

    current_state = app.get_state(config)

    user_name = user_name.strip()
    user_name = user_name if user_name else "Colaborador"

    if not current_state.values or not current_state.values.get("messages"):
        welcome_text = (
            f"Olá,\t **{user_name}**! 👋\n\n"
            "Sou o **MentorIA**, seu assistente de onboarding.\n"
            "Estou aqui para tirar suas dúvidas sobre cultura, processos e ferramentas.\n\n"
            "Por onde você gostaria de começar hoje?"
        )

        welcome_message = AIMessage(content=welcome_text)
        app.update_state(config, {"messages": [welcome_message]}, as_node="agent")
