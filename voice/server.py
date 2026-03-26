import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from voice.context import get_chat_context
from voice.realtime import bridge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/voice/{thread_id}")
async def voice_endpoint(websocket: WebSocket, thread_id: str):
    await websocket.accept()
    logger.info(f"Voice session started for thread: {thread_id}")

    context = get_chat_context(thread_id)
    logger.info(f"Loaded context ({len(context)} chars)")

    try:
        await bridge(websocket, thread_id, context)
    except WebSocketDisconnect:
        logger.info("Browser disconnected cleanly")
    except Exception as e:
        logger.error(f"Bridge error: {e}", exc_info=True)