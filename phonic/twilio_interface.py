import asyncio
import base64
import json
import numpy as np
import queue
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
        self.output_dtype = np.uint8

        # Input / Output threads and loops
        self.main_loop = asyncio.get_event_loop()
        self.twilio_websocket: WebSocket | None = None
        self.twilio_stream_sid = None
        self.playback_queue: queue.Queue = queue.Queue()
        self.output_msg_thread = threading.Thread(
            target=asyncio.run_coroutine_threadsafe,
            args=(self._start_output_stream(), self.main_loop),
        )
        self.output_audio_thread = threading.Thread(
            target=asyncio.run,
            args=(self._start_audio_stream(),),
        )

        self.output_msg_thread.daemon = True
        self.output_audio_thread.daemon = True

        self.output_msg_thread.start()
        self.output_audio_thread.start()

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
        Receive messages from Phonic websocket, adds them to a playback queue
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

                twilio_message = {
                    "event": "media",
                    "streamSid": self.twilio_stream_sid,
                    "media": {"payload": audio},
                }
                self.playback_queue.put(twilio_message)
            elif message_type == "audio_finished":
                logger.info(f"Assistant: {text_buffer}")
                text_buffer = ""
            elif message_type == "input_text":
                logger.info(f"You: {message['text']}")
            elif message_type == "interrupted_response":
                # TODO: also stop the chunk that it's playing as well?
                with self.playback_queue.mutex:
                    self.playback_queue.queue.clear()
                logger.info("Response interrupted")
            else:
                logger.info(f"Received unknown message: {message}")

    async def _start_audio_stream(self):
        """
        Takes from the playback queue and sends them to Twilio websocket
        """
        while True:
            try:
                twilio_message = self.playback_queue.get()
                audio_duration = len(
                    np.frombuffer(
                        base64.b64decode(twilio_message["media"]["payload"]),
                        dtype=self.output_dtype,
                    )
                )
                logger.debug(f"self.playback_queue got {twilio_message=}")
                twilio_send = asyncio.run_coroutine_threadsafe(
                    self.twilio_websocket.send_json(twilio_message), self.main_loop
                )
                twilio_send.result()  # ensure no race conditions
                logger.debug(f"sent to {self.twilio_websocket=}")
                logger.debug(f"{self.playback_queue.qsize()=}")
                await asyncio.sleep(audio_duration / self.sample_rate)
                logger.debug(f"slept for {audio_duration / self.sample_rate=}")
            except Exception as e:
                logger.error(e)
                raise
