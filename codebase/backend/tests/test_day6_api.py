import pytest
import tempfile
from pathlib import Path
from httpx import ASGITransport, AsyncClient

from vinm_backend.app_factory import create_app
from vinm_backend.intake import SmartIntakeService
from vinm_backend.storage import SqliteIntakeStore


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


@pytest.mark.asyncio
async def test_only_severe_red_flags_trigger_emergency_handoff():
    intake = SmartIntakeService()
    app = create_app(flow=FakeFlow(), intake=intake)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        severe_session = (await client.post("/chat/session")).json()
        severe = await client.post(
            "/chat/message",
            json={
                "session_id": severe_session["session_id"],
                "content": "Toi dau dau dot ngot, co gay va lo mo.",
            },
        )

        non_severe_session = (await client.post("/chat/session")).json()
        non_severe = await client.post(
            "/chat/message",
            json={
                "session_id": non_severe_session["session_id"],
                "content": "Toi met moi keo dai va sut can khong ro ly do.",
            },
        )

    assert severe.json()["response_type"] == "emergency_handoff"
    assert non_severe.json()["response_type"] != "emergency_handoff"
    assert non_severe.json()["case"]["red_flag_status"] == "none"


@pytest.mark.asyncio
async def test_doctor_login_stats_and_case_logs_use_sqlite_store():
    store = SqliteIntakeStore(Path(tempfile.mkdtemp()) / "intake.sqlite3")
    intake = SmartIntakeService(store=store)
    app = create_app(flow=FakeFlow(), intake=intake)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        login = await client.post("/doctor/login", json={"code": "VINMEC-DR-01"})
        session = (await client.post("/chat/session")).json()
        await client.post(
            "/chat/message",
            json={
                "session_id": session["session_id"],
                "content": "Toi dau da day, day hoi kho tieu 2 tuan nay.",
            },
        )
        await client.post(
            "/chat/message",
            json={
                "session_id": session["session_id"],
                "content": "Me toi 58 tuoi, dau vua.",
            },
        )
        stats = await client.get("/doctor/dashboard/stats")
        logs = await client.get(f"/doctor/cases/{session['case_id']}/logs")

    assert login.json()["ok"] is True
    assert stats.json()["total_conversations"] == 1
    assert logs.json()
    assert any(log["event"] == "intake_slots_extracted" for log in logs.json())
