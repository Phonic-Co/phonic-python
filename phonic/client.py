import asyncio
import base64
import json
from typing import Any, AsyncIterator, Generator

import numpy as np
import requests
import websockets
from loguru import logger
from typing_extensions import Literal
from websockets.sync.client import connect


class PhonicSyncWebsocketClient:
    def __init__(
        self,
        url: str,
        api_key: str,
        query_params: dict | None = None,
        additional_headers: dict | None = None,
    ):
        """
        Initialize a synchronous WebSocket client for the Phonic TTS API.

        Args:
            url (str): The URL to connect to.
            api_key (str): The API key to use for authentication.
            query_params (dict, optional): Additional query parameters to include in the URL. Defaults to None.
            additional_headers (dict, optional): Additional headers to include in the request. Defaults to None.
        """
        self.api_key = api_key
        self._websocket = None

        if query_params is not None:
            query_string = "&".join(f"{k}={v}" for k, v in query_params.items())
            self.url = f"{url}?{query_string}"
        else:
            self.url = url

        self.additional_headers = additional_headers

    def connect(self):
        self._websocket = connect(
            self.url,
            additional_headers={
                "Authorization": f"Bearer {self.api_key}",
                **self.additional_headers,
            },
        )
        return self

    def close(self):
        self._websocket.close()

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class PhonicAsyncWebsocketClient:
    def __init__(self, uri: str, api_key: str) -> None:
        self.uri = uri
        self.api_key = api_key
        self._websocket: websockets.WebSocketClientProtocol | None = None
        self._send_queue = asyncio.Queue()
        self._is_running = False
        self._tasks = []

    async def __aenter__(self) -> "PhonicAsyncWebsocketClient":
        self._websocket = await websockets.connect(
            self.uri,
            additional_headers={"Authorization": f"Bearer {self.api_key}"},
            max_size=5 * 1024 * 1024,
        )
        self._is_running = True
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore[no-untyped-def]
        self._is_running = False
        for task in self._tasks:
            if not task.done():
                task.cancel()

        assert self._websocket is not None
        await self._websocket.close()
        self._websocket = None

    async def start_bidirectional_stream(self) -> AsyncIterator[dict[str, Any]]:
        if not self._is_running or self._websocket is None:
            raise RuntimeError("WebSocket connection not established")

        # Sender
        sender_task = asyncio.create_task(self._sender_loop())
        self._tasks.append(sender_task)

        # Receiver
        async for message in self._receiver_loop():
            yield message

    async def _sender_loop(self) -> None:
        """Task that continuously sends queued messages"""
        assert self._websocket is not None

        try:
            while self._is_running:
                message = await self._send_queue.get()
                await self._websocket.send(json.dumps(message))
                self._send_queue.task_done()
        except asyncio.CancelledError:
            logger.info("Sender task cancelled")
        except Exception as e:
            logger.error(f"Error in sender loop: {e}")
            self._is_running = False
            raise

    async def _receiver_loop(self) -> AsyncIterator[dict[str, Any]]:
        """Generator that continuously receives and yields messages"""
        assert self._websocket is not None

        try:
            async for raw_message in self._websocket:
                if not self._is_running:
                    break

                message = json.loads(raw_message)
                type = message.get("type")

                if type == "error":
                    raise RuntimeError(message)
                else:
                    yield message
        except asyncio.CancelledError:
            logger.info("Receiver task cancelled")
        except Exception as e:
            logger.error(f"Error in receiver loop: {e}")
            self._is_running = False
            raise


class PhonicTTSClient(PhonicSyncWebsocketClient):
    def generate_audio(
        self, text: str, speed: float = 1.0
    ) -> Generator[np.ndarray, None, None]:
        self._websocket.send(
            json.dumps(
                {
                    "type": "generate",
                    "text": text,
                    "speed": speed,
                }
            )
        )
        self._websocket.send(json.dumps({"type": "flush"}))

        for message in self._websocket:
            json_message = json.loads(message)
            type = json_message.get("type")

            if type == "config":
                pass
            elif type == "audio_chunk":
                audio_base64 = json_message["audio"]
                buffer = base64.b64decode(audio_base64)
                audio = np.frombuffer(buffer, dtype=np.int16)
                yield audio
            elif type == "flush_confirm":
                return
            elif type == "stop_confirm":
                return
            else:
                raise ValueError(f"Unknown message type: {type}")


class PhonicSTSClient(PhonicAsyncWebsocketClient):
    async def send_audio(self, audio: np.ndarray) -> None:
        if not self._is_running:
            raise RuntimeError("WebSocket connection not established")

        buffer = audio.astype(np.float32).tobytes()
        audio_base64 = base64.b64encode(buffer).decode("utf-8")

        message = {
            "type": "audio_chunk",
            "audio": audio_base64,
        }

        await self._send_queue.put(message)

    async def sts(
        self,
        input_format: Literal["pcm_44100", "mulaw_8000"] = "pcm_44100",
        output_format: Literal["pcm_44100", "mulaw_8000"] = "pcm_44100",
        system_prompt: (
            str | None
        ) = "You are a helpful assistant. Respond in 2-3 sentences.",
        output_audio_speed: float = 1.0,
        welcome_message: str = "",
        voice_id: str | None = "meredith",
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Args:
            input_format: input audio format
            output_format: output audio format
            system_prompt: system prompt for assistant
            output_audio_speed: output audio speed
            welcome_message: welcome message for assistant
            voice_id: voice id
        """
        if not self._is_running:
            raise RuntimeError("WebSocket connection not established")

        config_message = {
            "type": "config",
            "input_format": input_format,
            "output_format": output_format,
            "system_prompt": system_prompt,
            "output_audio_speed": output_audio_speed,
            "welcome_message": welcome_message,
            "voice_id": voice_id,
        }
        await self._websocket.send(json.dumps(config_message))

        async for message in self.start_bidirectional_stream():
            yield message


# Utilities


def get_voices(
    api_key: str,
    url: str = "https://api.phonic.co/v1/voices",
    model: str = "tahoe",
) -> list[dict[str, str]]:
    """
    Returns a list of available voices from the Phonic API.
    """
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"model": model}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return data["voices"]
    else:
        logger.error(f"Error: {response.status_code}")
        logger.error(response.text)
