"""Unit tests for the reconnect close-code predicate.

Mirrors phonic-api's isReconnectableClose and phonic-node's
ReconnectableConversationsSocket: reconnect on 1006, 1012, or a
1001/"restarting" (fly proxy drain), but never on a bare 1001 (a deliberate
"going away" — caller ended the conversation, tab closed/suspended).
"""

import pytest
from websockets.exceptions import ConnectionClosed
from websockets.frames import Close

from phonic.conversations.reconnectable_socket_client import (
    ABNORMAL_CLOSURE,
    GOING_AWAY,
    SERVICE_RESTART,
    _close_code,
    _close_reason,
    _is_reconnectable_close,
)


@pytest.mark.parametrize(
    "code, reason, expected",
    [
        (ABNORMAL_CLOSURE, "", True),          # 1006 abnormal closure
        (SERVICE_RESTART, "restarting", True),  # 1012 fly proxy redeploy
        (SERVICE_RESTART, "", True),            # 1012 regardless of reason
        (GOING_AWAY, "restarting", True),       # 1001 drain surfacing as going-away
        (GOING_AWAY, "", False),                # bare 1001 = deliberate close
        (GOING_AWAY, "going away", False),      # 1001 without the restarting reason
        (1000, "", False),                      # normal closure
        (4800, "", False),                      # terminal: reconnect session not found
        (4000, "", False),                      # downstream websocket closed
        (None, "", False),                      # not a ConnectionClosed
    ],
)
def test_is_reconnectable_close(code, reason, expected):
    assert _is_reconnectable_close(code, reason) is expected


def test_close_code_and_reason_from_frame():
    exc = ConnectionClosed(Close(SERVICE_RESTART, "restarting"), None)
    assert _close_code(exc) == SERVICE_RESTART
    assert _close_reason(exc) == "restarting"


def test_close_code_defaults_to_abnormal_when_no_frame():
    # No close frame received -> synthesized 1006, empty reason.
    exc = ConnectionClosed(None, None)
    assert _close_code(exc) == ABNORMAL_CLOSURE
    assert _close_reason(exc) == ""
