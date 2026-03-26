# Kyron Medical — AI Patient Appointment Assistant

An AI-powered patient appointment assistant built for Kyron Medical. Patients interact with a conversational AI that collects their information, matches them to the right doctor, books an appointment, sends confirmation via email and SMS, and can seamlessly switch to a live browser-based voice call — all while retaining full context.

---

## Features

- **Conversational intake** — AI collects patient name, DOB, phone, email, and reason for visit through natural conversation
- **Semantic doctor matching** — LLM matches the patient's symptoms to the right specialist automatically
- **Real-time availability** — shows only genuinely available slots with double-booking prevention at both the application and database level
- **Appointment booking** — confirms details with the patient before writing to the database
- **Email confirmation** — sends a formatted confirmation email via Gmail after booking
- **SMS confirmation** — sends a text message to the patient's phone via Twilio
- **Browser-based voice call** — patient can switch from chat to voice at any point; the voice AI loads the full chat history and continues the conversation naturally
- **Conversation history** — all past conversations are saved and accessible from the sidebar
- **Production deployment** — hosted on AWS EC2 behind Nginx with HTTPS

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI Agent Framework | LangGraph |
| Language Model | GPT-4o (OpenAI) |
| Database | SQLite |
| Frontend | Streamlit |
| Email | yagmail (Gmail) |
| SMS | Twilio |
| Voice AI | OpenAI Realtime API |
| Voice Server | FastAPI + WebSockets |
| Deployment | AWS EC2, Nginx, systemd |

---

## Project Structure

```
kyron/
│
├── app.py                        # Streamlit frontend — chat UI, streaming, voice button
├── requirements.txt
├── .env                          # API keys (not in repo)
│
├── backend/
│   ├── graph.py                  # LangGraph graph — nodes, edges, checkpointer
│   ├── nodes.py                  # chat_node — formats prompt, calls LLM with tools
│   ├── prompts.py                # System prompt with 6-step workflow
│   └── state.py                  # ChatState TypedDict
│
├── data/
│   ├── database.py               # SQLite setup — patients + appointments tables
│   └── doctors.py                # Hardcoded doctors, specialties, available slots
│
├── tools/
│   ├── patient_tools.py          # save_patient_info, get_patient_by_email
│   ├── appointment_tools.py      # check_availability, book_appointment
│   ├── email_tools.py            # send_confirmation_email via yagmail
│   └── sms_tools.py              # send_confirmation_sms via Twilio
│
└── voice/
    ├── server.py                 # FastAPI WebSocket endpoint
    ├── realtime.py               # OpenAI Realtime API bridge
    ├── context.py                # Loads web chat history for voice session
    └── voice_component.html      # Browser mic capture + audio playback (JS)
```

---

## Doctors (Hardcoded for Demo)

| Doctor | Specialty | Treats |
|---|---|---|
| Dr. Sarah Chen | Cardiology | Heart, chest, blood pressure |
| Dr. Marcus Webb | Orthopedics | Bones, joints, knee, back, shoulder |
| Dr. Priya Nair | Dermatology | Skin, rash, acne, eczema |
| Dr. James Okafor | Neurology | Headaches, migraines, nerves, brain |

Slots are available across April – May 2025. The LLM semantically matches the patient's reason to the correct doctor — no keyword lists needed.

---

## How the Agent Works

```
Patient message
      ↓
chat_node  →  LLM reads full conversation history + system prompt
      ↓
tools_condition checks: did the LLM request a tool?
      ↓ YES                          ↓ NO
  ToolNode runs the tool          END → reply sent to patient
      ↓
  result returned to LLM
      ↓
  back to chat_node
```

The LLM follows a six-step workflow defined in the system prompt:

1. **Intake** — collect name, DOB, phone, email, reason
2. **Save** — call `save_patient_info()` to persist to SQLite
3. **Match** — pick the right doctor based on specialty
4. **Availability** — call `check_availability()`, show open slots
5. **Book** — call `book_appointment()` after patient confirms
6. **Notify** — call `send_confirmation_email()` and `send_confirmation_sms()`

---

## Double-Booking Prevention

Two layers of protection:

1. **Application layer** — `book_appointment` does an explicit `SELECT` before every `INSERT`. If the slot was taken between the patient seeing it and confirming, a clean error is returned and the LLM offers alternatives.

