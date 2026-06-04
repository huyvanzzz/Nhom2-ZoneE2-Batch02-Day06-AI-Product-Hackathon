import pytest

from vinm_backend.intake import SmartIntakeService
from vinm_backend.models import SourceRef


class FakeLLM:
    def __init__(self):
        self.prompts = []

    async def complete(self, prompt: str):
        self.prompts.append(prompt)
        return (
            "AI: Hien chua thay dau hieu khan cap. Nen an nhe, uong du nuoc, "
            "theo doi va dat lich Noi Tieu hoa neu keo dai."
        )


class FakeMedicalSearch:
    def __init__(self):
        self.queries = []

    async def search(self, case):
        self.queries.append(case.main_symptom)
        return (
            {
                "warning_signs": ["non ra mau", "phan den"],
                "safe_guidance_points": ["an nhe", "uong du nuoc"],
                "possible_specialties": ["Noi Tieu hoa"],
            },
            [
                SourceRef(
                    title="Digestive guidance",
                    url="https://example.com/digestive",
                    summary="when to seek care",
                )
            ],
        )


@pytest.mark.asyncio
async def test_normal_case_creates_booking_and_dashboard_case():
    service = SmartIntakeService()
    session = service.create_session()

    first = await service.handle_message(
        session.session_id,
        "Toi dau da day, day hoi kho tieu 2 tuan nay.",
    )
    assert first.response_type == "ask_more"
    assert "tuoi" in first.assistant_text.lower()

    second = await service.handle_message(
        session.session_id,
        "Me toi 58 tuoi, dau vua.",
    )
    assert second.response_type == "safe_guidance"
    assert second.case.priority == "medium"
    assert second.case.suggested_specialty == "Noi Tieu hoa"

    third = await service.handle_message(session.session_id, "Dat lich kham ao")
    assert third.response_type == "ask_booking_details"

    fourth = await service.handle_message(session.session_id, "Times City, sang mai")
    assert fourth.response_type == "booking_confirmation"

    final = await service.handle_message(session.session_id, "Xac nhan")
    assert final.response_type == "booking_created"
    assert final.booking is not None
    assert final.booking.booking_status == "draft"

    doctor_cases = service.list_doctor_cases()
    assert doctor_cases[0].booking_status == "draft"


@pytest.mark.asyncio
async def test_red_flag_overrides_normal_flow_and_blocks_booking():
    service = SmartIntakeService()
    session = service.create_session()

    response = await service.handle_message(session.session_id, "Toi dau nguc va kho tho.")

    assert response.response_type == "emergency_handoff"
    assert response.case.priority == "high"
    assert response.case.red_flag_status == "confirmed"
    assert response.case.booking_id is None


def test_doctor_notes_and_audit_logs_are_stored():
    service = SmartIntakeService()
    session = service.create_session()

    service.add_doctor_note(session.case_id, "CSKH called patient.")
    logs = service.list_audit_logs(session.case_id)

    assert service.get_case(session.case_id).doctor_notes == ["CSKH called patient."]
    assert logs[0].event == "session_created"


@pytest.mark.asyncio
async def test_intake_chat_uses_ai_and_search_context_for_safe_guidance():
    llm = FakeLLM()
    search = FakeMedicalSearch()
    service = SmartIntakeService(llm=llm, context_search=search)
    session = service.create_session()

    await service.handle_message(
        session.session_id,
        "Toi dau da day, day hoi kho tieu 2 tuan nay.",
    )
    response = await service.handle_message(
        session.session_id,
        "Me toi 58 tuoi, dau vua.",
    )

    assert response.assistant_text.startswith("AI:")
    assert response.sources[0].url == "https://example.com/digestive"
    assert search.queries == ["dau da day, day hoi, kho tieu", "dau da day, day hoi, kho tieu"]
    assert "Evidence context" in llm.prompts[-1]


@pytest.mark.asyncio
async def test_red_flag_does_not_call_ai_safe_guidance():
    llm = FakeLLM()
    service = SmartIntakeService(llm=llm)
    session = service.create_session()

    response = await service.handle_message(session.session_id, "Toi dau nguc va kho tho.")

    assert response.response_type == "emergency_handoff"
    assert llm.prompts == []
