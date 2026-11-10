import typing

import pytest
from websockets.exceptions import ConnectionClosed
from websockets.frames import Close

from phonic.conversations import reconnectable_socket_client as rsc
from phonic.conversations.reconnectable_socket_client import (
    ReconnectableAsyncConversationsSocketClient,
    ReconnectableConversationsSocketClient,
)


def _abnormal_close() -> ConnectionClosed:
    # no close frame received -> treated as 1006
    return ConnectionClosed(None, None)


def _deliberate_close() -> ConnectionClosed:
    return ConnectionClosed(Close(4800, "session expired"), None)


class _FakeAsyncInner:
    def __init__(self, recv_results: typing.List[typing.Any], send_error: typing.Optional[BaseException] = None):
        self._recv_results = recv_results
        self._send_error = send_error
        self.sent: typing.List[typing.Any] = []

    async def recv(self) -> typing.Any:
        result = self._recv_results.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result

    async def send_audio_chunk(self, message: typing.Any) -> None:
        if self._send_error is not None:
            raise self._send_error
        self.sent.append(message)


class _FakeSyncInner(_FakeAsyncInner):
    def recv(self) -> typing.Any:  # type: ignore[override]
        result = self._recv_results.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result

    def send_audio_chunk(self, message: typing.Any) -> None:  # type: ignore[override]
        if self._send_error is not None:
            raise self._send_error
        self.sent.append(message)


@pytest.fixture(autouse=True)
def _no_reconnect_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rsc, "_reconnect_delay_sec", lambda attempt_number: 0)


def _async_socket(inner: _FakeAsyncInner, replacement: _FakeAsyncInner) -> ReconnectableAsyncConversationsSocketClient:
    socket = ReconnectableAsyncConversationsSocketClient(
        initial_cm=None,
        initial_protocol=None,
        client_wrapper=None,
        request_options=None,  # type: ignore[arg-type]
    )
    socket._inner = inner  # type: ignore[assignment]
    socket._conversation_id = "conv_test"

    async def _reconnect() -> None:
        socket._inner = replacement  # type: ignore[assignment]

    socket._reconnect = _reconnect  # type: ignore[method-assign]
    return socket


def _sync_socket(inner: _FakeSyncInner, replacement: _FakeSyncInner) -> ReconnectableConversationsSocketClient:
    socket = ReconnectableConversationsSocketClient(
        initial_cm=None,
        initial_protocol=None,
        client_wrapper=None,
        request_options=None,  # type: ignore[arg-type]
    )
    socket._inner = inner  # type: ignore[assignment]
    socket._conversation_id = "conv_test"

    def _reconnect() -> None:
        socket._inner = replacement  # type: ignore[assignment]

    socket._reconnect = _reconnect  # type: ignore[method-assign]
    return socket


async def test_async_send_first_abnormal_close_is_dropped_and_recv_reconnects() -> None:
    replacement = _FakeAsyncInner(recv_results=["after reconnect"])
    socket = _async_socket(_FakeAsyncInner(recv_results=[_abnormal_close()], send_error=_abnormal_close()), replacement)

    await socket.send_audio_chunk("chunk-1")

    assert await socket.recv() == "after reconnect"
    await socket.send_audio_chunk("chunk-2")
    assert replacement.sent == ["chunk-2"]


async def test_async_recv_first_abnormal_close_reconnects() -> None:
    replacement = _FakeAsyncInner(recv_results=["after reconnect"])
    original = _FakeAsyncInner(recv_results=[_abnormal_close()])
    socket = _async_socket(original, replacement)

    assert await socket.recv() == "after reconnect"
    await socket.send_audio_chunk("chunk")
    assert original.sent == []
    assert replacement.sent == ["chunk"]


async def test_async_send_deliberate_close_still_raises() -> None:
    socket = _async_socket(
        _FakeAsyncInner(recv_results=[], send_error=_deliberate_close()), _FakeAsyncInner(recv_results=[])
    )

    with pytest.raises(ConnectionClosed):
        await socket.send_audio_chunk("chunk")


def test_sync_send_first_abnormal_close_is_dropped_and_recv_reconnects() -> None:
    replacement = _FakeSyncInner(recv_results=["after reconnect"])
    socket = _sync_socket(_FakeSyncInner(recv_results=[_abnormal_close()], send_error=_abnormal_close()), replacement)

    socket.send_audio_chunk("chunk-1")

    assert socket.recv() == "after reconnect"
    socket.send_audio_chunk("chunk-2")
    assert replacement.sent == ["chunk-2"]


def test_sync_send_deliberate_close_still_raises() -> None:
    socket = _sync_socket(
        _FakeSyncInner(recv_results=[], send_error=_deliberate_close()), _FakeSyncInner(recv_results=[])
    )

    with pytest.raises(ConnectionClosed):
        socket.send_audio_chunk("chunk")
