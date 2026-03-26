from langchain_core.tools import tool
from data.database import get_connection
from data.doctors import DOCTORS

@tool
def check_availability(doctor_id: str) -> dict:
    """
    Return all available (not yet booked) slots for a given doctor.
    doctor_id must be one of: dr_chen, dr_webb, dr_nair, dr_okafor.
    The LLM will filter by day preference from the returned list if the patient asks.
    """
    if doctor_id not in DOCTORS:
        return {"error": f"Unknown doctor_id '{doctor_id}'. Valid options: {list(DOCTORS.keys())}"}

    doctor = DOCTORS[doctor_id]

    # Fetch already-booked slots from DB and subtract from hardcoded list
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT slot FROM appointments WHERE doctor_id = ? AND status = 'confirmed'",
        (doctor_id,),
    )
    booked_slots = {row[0] for row in cursor.fetchall()}
    conn.close()

    available = [s for s in doctor["slots"] if s not in booked_slots]

    if not available:
        return {
            "doctor_name": doctor["name"],
            "specialty": doctor["specialty"],
            "available_slots": [],
            "message": "No slots currently available. Please call the office directly.",
        }

    return {
        "doctor_name": doctor["name"],
        "specialty": doctor["specialty"],
        "available_slots": available,
    }


@tool
def book_appointment(patient_id: int, doctor_id: str, slot: str, reason: str) -> dict:
    """
    Book an appointment for a patient.
    Checks that the slot is still available before inserting.
    Returns success confirmation or an error if the slot was just taken.
    """
    if doctor_id not in DOCTORS:
        return {"error": f"Unknown doctor_id '{doctor_id}'."}

    doctor = DOCTORS[doctor_id]
    conn = get_connection()
    cursor = conn.cursor()

    # Check if this slot is already booked (race-condition-safe check before insert)
    cursor.execute(
        "SELECT id FROM appointments WHERE doctor_id = ? AND slot = ? AND status = 'confirmed'",
        (doctor_id, slot),
    )
    if cursor.fetchone():
        conn.close()
        return {
            "success": False,
            "error": f"Slot '{slot}' with {doctor['name']} was just taken. Please choose another slot.",
        }

    # All clear — insert the appointment
    try:
        cursor.execute(
            """
            INSERT INTO appointments (patient_id, doctor_id, doctor_name, slot, reason)
            VALUES (?, ?, ?, ?, ?)
            """,
            (patient_id, doctor_id, doctor["name"], slot, reason),
        )
        conn.commit()
        return {
            "success": True,
            "appointment_id": cursor.lastrowid,
            "doctor_name": doctor["name"],
            "specialty": doctor["specialty"],
            "slot": slot,
            "reason": reason,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

    finally:
        conn.close()