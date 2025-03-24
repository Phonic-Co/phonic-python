import asyncio
import base64
import json
import numpy as np
import threading
from fastapi import WebSocket
from loguru import logger

from phonic.audio_interface import ContinuousAudioInterface
from phonic.client import PhonicSTSClient


class TwilioInterface(ContinuousAudioInterface):
    """Links between Phonic and Twilio"""

    def __init__(
        self,
        client: PhonicSTSClient,
        system_prompt: str,
        welcome_message: str,
        output_voice: str,
    ):
        self.client = client
        self.sts_stream = self.client.sts(
            input_format="mulaw_8000",
            output_format="mulaw_8000",
            system_prompt=system_prompt,
            welcome_message=welcome_message,
            voice_id=output_voice,
        )

        logger.info(f"Starting STS conversation with {output_voice}...")

        # Input / Output constants and buffer
        # Twilio always uses mulaw, 8000 Hz 8-bit PCM
        self.sample_rate = 8000
        self.input_dtype = np.uint8

        # Input / Output threads and loops
        self.main_loop = asyncio.get_event_loop()
        self.twilio_websocket: WebSocket | None = None
        self.twilio_stream_sid = None

    def _input_callback(self, indata, frames, time, status):
        # unused, use _twilio_input_callback instead
        return

    async def _twilio_input_callback(self, message: str):
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
                audio_np = np.frombuffer(audio_bytes, dtype=self.input_dtype)

                asyncio.run_coroutine_threadsafe(
                    self.client.send_audio(audio_np), self.main_loop
                )

    def _start_input_stream(self):
        # unused, handled by Twilio
        return

    def _output_callback(self, indata, frames, time, status):
        # unused, see _start_output_stream
        return

    async def _start_output_stream(self):
        """
        Receive messages from Phonic websocket, sends them to Twilio websocket
        """
        text_buffer = ""
        async for message in self.sts_stream:
            message_type = message.get("type")
            match message_type:
                case "audio_chunk":
                    audio = message["audio"]
                    if text := message.get("text"):
                        text_buffer += text
                        if any(punc in text_buffer for punc in ".!?"):
                            logger.info(f"Assistant: {text_buffer}")
                            text_buffer = ""

                    twilio_message = {
                        "event": "media",
                        "streamSid": self.twilio_stream_sid,
                        "media": {"payload": audio},
                    }
                    await self.twilio_websocket.send_json(twilio_message)
                case "audio_finished":
                    if len(text_buffer) > 0:
                        logger.info(f"Assistant: {text_buffer}")
                        text_buffer = ""
                case "input_text":
                    logger.info(f"You: {message['text']}")
                case "interrupted_response":
                    await self.interrupt_playback()
                    logger.info("Response interrupted")
                case _:
                    logger.info(f"Received unknown message: {message}")

    async def start(self):
        self.output_thread = threading.Thread(
            target=asyncio.run_coroutine_threadsafe,
            args=(self._start_output_stream(), self.main_loop),
        )
        self.output_thread.start()

    async def stop(self):
        # unused, hanging up stops
        return

    async def add_audio_to_playback(self, audio_encoded):
        # unused, sends audio through Twilio websocket
        return

    async def interrupt_playback(self):
        twilio_message = {
            "event": "clear",
            "streamSid": self.twilio_stream_sid,
        }
        await self.twilio_websocket.send_json(twilio_message)
