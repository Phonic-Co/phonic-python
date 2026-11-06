import asyncio
import base64
import hashlib
import socket
import threading
import time
from typing import Iterator, List, Union

import pytest

from phonic import AsyncPhonic, Phonic
from phonic.conversations import websocket_connect
from phonic.core.api_error import ApiError
from phonic.environment import PhonicEnvironment

# Per attempt, the server hangs the upgrade, rejects it with a status, or accepts it.
Behavior = Union[str, int]
_WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class _Server:
    def __init__(self, behaviors: List[Behavior]) -> None:
        self._behaviors = behaviors
        self.attempts = 0
        self._conns: List[socket.socket] = []
        self._sock = socket.socket()
        self._sock.bind(("127.0.0.1", 0))
        self._sock.listen(16)
        self.port = self._sock.getsockname()[1]
        threading.Thread(target=self._serve, daemon=True).start()

    def _serve(self) -> None:
        while True:
            try:
                conn, _ = self._sock.accept()
            except OSError:
                return
            self._conns.append(conn)
            behavior = self._behaviors[min(self.attempts, len(self._behaviors) - 1)]
            self.attempts += 1
            threading.Thread(target=self._handle, args=(conn, behavior), daemon=True).start()

    def _handle(self, conn: socket.socket, behavior: Behavior) -> None:
        request = b""
        while b"\r\n\r\n" not in request:
            chunk = conn.recv(4096)
            if not chunk:
                return
            request += chunk
        if behavior == "hang":
            return
        if behavior == "accept":
            key = next(
                line.split(":", 1)[1].strip()
                for line in request.decode().split("\r\n")
                if line.lower().startswith("sec-websocket-key:")
            )
            accept = base64.b64encode(hashlib.sha1((key + _WS_GUID).encode()).digest()).decode()
            conn.sendall(
                (
                    "HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                    f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
                ).encode()
            )
            # Hang up once the client sends anything (its close frame), so the
            # client's closing handshake doesn't wait out its close timeout.
            conn.recv(4096)
            conn.close()
            return
        conn.sendall(f"HTTP/1.1 {behavior} Error\r\nContent-Length: 0\r\nConnection: close\r\n\r\n".encode())
        conn.close()

    def environment(self) -> PhonicEnvironment:
        return PhonicEnvironment(base=f"http://127.0.0.1:{self.port}/v1", production=f"ws://127.0.0.1:{self.port}")

    def stop(self) -> None:
        self._sock.close()
        for conn in self._conns:
            conn.close()


@pytest.fixture(autouse=True)
def fast_backoff(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(websocket_connect, "_CONNECT_RETRY_BASE_DELAY_SEC", 0.01)


@pytest.fixture
def server_factory() -> Iterator:
    servers: List[_Server] = []

    def make(behaviors: List[Behavior]) -> _Server:
        server = _Server(behaviors)
        servers.append(server)
        return server

    yield make
    for server in servers:
        server.stop()


@pytest.mark.parametrize("reconnectable", [False, True])
def test_retries_timed_out_connect_then_raises(server_factory, reconnectable: bool) -> None:
    server = server_factory(["hang"])
    client = Phonic(
        api_key="test",
        environment=server.environment(),
        reconnect_conversation_on_abnormal_disconnect=reconnectable,
    )
    with pytest.raises(TimeoutError):
        with client.conversations.connect(connection_timeout_in_seconds=0.2, reconnect_attempts=2):
            pass
    assert server.attempts == 3


@pytest.mark.parametrize("reconnectable", [False, True])
def test_opens_on_a_later_attempt(server_factory, reconnectable: bool) -> None:
    server = server_factory(["hang", 503, "accept"])
    client = Phonic(
        api_key="test",
        environment=server.environment(),
        reconnect_conversation_on_abnormal_disconnect=reconnectable,
    )
    with client.conversations.connect(connection_timeout_in_seconds=0.2, reconnect_attempts=2):
        pass
    assert server.attempts == 3


def test_does_not_retry_4xx(server_factory) -> None:
    server = server_factory([401])
    client = Phonic(api_key="test", environment=server.environment())
    with pytest.raises(ApiError) as exc_info:
        with client.conversations.connect(connection_timeout_in_seconds=0.2, reconnect_attempts=2):
            pass
    assert exc_info.value.status_code == 401
    assert server.attempts == 1


def test_default_retry_policy(server_factory, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(websocket_connect, "DEFAULT_CONNECTION_TIMEOUT_SEC", 0.2)
    server = server_factory(["hang"])
    client = Phonic(api_key="test", environment=server.environment())
    start = time.monotonic()
    with pytest.raises(TimeoutError):
        with client.conversations.connect():
            pass
    assert server.attempts == 1 + websocket_connect.DEFAULT_CONNECT_RETRIES
    assert time.monotonic() - start < 5


async def _release_stalled(server: _Server) -> None:
    # Hang up on stalled attempts so their background cleanup finishes before
    # the test's event loop closes.
    server.stop()
    await asyncio.sleep(0.1)


@pytest.mark.parametrize("reconnectable", [False, True])
async def test_async_opens_on_a_later_attempt(server_factory, reconnectable: bool) -> None:
    server = server_factory(["hang", 503, "accept"])
    client = AsyncPhonic(
        api_key="test",
        environment=server.environment(),
        reconnect_conversation_on_abnormal_disconnect=reconnectable,
    )
    async with client.conversations.connect(connection_timeout_in_seconds=0.2, reconnect_attempts=2):
        pass
    assert server.attempts == 3
    await _release_stalled(server)


async def test_async_retries_timed_out_connect_then_raises(server_factory) -> None:
    server = server_factory(["hang"])
    client = AsyncPhonic(api_key="test", environment=server.environment())
    start = time.monotonic()
    with pytest.raises((TimeoutError, asyncio.TimeoutError)):
        async with client.conversations.connect(connection_timeout_in_seconds=0.2, reconnect_attempts=2):
            pass
    assert server.attempts == 3
    # Each attempt is bounded by the connection timeout, not the client's close timeout.
    assert time.monotonic() - start < 3
    await _release_stalled(server)
