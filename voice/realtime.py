import os
import json
import asyncio
import base64
import logging
import websockets
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
REALTIME_WS_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview"

VOICE_SYSTEM_PROMPT = """You are a warm, professional medical receptionist for Kyron Medical continuing 
a conversation that was started on the web chat. You already have context of what was discussed.

RULES:
- Always respond in English regardless of any other language in the context.
- Never provide medical advice or diagnoses.
- Be concise since this is a voice call — keep responses short and clear.
- If the patient asks anything medical (symptoms, treatments, medications), say:
  "I'm not able to advise on medical matters, but I can help with scheduling or general questions."
- You can help with: rescheduling appointments, office hours, directions, and general questions.

PRIOR CONVERSATION CONTEXT:
{context}
"""


async def bridge(browser_ws, thread_id: str, context: str):
    """
    Opens WebSocket to OpenAI Realtime API and bridges audio
    between browser and OpenAI until either side disconnects.
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set in .env")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1",
    }

    logger.info(f"Connecting to OpenAI Realtime API...")

    try:
        async with websockets.connect(REALTIME_WS_URL, additional_headers=headers) as openai_ws:
            logger.info("Connected to OpenAI Realtime API")

            # Configure session
            await openai_ws.send(json.dumps({
                "type": "session.update",
                "session": {
                    "modalities": ["audio", "text"],
                    "voice": "alloy",
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "input_audio_transcription": {"model": "whisper-1"},
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "silence_duration_ms": 600,
                    },
                    "instructions": VOICE_SYSTEM_PROMPT.format(context=context),
                }
            }))
            logger.info("Session configured, bridging audio...")

            # Run both directions concurrently
            await asyncio.gather(
                _browser_to_openai(browser_ws, openai_ws),
                _openai_to_browser(openai_ws, browser_ws),
            )

    except websockets.exceptions.InvalidStatusCode as e:
        logger.error(f"OpenAI rejected connection: {e.status_code} — check your OPENAI_API_KEY and model access")
        raise
    except Exception as e:
        logger.error(f"Bridge failed: {e}", exc_info=True)
        raise


async def _browser_to_openai(browser_ws, openai_ws):
    """Forward raw PCM16 audio bytes from browser → OpenAI."""
    try:
        async for message in browser_ws.iter_bytes():
            audio_b64 = base64.b64encode(message).decode("utf-8")
            await openai_ws.send(json.dumps({
                "type": "input_audio_buffer.append",
                "audio": audio_b64,
            }))
    except Exception as e:
        logger.info(f"Browser → OpenAI stream ended: {e}")


async def _openai_to_browser(openai_ws, browser_ws):
    """Forward audio deltas from OpenAI → browser."""
    try:
        async for raw in openai_ws:
            event      = json.loads(raw)
            event_type = event.get("type", "")

            logger.debug(f"OpenAI event: {event_type}")

            if event_type == "response.audio.delta":
                await browser_ws.send_json({
                    "type": "audio",
                    "audio": event["delta"],
                })

            elif event_type == "response.audio_transcript.delta":
                await browser_ws.send_json({
                    "type": "transcript",
                    "text": event.get("delta", ""),
                })

            elif event_type == "response.done":
                await browser_ws.send_json({"type": "response_done"})

            # Log any errors coming back from OpenAI
            elif event_type == "error":
                logger.error(f"OpenAI Realtime error: {event}")

    except Exception as e:
        logger.info(f"OpenAI → Browser stream ended: {e}")