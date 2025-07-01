import asyncio
import base64
import json
from typing import Any, AsyncIterator, Generator

import numpy as np
import requests
from loguru import logger
from typing_extensions import Literal
from websockets.exceptions import ConnectionClosedError
from websockets.asyncio.client import (
    ClientConnection,
    connect,
)
from urllib.parse import urlencode

DEFAULT_HTTP_TIMEOUT = 30
INSUFFICIENT_CAPACITY_AVAILABLE_ERROR_CODE = 4004

PhonicSTSTool = Literal["send_dtmf_tone", "end_conversation"]


class InsufficientCapacityError(Exception):
    def __init__(
        self,
        message="Insufficient capacity available.",
        code=INSUFFICIENT_CAPACITY_AVAILABLE_ERROR_CODE,
    ):
        super().__init__(message)
        self.code = code


class PhonicAsyncWebsocketClient:
    def __init__(
        self, uri: str, api_key: str, additional_headers: dict | None = None
    ) -> None:
        self.uri = uri
        self.api_key = api_key
        self._websocket: ClientConnection | None = None
        self._send_queue: asyncio.Queue = asyncio.Queue()
        self._is_running = False
        self._tasks: list[asyncio.Task] = []
        self.additional_headers = (
            additional_headers if additional_headers is not None else {}
        )

    def _is_4004(self, exception: Exception) -> bool:
        if (
            isinstance(exception, ConnectionClosedError)
            and exception.code == INSUFFICIENT_CAPACITY_AVAILABLE_ERROR_CODE
        ):
            return True
        else:
            return False

    async def __aenter__(self) -> "PhonicAsyncWebsocketClient":
        self._websocket = await connect(
            self.uri,
            additional_headers={
                "Authorization": f"Bearer {self.api_key}",
                **self.additional_headers,
            },
            max_size=5 * 1024 * 1024,
            open_timeout=20,  # 4004 takes up to 15 seconds
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

    async def start_bidirectional_stream(
        self,
    ) -> AsyncIterator[dict[str, Any]]:
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
                message_type = message.get("type")

                if message_type == "error":
                    raise RuntimeError(message)
                else:
                    yield message
        except asyncio.CancelledError:
            logger.info("Receiver task cancelled")
        except Exception as e:
            if self._is_4004(e):
                logger.error("Insufficient capacity available")
                raise InsufficientCapacityError()
            logger.error(f"Error in receiver loop: {e}")
            raise


class PhonicSTSClient(PhonicAsyncWebsocketClient):
    def __init__(
        self,
        uri: str,
        api_key: str,
        additional_headers: dict | None = None,
        downstreamWebSocketUrl: str | None = None,
    ) -> None:
        if downstreamWebSocketUrl is not None:
            query_params = {"downstream_websocket_url": downstreamWebSocketUrl}
            query_string = urlencode(query_params)
            uri = f"{uri}?{query_string}"
        super().__init__(uri, api_key, additional_headers)
        self.input_format: Literal["pcm_44100", "mulaw_8000"] | None = None

    async def send_audio(self, audio: np.ndarray) -> None:
        if not self._is_running:
            raise RuntimeError("WebSocket connection not established")

        if self.input_format == "pcm_44100":
            buffer = audio.astype(np.int16).tobytes()
        else:
            buffer = audio.astype(np.uint8).tobytes()
        audio_base64 = base64.b64encode(buffer).decode("utf-8")

        message = {
            "type": "audio_chunk",
            "audio": audio_base64,
        }

        await self._send_queue.put(message)

    async def update_system_prompt(self, system_prompt: str) -> None:
        if not self._is_running:
            raise RuntimeError("WebSocket connection not established")

        message = {
            "type": "update_system_prompt",
            "system_prompt": system_prompt,
        }

        await self._send_queue.put(message)

    async def set_external_id(self, external_id: str) -> None:
        if not self._is_running:
            raise RuntimeError("WebSocket connection not established")

        message = {
            "type": "set_external_id",
            "external_id": external_id,
        }
        await self._send_queue.put(message)

    async def sts(
        self,
        agent: str | None = None,
        project: str = "main",
        model: str | None = None,
        input_format: Literal["pcm_44100", "mulaw_8000"] = "pcm_44100",
        output_format: Literal["pcm_44100", "mulaw_8000"] = "pcm_44100",
        system_prompt: (
            str | None
        ) = "You are a helpful assistant. Respond in 2-3 sentences.",
        output_audio_speed: float = 1.0,
        welcome_message: str | None = "",
        voice_id: str | None = "meredith",
        enable_silent_audio_fallback: bool = False,
        vad_prebuffer_duration_ms: int | None = None,
        vad_min_speech_duration_ms: int | None = None,
        vad_min_silence_duration_ms: int | None = None,
        vad_threshold: float | None = None,
        enable_documents_rag: bool | None = None,
        enable_transcripts_rag: bool | None = None,
        no_input_poke_sec: int | None = None,
        no_input_poke_text: str | None = None,
        no_input_end_conversation_sec: int | None = None,
        boosted_keywords: list[str] | None = None,
        tools: list[PhonicSTSTool] | None = None,
        experimental_params: dict[str, Any] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Args:
            agent: agent identifier (optional)
            project: project name (optional, defaults to "main")
            model: STS model to use (optional)
            input_format: input audio format (defaults to "pcm_44100")
            output_format: output audio format (defaults to "pcm_44100")
            system_prompt: system prompt for assistant
                (defaults to "You are a helpful assistant. Respond in 2-3 sentences.")
            output_audio_speed: output audio speed (defaults to 1.0)
            welcome_message: welcome message for assistant (defaults to "")
            voice_id: voice id (defaults to "meredith")
            enable_silent_audio_fallback: enable silent audio fallback (defaults to False)
            vad_prebuffer_duration_ms: VAD prebuffer duration in milliseconds (optional)
            vad_min_speech_duration_ms: VAD minimum speech duration in milliseconds (optional)
            vad_min_silence_duration_ms: VAD minimum silence duration in milliseconds (optional)
            vad_threshold: VAD threshold (optional)
            enable_documents_rag: enable documents RAG (optional)
            enable_transcripts_rag: enable transcripts RAG (optional)
            no_input_poke_sec: seconds before no input poke (optional)
            no_input_poke_text: text for no input poke (optional)
            no_input_end_conversation_sec: seconds before ending conversation on no input (optional)
            boosted_keywords: list of keywords to boost in speech recognition (optional)
            tools: list of tools to enable (optional)
            experimental_params: experimental parameters (optional)
        """
        assert self._websocket is not None

        if not self._is_running:
            raise RuntimeError("WebSocket connection not established")

        self.input_format = input_format

        # Build config message with all parameters, then filter out None values
        config_message = {
            "type": "config",
            "project": project,
            "input_format": input_format,
            "output_format": output_format,
            "system_prompt": system_prompt,
            "output_audio_speed": output_audio_speed,
            "welcome_message": welcome_message,
            "voice_id": voice_id,
            "enable_silent_audio_fallback": enable_silent_audio_fallback,
            "agent": agent,
            "model": model,
            "vad_prebuffer_duration_ms": vad_prebuffer_duration_ms,
            "vad_min_speech_duration_ms": vad_min_speech_duration_ms,
            "vad_min_silence_duration_ms": vad_min_silence_duration_ms,
            "vad_threshold": vad_threshold,
            "enable_documents_rag": enable_documents_rag,
            "enable_transcripts_rag": enable_transcripts_rag,
            "no_input_poke_sec": no_input_poke_sec,
            "no_input_poke_text": no_input_poke_text,
            "no_input_end_conversation_sec": no_input_end_conversation_sec,
            "boosted_keywords": boosted_keywords,
            "tools": tools,
            "experimental_params": experimental_params,
        }

        config_message = {k: v for k, v in config_message.items() if v is not None}
        await self._websocket.send(json.dumps(config_message))

        async for message in self.start_bidirectional_stream():
            yield message


class PhonicHTTPClient:
    """Base HTTP client for Phonic API requests."""

    def __init__(
        self,
        api_key: str,
        additional_headers: dict | None = None,
        base_url: str = "https://api.phonic.co/v1",
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.additional_headers = additional_headers or {}

    def get(self, path: str, params: dict | None = None) -> dict:
        """Make a GET request to the Phonic API."""
        headers = {"Authorization": f"Bearer {self.api_key}", **self.additional_headers}

        response = requests.get(
            f"{self.base_url}{path}",
            headers=headers,
            params=params,
            timeout=DEFAULT_HTTP_TIMEOUT,
        )

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error: {response.status_code}")
            logger.error(response.text)
            raise ValueError(
                f"Error in GET request: {response.status_code} {response.text}"
            )

    def post(self, path: str, data: dict | None = None) -> dict:
        """Make a POST request to the Phonic API."""
        headers = {"Authorization": f"Bearer {self.api_key}", **self.additional_headers}

        data = data or {}

        response = requests.post(
            f"{self.base_url}{path}",
            headers=headers,
            json=data,
            timeout=DEFAULT_HTTP_TIMEOUT,
        )

        if response.status_code in (200, 201):
            return response.json()
        else:
            logger.error(f"Error: {response.status_code}")
            logger.error(response.text)
            raise ValueError(
                f"Error in POST request: {response.status_code} {response.text}"
            )

    def delete(self, path: str, params: dict | None = None) -> dict:
        """Make a DELETE request to the Phonic API."""
        headers = {"Authorization": f"Bearer {self.api_key}", **self.additional_headers}

        response = requests.delete(
            f"{self.base_url}{path}",
            headers=headers,
            params=params,
            timeout=DEFAULT_HTTP_TIMEOUT,
        )

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error: {response.status_code}")
            logger.error(response.text)
            raise ValueError(
                f"Error in DELETE request: {response.status_code} {response.text}"
            )

    def patch(
        self, path: str, data: dict | None = None, params: dict | None = None
    ) -> dict:
        """Make a PATCH request to the Phonic API."""
        headers = {"Authorization": f"Bearer {self.api_key}", **self.additional_headers}

        response = requests.patch(
            f"{self.base_url}{path}",
            headers=headers,
            json=data,
            params=params,
            timeout=DEFAULT_HTTP_TIMEOUT,
        )

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error: {response.status_code}")
            logger.error(response.text)
            raise ValueError(
                f"Error in PATCH request: {response.status_code} {response.text}"
            )


class Conversations(PhonicHTTPClient):
    """Client for interacting with Phonic conversation endpoints."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.phonic.co/v1",
        additional_headers: dict | None = None,
    ):
        super().__init__(api_key, additional_headers, base_url)

    def get_conversation(self, conversation_id: str) -> dict:
        """Get a conversation by ID.

        Args:
            conversation_id: ID of the conversation to retrieve

        Returns:
            Dictionary containing the conversation details
        """
        return self.get(f"/conversations/{conversation_id}")

    def get_by_external_id(self, external_id: str, project: str = "main") -> dict:
        """Get a conversation by external ID.

        Args:
            external_id: External ID of the conversation to retrieve

        Returns:
            Dictionary containing the conversation details
        """
        params = {"external_id": external_id, "project": project}
        return self.get("/conversations", params)

    def list(
        self,
        project: str = "main",
        duration_min: int | None = None,
        duration_max: int | None = None,
        started_at_min: str | None = None,
        started_at_max: str | None = None,
        before: str | None = None,
        after: str | None = None,
        limit: int = 100,
    ) -> dict:
        """
        List conversations with optional filters and pagination.

        Args:
            project: Project name (optional, defaults to "main")
            duration_min: Minimum duration in seconds (optional)
            duration_max: Maximum duration in seconds (optional)
            started_at_min: Minimum start time (ISO format: YYYY-MM-DD or YYYY-MM-DDThh:mm:ss.sssZ) (optional)
            started_at_max: Maximum start time (ISO format: YYYY-MM-DD or YYYY-MM-DDThh:mm:ss.sssZ) (optional)
            before: Cursor for backward pagination - get items before this conversation ID (optional)
            after: Cursor for forward pagination - get items after this conversation ID (optional)
            limit: Maximum number of items to return (optional, defaults to 100)

        Returns:
            Dictionary containing the paginated conversations under the "conversations" key
            and pagination information under the "pagination" key with "prev_cursor"
            and "next_cursor" values.
        """
        params: dict[str, Any] = {}
        if duration_min is not None:
            params["duration_min"] = duration_min
        if duration_max is not None:
            params["duration_max"] = duration_max
        if started_at_min is not None:
            params["started_at_min"] = started_at_min
        if started_at_max is not None:
            params["started_at_max"] = started_at_max
        if project is not None:
            params["project"] = project
        if before is not None:
            params["before"] = before
        if after is not None:
            params["after"] = after
        if limit is not None:
            params["limit"] = limit

        return self.get("/conversations", params)

    def scroll(
        self,
        max_items: int | None = None,
        project: str = "main",
        duration_min: int | None = None,
        duration_max: int | None = None,
        started_at_min: str | None = None,
        started_at_max: str | None = None,
        batch_size: int = 20,
    ) -> Generator[dict, None, None]:
        """
        Iterate through all conversations with automatic pagination.

        Args:
            max_items: Maximum total number of conversations to return (optional, no limit if None)
            project: Project name (optional, defaults to "main")
            duration_min: Minimum duration in seconds (optional)
            duration_max: Maximum duration in seconds (optional)
            started_at_min: Minimum start time (ISO format: YYYY-MM-DD or YYYY-MM-DDThh:mm:ss.sssZ) (optional)
            started_at_max: Maximum start time (ISO format: YYYY-MM-DD or YYYY-MM-DDThh:mm:ss.sssZ) (optional)
            batch_size: Number of items to fetch per API request (optional, defaults to 20)

        Yields:
            Each conversation object individually
        """
        items_returned = 0
        next_cursor = None

        while True:
            current_page_limit = batch_size
            if max_items is not None:
                remaining = max_items - items_returned
                if remaining <= 0:
                    return
                current_page_limit = min(batch_size, remaining)

            response = self.list(
                project=project,
                duration_min=duration_min,
                duration_max=duration_max,
                started_at_min=started_at_min,
                started_at_max=started_at_max,
                after=next_cursor,
                limit=current_page_limit,
            )

            conversations = response.get("conversations", [])

            if not conversations:
                break

            for conversation in conversations:
                yield conversation
                items_returned += 1

                if max_items is not None and items_returned >= max_items:
                    return

            pagination = response.get("pagination", {})
            next_cursor = pagination.get("next_cursor")

            if not next_cursor:
                break

    def execute_evaluation(self, conversation_id: str, prompt_id: str) -> dict:
        """Execute an evaluation on a conversation.

        Args:
            conversation_id: ID of the conversation to evaluate
            prompt_id: ID of the evaluation prompt to use

        Returns:
            Dictionary containing the evaluation result with a "result" key
            that's one of "successful", "unsuccessful", or "undecided"
        """
        return self.post(
            f"/conversations/{conversation_id}/evals", {"prompt_id": prompt_id}
        )

    def list_evaluation_prompts(self, project_id: str) -> dict:
        """List evaluation prompts for a project.

        Args:
            project_id: ID of the project

        Returns:
            Dictionary containing a list of evaluation prompts under the
            "conversation_eval_prompts" key
        """
        return self.get(f"/projects/{project_id}/conversation_eval_prompts")

    def create_evaluation_prompt(self, project_id: str, name: str, prompt: str) -> dict:
        """Create a new evaluation prompt."""
        return self.post(
            f"/projects/{project_id}/conversation_eval_prompts",
            {"name": name, "prompt": prompt},
        )

    def summarize_conversation(self, conversation_id: str) -> dict:
        """Generate a summary of a conversation.

        Args:
            conversation_id: ID of the conversation to summarize

        Returns:
            Dictionary containing the summary text under the "summary" key
        """
        return self.post(f"/conversations/{conversation_id}/summarize")

    def extract_data(
        self, conversation_id: str, instructions: str, fields: dict
    ) -> dict:
        """Extract structured data from a conversation.

        Args:
            conversation_id: ID of the conversation to extract data from
            instructions: Instructions for the extraction process
            fields: Dictionary of fields to extract, where each field should have:
                - type: One of "string", "int", "float", "bool", "string[]", "int[]", "float[]", "bool[]"
                - description: Optional description of the field

        Example fields format:
            {
                "customer_name": {"type": "string", "description": "Full name of the customer"},
                "order_items": {"type": "string[]", "description": "List of items ordered"}
            }
        """
        return self.post(
            f"/conversations/{conversation_id}/extract",
            {"instructions": instructions, "fields": fields},
        )

    def create_extraction(self, conversation_id: str, schema_id: str) -> dict:
        """Create a new extraction for a conversation using a schema.

        Args:
            conversation_id: ID of the conversation to extract data from
            schema_id: ID of the extraction schema to use

        Returns:
            Dictionary containing the extraction result or error
        """
        return self.post(
            f"/conversations/{conversation_id}/extractions",
            {"schema_id": schema_id},
        )

    def list_extractions(self, conversation_id: str) -> dict:
        """List all extractions for a conversation.

        Args:
            conversation_id: ID of the conversation

        Returns:
            Dictionary containing the list of extractions under the "extractions" key,
            where each extraction includes id, conversation_id, schema information,
            result, error, and created_at timestamp
        """
        return self.get(f"/conversations/{conversation_id}/extractions")

    def list_extraction_schemas(self, project_id: str) -> dict:
        """List all extraction schemas for a project.

        Args:
            project_id: ID of the project

        Returns:
            Dictionary containing the list of extraction schemas under the
            "conversation_extraction_schemas" key, where each schema includes
            id, name, prompt, schema definition, and created_at timestamp
        """
        return self.get(f"/projects/{project_id}/conversation_extraction_schemas")

    def create_extraction_schema(
        self, project_id: str, name: str, prompt: str, schema: dict
    ) -> dict:
        """Create a new extraction schema.

        Args:
            project_id: ID of the project
            name: Name of the schema
            prompt: Prompt for the extraction
            schema: Schema definition object with field names as keys and field definitions as values.
                    Each field definition should be a dictionary with a "type" key (one of: "string",
                    "int", "float", "bool", "string[]", "int[]", "float[]", "bool[]") and an optional
                    "description" key providing details about the field. For example:
                    {
                        "customer_name": {"type": "string", "description": "Full name of the customer"},
                        "age": {"type": "int", "description": "Customer's age"},
                        "purchase_items": {"type": "string[]", "description": "List of items purchased"}
                    }

        Returns:
            Dictionary containing the ID of the created schema
        """
        return self.post(
            f"/projects/{project_id}/conversation_extraction_schemas",
            {"name": name, "prompt": prompt, "schema": schema},
        )


class Agents(PhonicHTTPClient):
    """Client for interacting with Phonic agent endpoints."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.phonic.co/v1",
        additional_headers: dict | None = None,
    ):
        super().__init__(api_key, additional_headers, base_url)

    def create(
        self,
        name: str,
        project: str = "main",
        phone_number: Literal["assign-automatically"] | None = None,
        voice_id: str = "grant",
        audio_format: Literal["pcm_44100", "mulaw_8000"] = "pcm_44100",
        welcome_message: str = "",
        system_prompt: str = "Respond in 1-2 sentences.",
        tools: list[str] | None = None,
        no_input_poke_sec: int | None = None,
        no_input_poke_text: str | None = None,
        no_input_end_conversation_sec: int = 180,
        boosted_keywords: list[str] | None = None,
        configuration_endpoint: dict[str, Any] | None = None,
        supervisor_system_prompt: str | None = None,
        model_settings: dict[str, str] | None = None,
        vad_prebuffer_duration_ms: int | None = None,
        vad_min_speech_duration_ms: int | None = None,
        vad_min_silence_duration_ms: int | None = None,
        vad_threshold: float | None = None,
        downstream_websocket_url: str | None = None,
        experimental_params: str | None = None,
    ) -> dict:
        """Create a new agent.

        Args:
            project: Required. The name of the project to create the agent in.
            name: Required. The name of the agent. Can only contain lowercase letters,
                  numbers and hyphens. Must be unique within the project.
            phone_number: Optional. Either None (no phone number) or "assign-automatically"
                         to auto-assign a phone number. Defaults to None.
            voice_id: Optional. The voice ID to use. Defaults to "grant".
            audio_format: Optional. Audio format, either "pcm_44100" or "mulaw_8000".
                         Defaults to "pcm_44100".
            welcome_message: Optional. Message to play when the conversation starts.
                           Defaults to empty string.
            system_prompt: Optional. System prompt for the AI assistant.
                          Defaults to "Respond in 1-2 sentences.".
            tools: Optional. Array of tool names (built-in or custom). Defaults to None.
            no_input_poke: Optional. Dictionary with 'sec' (seconds of silence) and 'text'
                          (message to send). Both fields required if provided. Defaults to None.
            no_input_end_conversation_sec: Optional. Seconds of silence before ending
                                         conversation. Defaults to 180.
            boosted_keywords: Optional. Array of keywords to boost in speech recognition.
                            Defaults to None.
            configuration_endpoint: Optional. Dictionary with 'url' (required), 'headers'
                                   (optional), and 'timeout_ms' (optional, defaults to 5000).
                                   Defaults to None.

        Returns:
            Dictionary containing the agent ID and name: {"id": "agent_...", "name": "..."}
        """
        data: dict[str, Any] = {
            "project": project,
            "name": name,
            "voice_id": voice_id,
            "audio_format": audio_format,
            "welcome_message": welcome_message,
            "system_prompt": system_prompt,
            "no_input_end_conversation_sec": no_input_end_conversation_sec,
        }

        # Add optional parameters only if they're provided
        if phone_number is not None:
            data["phone_number"] = phone_number
        if tools is not None:
            data["tools"] = tools
        if no_input_poke_sec is not None:
            data["no_input_poke_sec"] = no_input_poke_sec
        if no_input_poke_text is not None:
            data["no_input_poke_text"] = no_input_poke_text
        if boosted_keywords is not None:
            data["boosted_keywords"] = boosted_keywords
        if configuration_endpoint is not None:
            data["configuration_endpoint"] = configuration_endpoint
        if supervisor_system_prompt is not None:
            data["supervisor_system_prompt"] = supervisor_system_prompt
        if model_settings is not None:
            data["model_settings"] = model_settings
        if vad_prebuffer_duration_ms is not None:
            data["vad_prebuffer_duration_ms"] = vad_prebuffer_duration_ms
        if vad_min_speech_duration_ms is not None:
            data["vad_min_speech_duration_ms"] = vad_min_speech_duration_ms
        if vad_min_silence_duration_ms is not None:
            data["vad_min_silence_duration_ms"] = vad_min_silence_duration_ms
        if vad_threshold is not None:
            data["vad_threshold"] = vad_threshold
        if downstream_websocket_url is not None:
            data["downstream_websocket_url"] = downstream_websocket_url
        if experimental_params is not None:
            data["experimental_params"] = experimental_params

        return self.post("/agents", data)

    def get_agent(self, identifier: str) -> dict:
        """Get an agent by ID or name.

        Args:
            identifier: Agent ID (starting with "agent_") or agent name

        Returns:
            Dictionary containing the agent details under the "agent" key
        """
        return super().get(f"/agents/{identifier}")

    def delete_agent(self, identifier: str) -> dict:
        """Delete an agent by ID or name.

        Args:
            identifier: Agent ID (starting with "agent_") or agent name

        Returns:
            Dictionary containing success status: {"success": true}
        """
        return super().delete(f"/agents/{identifier}")

    def update(
        self,
        identifier: str,
        name: str | None = None,
        phone_number: (
            Literal["none", "assign-automatically", "dont-update"] | None
        ) = None,
        voice_id: str | None = None,
        audio_format: Literal["pcm_44100", "mulaw_8000"] | None = None,
        welcome_message: str | None = None,
        system_prompt: str | None = None,
        tools: list[str] | None = None,
        no_input_poke: dict[str, Any] | None = None,
        no_input_end_conversation_sec: int | None = None,
        boosted_keywords: list[str] | None = None,
        configuration_endpoint: dict[str, Any] | None = None,
        supervisor_system_prompt: str | None = None,
        model_settings: dict[str, str] | None = None,
        vad_prebuffer_duration_ms: int | None = None,
        vad_min_speech_duration_ms: int | None = None,
        vad_min_silence_duration_ms: int | None = None,
        vad_threshold: float | None = None,
        downstream_websocket_url: str | None = None,
        experimental_params: str | None = None,
    ) -> dict:
        """Update an agent by ID or name.

        Args:
            identifier: Agent ID (starting with "agent_") or agent name
            name: New agent name
            phone_number: "none", "assign-automatically", or "dont-update"
            voice_id: Voice ID
            audio_format: "pcm_44100" or "mulaw_8000"
            welcome_message: Welcome message text
            system_prompt: System prompt text
            tools: Array of tool names
            no_input_poke: Dict with 'sec' and 'text' fields
            no_input_end_conversation_sec: Seconds before ending on no input
            boosted_keywords: Array of keywords to boost
            configuration_endpoint: Dict with 'url', 'headers', 'timeout_ms'
        Returns:
            Dictionary containing success status: {"success": true}
        """
        data: dict[str, Any] = {}

        # Add parameters only if they're provided
        if name is not None:
            data["name"] = name
        if phone_number is not None:
            data["phone_number"] = phone_number
        if voice_id is not None:
            data["voice_id"] = voice_id
        if audio_format is not None:
            data["audio_format"] = audio_format
        if welcome_message is not None:
            data["welcome_message"] = welcome_message
        if system_prompt is not None:
            data["system_prompt"] = system_prompt
        if tools is not None:
            data["tools"] = tools
        if no_input_poke is not None:
            data["no_input_poke"] = no_input_poke
        if no_input_end_conversation_sec is not None:
            data["no_input_end_conversation_sec"] = no_input_end_conversation_sec
        if boosted_keywords is not None:
            data["boosted_keywords"] = boosted_keywords
        if configuration_endpoint is not None:
            data["configuration_endpoint"] = configuration_endpoint
        if supervisor_system_prompt is not None:
            data["supervisor_system_prompt"] = supervisor_system_prompt
        if model_settings is not None:
            data["model_settings"] = model_settings
        if vad_prebuffer_duration_ms is not None:
            data["vad_prebuffer_duration_ms"] = vad_prebuffer_duration_ms
        if vad_min_speech_duration_ms is not None:
            data["vad_min_speech_duration_ms"] = vad_min_speech_duration_ms
        if vad_min_silence_duration_ms is not None:
            data["vad_min_silence_duration_ms"] = vad_min_silence_duration_ms
        if vad_threshold is not None:
            data["vad_threshold"] = vad_threshold
        if downstream_websocket_url is not None:
            data["downstream_websocket_url"] = downstream_websocket_url
        if experimental_params is not None:
            data["experimental_params"] = experimental_params

        return self.patch(f"/agents/{identifier}", data)

    def list(self, project: str | None = None) -> dict:
        """List all agents, optionally filtered by project.

        Args:
            project: Optional. The name of the project to list agents from.
                    If not provided, lists all agents across all projects.

        Returns:
            Dictionary containing a list of agents under the "agents" key
        """
        params = {}
        if project is not None:
            params["project"] = project
        return self.get("/agents", params)


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

    response = requests.get(
        url, headers=headers, params=params, timeout=DEFAULT_HTTP_TIMEOUT
    )

    if response.status_code == 200:
        data = response.json()
        return data["voices"]
    else:
        logger.error(f"Error: {response.status_code}")
        logger.error(response.text)
        raise ValueError(
            f"Error in get_voice: {response.status_code} " f"{response.text}"
        )
