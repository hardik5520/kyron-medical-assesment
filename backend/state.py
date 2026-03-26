from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    # add_messages merges new messages into the list rather than overwriting
    messages: Annotated[list[BaseMessage], add_messages]