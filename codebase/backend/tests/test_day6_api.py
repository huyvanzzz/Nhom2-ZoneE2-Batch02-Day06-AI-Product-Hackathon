import pytest
from httpx import ASGITransport, AsyncClient

from vinm_backend.app_factory import create_app
from vinm_backend.intake import SmartIntakeService


class FakeFlow:
    async def run(self, request):
        return {"status": "ok", "answer": "done", "sources": []}


@pytest.mark.asyncio
async def test_day6_chat_booking_and_dashboard_endpoints():
    intake = SmartIntakeService()
    app = create_app(flow=FakeFlow(), intake=intake)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        session_res = await client.post("/chat/session")
        session = session_res.json()

        first = await client.post(
            "/chat/message",
            json={
                "session_id": session["session_id"],
                "content": "Toi dau da day, day hoi kho tieu 2 tuan nay.",
            },
        )
        second = await client.post(
            "/chat/message",
            json={
                "session_id": session["session_id"],
                "content": "Me toi 58 tuoi, dau vua.",
            },
        )
        messages = await client.get(f"/chat/session/{session['session_id']}/messages")
        cases = await client.get("/doctor/cases")
        case_detail = await client.get(f"/doctor/cases/{session['case_id']}")

    assert session_res.status_code == 200
    assert first.json()["response_type"] == "ask_more"
    assert second.json()["response_type"] == "safe_guidance"
    assert len(messages.json()) == 4
    assert cases.json()[0]["case_id"] == session["case_id"]
    assert case_detail.json()["suggested_specialty"] == "Noi Tieu hoa"


@pytest.mark.asyncio
async def test_day6_red_flag_endpoint_returns_emergency_handoff():
    intake = SmartIntakeService()
    app = create_app(flow=FakeFlow(), intake=intake)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        session = (await client.post("/chat/session")).json()
        response = await client.post(
            "/chat/message",
            json={"session_id": session["session_id"], "content": "Toi dau nguc va kho tho."},
        )

    assert response.status_code == 200
    assert response.json()["response_type"] == "emergency_handoff"
    assert response.json()["case"]["priority"] == "high"
