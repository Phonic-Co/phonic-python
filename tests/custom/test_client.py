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
        responses_1 = client.responses
        responses_2 = client.responses

        assert isinstance(responses_1, ResponsesClient)
        assert responses_1 is responses_2
        assert responses_1.with_raw_response._client_wrapper is client._client_wrapper
        assert client._client_wrapper._reconnect_conversation_on_abnormal_disconnect is True


def test_async_responses_client_uses_shared_client_wrapper() -> None:
    httpx_client = httpx.AsyncClient()
    try:
        client = AsyncPhonic(
            api_key="test",
            httpx_client=httpx_client,
            reconnect_conversation_on_abnormal_disconnect=True,
        )
        responses_1 = client.responses
        responses_2 = client.responses

        assert isinstance(responses_1, AsyncResponsesClient)
        assert responses_1 is responses_2
        assert responses_1.with_raw_response._client_wrapper is client._client_wrapper
        assert client._client_wrapper._reconnect_conversation_on_abnormal_disconnect is True
    finally:
        asyncio.run(httpx_client.aclose())
