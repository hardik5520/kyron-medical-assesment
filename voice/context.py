from langchain_core.messages import HumanMessage, AIMessage
from backend.graph import chatbot


def get_chat_context(thread_id: str) -> str:
    """
    Load the web chat history for a thread and format it as a
    plain string so it can be injected into the voice AI's system prompt.
    Returns empty string if no history found.
    """
    config = {"configurable": {"thread_id": thread_id}}
    state = chatbot.get_state(config=config)
    messages = state.values.get("messages", [])

    if not messages:
        return ""

    lines = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            lines.append(f"Patient: {msg.content}")
        elif isinstance(msg, AIMessage) and msg.content:
            lines.append(f"Assistant: {msg.content}")

    return "\n".join(lines)