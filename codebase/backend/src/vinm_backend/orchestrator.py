from vinm_backend.models import AssistRequest, AssistResponse


class ResearchFlow:
    def __init__(self, tavily, firecrawl, llm, telegram):
        self.tavily = tavily
        self.firecrawl = firecrawl
        self.llm = llm
        self.telegram = telegram

    async def run(self, request: AssistRequest) -> AssistResponse:
        sources = await self.tavily.search(request.query)
        snippets = []
        for source in sources[:3]:
            snippets.append(await self.firecrawl.scrape(source.url))
        prompt = f"Question: {request.query}\n\nContext:\n" + "\n".join(snippets)
        answer = await self.llm.complete(prompt)
        await self.telegram.notify(answer)
        return AssistResponse(status="ok", answer=answer, sources=sources)
