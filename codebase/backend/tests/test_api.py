import pytest
from httpx import ASGITransport, AsyncClient

from vinm_backend.app_factory import create_app


class FakeFlow:
    async def run(self, request):
        return {"status": "ok", "answer": "done", "sources": []}


@pytest.mark.asyncio
async def test_health_and_assist_endpoint():
    app = create_app(flow=FakeFlow())

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        health = await client.get("/health")
        assist = await client.post("/v1/assist", json={"query": "hello"})

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert assist.status_code == 200
    assert assist.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_frontend_cors_preflight_for_chat_endpoint():
    app = create_app(flow=FakeFlow())

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.options(
            "/chat/message",
            headers={
                "Origin": "http://localhost:4173",
                "Access-Control-Request-Method": "POST",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "*"
    assert "POST" in response.headers["access-control-allow-methods"]
