import asyncio
import base64
import json
import numpy as np
import threading
from fastapi import WebSocket
from loguru import logger

from phonic.client import PhonicSTSClient


class TwilioInterface:
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
        self.sample_rate = 8000
        self.input_dtype = np.uint8
        self.input_buffer: list[np.ndarray] = []
        self.input_buffer_len = 0.0

        # Input / Output threads and loops
        self.main_loop = asyncio.get_event_loop()
        self.twilio_websocket: WebSocket | None = None
        self.twilio_stream_sid = None
        self.output_thread = threading.Thread(
            target=asyncio.run_coroutine_threadsafe,
            args=(self._start_output_stream(), self.main_loop),
        )
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
                audio_np = np.frombuffer(audio_bytes, dtype=self.input_dtype)

                # Twilio chunks are too short (20ms);
                # accumulate to >=250ms then send to Phonic API
                self.input_buffer.append(audio_np)
                self.input_buffer_len += len(audio_np) / self.sample_rate

        if self.input_buffer_len >= 0.250:
            concat_audio_np = np.concatenate(self.input_buffer)
            self.input_buffer = []
            self.input_buffer_len = 0.0

            # Send to PhonicAsyncWebsocketClient
            asyncio.run_coroutine_threadsafe(
                self.client.send_audio(concat_audio_np), self.main_loop
            )

    async def _start_output_stream(self):
        """
        Receive messages from Phonic websocket, sends them to Twilio websocket
        """
        text_buffer = ""
        async for message in self.sts_stream:
            message_type = message.get("type")
            if message_type == "audio_chunk":
                audio = message["audio"]
                if text := message.get("text"):
                    text_buffer += text
                    if any(punc in text_buffer for punc in ".!?"):
                        logger.info(f"Assistant: {text_buffer}")
                        text_buffer = ""
                    # TODO (arun): should be careful about any leftovers

                twilio_message = {
                    "event": "media",
                    "streamSid": self.twilio_stream_sid,
                    "media": {"payload": audio},
                }
                await self.twilio_websocket.send_json(twilio_message)
            elif message_type == "input_text":
                logger.info(f"You: {message['text']}")
            else:
                logger.info(f"Received unknown message: {message}")
