import asyncio

import httpx

from phonic import AsyncPhonic, Phonic
from phonic.responses.client import AsyncResponsesClient, ResponsesClient


def test_responses_client_uses_shared_client_wrapper() -> None:
    with httpx.Client() as httpx_client:
        client = Phonic(
            api_key="test",
            httpx_client=httpx_client,
            reconnect_conversation_on_abnormal_disconnect=True,
        )

        assert isinstance(client.responses, ResponsesClient)
        assert client.responses is client.responses
        assert client.responses.with_raw_response._client_wrapper is client._client_wrapper
        assert client._client_wrapper._reconnect_conversation_on_abnormal_disconnect is True


def test_async_responses_client_uses_shared_client_wrapper() -> None:
    httpx_client = httpx.AsyncClient()
    try:
        client = AsyncPhonic(
            api_key="test",
            httpx_client=httpx_client,
            reconnect_conversation_on_abnormal_disconnect=True,
        )

        assert isinstance(client.responses, AsyncResponsesClient)
        assert client.responses is client.responses
        assert client.responses.with_raw_response._client_wrapper is client._client_wrapper
        assert client._client_wrapper._reconnect_conversation_on_abnormal_disconnect is True
    finally:
        asyncio.run(httpx_client.aclose())
