"""Workspace read + safe update round-trip.

Workspace has no create/delete — only get/update — and update mutates global workspace
state, so this test reads the current value, writes it straight back, and asserts the
round-trip succeeds without changing anything observable.
"""

from .conftest import requires_api_key

from phonic import Phonic


@requires_api_key
def test_workspace_get(client: Phonic) -> None:
    ws = client.workspace.get()
    assert isinstance(ws.active_conversations, int)
    assert isinstance(ws.max_active_conversations, int)
    assert isinstance(ws.invite_link_allowed_domains, list)
    assert isinstance(ws.ip_allowlist, list)


@requires_api_key
def test_workspace_update_roundtrip(client: Phonic) -> None:
    ws = client.workspace.get()

    # Write the existing values back unchanged — exercises the update path without
    # altering the workspace.
    client.workspace.update(
        invite_link_allowed_domains=ws.invite_link_allowed_domains,
        ip_allowlist=ws.ip_allowlist,
    )

    after = client.workspace.get()
    assert sorted(after.invite_link_allowed_domains) == sorted(ws.invite_link_allowed_domains)
    assert sorted(after.ip_allowlist) == sorted(ws.ip_allowlist)
