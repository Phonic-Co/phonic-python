"""STS WebSocket URL construction and connect helpers for conversations clients."""

from __future__ import annotations

import asyncio
import random
import ssl
import time
import typing
import urllib.parse
from contextlib import AsyncExitStack, asynccontextmanager, contextmanager
from typing import Any, AsyncIterator, Dict, Iterator, NoReturn, Optional, Tuple, TYPE_CHECKING

import websockets.sync.client as websockets_sync_client
from websockets.exceptions import InvalidHandshake, InvalidStatus

from ..core.api_error import ApiError
from ..core.client_wrapper import BaseClientWrapper
from ..core.jsonable_encoder import jsonable_encoder
from ..core.query_encoder import encode_query
from ..core.remove_none_from_dict import remove_none_from_dict
from ..core.request_options import RequestOptions
from ..core.websocket_compat import InvalidWebSocketStatus, get_status_code
from .socket_client import AsyncConversationsSocketClient, ConversationsSocketClient

try:
    from websockets.legacy.client import connect as websockets_client_connect  # type: ignore
except ImportError:
    from websockets import connect as websockets_client_connect  # type: ignore

if TYPE_CHECKING:
    from .reconnectable_socket_client import (
        ReconnectableAsyncConversationsSocketClient,
        ReconnectableConversationsSocketClient,
    )


# Policy for the initial connect, shared with the Node SDK: a 3s handshake
# timeout, then up to 2 retries with backoff of 0.5s doubling to a 5s cap and
# +/-20% jitter. Only failures before the socket opens are retried here;
# drops after that are handled by the reconnectable client.
DEFAULT_CONNECT_RETRIES = 2
DEFAULT_CONNECTION_TIMEOUT_SEC = 3.0
_CONNECT_RETRY_BASE_DELAY_SEC = 0.5
_CONNECT_RETRY_MAX_DELAY_SEC = 5.0


def _connect_retry_delay_sec(retry_number: int) -> float:
    delay = min(_CONNECT_RETRY_BASE_DELAY_SEC * (2 ** (retry_number - 1)), _CONNECT_RETRY_MAX_DELAY_SEC)
    return delay * (0.8 + random.random() * 0.4)


# The sync client raises InvalidStatus even where the legacy async client
# raises InvalidStatusCode, so status rejections can arrive as either.
_INVALID_STATUS_ERRORS: Tuple[type, ...] = (InvalidWebSocketStatus, InvalidStatus)


def _rejected_status_code(exc: BaseException) -> int:
    if isinstance(exc, InvalidStatus):
        return exc.response.status_code
    return get_status_code(exc)  # type: ignore[arg-type]


def _is_retryable_connect_error(exc: BaseException) -> bool:
    if isinstance(exc, _INVALID_STATUS_ERRORS):
        # A 4xx (bad credentials, rate limit) fails the same way on every attempt.
        return _rejected_status_code(exc) >= 500
    if isinstance(exc, ssl.SSLCertVerificationError):
        return False
    return isinstance(exc, (OSError, TimeoutError, asyncio.TimeoutError, InvalidHandshake))


def _connect_sync_with_retries(
    ws_url: str,
    headers: Dict[str, str],
    *,
    retries: Optional[int],
    timeout: Optional[float],
) -> Any:
    max_retries = DEFAULT_CONNECT_RETRIES if retries is None else retries
    open_timeout = DEFAULT_CONNECTION_TIMEOUT_SEC if timeout is None else timeout
    attempt = 0
    while True:
        try:
            return websockets_sync_client.connect(ws_url, additional_headers=headers, open_timeout=open_timeout)
        except Exception as exc:
            if attempt >= max_retries or not _is_retryable_connect_error(exc):
                raise
            attempt += 1
            time.sleep(_connect_retry_delay_sec(attempt))


async def _enter_within(cm: Any, timeout: Optional[float]) -> Any:
    # After a handshake timeout the legacy client waits its close timeout (10s)
    # for a stalled peer to hang up before raising. Stop waiting at the timeout
    # and let that cleanup finish in the background.
    task = asyncio.ensure_future(cm.__aenter__())
    done, _ = await asyncio.wait({task}, timeout=timeout)
    if not done:
        task.cancel()
        task.add_done_callback(lambda t: t.cancelled() or t.exception())
        raise asyncio.TimeoutError("timed out during handshake")
    return task.result()


async def _connect_async_with_retries(
    ws_url: str,
    headers: Dict[str, str],
    *,
    retries: Optional[int],
    timeout: Optional[float],
) -> Tuple[Any, Any]:
    """Returns the entered connect context manager and its protocol."""
    max_retries = DEFAULT_CONNECT_RETRIES if retries is None else retries
    open_timeout = DEFAULT_CONNECTION_TIMEOUT_SEC if timeout is None else timeout
    attempt = 0
    while True:
        cm = websockets_client_connect(ws_url, extra_headers=headers, open_timeout=open_timeout)
        try:
            return cm, await _enter_within(cm, open_timeout)
        except Exception as exc:
            if attempt >= max_retries or not _is_retryable_connect_error(exc):
                raise
            attempt += 1
            await asyncio.sleep(_connect_retry_delay_sec(attempt))


