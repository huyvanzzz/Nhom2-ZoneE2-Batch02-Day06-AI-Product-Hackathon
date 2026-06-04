from fastapi import FastAPI

from vinm_backend.intake import ChatMessageRequest, SmartIntakeService
from vinm_backend.models import AssistRequest
from vinm_backend.orchestrator import ResearchFlow


def create_app(flow: ResearchFlow, intake: SmartIntakeService | None = None) -> FastAPI:
    app = FastAPI()
    intake_service = intake or SmartIntakeService()

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/v1/assist")
    async def assist(payload: AssistRequest):
        return await flow.run(payload)

    @app.post("/chat/session")
    async def create_chat_session():
        return intake_service.create_session()

    @app.post("/chat/message")
    async def chat_message(payload: ChatMessageRequest):
        return await intake_service.handle_message(payload.session_id, payload.content)

    @app.get("/chat/session/{session_id}/messages")
    async def chat_messages(session_id: str):
        return intake_service.list_messages(session_id)

    @app.get("/cases/{case_id}")
    async def get_case(case_id: str):
        return intake_service.get_case(case_id)

    @app.patch("/cases/{case_id}")
    async def patch_case(case_id: str, payload: dict):
        return intake_service.patch_case(case_id, payload)

    @app.post("/booking/draft")
    async def create_booking_draft(payload: dict):
        return intake_service.create_booking_draft(
            case_id=payload["case_id"],
            hospital=payload["hospital"],
            preferred_time=payload["preferred_time"],
        )

    @app.get("/booking/{booking_id}")
    async def get_booking(booking_id: str):
        return intake_service.get_booking(booking_id)

    @app.patch("/booking/{booking_id}")
    async def patch_booking(booking_id: str, payload: dict):
        return intake_service.patch_booking(booking_id, payload)

    @app.get("/doctor/cases")
    async def doctor_cases():
        return intake_service.list_doctor_cases()

    @app.get("/doctor/cases/{case_id}")
    async def doctor_case_detail(case_id: str):
        return intake_service.get_case(case_id)

    @app.post("/doctor/cases/{case_id}/notes")
    async def add_doctor_note(case_id: str, payload: dict):
        return intake_service.add_doctor_note(case_id, payload["note"])

    @app.patch("/doctor/cases/{case_id}/status")
    async def patch_case_status(case_id: str, payload: dict):
        return intake_service.patch_case_status(case_id, payload["status"])

    @app.get("/debug/cases/{case_id}/logs")
    async def audit_logs(case_id: str):
        return intake_service.list_audit_logs(case_id)

    return app
