"""
Session-aware WebSocket reconnection on abnormal close (1006) with reconnect_conv_id.

Mirrors phonic-node ReconnectableConversationsSocket behavior.
"""

from __future__ import annotations

import asyncio
import time
import typing

import websockets.sync.client as websockets_sync_client
from websockets.exceptions import ConnectionClosed

try:
    from websockets.legacy.client import connect as websockets_client_connect  # type: ignore
except ImportError:
    from websockets import connect as websockets_client_connect  # type: ignore

from ..core.client_wrapper import BaseClientWrapper
from ..core.events import EventEmitterMixin, EventType
from ..core.request_options import RequestOptions
from .socket_client import AsyncConversationsSocketClient, ConversationsSocketClient
from .websocket_connect import build_sts_websocket_url_and_headers

ABNORMAL_CLOSURE = 1006
BASE_RECONNECT_DELAY_SEC = 0.5
MAX_RECONNECT_DELAY_SEC = 5.0
# Safety cap: stop retrying if the server is completely unreachable.
# In normal operation the server's terminal codes (4800/4801) stop
# retries much sooner (within the 10s grace period).
_MAX_RECONNECT_ATTEMPTS = 10


def _close_code(exc: BaseException) -> typing.Optional[int]:
    if isinstance(exc, ConnectionClosed):
        # no close frame received -> 1006 (abnormal closure)
        return exc.rcvd.code if exc.rcvd is not None else ABNORMAL_CLOSURE
    return None


def _reconnect_delay_sec(attempt_number: int) -> float:
    # attempt_number is 1-based after increment (matches Node)
    delay = BASE_RECONNECT_DELAY_SEC * (2 ** max(0, attempt_number - 1))
    return min(delay, MAX_RECONNECT_DELAY_SEC)


