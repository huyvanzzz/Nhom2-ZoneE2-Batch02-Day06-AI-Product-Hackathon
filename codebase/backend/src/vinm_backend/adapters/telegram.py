import httpx


class TelegramClient:
    def __init__(self, bot_token: str, chat_id: str, transport=None):
        self._client = httpx.AsyncClient(
            base_url="https://api.telegram.org",
            transport=transport,
        )
        self._bot_token = bot_token
        self._chat_id = chat_id

    async def notify(self, message: str) -> None:
        await self._client.post(
            f"/bot{self._bot_token}/sendMessage",
            json={"chat_id": self._chat_id, "text": message},
        )
