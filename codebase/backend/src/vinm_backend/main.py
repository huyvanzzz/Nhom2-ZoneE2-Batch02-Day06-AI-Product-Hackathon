from vinm_backend.adapters.firecrawl import FirecrawlClient
from vinm_backend.adapters.openai_gateway import OpenAIGatewayClient
from vinm_backend.adapters.tavily import TavilyClient
from vinm_backend.adapters.telegram import TelegramClient
from vinm_backend.app_factory import create_app
from vinm_backend.intake import MedicalContextSearchTool, SmartIntakeService
from vinm_backend.orchestrator import ResearchFlow
from vinm_backend.settings import Settings


def build_flow(settings: Settings) -> ResearchFlow:
    tavily = TavilyClient(api_key=settings.tavily_api_key)
    firecrawl = FirecrawlClient(api_key=settings.firecrawl_api_key)
    llm = OpenAIGatewayClient(
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
        model=settings.openai_model,
    )
    return ResearchFlow(
        tavily=tavily,
        firecrawl=firecrawl,
        llm=llm,
        telegram=TelegramClient(
            bot_token=settings.telegram_bot_token,
            chat_id=settings.telegram_chat_id,
        ),
    )


def build_intake(settings: Settings) -> SmartIntakeService:
    tavily = TavilyClient(api_key=settings.tavily_api_key)
    firecrawl = FirecrawlClient(api_key=settings.firecrawl_api_key)
    llm = OpenAIGatewayClient(
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
        model=settings.openai_model,
    )
    return SmartIntakeService(
        llm=llm,
        context_search=MedicalContextSearchTool(tavily=tavily, firecrawl=firecrawl),
    )


settings = Settings()
app = create_app(flow=build_flow(settings), intake=build_intake(settings))