def build_sts_websocket_url_and_headers(
    client_wrapper: BaseClientWrapper,
    *,
    request_options: Optional[RequestOptions] = None,
    reconnect_conv_id: Optional[str] = None,
) -> Tuple[str, Dict[str, str]]:
    ws_url = client_wrapper.get_environment().production + "/v1/sts/ws"
    query: Dict[str, Any] = {
        **(
            request_options.get("additional_query_parameters", {}) or {}
            if request_options is not None
            else {}
        ),
    }
    if reconnect_conv_id is not None:
        query["reconnect_conv_id"] = reconnect_conv_id
    _encoded_query_params = encode_query(jsonable_encoder(remove_none_from_dict(query)))
    if _encoded_query_params:
        ws_url = ws_url + "?" + urllib.parse.urlencode(_encoded_query_params)
    headers = client_wrapper.get_headers()
    if request_options and "additional_headers" in request_options:
        headers.update(request_options["additional_headers"])
    return ws_url, headers


def _raise_api_error_for_invalid_websocket_status(exc: BaseException, headers: Dict[str, str]) -> NoReturn:
    status_code: int = _rejected_status_code(exc)
    if status_code == 401:
        raise ApiError(
            status_code=status_code,
            headers=dict(headers),
            body="Websocket initialized with invalid credentials.",
        )
    raise ApiError(
        status_code=status_code,
        headers=dict(headers),
        body="Unexpected error when initializing websocket connection.",
    )


@contextmanager
def open_conversations_socket_sync(
    client_wrapper: BaseClientWrapper,
    *,
    request_options: Optional[RequestOptions] = None,
    reconnect_attempts: Optional[int] = None,
    connection_timeout_in_seconds: Optional[float] = None,
) -> Iterator[ConversationsSocketClient]:
    ws_url, headers = build_sts_websocket_url_and_headers(
        client_wrapper,
        request_options=request_options,
    )
    try:
        protocol = _connect_sync_with_retries(
            ws_url, headers, retries=reconnect_attempts, timeout=connection_timeout_in_seconds
        )
    except _INVALID_STATUS_ERRORS as exc:
        _raise_api_error_for_invalid_websocket_status(exc, headers)
    with protocol:
        yield ConversationsSocketClient(websocket=protocol)


@asynccontextmanager
async def open_conversations_socket_async(
    client_wrapper: BaseClientWrapper,
    *,
    request_options: Optional[RequestOptions] = None,
    reconnect_attempts: Optional[int] = None,
    connection_timeout_in_seconds: Optional[float] = None,
) -> AsyncIterator[AsyncConversationsSocketClient]:
    ws_url, headers = build_sts_websocket_url_and_headers(
        client_wrapper,
        request_options=request_options,
    )
    try:
        cm, protocol = await _connect_async_with_retries(
            ws_url, headers, retries=reconnect_attempts, timeout=connection_timeout_in_seconds
        )
    except _INVALID_STATUS_ERRORS as exc:
        _raise_api_error_for_invalid_websocket_status(exc, headers)
    async with AsyncExitStack() as stack:
        stack.push_async_exit(cm)
        yield AsyncConversationsSocketClient(websocket=protocol)


@contextmanager
def open_reconnectable_conversations_socket_sync(
    client_wrapper: BaseClientWrapper,
    *,
    request_options: Optional[RequestOptions] = None,
    reconnect_attempts: Optional[int] = None,
    connection_timeout_in_seconds: Optional[float] = None,
) -> Iterator["ReconnectableConversationsSocketClient"]:
    from .reconnectable_socket_client import ReconnectableConversationsSocketClient

    ws_url, headers = build_sts_websocket_url_and_headers(
        client_wrapper,
        request_options=request_options,
    )
    try:
        cm = _connect_sync_with_retries(
            ws_url, headers, retries=reconnect_attempts, timeout=connection_timeout_in_seconds
        )
        protocol = cm.__enter__()
    except _INVALID_STATUS_ERRORS as exc:
        _raise_api_error_for_invalid_websocket_status(exc, headers)
    client = ReconnectableConversationsSocketClient(
        initial_cm=cm,
        initial_protocol=protocol,
        client_wrapper=client_wrapper,
        request_options=request_options,
    )
    try:
        yield client
    finally:
        client.close()


@asynccontextmanager
async def open_reconnectable_conversations_socket_async(
    client_wrapper: BaseClientWrapper,
    *,
    request_options: Optional[RequestOptions] = None,
    reconnect_attempts: Optional[int] = None,
    connection_timeout_in_seconds: Optional[float] = None,
) -> AsyncIterator["ReconnectableAsyncConversationsSocketClient"]:
    from .reconnectable_socket_client import ReconnectableAsyncConversationsSocketClient

    ws_url, headers = build_sts_websocket_url_and_headers(
        client_wrapper,
        request_options=request_options,
    )
    try:
        cm, protocol = await _connect_async_with_retries(
            ws_url, headers, retries=reconnect_attempts, timeout=connection_timeout_in_seconds
        )
    except _INVALID_STATUS_ERRORS as exc:
        _raise_api_error_for_invalid_websocket_status(exc, headers)
    client = ReconnectableAsyncConversationsSocketClient(
        initial_cm=cm,
        initial_protocol=protocol,
        client_wrapper=client_wrapper,
        request_options=request_options,
    )
    try:
        yield client
    finally:
        await client.close()
