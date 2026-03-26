import sqlite3

DB_PATH = "chatbot.db"

def get_connection():
    """Return a shared SQLite connection (check_same_thread=False for Streamlit)."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    """Create tables if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Stores patient intake info collected during chat
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name  TEXT NOT NULL,
            last_name   TEXT NOT NULL,
            dob         TEXT NOT NULL,
            phone       TEXT NOT NULL,
            email       TEXT NOT NULL UNIQUE,
            reason      TEXT NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Stores confirmed appointments; slot is checked here before booking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id  INTEGER NOT NULL,
            doctor_id   TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            slot        TEXT NOT NULL,           -- e.g. "2025-04-15 10:00 AM"
            reason      TEXT NOT NULL,
            status      TEXT DEFAULT 'confirmed',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            UNIQUE (doctor_id, slot)             -- prevents double-booking same slot
        )
    """)

    conn.commit()
    conn.close()