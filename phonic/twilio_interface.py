import asyncio
import base64
import json
import numpy as np
import os
import threading
import traceback
from fastapi import WebSocket
from loguru import logger

from phonic.client import PhonicAsyncWebsocketClient, PhonicSTSClient, get_voices


class TwilioInterface:
    """Links between Phonic and Twilio"""

    def __init__(
        self,
        client: PhonicAsyncWebsocketClient,
        output_voice: str,
        sample_rate: int = 44100,
    ):
        self.client = client
        self.output_voice = output_voice
        self.sample_rate = sample_rate
        self.channels = 1
        self.dtype = np.int16

        self.twilio_websocket: WebSocket | None = None
        self.twilio_stream_sid = None
        self.output_thread = threading.Thread(target=self._start_output_stream)
        self.output_thread.start()

    async def input_callback(self, message: str):
        """Process incoming WebSocket messages"""
        try:
            data = json.loads(message)
        except json.JSONDecodeError as e:
            logger.info(f"Received error {e} decoding json")
            logger.info(f"The message was {message}")
            return

        if data["event"] == "connected":
            logger.info("Twilio: Connected event received")

        if data["event"] == "start":
            logger.info("Twilio: Start event received")

        if data["event"] == "media":
            if not self.twilio_stream_sid:
                self.twilio_stream_sid = data["streamSid"]

            if data.get("media", {}).get("track") == "inbound":
                audio_bytes = base64.b64decode(data["media"]["payload"])
                audio_np = np.frombuffer(audio_bytes, dtype=self.dtype)

                # Send to PhonicAsyncWebsocketClient
                self.client.send_audio(audio_np)

    async def _start_output_stream(self):
        """
        Receive messages from Phonic websocket, sends them to Twilio websocket
        """
        sts_stream = self.client.sts(
            input_format="pcm_44100",
            output_format="pcm_44100",
            system_prompt="You are a helpful voice assistant. Respond conversationally.",
            welcome_message="Hello! I'm your voice assistant. How can I help you today?",
            voice_id=self.output_voice,
        )

        logger.info(f"Starting STS conversation with voice {self.output_voice}...")

        # Process messages from STS
        async for message in sts_stream:
            message_type = message.get("type")
            if message_type == "audio_chunk":
                logger.info(f"Received audio chunk: {message['text']}")
                audio = message["audio"]
                if text := message.get("text"):
                    logger.info(f"Assistant: {text}")

                twilio_message = {
                    "event": "media",
                    "streamSid": self.stream_sid,
                    "media": {"payload": audio},
                }
                await self.twilio_websocket.send_json(twilio_message)
            elif message_type == "input_text":
                logger.info(f"You: {message['text']}")
            else:
                logger.info(f"Received unknown message: {message}")


# Modal app
# TODO: create modal app here


@app.websocket("/streams")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for media streaming"""
    STS_URI = "wss://api.phonic.co/v1/sts/ws"
    API_KEY = os.environ["PHONIC_API_KEY"]
    SAMPLE_RATE = 44100

    voices = get_voices(API_KEY)
    voice_ids = [voice["id"] for voice in voices]
    logger.info(f"Available voices: {voice_ids}")
    voice_selected = "katherine"

    try:
        async with PhonicSTSClient(STS_URI, API_KEY) as client:
            await websocket.accept()
            twilio_interface = TwilioInterface(
                client=client,
                output_voice=voice_selected,
                sample_rate=SAMPLE_RATE,
            )
            twilio_interface.twilio_websocket = websocket

            while True:
                message = await websocket.receive_text()
                await twilio_interface.input_callback(message)
    except Exception as e:
        logger.info(f"WebSocket error: {e}")
        logger.info(traceback.format_exc())


# TODO: continue here


# Route for Twilio to handle incoming calls
@app.post("/twiml")
async def serve_twiml():
    # Construct the file path to the TwiML template
    file_path = Path(os.path.dirname(__file__)) / "templates" / "streams.xml"

    # Return a FileResponse, which handles setting content type and length automatically
    return FileResponse(path=file_path, media_type="text/xml")