class ReconnectableAsyncConversationsSocketClient(EventEmitterMixin):
    """Async conversations socket with automatic reconnect after close code 1006."""

    def __init__(
        self,
        *,
        initial_cm: typing.Any,
        initial_protocol: typing.Any,
        client_wrapper: BaseClientWrapper,
        websocket_url: typing.Optional[str],
        request_options: typing.Optional[RequestOptions],
    ) -> None:
        super().__init__()
        self._cm = initial_cm
        self._inner = AsyncConversationsSocketClient(websocket=initial_protocol)
        self._client_wrapper = client_wrapper
        self._websocket_url = websocket_url
        self._request_options = request_options
        self._conversation_id: typing.Optional[str] = None
        self._reconnect_attempts = 0
        self._user_closed = False
        self._reconnecting = False

    @property
    def conversation_id(self) -> typing.Optional[str]:
        return self._conversation_id

    def _is_send_safe(self) -> bool:
        return not self._user_closed and not self._reconnecting

    def _observe_json(self, json_data: typing.Any) -> None:
        if not isinstance(json_data, dict):
            return
        t = json_data.get("type")
        if t == "conversation_created" and "conversation_id" in json_data:
            self._conversation_id = typing.cast(str, json_data["conversation_id"])
        if t == "conversation_reconnected":
            self._reconnect_attempts = 0

    def _observe_message(self, msg: typing.Any) -> None:
        if isinstance(msg, dict):
            self._observe_json(msg)
        elif hasattr(msg, "dict"):
            try:
                self._observe_json(msg.dict())
            except Exception:
                pass

    async def close(self) -> None:
        self._user_closed = True
        self._reconnecting = False
        await self._close_current_connection()

    async def _close_current_connection(self) -> None:
        if self._cm is not None:
            try:
                await self._cm.__aexit__(None, None, None)
            except Exception:
                pass
            self._cm = None

    async def _reconnect(self) -> None:
        if self._conversation_id is None:
            raise RuntimeError("reconnect requested without conversation_id")

        ws_url, headers = build_sts_websocket_url_and_headers(
            self._client_wrapper,
            websocket_url=self._websocket_url,
            request_options=self._request_options,
            reconnect_conv_id=self._conversation_id,
        )
        await self._close_current_connection()
        new_cm = websockets_client_connect(ws_url, extra_headers=headers)
        new_protocol = await new_cm.__aenter__()
        self._cm = new_cm
        self._inner = AsyncConversationsSocketClient(websocket=new_protocol)

    def _should_reconnect(self, exc: BaseException) -> bool:
        if self._user_closed:
            return False
        if _close_code(exc) != ABNORMAL_CLOSURE:
            return False
        if not self._conversation_id:
            return False
        if self._reconnect_attempts >= _MAX_RECONNECT_ATTEMPTS:
            return False
        return True

    async def recv(self) -> typing.Any:
        try:
            msg = await self._inner.recv()
            self._observe_message(msg)
            return msg
        except ConnectionClosed as exc:
            return await self._recv_with_reconnect(exc)

    async def _recv_with_reconnect(self, exc: ConnectionClosed) -> typing.Any:
        if not self._should_reconnect(exc):
            self._reconnecting = False
            raise exc
        self._reconnecting = True
        self._reconnect_attempts += 1
        await asyncio.sleep(_reconnect_delay_sec(self._reconnect_attempts))
        if self._user_closed:
            self._reconnecting = False
            raise exc
        try:
            await self._reconnect()
            self._reconnecting = False
        except ConnectionClosed as reconnect_exc:
            return await self._recv_with_reconnect(reconnect_exc)
        except Exception:
            return await self._recv_with_reconnect(exc)
        return await self.recv()

    async def __aiter__(self) -> typing.AsyncIterator[typing.Any]:
        while not self._user_closed:
            try:
                msg = await self.recv()
                yield msg
            except ConnectionClosed:
                break

    async def start_listening(self) -> None:
        await self._emit_async(EventType.OPEN, None)
        try:
            while not self._user_closed:
                try:
                    msg = await self.recv()
                    await self._emit_async(EventType.MESSAGE, msg)
                except ConnectionClosed as exc:
                    await self._emit_async(EventType.ERROR, exc)
                    break
        finally:
            await self._emit_async(EventType.CLOSE, None)

    async def send_config(self, message: typing.Any) -> None:
        if self._is_send_safe():
            await self._inner.send_config(message)

    async def send_audio_chunk(self, message: typing.Any) -> None:
        if self._is_send_safe():
            await self._inner.send_audio_chunk(message)

    async def send_update_system_prompt(self, message: typing.Any) -> None:
        if self._is_send_safe():
            await self._inner.send_update_system_prompt(message)

    async def send_add_system_message(self, message: typing.Any) -> None:
        if self._is_send_safe():
            await self._inner.send_add_system_message(message)

    async def send_set_external_id(self, message: typing.Any) -> None:
        if self._is_send_safe():
            await self._inner.send_set_external_id(message)

    async def send_tool_call_output(self, message: typing.Any) -> None:
        if self._is_send_safe():
            await self._inner.send_tool_call_output(message)

    async def send_generate_reply(self, message: typing.Any) -> None:
        if self._is_send_safe():
            await self._inner.send_generate_reply(message)

    async def send_say(self, message: typing.Any) -> None:
        if self._is_send_safe():
            await self._inner.send_say(message)


