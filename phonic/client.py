import base64
import json
from typing import Generator

import numpy as np
from websockets.sync.client import connect


class PhonicSyncWebSocketClient:
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
