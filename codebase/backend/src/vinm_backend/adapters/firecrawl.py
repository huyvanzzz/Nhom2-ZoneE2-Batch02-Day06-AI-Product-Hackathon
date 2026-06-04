import httpx


class FirecrawlClient:
    def __init__(self, api_key: str, transport=None):
        self._client = httpx.AsyncClient(
            base_url="https://api.firecrawl.dev",
            transport=transport,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    async def scrape(self, url: str) -> str:
        response = await self._client.post("/scrape", json={"url": url})
        response.raise_for_status()
        data = response.json()
        return data["data"]["markdown"]
