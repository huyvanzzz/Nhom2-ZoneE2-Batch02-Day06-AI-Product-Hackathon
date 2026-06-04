from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../../.env", extra="ignore")

    openai_api_key: str
    openai_base_url: str
    openai_model: str
    firecrawl_api_key: str
    tavily_api_key: str
    telegram_bot_token: str
    telegram_chat_id: str
