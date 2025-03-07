import modal
import os
import traceback
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from loguru import logger
from pathlib import Path

from phonic.client import PhonicSTSClient, get_voices
from phonic.twilio_interface import TwilioInterface

app = modal.App(
    "twilio-phonic-sdk",
    image=modal.Image.debian_slim()
    .pip_install(["loguru", "numpy", "requests", "websockets"])
    .add_local_python_source("phonic")
    .add_local_dir("templates", "/root/templates"),
)


@app.function(
    keep_warm=1,
    container_idle_timeout=20 * 60,
    timeout=30 * 60,
    secrets=[
        modal.Secret.from_name("phonic-api-key"),
    ],
)
@modal.asgi_app()
def twilio_app():
    fastapi_app = FastAPI()

    # Route for Twilio to handle incoming calls
    @fastapi_app.post("/twiml")
    async def serve_twiml():
        # Use TwiML template
        file_path = Path("/") / "root" / "templates" / "twilio.xml"
        return FileResponse(path=file_path, media_type="text/xml")

    @fastapi_app.websocket("/sts")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for media streaming"""
        STS_URI = "wss://api.phonic.co/v1/sts/ws"
        API_KEY = os.environ["PHONIC_API_KEY"]

        voices = get_voices(API_KEY)
        voice_ids = [voice["id"] for voice in voices]
        logger.info(f"Available voices: {voice_ids}")
        voice_selected = "katherine"

        try:
            async with PhonicSTSClient(STS_URI, API_KEY) as client:
                await websocket.accept()
                twilio_interface = TwilioInterface(
                    client=client,
                    system_prompt=(
                        "You are a helpful voice assistant. "
                        "Respond conversationally."
                    ),
                    welcome_message=(
                        f"Hello! I'm {voice_selected.title()}, "
                        "your voice assistant. "
                        "How can I help you today?"
                    ),
                    output_voice=voice_selected,
                )
                await twilio_interface.start()
                twilio_interface.twilio_websocket = websocket

                while True:
                    message = await websocket.receive_text()
                    await twilio_interface._twilio_input_callback(message)
        except Exception as e:
            logger.info(f"WebSocket error: {e}")
            logger.info(traceback.format_exc())

    return fastapi_app
