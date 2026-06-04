import httpx

from vinm_backend.models import SourceRef


class TavilyClient:
    def __init__(self, api_key: str, transport=None):
        self._client = httpx.AsyncClient(
            base_url="https://api.tavily.com",
            transport=transport,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    async def search(self, query: str) -> list[SourceRef]:
        response = await self._client.post("/search", json={"query": query})
        response.raise_for_status()
        data = response.json()
        return [
            SourceRef(
                title=item["title"],
                url=item["url"],
                summary=item.get("content", ""),
            )
            for item in data["results"]
        ]
