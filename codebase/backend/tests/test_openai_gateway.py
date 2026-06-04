import json

import pytest
from httpx import MockTransport, Response

from vinm_backend.adapters.openai_gateway import OpenAIGatewayClient


@pytest.mark.asyncio
async def test_openai_client_posts_chat_completion_and_returns_text():
    captured = {}

    async def handler(request):
        captured["path"] = request.url.path
        captured["json"] = json.loads(request.content.decode())
        return Response(
            200,
            json={
                "choices": [
                    {"message": {"content": "answer text"}},
                ],
            },
        )

    client = OpenAIGatewayClient(
        base_url="http://test",
        api_key="test-key",
        model="cx/gpt-5.4-mini",
        transport=MockTransport(handler),
    )

    text = await client.complete("prompt")

    assert captured["path"] == "/chat/completions"
    assert captured["json"]["model"] == "cx/gpt-5.4-mini"
    assert text == "answer text"
