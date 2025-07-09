import asyncio
import base64
import json
import warnings
from typing import Any, AsyncIterator, Generator
from urllib.parse import urlencode

import numpy as np
import requests
from loguru import logger
from typing_extensions import Literal
from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosedError

from ._base import (
    DEFAULT_HTTP_TIMEOUT,
    INSUFFICIENT_CAPACITY_AVAILABLE_ERROR_CODE,
    InsufficientCapacityError,
    PhonicHTTPClient,
    is_agent_id,
)
from ._types import NOT_GIVEN, NotGiven, PhonicSTSTool


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
        agent: str | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        model: str | NotGiven = NOT_GIVEN,
        input_format: Literal["pcm_44100", "mulaw_8000"] = "pcm_44100",
        output_format: Literal["pcm_44100", "mulaw_8000"] = "pcm_44100",
        system_prompt: (
            str | NotGiven
        ) = "You are a helpful assistant. Respond in 1-2 sentences.",
        output_audio_speed: float | NotGiven = NOT_GIVEN,
        welcome_message: str | None | NotGiven = NOT_GIVEN,
        voice_id: str | NotGiven = NOT_GIVEN,
        enable_silent_audio_fallback: bool | NotGiven = NOT_GIVEN,
        vad_prebuffer_duration_ms: int | NotGiven = NOT_GIVEN,
        vad_min_speech_duration_ms: int | NotGiven = NOT_GIVEN,
        vad_min_silence_duration_ms: int | NotGiven = NOT_GIVEN,
        vad_threshold: float | NotGiven = NOT_GIVEN,
        enable_documents_rag: bool | NotGiven = NOT_GIVEN,
        enable_transcripts_rag: bool | NotGiven = NOT_GIVEN,
        no_input_poke_sec: int | None | NotGiven = NOT_GIVEN,
        no_input_poke_text: str | NotGiven = NOT_GIVEN,
        no_input_end_conversation_sec: int | NotGiven = NOT_GIVEN,
        boosted_keywords: list[str] | NotGiven = NOT_GIVEN,
        tools: list[PhonicSTSTool] | NotGiven = NOT_GIVEN,
        experimental_params: dict[str, Any] | NotGiven = NOT_GIVEN,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Args:
            agent: agent identifier (optional)
            project: project name (optional, defaults to "main")
            model: STS model to use (optional)
            input_format: input audio format (defaults to "pcm_44100")
            output_format: output audio format (defaults to "pcm_44100")
            system_prompt: system prompt for assistant (optional)
            welcome_message: welcome message for assistant (optional)
            voice_id: voice id (optional)
            enable_silent_audio_fallback: enable silent audio fallback (defaults to False)
            vad_prebuffer_duration_ms: VAD prebuffer duration in milliseconds (optional)
            vad_min_speech_duration_ms: VAD minimum speech duration in milliseconds (optional)
            vad_min_silence_duration_ms: VAD minimum silence duration in milliseconds (optional)
            vad_threshold: VAD threshold (optional)
            enable_documents_rag: enable documents RAG (optional)
            enable_transcripts_rag: enable transcripts RAG (optional)
            no_input_poke_sec: seconds before no input poke (optional, None to disable)
            no_input_poke_text: text for no input poke (optional)
            no_input_end_conversation_sec: seconds before ending conversation on no input (optional)
            boosted_keywords: list of keywords to boost in speech recognition (optional)
            tools: list of tools to enable (optional)
            experimental_params: experimental parameters (optional)
        """
        assert self._websocket is not None

        if not self._is_running:
            raise RuntimeError("WebSocket connection not established")

        if output_audio_speed is not NOT_GIVEN:
            warnings.warn(
                "output_audio_speed is not supported at this time.",
                DeprecationWarning,
                stacklevel=2,
            )

        self.input_format = input_format

        config_message = {
            "type": "config",
            "project": project,
            "input_format": input_format,
            "output_format": output_format,
            "system_prompt": system_prompt,
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

        config_message = {k: v for k, v in config_message.items() if v is not NOT_GIVEN}
        await self._websocket.send(json.dumps(config_message))

        async for message in self.start_bidirectional_stream():
            yield message


class Conversations(PhonicHTTPClient):
    """Client for interacting with Phonic conversation endpoints."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.phonic.co/v1",
        additional_headers: dict | None = None,
    ):
        super().__init__(api_key, additional_headers, base_url)

    def get(self, conversation_id: str) -> dict:
        """Get a conversation by ID.

        Args:
            conversation_id: ID of the conversation to retrieve

        Returns:
            Dictionary containing the conversation details
        """
        return self._get(f"/conversations/{conversation_id}")

    def get_conversation(self, conversation_id: str) -> dict:
        """Get a conversation by ID.

        .. deprecated::
            This method is deprecated. Use get() instead.

        Args:
            conversation_id: ID of the conversation to retrieve

        Returns:
            Dictionary containing the conversation details
        """
        warnings.warn(
            "get_conversation() is deprecated. Use get() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get(conversation_id)

    def get_by_external_id(self, external_id: str, project: str = "main") -> dict:
        """Get a conversation by external ID.

        Args:
            external_id: External ID of the conversation to retrieve

        Returns:
            Dictionary containing the conversation details
        """
        params = {"external_id": external_id, "project": project}
        return self._get("/conversations", params)

    def outbound_call(
        self,
        to_phone_number: str,
        *,
        agent: str | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        model: str | NotGiven = NOT_GIVEN,
        system_prompt: str | NotGiven = NOT_GIVEN,
        template_variables: dict[str, str] | NotGiven = NOT_GIVEN,
        output_audio_speed: float | NotGiven = NOT_GIVEN,
        welcome_message: str | None | NotGiven = NOT_GIVEN,
        voice_id: str | NotGiven = NOT_GIVEN,
        enable_silent_audio_fallback: bool | NotGiven = NOT_GIVEN,
        vad_prebuffer_duration_ms: int | NotGiven = NOT_GIVEN,
        vad_min_speech_duration_ms: int | NotGiven = NOT_GIVEN,
        vad_min_silence_duration_ms: int | NotGiven = NOT_GIVEN,
        vad_threshold: float | NotGiven = NOT_GIVEN,
        enable_documents_rag: bool | NotGiven = NOT_GIVEN,
        enable_transcripts_rag: bool | NotGiven = NOT_GIVEN,
        no_input_poke_sec: int | None | NotGiven = NOT_GIVEN,
        no_input_poke_text: str | NotGiven = NOT_GIVEN,
        no_input_end_conversation_sec: int | NotGiven = NOT_GIVEN,
        boosted_keywords: list[str] | NotGiven = NOT_GIVEN,
        tools: list[str] | NotGiven = NOT_GIVEN,
        experimental_params: dict[str, Any] | NotGiven = NOT_GIVEN,
        downstream_websocket_url: str | NotGiven = NOT_GIVEN,
    ) -> dict:
        """Make an outbound SIP call to a phone number.

        Args:
            to_phone_number: Required. Phone number to call in E.164 format (e.g., "+15551234567")
            agent: Optional. Agent identifier to use for the call
            project: Optional. Project name (defaults to "main" if not provided)
            model: Optional. STS model to use for the call
            system_prompt: Optional. System prompt for the AI assistant
            template_variables: Optional. Template variables for prompt substitution
            output_audio_speed: Optional. Audio playback speed (0.5-2.0)
            welcome_message: Optional. Message to play when call connects (None for no message)
            voice_id: Optional. Voice ID to use for speech synthesis
            enable_silent_audio_fallback: Optional. Enable fallback for silent audio
            vad_prebuffer_duration_ms: Optional. VAD prebuffer duration in milliseconds
            vad_min_speech_duration_ms: Optional. VAD minimum speech duration in milliseconds
            vad_min_silence_duration_ms: Optional. VAD minimum silence duration in milliseconds
            vad_threshold: Optional. VAD threshold value
            enable_documents_rag: Optional. Enable document retrieval augmented generation
            enable_transcripts_rag: Optional. Enable transcript retrieval augmented generation
            no_input_poke_sec: Optional. Seconds before sending poke message (None to disable)
            no_input_poke_text: Optional. Text for poke message
            no_input_end_conversation_sec: Optional. Seconds before ending conversation on no input
            boosted_keywords: Optional. Keywords to boost in speech recognition
            tools: Optional. List of tool names to enable
            experimental_params: Optional. Experimental parameters
            token: Optional. Authentication token for downstream services
            downstream_websocket_url: Optional. URL for downstream WebSocket connection

        Returns:
            Dictionary containing call initiation result:
            - On success: {"success": true, "conversation_id": "conv_..."}
            - On error: {"error": {"message": "..."}}
        """
        excluded = {
            "self",
            "to_phone_number",
            "token",
            "downstream_websocket_url",
            "excluded",
        }
        config = {
            k: v
            for k, v in locals().items()
            if k not in excluded and v is not NOT_GIVEN
        }

        params: dict = {}
        if downstream_websocket_url is not NOT_GIVEN:
            params["downstream_websocket_url"] = downstream_websocket_url

        return self._post(
            "/sts/outbound_call_sip",
            {"to_phone_number": to_phone_number, "config": config},
            params,
        )

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

        return self._get("/conversations", params)

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
        return self._post(
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
        return self._get(f"/projects/{project_id}/conversation_eval_prompts")

    def create_evaluation_prompt(self, project_id: str, name: str, prompt: str) -> dict:
        """Create a new evaluation prompt."""
        return self._post(
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
        return self._post(f"/conversations/{conversation_id}/summarize")

    def create_extraction(self, conversation_id: str, schema_id: str) -> dict:
        """Create a new extraction for a conversation using a schema.

        Args:
            conversation_id: ID of the conversation to extract data from
            schema_id: ID of the extraction schema to use

        Returns:
            Dictionary containing the extraction result or error
        """
        return self._post(
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
        return self._get(f"/conversations/{conversation_id}/extractions")

    def list_extraction_schemas(self, project_id: str) -> dict:
        """List all extraction schemas for a project.

        Args:
            project_id: ID of the project

        Returns:
            Dictionary containing the list of extraction schemas under the
            "conversation_extraction_schemas" key, where each schema includes
            id, name, prompt, schema definition, and created_at timestamp
        """
        return self._get(f"/projects/{project_id}/conversation_extraction_schemas")

    def create_extraction_schema(
        self, project_id: str, name: str, prompt: str, fields: dict
    ) -> dict:
        """Create a new extraction fields.

        Args:
            project_id: ID of the project
            name: Name of the fields
            prompt: Prompt for the extraction
            fields: list of field definition objects, where each object contains "name", "type",
                    and an optional "description" key. For example:
                [
                    {
                        "name": "Date",
                        "type": "string",
                        "description": "The date of the appointment",
                    },
                    {
                        "name": "Copay",
                        "type": "string",
                        "description": "Amount of money the patient pays for the appointment",
                    },
                ]

        Returns:
            Dictionary containing the ID of the created fields
        """
        return self._post(
            f"/projects/{project_id}/conversation_extraction_schemas",
            {"name": name, "prompt": prompt, "fields": fields},
        )

    def cancel(self, conversation_id: str) -> dict:
        """Cancel an active conversation.

        Args:
            conversation_id: ID of the conversation to cancel

        Returns:
            Dictionary containing success status: {"success": true} on success
            Dictionary containing error status: {"error": {"message": <error message>}} on error
        """
        return self._post(f"/conversations/{conversation_id}/cancel")


class Tools(PhonicHTTPClient):
    """Client for interacting with Phonic tool endpoints."""

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
        description: str,
        endpoint_url: str,
        *,
        endpoint_timeout_ms: int | NotGiven = NOT_GIVEN,
        parameters: list[dict[str, Any]] | NotGiven = NOT_GIVEN,
        endpoint_headers: dict[str, str] | NotGiven = NOT_GIVEN,
    ) -> dict:
        """Create a new tool.

        Args:
            name: Required. The name of the tool. Must be snake_case (lowercase letters,
                  numbers, and underscores only). Must be unique within the organization.
            description: Required. A description of what the tool does.
            endpoint_url: Required. The URL that will be called when the tool is invoked.
            endpoint_timeout_ms: Optional. Timeout in milliseconds for the endpoint call.
                                Defaults to 15000 ms if not provided.
            parameters: Optional. Array of parameter definitions for the tool.
                       Defaults to empty array [] if not provided.
            endpoint_headers: Optional. Dictionary of header key-value pairs.
                            Defaults to empty dictionary {} if not provided.

        Parameter definition format:
            Each parameter should have:
            - type: One of "string", "integer", "number", "boolean", "array"
            - item_type: Required only when type is "array". The type of items in the array.
            - name: The parameter name.
            - description: Description of the parameter.
            - is_required: Boolean indicating if the parameter is required.

        Returns:
            Dictionary containing the tool ID and name: {"id": "tool_...", "name": "..."}
        """
        excluded = {"self", "excluded"}
        data = {
            k: v
            for k, v in locals().items()
            if k not in excluded and v is not NOT_GIVEN
        }

        return self._post("/tools", data)

    def get(self, identifier: str) -> dict:
        """Get a tool by ID or name.

        Args:
            identifier: Tool ID (starting with "tool_" followed by UUID) or tool name

        Returns:
            Dictionary containing the tool details under the "tool" key
        """
        return self._get(f"/tools/{identifier}")

    def delete(self, identifier: str) -> dict:
        """Delete a tool by ID or name.

        Args:
            identifier: Tool ID (starting with "tool_" followed by UUID) or tool name

        Returns:
            Dictionary containing success status: {"success": true}
        """
        return self._delete(f"/tools/{identifier}")

    def update(
        self,
        identifier: str,
        *,
        name: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        endpoint_url: str | NotGiven = NOT_GIVEN,
        endpoint_timeout_ms: int | NotGiven = NOT_GIVEN,
        parameters: list[dict[str, Any]] | NotGiven = NOT_GIVEN,
        endpoint_headers: dict[str, str] | NotGiven = NOT_GIVEN,
    ) -> dict:
        """Update a tool by ID or name.

        Args:
            identifier: Tool ID (starting with "tool_") or tool name
            name: Tool name. Must be snake_case and unique within the organization.
            description: Description of what the tool does.
            endpoint_url: The URL that will be called when the tool is invoked.
            endpoint_timeout_ms: Timeout in milliseconds for the endpoint call.
            parameters: Array of parameter definitions (same format as create).
            endpoint_headers: Dictionary of header key-value pairs.

        Returns:
            Dictionary containing success status: {"success": true}
        """
        excluded = {"self", "identifier", "excluded"}
        data = {
            k: v
            for k, v in locals().items()
            if k not in excluded and v is not NOT_GIVEN
        }

        return self._patch(f"/tools/{identifier}", data)

    def list(self) -> dict:
        """List all tools for the organization.

        Returns:
            Dictionary containing a list of tools with full details under the "tools" key
        """
        return self._get("/tools")


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
        *,
        project: str = "main",
        phone_number: Literal["assign-automatically"] | None = None,
        timezone: str | None = None,
        voice_id: str = "grant",
        audio_format: Literal["pcm_44100", "mulaw_8000"] = "pcm_44100",
        welcome_message: str = "",
        system_prompt: str = "Respond in 1-2 sentences.",
        template_variables: dict[str, dict[str, str | None]] | None = None,
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
        experimental_params: dict[str, Any] | None = None,
    ) -> dict:
        """Create a new agent.

        Args:
            name: Required. The name of the agent. Can only contain lowercase letters,
                  numbers and hyphens. Must be unique within the project.
            project: Required. The name of the project to create the agent in.
            phone_number: Optional. Either None (no phone number) or "assign-automatically"
                         to auto-assign a phone number. Defaults to None.
            timezone: Optional. Timezone like "America/Los_Angeles". Used to format system
                     variables e.g. {{current_time}}. Defaults to None.
            voice_id: Optional. The voice ID to use. Defaults to "grant".
            audio_format: Optional. Audio format, either "pcm_44100" or "mulaw_8000".
                         Defaults to "pcm_44100".
            welcome_message: Optional. Message to play when the conversation starts.
                           Defaults to empty string.
            system_prompt: Optional. System prompt for the AI assistant.
                          Defaults to "Respond in 1-2 sentences.".
            template_variables: Optional. Dictionary with snake_case keys (variables) and
                              values of type {"default_value": str | None}. These variables
                              replace {{variable_name}} placeholders in system_prompt.
                              Defaults to None.
            tools: Optional. Array of tool names (built-in or custom). Defaults to None.
            no_input_poke_sec: Optional. Seconds of silence before sending poke message.
                              Defaults to None.
            no_input_poke_text: Optional. Text message to send after silence period.
                               Defaults to None.
            no_input_end_conversation_sec: Optional. Seconds of silence before ending
                                         conversation. Defaults to 180.
            boosted_keywords: Optional. Array of keywords to boost in speech recognition.
                            Defaults to None.
            configuration_endpoint: Optional. Dictionary with 'url' (required), 'headers'
                                   (optional), and 'timeout_ms' (optional, defaults to 3000).
                                   Defaults to None.

        Returns:
            Dictionary containing the agent ID and name: {"id": "agent_...", "name": "..."}
        """
        excluded = {"self", "name", "project", "excluded"}
        data = {
            k: v for k, v in locals().items() if k not in excluded and v is not None
        }

        data["name"] = name

        params = {"project": project}

        return self._post("/agents", data, params)

    def get(self, identifier: str, *, project: str = "main") -> dict:
        """Get an agent by ID or name.

        Args:
            identifier: Agent ID (starting with "agent_" followed by UUID) or agent name
            project: Optional. The name of the project containing the agent.
                    Defaults to "main". Only used when looking up by name.

        Returns:
            Dictionary containing the agent details under the "agent" key
        """
        params = {}
        if not is_agent_id(identifier):
            params["project"] = project
        return self._get(f"/agents/{identifier}", params)

    def delete(self, identifier: str, *, project: str = "main") -> dict:
        """Delete an agent by ID or name.

        Args:
            identifier: Agent ID (starting with "agent_" followed by UUID) or agent name
            project: Optional. The name of the project containing the agent.
                    Defaults to "main". Only used when deleting by name.

        Returns:
            Dictionary containing success status: {"success": true}
        """
        params = {}
        if not is_agent_id(identifier):
            params["project"] = project
        return self._delete(f"/agents/{identifier}", params)

    def update(
        self,
        identifier: str,
        *,
        project: str = "main",
        name: str | NotGiven = NOT_GIVEN,
        phone_number: Literal["assign-automatically"] | None | NotGiven = NOT_GIVEN,
        timezone: str | NotGiven = NOT_GIVEN,
        voice_id: str | NotGiven = NOT_GIVEN,
        audio_format: Literal["pcm_44100", "mulaw_8000"] | NotGiven = NOT_GIVEN,
        welcome_message: str | NotGiven = NOT_GIVEN,
        system_prompt: str | NotGiven = NOT_GIVEN,
        template_variables: dict[str, dict[str, str | None]] | NotGiven = NOT_GIVEN,
        tools: list[str] | NotGiven = NOT_GIVEN,
        no_input_poke_sec: int | NotGiven = NOT_GIVEN,
        no_input_poke_text: str | NotGiven = NOT_GIVEN,
        no_input_end_conversation_sec: int | NotGiven = NOT_GIVEN,
        boosted_keywords: list[str] | NotGiven = NOT_GIVEN,
        configuration_endpoint: dict[str, Any] | NotGiven = NOT_GIVEN,
        supervisor_system_prompt: str | NotGiven = NOT_GIVEN,
        model_settings: dict[str, str] | NotGiven = NOT_GIVEN,
        vad_prebuffer_duration_ms: int | NotGiven = NOT_GIVEN,
        vad_min_speech_duration_ms: int | NotGiven = NOT_GIVEN,
        vad_min_silence_duration_ms: int | NotGiven = NOT_GIVEN,
        vad_threshold: float | NotGiven = NOT_GIVEN,
        downstream_websocket_url: str | NotGiven = NOT_GIVEN,
        experimental_params: dict[str, Any] | NotGiven = NOT_GIVEN,
    ) -> dict:
        """Update an agent by ID or name.

        Args:
            identifier: Agent ID (starting with "agent_") or agent name
            project: Optional. The name of the project containing the agent.
                    Defaults to "main". Only used when updating by name.
            name: Agent name. Can only contain lowercase letters, numbers and hyphens.
                 Use None to clear the field, or NOT_GIVEN to leave unchanged.
            phone_number: Either "assign-automatically" or None to clear.
                         Use NOT_GIVEN to leave unchanged.
            timezone: Timezone like "America/Los_Angeles". Used to format system
                     variables e.g. {{current_time}}. Use None to clear, NOT_GIVEN to leave unchanged.
            voice_id: Voice ID to use. Use None to clear, NOT_GIVEN to leave unchanged.
            audio_format: Audio format, either "pcm_44100" or "mulaw_8000".
                         Use NOT_GIVEN to leave unchanged.
            welcome_message: Message to play when the conversation starts.
                           Use None to clear, NOT_GIVEN to leave unchanged.
            system_prompt: System prompt for the AI assistant.
                          Use None to clear, NOT_GIVEN to leave unchanged.
            template_variables: Dictionary with snake_case keys (variables) and
                              values of type {"default_value": str | None}. These variables
                              replace {{variable_name}} placeholders in system_prompt.
                              Use None to clear, NOT_GIVEN to leave unchanged.
            tools: Array of tool names (built-in or custom).
                  Use None to clear, NOT_GIVEN to leave unchanged.
            no_input_poke_sec: Seconds of silence before sending poke message.
                              Use None to clear, NOT_GIVEN to leave unchanged.
            no_input_poke_text: Text message to send after silence period.
                               Use None to clear, NOT_GIVEN to leave unchanged.
            no_input_end_conversation_sec: Seconds of silence before ending conversation.
                                         Use None to clear, NOT_GIVEN to leave unchanged.
            boosted_keywords: Array of keywords to boost in speech recognition.
                            Use None to clear, NOT_GIVEN to leave unchanged.
            configuration_endpoint: Dictionary with 'url' (required), 'headers' (optional),
                                   and 'timeout_ms' (optional).
                                   Use None to clear, NOT_GIVEN to leave unchanged.

        Returns:
            Dictionary containing success status: {"success": true}
        """
        excluded = {"self", "identifier", "project", "excluded"}
        data = {
            k: v
            for k, v in locals().items()
            if k not in excluded and v is not NOT_GIVEN
        }

        params = {}
        if not is_agent_id(identifier):
            params["project"] = project

        return self._patch(f"/agents/{identifier}", data, params)

    def list(self, *, project: str | None = None) -> dict:
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
        return self._get("/agents", params)


# Utilities


def get_voices(
    api_key: str,
    url: str = "https://api.phonic.co/v1/voices",
    model: str = "merritt",
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
        raise ValueError(f"Error in get_voice: {response.status_code} {response.text}")


__all__ = [
    "PhonicSTSClient",
    "PhonicHTTPClient",
    "Conversations",
    "Agents",
    "Tools",
    "get_voices",
    "NOT_GIVEN",
    "NotGiven",
    "InsufficientCapacityError",
]
