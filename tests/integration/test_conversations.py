"""Read-only checks for the conversations REST surface.

Conversations are created through the realtime websocket / phone calls rather than a REST
create, so this only exercises list + pagination shape and a get of whatever the list
returns (if anything).
"""

from .conftest import requires_api_key

from phonic import Phonic


@requires_api_key
def test_conversations_list(client: Phonic) -> None:
    listing = client.conversations.list(limit=5)
    assert isinstance(listing.conversations, list)
    assert listing.pagination is not None


@requires_api_key
def test_conversations_get_first(client: Phonic) -> None:
    listing = client.conversations.list(limit=1)
    if not listing.conversations:
        # Fresh test workspace may have no conversations yet — list shape is still verified above.
        return
    conv_id = listing.conversations[0].id
    got = client.conversations.get(id=conv_id)
    assert got is not None