class ReconnectableConversationsSocketClient(EventEmitterMixin):
    """Sync conversations socket with automatic reconnect after close code 1006."""

    def __init__(
        self,
        *,
        initial_cm: typing.Any,
        initial_protocol: typing.Any,
        client_wrapper: BaseClientWrapper,
        websocket_url: typing.Optional[str],
        request_options: typing.Optional[RequestOptions],
    ) -> None:
        super().__init__()
        self._cm = initial_cm
        self._inner = ConversationsSocketClient(websocket=initial_protocol)
        self._client_wrapper = client_wrapper
        self._websocket_url = websocket_url
        self._request_options = request_options
        self._conversation_id: typing.Optional[str] = None
        self._reconnect_attempts = 0
        self._user_closed = False
        self._reconnecting = False

    @property
    def conversation_id(self) -> typing.Optional[str]:
        return self._conversation_id

    def _is_send_safe(self) -> bool:
        return not self._user_closed and not self._reconnecting

    def _observe_json(self, json_data: typing.Any) -> None:
        if not isinstance(json_data, dict):
            return
        t = json_data.get("type")
        if t == "conversation_created" and "conversation_id" in json_data:
            self._conversation_id = typing.cast(str, json_data["conversation_id"])
        if t == "conversation_reconnected":
            self._reconnect_attempts = 0

    def _observe_message(self, msg: typing.Any) -> None:
        if isinstance(msg, dict):
            self._observe_json(msg)
        elif hasattr(msg, "dict"):
            try:
                self._observe_json(msg.dict())
            except Exception:
                pass

    def close(self) -> None:
        self._user_closed = True
        self._reconnecting = False
        self._close_current_connection()

    def _close_current_connection(self) -> None:
        if self._cm is not None:
            try:
                self._cm.__exit__(None, None, None)
            except Exception:
                pass
            self._cm = None

    def _reconnect(self) -> None:
        if self._conversation_id is None:
            raise RuntimeError("reconnect requested without conversation_id")

        ws_url, headers = build_sts_websocket_url_and_headers(
            self._client_wrapper,
            websocket_url=self._websocket_url,
            request_options=self._request_options,
            reconnect_conv_id=self._conversation_id,
        )
        self._close_current_connection()
        new_cm = websockets_sync_client.connect(ws_url, additional_headers=headers)
        new_protocol = new_cm.__enter__()
        self._cm = new_cm
        self._inner = ConversationsSocketClient(websocket=new_protocol)

    def _should_reconnect(self, exc: BaseException) -> bool:
        if self._user_closed:
            return False
        if _close_code(exc) != ABNORMAL_CLOSURE:
            return False
        if not self._conversation_id:
            return False
        if self._reconnect_attempts >= _MAX_RECONNECT_ATTEMPTS:
            return False
        return True

    def recv(self) -> typing.Any:
        try:
            msg = self._inner.recv()
            self._observe_message(msg)
            return msg
        except ConnectionClosed as exc:
            return self._recv_with_reconnect(exc)

    def _recv_with_reconnect(self, exc: ConnectionClosed) -> typing.Any:
        if not self._should_reconnect(exc):
            self._reconnecting = False
            raise exc
        self._reconnecting = True
        self._reconnect_attempts += 1
        time.sleep(_reconnect_delay_sec(self._reconnect_attempts))
        if self._user_closed:
            self._reconnecting = False
            raise exc
        try:
            self._reconnect()
            self._reconnecting = False
        except ConnectionClosed as reconnect_exc:
            return self._recv_with_reconnect(reconnect_exc)
        except Exception:
            return self._recv_with_reconnect(exc)
        return self.recv()

    def __iter__(self) -> typing.Iterator[typing.Any]:
        while not self._user_closed:
            try:
                yield self.recv()
            except ConnectionClosed:
                break

    def start_listening(self) -> None:
        self._emit(EventType.OPEN, None)
        try:
            while not self._user_closed:
                try:
                    msg = self.recv()
                    self._emit(EventType.MESSAGE, msg)
                except ConnectionClosed as exc:
                    self._emit(EventType.ERROR, exc)
                    break
        finally:
            self._emit(EventType.CLOSE, None)

    def send_config(self, message: typing.Any) -> None:
        if self._is_send_safe():
            self._inner.send_config(message)

    def send_audio_chunk(self, message: typing.Any) -> None:
        if self._is_send_safe():
            self._inner.send_audio_chunk(message)

    def send_update_system_prompt(self, message: typing.Any) -> None:
        if self._is_send_safe():
            self._inner.send_update_system_prompt(message)

    def send_add_system_message(self, message: typing.Any) -> None:
        if self._is_send_safe():
            self._inner.send_add_system_message(message)

    def send_set_external_id(self, message: typing.Any) -> None:
        if self._is_send_safe():
            self._inner.send_set_external_id(message)

    def send_tool_call_output(self, message: typing.Any) -> None:
        if self._is_send_safe():
            self._inner.send_tool_call_output(message)

    def send_generate_reply(self, message: typing.Any) -> None:
        if self._is_send_safe():
            self._inner.send_generate_reply(message)

    def send_say(self, message: typing.Any) -> None:
        if self._is_send_safe():
            self._inner.send_say(message)
