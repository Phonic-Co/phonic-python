"""STS WebSocket URL construction and connect helpers for conversations clients."""

from __future__ import annotations

import typing
import urllib.parse
from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncIterator, Dict, Iterator, NoReturn, Optional, Tuple, TYPE_CHECKING

import websockets.sync.client as websockets_sync_client

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


def build_sts_websocket_url_and_headers(
    client_wrapper: BaseClientWrapper,
    *,
    websocket_url: Optional[str] = None,
    request_options: Optional[RequestOptions] = None,
    reconnect_conv_id: Optional[str] = None,
) -> Tuple[str, Dict[str, str]]:
    ws_url = client_wrapper.get_environment().production + "/v1/sts/ws"
    query: Dict[str, Any] = {
        "downstream_websocket_url": websocket_url,
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


def _raise_api_error_for_invalid_websocket_status(
    exc: InvalidWebSocketStatus, headers: Dict[str, str]
) -> NoReturn:
    status_code: int = get_status_code(exc)
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
    websocket_url: Optional[str] = None,
    request_options: Optional[RequestOptions] = None,
) -> Iterator[ConversationsSocketClient]:
    ws_url, headers = build_sts_websocket_url_and_headers(
        client_wrapper,
        websocket_url=websocket_url,
        request_options=request_options,
    )
    try:
        with websockets_sync_client.connect(ws_url, additional_headers=headers) as protocol:
            yield ConversationsSocketClient(websocket=protocol)
    except InvalidWebSocketStatus as exc:
        _raise_api_error_for_invalid_websocket_status(exc, headers)


@asynccontextmanager
async def open_conversations_socket_async(
    client_wrapper: BaseClientWrapper,
    *,
    websocket_url: Optional[str] = None,
    request_options: Optional[RequestOptions] = None,
) -> AsyncIterator[AsyncConversationsSocketClient]:
    ws_url, headers = build_sts_websocket_url_and_headers(
        client_wrapper,
        websocket_url=websocket_url,
        request_options=request_options,
    )
    try:
        async with websockets_client_connect(ws_url, extra_headers=headers) as protocol:
            yield AsyncConversationsSocketClient(websocket=protocol)
    except InvalidWebSocketStatus as exc:
        _raise_api_error_for_invalid_websocket_status(exc, headers)


@contextmanager
def open_reconnectable_conversations_socket_sync(
    client_wrapper: BaseClientWrapper,
    *,
    websocket_url: Optional[str] = None,
    request_options: Optional[RequestOptions] = None,
) -> Iterator["ReconnectableConversationsSocketClient"]:
    from .reconnectable_socket_client import ReconnectableConversationsSocketClient

    ws_url, headers = build_sts_websocket_url_and_headers(
        client_wrapper,
        websocket_url=websocket_url,
        request_options=request_options,
    )
    try:
        cm = websockets_sync_client.connect(ws_url, additional_headers=headers)
        protocol = cm.__enter__()
    except InvalidWebSocketStatus as exc:
        _raise_api_error_for_invalid_websocket_status(exc, headers)
    client = ReconnectableConversationsSocketClient(
        initial_cm=cm,
        initial_protocol=protocol,
        client_wrapper=client_wrapper,
        websocket_url=websocket_url,
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
    websocket_url: Optional[str] = None,
    request_options: Optional[RequestOptions] = None,
) -> AsyncIterator["ReconnectableAsyncConversationsSocketClient"]:
    from .reconnectable_socket_client import ReconnectableAsyncConversationsSocketClient

    ws_url, headers = build_sts_websocket_url_and_headers(
        client_wrapper,
        websocket_url=websocket_url,
        request_options=request_options,
    )
    try:
        cm = websockets_client_connect(ws_url, extra_headers=headers)
        protocol = await cm.__aenter__()
    except InvalidWebSocketStatus as exc:
        _raise_api_error_for_invalid_websocket_status(exc, headers)
    client = ReconnectableAsyncConversationsSocketClient(
        initial_cm=cm,
        initial_protocol=protocol,
        client_wrapper=client_wrapper,
        websocket_url=websocket_url,
        request_options=request_options,
    )
    try:
        yield client
    finally:
        await client.close()
