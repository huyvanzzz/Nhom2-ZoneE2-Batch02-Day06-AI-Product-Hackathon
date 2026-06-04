import httpx

from vinm_backend.models import SourceRef


class TavilyClient:
    def __init__(
        self,
        api_key: str,
        transport=None,
        *,
        default_search_depth: str = "advanced",
        default_max_results: int = 5,
        default_include_raw_content: str = "markdown",
        default_topic: str = "general",
    ):
        self._client = httpx.AsyncClient(
            base_url="https://api.tavily.com",
            transport=transport,
            headers={"Authorization": f"Bearer {api_key}"},
        )
        self._defaults = {
            "search_depth": default_search_depth,
            "max_results": default_max_results,
            "include_raw_content": default_include_raw_content,
            "topic": default_topic,
        }

    async def search(
        self,
        query: str,
        *,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
        search_depth: str | None = None,
        max_results: int | None = None,
        include_raw_content: str | bool | None = None,
        topic: str | None = None,
        auto_parameters: bool = False,
        country: str | None = None,
    ) -> list[SourceRef]:
        payload: dict[str, object] = {
            "query": query,
            "search_depth": search_depth or self._defaults["search_depth"],
            "max_results": max_results or self._defaults["max_results"],
            "include_raw_content": (
                self._defaults["include_raw_content"] if include_raw_content is None else include_raw_content
            ),
            "topic": topic or self._defaults["topic"],
            "auto_parameters": auto_parameters,
        }
        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains
        if country:
            payload["country"] = country

        response = await self._client.post("/search", json=payload)
        response.raise_for_status()
        data = response.json()
        return [
            SourceRef(
                title=item["title"],
                url=item["url"],
                summary=item.get("content", "") or item.get("raw_content", "") or item.get("markdown", ""),
            )
            for item in data["results"]
        ]
