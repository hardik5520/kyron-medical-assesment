from langchain_core.tools import tool
from data.database import get_connection

@tool
def save_patient_info(
    first_name: str,
    last_name: str,
    dob: str,
    phone: str,
    email: str,
    reason: str,
) -> dict:
    """
    Save patient intake information to the database.
    Call this once all six fields have been collected from the patient.
    Returns the new patient's ID on success.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO patients (first_name, last_name, dob, phone, email, reason)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (first_name, last_name, dob, phone, email, reason),
        )
        conn.commit()
        patient_id = cursor.lastrowid
        return {"success": True, "patient_id": patient_id}

    except Exception as e:
        # Email unique constraint will trigger here if patient already exists
        return {"success": False, "error": str(e)}

    finally:
        conn.close()


@tool
def get_patient_by_email(email: str) -> dict:
    """
    Look up a patient record by email address.
    Useful to retrieve patient_id before booking an appointment.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if row:
        keys = ["id", "first_name", "last_name", "dob", "phone", "email", "reason", "created_at"]
        return dict(zip(keys, row))

    return {"error": "Patient not found"}