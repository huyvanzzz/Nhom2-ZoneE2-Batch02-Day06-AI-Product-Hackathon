from vinm_backend.settings import Settings


def test_settings_reads_required_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "http://localhost:20128/v1")
    monkeypatch.setenv("OPENAI_MODEL", "cx/gpt-5.4-mini")
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-key")
    monkeypatch.setenv("TAVILY_API_KEY", "tv-key")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tg-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123456")

    settings = Settings()

    assert settings.openai_base_url == "http://localhost:20128/v1"
    assert settings.openai_model == "cx/gpt-5.4-mini"