2. **Database layer** — the `appointments` table has a `UNIQUE(doctor_id, slot)` constraint. Even in a race condition the database rejects the second insert.

---

## Voice Call Architecture

```
Browser (mic)
    ↓  PCM16 audio bytes over WebSocket
FastAPI server  ←→  loads thread chat history from SQLite
    ↓  PCM16 audio + chat context as system prompt
OpenAI Realtime API
    ↓  PCM16 response audio + transcript
FastAPI server
    ↓  JSON over WebSocket
Browser (plays audio)
```

The voice AI receives the full web chat history as part of its system prompt before the first word is spoken, so it continues the conversation without the patient repeating themselves.

---

## Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/kyron-medical-assesment.git
cd kyron-medical-assesment
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create your `.env` file
```dotenv
OPENAI_API_KEY=sk-...

GMAIL_ADDRESS=you@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1xxxxxxxxxx
```

**Getting Gmail App Password:** Google Account → Security → 2-Step Verification → App Passwords → Generate

**Getting Twilio credentials:** [console.twilio.com](https://console.twilio.com) → Account SID and Auth Token on dashboard → Phone Numbers for a Twilio number

### 5. Run locally

```bash
# Terminal 1 — Streamlit chat
streamlit run app.py

# Terminal 2 — FastAPI voice server
uvicorn voice.server:app --port 8765
```

Open [http://localhost:8501](http://localhost:8501)

> **Note:** The voice call requires HTTPS for microphone access in production. Locally it works over `ws://localhost` without HTTPS.

---

## AWS EC2 Deployment

### Instance setup
- **AMI:** Ubuntu 24.04 LTS
- **Instance type:** t3.small
- **Security group ports:** 22 (SSH), 80 (HTTP), 443 (HTTPS), 8501 (Streamlit), 8765 (FastAPI)
- **Storage:** 20 GiB

### Server setup on EC2
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-venv python3-pip nginx -y

git clone https://github.com/yourusername/kyron-medical-assesment.git
cd kyron-medical-assesment
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Copy `.env` from local machine:
```bash
# Run on your local machine
scp -i kyron-key.pem .env ubuntu@YOUR_EC2_IP:~/kyron-medical-assesment/.env
```

### Self-signed SSL certificate
```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/kyron.key \
  -out /etc/ssl/certs/kyron.crt \
  -subj "/CN=YOUR_EC2_IP"
```

### Nginx config (`/etc/nginx/sites-available/kyron`)
```nginx
server {
    listen 80;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    ssl_certificate     /etc/ssl/certs/kyron.crt;
    ssl_certificate_key /etc/ssl/private/kyron.key;

    location / {
        proxy_pass         http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "upgrade";
        proxy_set_header   Host $host;
        proxy_read_timeout 86400;
    }

    location /voice/ {
        proxy_pass         http://127.0.0.1:8765;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "upgrade";
        proxy_set_header   Host $host;
        proxy_read_timeout 86400;
    }
}
```

### systemd services

`/etc/systemd/system/kyron-chat.service`:
```ini
[Unit]
Description=Kyron Streamlit App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/kyron-medical-assesment
Environment="PATH=/home/ubuntu/kyron-medical-assesment/env/bin"
ExecStart=/home/ubuntu/kyron-medical-assesment/env/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1
Restart=always

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/kyron-voice.service`:
```ini
[Unit]
Description=Kyron Voice FastAPI Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/kyron-medical-assesment
Environment="PATH=/home/ubuntu/kyron-medical-assesment/env/bin"
ExecStart=/home/ubuntu/kyron-medical-assesment/env/bin/uvicorn voice.server:app --host 127.0.0.1 --port 8765
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable kyron-chat kyron-voice
sudo systemctl start kyron-chat kyron-voice
```

---

## Environment Variables Reference

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key (GPT-4o + Realtime API) |
| `GMAIL_ADDRESS` | Gmail address to send confirmations from |
| `GMAIL_APP_PASSWORD` | Gmail App Password (not your account password) |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token |
| `TWILIO_FROM_NUMBER` | Your Twilio phone number (e.g. +15005550006) |

---

## What's Next

- Add a real domain with Let's Encrypt for a trusted SSL certificate
- Prescription refill status workflow
- Office address and hours lookup
- Model comparison — swap GPT-4o for Claude or Gemini (one line change in `backend/nodes.py`)
- Patient authentication so returning patients are recognized automatically