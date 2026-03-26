import os
import yagmail
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS     = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


@tool
def send_confirmation_email(
    to_email: str,
    patient_name: str,
    doctor_name: str,
    specialty: str,
    slot: str,
    reason: str,
) -> dict:
    """
    Send an appointment confirmation email to the patient via Gmail.
    Call this after a successful book_appointment.
    """
    subject = f"Your Appointment Confirmation — {doctor_name}"

    body = f"""Dear {patient_name},

Your appointment has been successfully scheduled. Here are your details:

  Doctor   : {doctor_name} ({specialty})
  Date/Time: {slot}
  Reason   : {reason}

Please arrive 10 minutes early and bring a valid photo ID.

If you need to reschedule or have any questions, please contact our office.

Warm regards,
Kyron Medical
"""

    try:
        yag = yagmail.SMTP(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        yag.send(to=to_email, subject=subject, contents=body)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}