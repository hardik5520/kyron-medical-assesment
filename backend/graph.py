import sqlite3
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver

from backend.state import ChatState
from backend.nodes import chat_node, TOOLS
from data.database import init_db, DB_PATH

# Ensure tables exist before anything runs
init_db()

# Persistent checkpointer — same pattern as the reference code
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# --- Build graph ---
graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)
graph.add_node("tools", ToolNode(TOOLS))

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)  # routes to tools or END
graph.add_edge("tools", "chat_node")                       # always return to LLM after tool

chatbot = graph.compile(checkpointer=checkpointer)


def retrieve_all_threads() -> list:
    """Return all thread IDs stored in the checkpointer (for sidebar history)."""
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)