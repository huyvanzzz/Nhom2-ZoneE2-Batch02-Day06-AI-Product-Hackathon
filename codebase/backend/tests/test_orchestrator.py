import pytest

from vinm_backend.models import AssistRequest, SourceRef
from vinm_backend.orchestrator import ResearchFlow


class FakeTavily:
    async def search(self, query: str):
        return [SourceRef(title="A", url="https://example.com/a", summary="snippet")]


class FakeFirecrawl:
    async def scrape(self, url: str):
        return "page text"


class FakeLLM:
    async def complete(self, prompt: str):
        return "final answer"


class FakeTelegram:
    def __init__(self):
        self.messages = []

    async def notify(self, message: str):
        self.messages.append(message)


@pytest.mark.asyncio
async def test_orchestrator_returns_answer_and_sources():
    flow = ResearchFlow(
        tavily=FakeTavily(),
        firecrawl=FakeFirecrawl(),
        llm=FakeLLM(),
        telegram=FakeTelegram(),
    )

    result = await flow.run(AssistRequest(query="What is this?"))

    assert result.status == "ok"
    assert result.answer == "final answer"
    assert result.sources[0].url == "https://example.com/a"
