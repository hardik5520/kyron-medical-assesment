from langchain_openai import ChatOpenAI
from backend.prompts import system_prompt
from tools.patient_tools import save_patient_info, get_patient_by_email
from tools.appointment_tools import check_availability, book_appointment
from tools.email_tool import send_confirmation_email
from tools.sms_tool import send_confirmation_sms

# All tools the LLM can call
TOOLS = [
    save_patient_info,
    get_patient_by_email,
    check_availability,
    book_appointment,
    send_confirmation_email,
    send_confirmation_sms,
]

model = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = model.bind_tools(TOOLS)


def chat_node(state: dict) -> dict:
    """Format the prompt with current messages and call the LLM."""
    # Format messages through the prompt template before passing to LLM
    formatted = system_prompt.invoke({"messages": state["messages"]})
    response = llm_with_tools.invoke(formatted)
    return {"messages": [response]}