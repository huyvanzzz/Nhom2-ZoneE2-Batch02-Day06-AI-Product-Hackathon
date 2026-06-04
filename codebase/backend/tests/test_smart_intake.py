import pytest

from vinm_backend.intake import SmartIntakeService


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
