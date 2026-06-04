import json

import pytest
from httpx import MockTransport, Response

from vinm_backend.adapters.firecrawl import FirecrawlClient
from vinm_backend.adapters.tavily import TavilyClient


@pytest.mark.asyncio
async def test_tavily_search_returns_normalized_sources():
    async def handler(request):
        payload = json.loads(request.content.decode())
        assert payload["query"] == "rustic bakery"
        return Response(
            200,
            json={
                "results": [
                    {
                        "title": "Result A",
                        "url": "https://example.com/a",
                        "content": "snippet A",
                    }
                ]
            },
        )

    client = TavilyClient(api_key="tv-key", transport=MockTransport(handler))
    results = await client.search("rustic bakery")

    assert results[0].url == "https://example.com/a"


@pytest.mark.asyncio
async def test_firecrawl_scrape_returns_text():
    async def handler(request):
        return Response(200, json={"data": {"markdown": "page text"}})

    client = FirecrawlClient(api_key="fc-key", transport=MockTransport(handler))
    text = await client.scrape("https://example.com/a")

    assert text == "page text"
