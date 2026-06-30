"""Realtime conversation websocket handshake.

This is a handshake-only test: it opens the STS websocket, sends the initial ``config``
message for a freshly created agent, and asserts the server replies with the expected
``ready_to_start_conversation`` and ``conversation_created`` events. It does not exchange
audio. The point is to confirm the (hand-maintained, ``.fernignore``-protected) websocket
client can connect, authenticate, serialize the config, and deserialize server events.
"""

import threading

from .conftest import requires_api_key, unique_name

from phonic import (
    ConfigPayload,
    ConversationCreatedPayload,
    ErrorPayload,
    Phonic,
    ReadyToStartConversationPayload,
)

# Generous bound so a misbehaving connection fails the test instead of hanging CI.
_HANDSHAKE_TIMEOUT_SEC = 30


@requires_api_key
def test_conversation_socket_handshake(client: Phonic, project) -> None:
    agent = client.agents.create(
        name=unique_name("sdk-it-ws"),
        project=project.name,
        system_prompt="You are a test agent. Be brief.",
    )

    collected: list = []
    error: list = []

    def _handshake() -> None:
        try:
            with client.conversations.connect() as socket:
                socket.send_config(ConfigPayload(agent=agent.name, project=project.name))
                # Read events until we've seen both expected ones (or an error).
                for _ in range(10):
                    msg = socket.recv()
                    collected.append(msg)
                    if isinstance(msg, ErrorPayload):
                        break
                    seen = {type(m) for m in collected}
                    if {ReadyToStartConversationPayload, ConversationCreatedPayload} <= seen:
                        break
        except Exception as exc:  # surface connection/parse failures to the assertions below
            error.append(exc)

    try:
        worker = threading.Thread(target=_handshake, daemon=True)
        worker.start()
        worker.join(_HANDSHAKE_TIMEOUT_SEC)

        assert not worker.is_alive(), f"websocket handshake did not complete within {_HANDSHAKE_TIMEOUT_SEC}s"
        assert not error, f"websocket handshake raised: {error[0]!r}"

        errors = [m for m in collected if isinstance(m, ErrorPayload)]
        assert not errors, f"server returned an error during handshake: {errors[0]!r}"

        types = {type(m) for m in collected}
        assert ReadyToStartConversationPayload in types, f"missing ready_to_start; got {types}"
        assert ConversationCreatedPayload in types, f"missing conversation_created; got {types}"

        created = next(m for m in collected if isinstance(m, ConversationCreatedPayload))
        assert created.conversation_id
    finally:
        client.agents.delete(name_or_id=agent.id)
