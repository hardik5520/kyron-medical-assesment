import streamlit as st
from backend.graph import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid
import os

VOICE_SERVER_URL   = "ws://localhost:8765"
VOICE_COMPONENT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice", "voice_component.html")

# ========================== Utilities ==========================

def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)
    st.session_state["message_history"] = []

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def load_conversation(thread_id):
    """Reload a past conversation from the checkpointer."""
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    return state.values.get("messages", [])

# ====================== Session Initialization =================

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

add_thread(st.session_state["thread_id"])

# =========================== Sidebar ===========================

st.sidebar.title("Kyron Medical")
st.sidebar.caption("Patient Appointment Assistant")

if st.sidebar.button("＋ New Conversation"):
    reset_chat()

st.sidebar.divider()
st.sidebar.header("Past Conversations")

for thread_id in st.session_state["chat_threads"][::-1]:
    label = f"🗂 {str(thread_id)[:8]}…"
    if st.sidebar.button(label, key=thread_id):
        st.session_state["thread_id"] = thread_id
        messages = load_conversation(thread_id)
        temp = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                temp.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage) and msg.content:
                temp.append({"role": "assistant", "content": msg.content})
        st.session_state["message_history"] = temp

# =========================== Main UI ===========================

st.title("👩‍⚕️ Kyron Medical — Appointment Assistant")

# Render existing message history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---- Voice call component ----
# Read HTML from file and inject thread_id + WS URL at runtime
with open(VOICE_COMPONENT_PATH, "r") as f:
    voice_html = (
        f.read()
        .replace("{{THREAD_ID}}", st.session_state["thread_id"])
        .replace("{{WS_URL}}", VOICE_SERVER_URL)
    )

st.components.v1.html(voice_html, height=160)

# ---- Chat input ----
user_input = st.chat_input("How can I help you today?")

if user_input:
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata":     {"thread_id": st.session_state["thread_id"]},
        "run_name":     "chat_turn",
    }

    with st.chat_message("assistant"):
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}`…", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}`…",
                            state="running",
                        )
                    with status_holder["box"]:
                        st.write(f"🔍 Called: `{tool_name}`")

                if isinstance(message_chunk, AIMessage) and message_chunk.content:
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        if status_holder["box"] is not None:
            status_holder["box"].update(label="✅ Done", state="complete", expanded=False)

    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )