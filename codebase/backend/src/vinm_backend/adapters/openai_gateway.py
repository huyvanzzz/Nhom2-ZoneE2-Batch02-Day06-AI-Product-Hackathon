import httpx


class OpenAIGatewayClient:
    def __init__(self, base_url: str, api_key: str, model: str, transport=None):
        self._client = httpx.AsyncClient(
            base_url=base_url,
            transport=transport,
            headers={"Authorization": f"Bearer {api_key}"},
        )
        self._model = model

    async def complete(self, prompt: str) -> str:
        response = await self._client.post(
            "/chat/completions",
            json={
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
