import pytest

from vinm_backend.models import AssistRequest
from vinm_backend.orchestrator import ResearchFlow


class FakeTavily:
    async def search(self, query: str):
        return []


class FakeFirecrawl:
    async def scrape(self, url: str):
        return ""


class FakeLLM:
    async def complete(self, prompt: str):
        return "fallback answer"


class FailingLLM:
    async def complete(self, prompt: str):
        raise RuntimeError("gateway unavailable")


class FakeTelegram:
    def __init__(self):
        self.messages = []

    async def notify(self, message: str):
        self.messages.append(message)


@pytest.mark.asyncio
async def test_smoke_flow_handles_happy_path_and_empty_search():
    flow = ResearchFlow(
        tavily=FakeTavily(),
        firecrawl=FakeFirecrawl(),
        llm=FakeLLM(),
        telegram=FakeTelegram(),
    )

    result = await flow.run(AssistRequest(query="short query"))

    assert result.status == "ok"
    assert result.answer == "fallback answer"


@pytest.mark.asyncio
async def test_smoke_flow_returns_structured_error_when_llm_fails():
    flow = ResearchFlow(
        tavily=FakeTavily(),
        firecrawl=FakeFirecrawl(),
        llm=FailingLLM(),
        telegram=FakeTelegram(),
    )

    result = await flow.run(AssistRequest(query="short query"))

    assert result.status == "error"
    assert result.answer == "AI gateway failed: gateway unavailable"
