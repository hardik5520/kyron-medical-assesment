"""
Four doctors with their specialty and available slots (April–May 2025).
The LLM semantically matches the patient's reason to the right doctor
based on specialty — no manual keyword matching needed.
Slot format: "YYYY-MM-DD HH:MM AM/PM"
"""

DOCTORS = {
    "dr_chen": {
        "name": "Dr. Sarah Chen",
        "specialty": "Cardiology",
        "slots": [
            "2025-04-14 09:00 AM",
            "2025-04-14 11:00 AM",
            "2025-04-16 02:00 PM",
            "2025-04-21 10:00 AM",
            "2025-04-23 03:00 PM",
            "2025-04-28 09:00 AM",
            "2025-05-02 11:00 AM",
            "2025-05-07 02:00 PM",
            "2025-05-12 09:00 AM",
        ],
    },
    "dr_webb": {
        "name": "Dr. Marcus Webb",
        "specialty": "Orthopedics",
        "slots": [
            "2025-04-15 08:00 AM",
            "2025-04-15 01:00 PM",
            "2025-04-17 10:00 AM",
            "2025-04-22 09:00 AM",
            "2025-04-24 02:00 PM",
            "2025-04-29 11:00 AM",
            "2025-05-01 08:00 AM",
            "2025-05-06 10:00 AM",
            "2025-05-13 01:00 PM",
        ],
    },
    "dr_nair": {
        "name": "Dr. Priya Nair",
        "specialty": "Dermatology",
        "slots": [
            "2025-04-14 10:00 AM",
            "2025-04-16 09:00 AM",
            "2025-04-18 03:00 PM",
            "2025-04-23 11:00 AM",
            "2025-04-25 08:00 AM",
            "2025-04-30 02:00 PM",
            "2025-05-05 10:00 AM",
            "2025-05-08 09:00 AM",
            "2025-05-14 11:00 AM",
        ],
    },
    "dr_okafor": {
        "name": "Dr. James Okafor",
        "specialty": "Neurology",
        "slots": [
            "2025-04-15 11:00 AM",
            "2025-04-17 02:00 PM",
            "2025-04-22 08:00 AM",
            "2025-04-24 10:00 AM",
            "2025-04-29 03:00 PM",
            "2025-05-02 09:00 AM",
            "2025-05-09 11:00 AM",
            "2025-05-13 02:00 PM",
            "2025-05-15 10:00 AM",
        ],
    },
}