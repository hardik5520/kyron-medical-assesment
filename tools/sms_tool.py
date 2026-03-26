import os
from langchain_core.tools import tool
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")  


@tool
def send_confirmation_sms(
    to_phone: str,
    patient_name: str,
    doctor_name: str,
    slot: str,
) -> dict:
    """
    Send a short appointment confirmation SMS to the patient via Twilio.
    Call this right after send_confirmation_email succeeds.
    to_phone must include country code e.g. +11234567890
    """
    body = (
        f"Hi {patient_name}, your appointment with {doctor_name} "
        f"is confirmed for {slot}. See you then! — Kyron Medical"
    )

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=body,
            from_=TWILIO_FROM_NUMBER,
            to=to_phone,
        )
        return {"success": True, "sid": message.sid}
    except Exception as e:
        return {"success": False, "error": str(e)}