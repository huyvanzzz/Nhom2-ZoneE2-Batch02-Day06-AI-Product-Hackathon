from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from vinm_backend.models import SourceRef


EMERGENCY_CONTACTS = [
    {
        "name": "Vinmec Times City",
        "phone": "024 3974 3556",
        "address": "Số 458 Minh Khai, Hà Nội",
    },
    {
        "name": "Vinmec Smart City",
        "phone": "024 3208 5678",
        "address": "Số 2A đường Tây Mỗ, Hà Nội",
    },
    {
        "name": "Vinmec Central Park",
        "phone": "028 3622 1166",
        "address": "720A Điện Biên Phủ, TP. Hồ Chí Minh",
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_text(value: str) -> str:
    lowered = value.lower()
    decomposed = unicodedata.normalize("NFD", lowered)
    ascii_text = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return ascii_text.replace("đ", "d").replace("Đ", "d")


def _extract_time_label(normalized: str) -> str | None:
    if "sang mai" in normalized:
        return "Sáng mai"
    if "chieu mai" in normalized:
        return "Chiều mai"
    if "toi nay" in normalized:
        return "Tối nay"
    if "cuoi tuan" in normalized:
        return "Cuối tuần"

    hour_match = re.search(r"\b(\d{1,2})\s*(gio|h)\b(?:\s*(chieu|toi|sang|trua))?", normalized)
    if not hour_match:
        return None

    hour = int(hour_match.group(1))
    suffix = hour_match.group(3) or ""
    if suffix in {"chieu", "toi"} and hour < 12:
        hour += 12
    suffix_label = {
        "chieu": "chiều",
        "toi": "tối",
        "sang": "sáng",
        "trua": "trưa",
    }.get(suffix, "")
    if suffix_label:
        return f"{hour:02d}:00 {suffix_label}".strip()
    return f"{hour:02d}:00"


def _extract_hospital_label(normalized: str) -> str | None:
    if any(term in normalized for term in ["times city", "vinmec times city"]):
        return "Vinmec Times City"
    if any(term in normalized for term in ["smart city", "vin smart city", "vinmec smart city"]):
        return "Vinmec Smart City"
    if "central park" in normalized:
        return "Vinmec Central Park"
    if "da nang" in normalized:
        return "Vinmec Da Nang"
    return None


class IntakeSession(BaseModel):
    session_id: str
    case_id: str
    patient_id: str
    created_at: str


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    created_at: str = Field(default_factory=_now_iso)


class ChatMessageRequest(BaseModel):
    session_id: str
    content: str


class PatientInfo(BaseModel):
    patient_id: str
    full_name: str = "unknown"
    age_or_birth_year: str = "unknown"
    gender: str = "unknown"
    relationship_to_customer: str = "unknown"
    phone: str | None = None


class BookingDraft(BaseModel):
    booking_id: str
    case_id: str
    patient_id: str
    specialty: str
    hospital: str
    preferred_time: str
    preferred_time_detail: str = "unknown"
    requested_at: str = Field(default_factory=_now_iso)
    booking_status: Literal["draft", "cancelled", "confirmed"] = "draft"
    doctor_summary_attached: bool = True


class IntakeCase(BaseModel):
    case_id: str
    session_id: str
    patient_id: str
    main_symptom: str = "unknown"
    duration: str = "unknown"
    severity: str = "unknown"
    associated_symptoms: list[str] = Field(default_factory=list)
    red_flag_status: Literal["unknown", "none", "suspected", "confirmed"] = "unknown"
    red_flags: list[str] = Field(default_factory=list)
    ai_triage_level: Literal["unknown", "low", "medium", "high"] = "unknown"
    ai_triage_reason: str = ""
    priority: Literal["low", "medium", "high"] = "medium"
    suggested_specialty: str = "unknown"
    case_status: str = "new"
    booking_id: str | None = None
    booking_intent: bool = False
    preferred_hospital: str = "unknown"
    preferred_time: str = "unknown"
    preferred_time_detail: str = "unknown"
    doctor_summary: str = ""
    evidence_context: dict = Field(default_factory=dict)
    sources: list[SourceRef] = Field(default_factory=list)
    doctor_notes: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=_now_iso)
    updated_at: str = Field(default_factory=_now_iso)


class DoctorCaseRow(BaseModel):
    case_id: str
    patient: str
    age_or_birth_year: str
    main_symptom: str
    red_flag_status: str
    priority: str
    suggested_specialty: str
    booking_status: str
    created_at: str


class AuditLog(BaseModel):
    case_id: str
    event: str
    detail: str
    created_at: str = Field(default_factory=_now_iso)


class IntakeResponse(BaseModel):
    response_type: str
    assistant_text: str
    quick_replies: list[str] = Field(default_factory=list)
    case: IntakeCase
    patient: PatientInfo
    booking: BookingDraft | None = None
    doctor_summary: str = ""
    sources: list[SourceRef] = Field(default_factory=list)


class IntakeExtractorTool:
    def extract(self, message: str) -> dict:
        normalized = _normalize_text(message)
        slots: dict[str, object] = {}

        if "me toi" in normalized or "ma toi" in normalized:
            slots["patient_relation"] = "mother"
        elif "bo toi" in normalized or "ba toi" in normalized:
            slots["patient_relation"] = "father"
        elif "con toi" in normalized:
            slots["patient_relation"] = "child"
        elif "toi" in normalized:
            slots["patient_relation"] = "self"

        age_match = re.search(r"\b(\d{1,3})\s*(tuoi|t)\b", normalized)
        if age_match:
            slots["age_or_birth_year"] = age_match.group(1)

        if any(term in normalized for term in ["da day", "day hoi", "kho tieu", "dau bung"]):
            slots["main_symptom"] = "dau da day, day hoi, kho tieu"
            slots["suggested_specialty"] = "Noi Tieu hoa"
        elif any(term in normalized for term in ["dau dau", "sot", "sot nong", "ho"]):
            symptoms = []
            if "dau dau" in normalized:
                symptoms.append("dau dau")
            if "sot" in normalized or "sot nong" in normalized:
                symptoms.append("sot")
            if "ho" in normalized:
                symptoms.append("ho")
            slots["main_symptom"] = ", ".join(symptoms) or "trieu chung toan than"
            slots["suggested_specialty"] = "Noi Tong quat"
        elif any(term in normalized for term in ["dau nguc", "kho tho"]):
            slots["main_symptom"] = "dau nguc, kho tho"
            slots["suggested_specialty"] = "Cap cuu"

        if "2 tuan" in normalized or "hai tuan" in normalized:
            slots["duration"] = "2 tuan"
        elif "may ngay" in normalized:
            slots["duration"] = "may ngay"

        if "rat nang" in normalized or "khong chiu duoc" in normalized:
            slots["severity"] = "rat nang"
        elif "nang" in normalized:
            slots["severity"] = "nang"
        elif "vua" in normalized:
            slots["severity"] = "vua"
        elif "nhe" in normalized:
            slots["severity"] = "nhe"

        if "dat lich" in normalized or "kham ao" in normalized:
            slots["booking_intent"] = True
        if hospital := _extract_hospital_label(normalized):
            slots["preferred_hospital"] = hospital
        if preferred_time := _extract_time_label(normalized):
            slots["preferred_time"] = preferred_time
            slots["preferred_time_detail"] = preferred_time

        return slots


class MedicalContextSearchTool:
    def __init__(self, tavily=None, firecrawl=None):
        self.tavily = tavily
        self.firecrawl = firecrawl

    async def search(self, case: IntakeCase) -> tuple[dict, list[SourceRef]]:
        fallback_context = {
            "warning_signs": [],
            "safe_guidance_points": [],
            "possible_specialties": [],
        }
        if case.suggested_specialty == "Noi Tieu hoa":
            fallback_context = {
                "warning_signs": [
                    "dau bung du doi",
                    "non ra mau",
                    "di ngoai phan den",
                    "sot cao",
                ],
                "safe_guidance_points": [
                    "an nhe",
                    "uong du nuoc",
                    "tranh do cay, dau mo, ruou bia",
                ],
                "possible_specialties": ["Noi Tieu hoa"],
            }
            fallback_sources = [
                SourceRef(
                    title="Vinmec digestive symptom guidance",
                    url="https://www.vinmec.com/",
                    summary="Trusted context placeholder for demo intake guidance.",
                )
            ]
        elif case.suggested_specialty == "Noi Tong quat":
            fallback_context = {
                "warning_signs": [
                    "sot cao keo dai",
                    "kho tho",
                    "lo mo",
                    "dau dau du doi",
                ],
                "safe_guidance_points": [
                    "uong du nuoc",
                    "nghi ngoi",
                    "theo doi nhiet do",
                ],
                "possible_specialties": ["Noi Tong quat"],
            }
            fallback_sources = [
                SourceRef(
                    title="General fever and cough guidance",
                    url="https://www.vinmec.com/",
                    summary="General safe guidance placeholder for demo intake.",
                )
            ]
        else:
            fallback_sources = []

        if not self.tavily:
            return fallback_context, fallback_sources

        query = (
            f"{case.main_symptom} {case.duration} warning signs when to seek care "
            "Vinmec NHS Mayo Clinic MedlinePlus"
        )
        try:
            sources = await self.tavily.search(query)
            scraped_points = []
            if self.firecrawl:
                for source in sources[:2]:
                    try:
                        scraped_points.append(await self.firecrawl.scrape(source.url))
                    except Exception:
                        continue
            context = {
                **fallback_context,
                "search_query": query,
                "scraped_context": scraped_points[:2],
            }
            return context, sources[:5] or fallback_sources
        except Exception:
            return fallback_context, fallback_sources


class TriageSafetyRuleTool:
    RED_FLAGS = {
        "dau nguc": "dau nguc",
        "kho tho": "kho tho",
        "sot 40": "sot 40 do",
        "chay mau nhieu": "chay mau nhieu",
        "dau bung du doi": "dau bung du doi",
        "non ra mau": "non ra mau",
        "phan den": "di ngoai phan den",
        "ngat": "ngat",
        "lo mo": "lo mo",
        "co giat": "co giat",
        "sung moi": "sung moi/mat/luoi",
        "sung mat": "sung moi/mat/luoi",
        "sung luoi": "sung moi/mat/luoi",
    }

    def classify(self, case: IntakeCase, message: str) -> IntakeCase:
        normalized = _normalize_text(message)
        red_flags = [label for term, label in self.RED_FLAGS.items() if term in normalized]
        if red_flags:
            case.red_flag_status = "confirmed"
            case.red_flags = sorted(set(case.red_flags + red_flags))
            case.priority = "high"
            case.case_status = "red_flag_detected"
            return case

        case.red_flag_status = "none"
        if case.severity in {"nang", "rat nang"}:
            case.priority = "high" if case.severity == "rat nang" else "medium"
        elif case.duration != "unknown":
            case.priority = "medium"
        else:
            case.priority = "low"
        return case


class ChatResponseSummaryTool:
    def __init__(self, llm=None):
        self.llm = llm

    async def build(self, case: IntakeCase, patient: PatientInfo, booking: BookingDraft | None) -> IntakeResponse:
        if case.red_flag_status == "confirmed":
            text = self._build_emergency_text(case)
            return IntakeResponse(
                response_type="emergency_handoff",
                assistant_text=text,
                quick_replies=["Gọi hotline Vinmec", "Đến cấp cứu gần nhất"],
                case=case,
                patient=patient,
                booking=None,
                doctor_summary=case.doctor_summary,
                sources=case.sources,
            )

        missing = []
        if case.main_symptom == "unknown":
            missing.append("trieu chung")
        if patient.age_or_birth_year == "unknown":
            missing.append("tuoi")
        if case.severity == "unknown":
            missing.append("muc do")
        if missing and not case.booking_intent:
            if missing == ["tuoi"]:
                assistant_text = "Cho mình xin tuổi hoặc năm sinh của người bệnh?"
                quick_replies = ["Tôi 25 tuổi", "Tôi 30 tuổi", "Mẹ tôi 58 tuổi", "Bố tôi 65 tuổi"]
            elif missing == ["muc do"]:
                assistant_text = "Mình đã ghi nhận tuổi. Mức độ khó chịu hiện tại của người bệnh là mức nào?"
                quick_replies = ["Nhẹ", "Vừa", "Nặng", "Rất nặng/không chịu được"]
            elif missing == ["trieu chung"]:
                assistant_text = "Bạn mô tả rõ hơn triệu chứng chính giúp mình được không?"
                quick_replies = ["Đau đầu và sốt", "Đau bụng", "Đau ngực/khó thở", "Ho và sốt"]
            else:
                assistant_text = "Mình cần hỏi thêm tuổi người bệnh và mức độ khó chịu hiện tại."
                quick_replies = ["Nhẹ", "Vừa", "Nặng", "Rất nặng/không chịu được"]
            assistant_text = await self._ask_more_text(case, patient, missing, assistant_text)
            return IntakeResponse(
                response_type="ask_more",
                assistant_text=assistant_text,
                quick_replies=quick_replies,
                case=case,
                patient=patient,
                doctor_summary=case.doctor_summary,
                sources=case.sources,
            )

        if case.booking_intent and case.preferred_hospital == "unknown":
            return IntakeResponse(
                response_type="ask_booking_details",
                assistant_text=(
                    "Mình đã ghi nhận nhu cầu đặt lịch. "
                    "Bạn muốn khám tại cơ sở Vinmec nào và vào khung giờ cụ thể nào? "
                    "Ví dụ: Vinmec Times City, 15 giờ chiều nay."
                ),
                quick_replies=[
                    "Vinmec Times City, 15 giờ chiều nay",
                    "Vinmec Smart City, 15 giờ chiều nay",
                    "Vinmec Central Park, sáng mai",
                    "Chưa chắc",
                ],
                case=case,
                patient=patient,
                doctor_summary=case.doctor_summary,
                sources=case.sources,
            )

        if case.booking_intent and booking is None:
            return IntakeResponse(
                response_type="booking_confirmation",
                assistant_text=(
                    "Mình xác nhận lại thông tin trước khi tạo lịch khám nháp: "
                    f"người bệnh {patient.relationship_to_customer}, tuổi {patient.age_or_birth_year}, "
                    f"khoa {case.suggested_specialty}, cơ sở {case.preferred_hospital}, "
                    f"thời gian {case.preferred_time_detail if case.preferred_time_detail != 'unknown' else case.preferred_time}. "
                    "Mình đã có đủ thông tin cơ bản và sẽ lưu hồ sơ, giờ khám, tóm tắt ca và nguồn tham khảo. "
                    "Bạn muốn tạo lịch nháp không?"
                ),
                quick_replies=["Xác nhận", "Sửa thông tin", "Hủy"],
                case=case,
                patient=patient,
                doctor_summary=case.doctor_summary,
                sources=case.sources,
            )

        if booking is not None:
            return IntakeResponse(
                response_type="booking_created",
                assistant_text=(
                    "Mình đã tạo lịch khám nháp và lưu lại hồ sơ người dùng, thời gian khám chi tiết, "
                    "tóm tắt ca bệnh, nguồn tham khảo và trạng thái đặt lịch. "
                    "Bác sĩ/CSKH sẽ xem được đầy đủ thông tin trước khi hỗ trợ tiếp."
                ),
                quick_replies=["Xem lại thông tin", "Kết thúc"],
                case=case,
                patient=patient,
                booking=booking,
                doctor_summary=case.doctor_summary,
                sources=case.sources,
            )

        assistant_text = await self._safe_guidance_text(case, patient)
        return IntakeResponse(
            response_type="safe_guidance",
            assistant_text=assistant_text,
            quick_replies=["Đặt lịch khám nháp", "Chọn thời gian khác", "Tôi muốn hỏi thêm"],
            case=case,
            patient=patient,
            doctor_summary=case.doctor_summary,
            sources=case.sources,
        )

    async def _safe_guidance_text(self, case: IntakeCase, patient: PatientInfo) -> str:
        source_text = self._format_sources(case.sources)
        fallback = (
            "Mình đã kiểm tra ngữ cảnh y tế liên quan và hiện chưa thấy dấu hiệu khẩn cấp rõ ràng từ thông tin bạn cung cấp. "
            "Đây là nhận định sơ bộ, không phải chẩn đoán y khoa. "
            f"Dựa trên triệu chứng hiện tại và nguồn tham khảo đã kiểm tra{source_text}, "
            f"bạn nên ưu tiên khám {case.suggested_specialty} tại Vinmec sớm hơn nếu triệu chứng kéo dài, lặp lại hoặc tăng mức độ. "
            "Nếu có sốt cao, khó thở, đau ngực, nôn ra máu, đi ngoài phân đen hoặc lơ mơ, hãy đi cấp cứu ngay. "
            "Nếu bạn muốn, mình có thể tạo lịch khám nháp ngay trong chat."
        )
        if not self.llm:
            return fallback

        prompt = (
            "Pha: safe_guidance.\n"
            "Vai trò: trợ lý tiếp nhận Vinmec, không chẩn đoán bệnh, không kê thuốc, không bỏ qua hardcoded red flags.\n"
            "Mục tiêu: phản hồi dài hơn 4-6 câu bằng tiếng Việt, dựa trên nguồn đã tìm kiếm để giải thích ngắn gọn vì sao nên ưu tiên khám sớm hay có thể theo dõi tại nhà.\n"
            "Bắt buộc gồm 4 phần:\n"
            "1) Tóm tắt tình trạng hiện tại của người bệnh.\n"
            "2) Nêu nhận định sơ bộ về mức độ ưu tiên khám.\n"
            "3) Dựa trên evidence_context và sources để gợi ý chuyên khoa hoặc cơ sở Vinmec phù hợp.\n"
            "4) Hỏi người dùng có muốn tạo lịch khám nháp trong chat không.\n"
            "Nếu nguồn chưa đủ thì nói rõ là đang dùng ngữ cảnh tham khảo và chỉ đề xuất an toàn.\n"
            f"Patient relation: {patient.relationship_to_customer}\n"
            f"Age or birth year: {patient.age_or_birth_year}\n"
            f"Main symptom: {case.main_symptom}\n"
            f"Duration: {case.duration}\n"
            f"Severity: {case.severity}\n"
            f"Suggested specialty: {case.suggested_specialty}\n"
            f"Priority: {case.priority}\n"
            f"Evidence context: {case.evidence_context}\n"
            f"Sources: {self._format_sources(case.sources)}\n"
            "Return a short Vietnamese chat reply with safe initial guidance, specialty suggestion, and a question asking whether the user wants a virtual booking.\n"
        )
        try:
            assistant_text = await self.llm.complete(prompt)
            return self._enrich_safe_guidance_text(assistant_text, case)
        except Exception:
            return fallback

    async def _ask_more_text(
        self,
        case: IntakeCase,
        patient: PatientInfo,
        missing: list[str],
        fallback: str,
    ) -> str:
        if not self.llm:
            return fallback
        prompt = (
            "Pha: ask_more.\n"
            "Chỉ hỏi lại thông tin còn thiếu, không gọi search, không chẩn đoán, không nói về nguồn, không kê thuốc.\n"
            "Chỉ được hỏi đúng 1 câu ngắn bằng tiếng Việt.\n"
            f"Missing fields: {missing}\n"
            f"Current symptom: {case.main_symptom}\n"
            f"Current duration: {case.duration}\n"
            f"Current severity: {case.severity}\n"
            "Ask one follow-up question for a Vinmec intake chat in Vietnamese.\n"
            f"Patient age: {patient.age_or_birth_year}\n"
        )
        try:
            return await self.llm.complete(prompt)
        except Exception:
            return fallback

    def _format_sources(self, sources: list[SourceRef]) -> str:
        if not sources:
            return ""
        top_sources = ", ".join(source.title for source in sources[:3])
        return f" ({top_sources})"

    def _build_emergency_text(self, case: IntakeCase) -> str:
        preferred_contacts = []
        if case.preferred_hospital != "unknown":
            preferred_contacts = [
                contact for contact in EMERGENCY_CONTACTS if contact["name"] == case.preferred_hospital
            ]
        contacts = preferred_contacts or EMERGENCY_CONTACTS[:3]
        contact_lines = [
            f"- {contact['name']}: {contact['phone']} - {contact['address']}"
            for contact in contacts
        ]
        return (
            "Đây là tình huống khẩn cấp. Mình đã khóa phiên chat này để không tiếp tục khai thác thêm ngữ cảnh. "
            "Bạn không cần gửi thêm triệu chứng trong khung chat.\n\n"
            "Việc cần làm ngay:\n"
            "- Gọi cấp cứu địa phương nếu triệu chứng đang nặng lên hoặc bạn thấy không an toàn.\n"
            "- Gọi hotline Vinmec của một trong các cơ sở dưới đây ngay để được hướng dẫn chuyển tiếp:\n"
            + "\n".join(contact_lines)
            + "\n\nNếu bạn không thể gọi, hãy nhờ người nhà đưa đến cơ sở y tế gần nhất ngay lập tức."
        )

    def _enrich_safe_guidance_text(self, assistant_text: str, case: IntakeCase) -> str:
        normalized = _normalize_text(assistant_text)
        if "nguon" in normalized and "vinmec" in normalized and "dat lich" in normalized:
            return assistant_text

        source_text = self._format_sources(case.sources)
        tail = [
            f"Dựa trên nguồn tham khảo đã kiểm tra{source_text}, mình gợi ý ưu tiên khám {case.suggested_specialty} tại Vinmec sớm hơn nếu triệu chứng kéo dài hoặc tăng mức độ.",
            "Nếu bạn muốn, mình có thể tạo lịch khám nháp ngay trong chat và lưu đầy đủ hồ sơ, giờ khám chi tiết, tóm tắt ca bệnh cùng nguồn tham khảo.",
        ]
        return assistant_text.rstrip() + "\n\n" + " ".join(tail)


class SmartIntakeService:
    def __init__(self, llm=None, context_search: MedicalContextSearchTool | None = None):
        self.llm = llm
        self.extractor = IntakeExtractorTool()
        self.context_search = context_search or MedicalContextSearchTool()
        self.triage = TriageSafetyRuleTool()
        self.response_builder = ChatResponseSummaryTool(llm=llm)
        self.sessions: dict[str, IntakeSession] = {}
        self.patients: dict[str, PatientInfo] = {}
        self.cases: dict[str, IntakeCase] = {}
        self.messages: dict[str, list[ChatMessage]] = {}
        self.bookings: dict[str, BookingDraft] = {}
        self.audit_logs: dict[str, list[AuditLog]] = {}
        self._session_counter = 0
        self._case_counter = 0
        self._patient_counter = 0
        self._booking_counter = 0

    def create_session(self) -> IntakeSession:
        self._session_counter += 1
        self._case_counter += 1
        self._patient_counter += 1
        session_id = f"sess_{self._session_counter:03d}"
        case_id = f"case_{self._case_counter:03d}"
        patient_id = f"pat_{self._patient_counter:03d}"
        session = IntakeSession(
            session_id=session_id,
            case_id=case_id,
            patient_id=patient_id,
            created_at=_now_iso(),
        )
        self.sessions[session_id] = session
        self.patients[patient_id] = PatientInfo(patient_id=patient_id)
        self.cases[case_id] = IntakeCase(case_id=case_id, session_id=session_id, patient_id=patient_id)
        self.messages[session_id] = []
        self.audit_logs[case_id] = []
        self._log(case_id, "session_created", session_id)
        return session

    async def handle_message(self, session_id: str, content: str) -> IntakeResponse:
        session = self.sessions[session_id]
        case = self.cases[session.case_id]
        patient = self.patients[session.patient_id]
        if case.red_flag_status == "confirmed" or case.case_status == "red_flag_detected":
            self._log(case.case_id, "blocked_user_message", content)
            response = await self.response_builder.build(case, patient, None)
            self._log(case.case_id, "assistant_response", response.response_type)
            return response

        self.messages[session_id].append(ChatMessage(role="user", content=content))
        self._log(case.case_id, "user_message", content)

        slots = self.extractor.extract(content)
        self._apply_slots(case, patient, slots)
        case = self.triage.classify(case, content)
        if self._has_minimum_intake(case, patient) and case.red_flag_status != "confirmed":
            case.evidence_context, case.sources = await self.context_search.search(case)
            case = await self._classify_with_ai(case, patient)
        case.doctor_summary = await self._build_doctor_summary(
            case,
            patient,
            use_ai=case.red_flag_status != "confirmed",
        )
        self.cases[case.case_id] = case

        booking = None
        if case.booking_intent and "xac nhan" in _normalize_text(content):
            booking = self._create_booking(case, patient)
            case.booking_id = booking.booking_id
            case.case_status = "booking_requested"
            self.cases[case.case_id] = case

        response = await self.response_builder.build(case, patient, booking)
        self.messages[session_id].append(ChatMessage(role="assistant", content=response.assistant_text))
        self._log(case.case_id, "assistant_response", response.response_type)
        return response

    def list_messages(self, session_id: str) -> list[ChatMessage]:
        return self.messages[session_id]

    def get_case(self, case_id: str) -> IntakeCase:
        return self.cases[case_id]

    def patch_case(self, case_id: str, patch: dict) -> IntakeCase:
        case = self.cases[case_id].model_copy(update=patch | {"updated_at": _now_iso()})
        self.cases[case_id] = case
        self._log(case_id, "case_patched", str(sorted(patch.keys())))
        return case

    def create_booking_draft(self, case_id: str, hospital: str, preferred_time: str) -> BookingDraft:
        case = self.cases[case_id]
        patient = self.patients[case.patient_id]
        case.preferred_hospital = hospital
        case.preferred_time = preferred_time
        case.preferred_time_detail = preferred_time
        booking = self._create_booking(case, patient)
        case.booking_id = booking.booking_id
        case.case_status = "booking_requested"
        self.cases[case_id] = case
        return booking

    def get_booking(self, booking_id: str) -> BookingDraft:
        return self.bookings[booking_id]

    def patch_booking(self, booking_id: str, patch: dict) -> BookingDraft:
        booking = self.bookings[booking_id].model_copy(update=patch)
        self.bookings[booking_id] = booking
        self._log(booking.case_id, "booking_patched", str(sorted(patch.keys())))
        return booking

    def list_doctor_cases(self) -> list[DoctorCaseRow]:
        rows = []
        for case in self.cases.values():
            patient = self.patients[case.patient_id]
            booking_status = "none"
            if case.booking_id:
                booking_status = self.bookings[case.booking_id].booking_status
            rows.append(
                DoctorCaseRow(
                    case_id=case.case_id,
                    patient=patient.relationship_to_customer,
                    age_or_birth_year=patient.age_or_birth_year,
                    main_symptom=case.main_symptom,
                    red_flag_status=case.red_flag_status,
                    priority=case.priority,
                    suggested_specialty=case.suggested_specialty,
                    booking_status=booking_status,
                    created_at=case.created_at,
                )
            )
        return rows

    def add_doctor_note(self, case_id: str, note: str) -> IntakeCase:
        case = self.cases[case_id]
        case.doctor_notes.append(note)
        case.updated_at = _now_iso()
        self._log(case_id, "doctor_note_added", note)
        return case

    def patch_case_status(self, case_id: str, status: str) -> IntakeCase:
        case = self.cases[case_id]
        case.case_status = status
        case.updated_at = _now_iso()
        self._log(case_id, "case_status_updated", status)
        return case

    def list_audit_logs(self, case_id: str) -> list[AuditLog]:
        return self.audit_logs[case_id]

    def _apply_slots(self, case: IntakeCase, patient: PatientInfo, slots: dict) -> None:
        if relation := slots.get("patient_relation"):
            patient.relationship_to_customer = str(relation)
        if age := slots.get("age_or_birth_year"):
            patient.age_or_birth_year = str(age)
        for key in [
            "main_symptom",
            "duration",
            "severity",
            "suggested_specialty",
            "preferred_hospital",
            "preferred_time",
            "preferred_time_detail",
        ]:
            if value := slots.get(key):
                setattr(case, key, value)
        if slots.get("booking_intent"):
            case.booking_intent = True

    def _has_minimum_intake(self, case: IntakeCase, patient: PatientInfo) -> bool:
        return (
            case.main_symptom != "unknown"
            and case.severity != "unknown"
            and patient.age_or_birth_year != "unknown"
        )

    def _create_booking(self, case: IntakeCase, patient: PatientInfo) -> BookingDraft:
        self._booking_counter += 1
        booking = BookingDraft(
            booking_id=f"book_{self._booking_counter:03d}",
            case_id=case.case_id,
            patient_id=patient.patient_id,
            specialty=case.suggested_specialty,
            hospital=case.preferred_hospital,
            preferred_time=case.preferred_time,
            preferred_time_detail=case.preferred_time_detail,
        )
        self.bookings[booking.booking_id] = booking
        self._log(case.case_id, "booking_draft_created", booking.booking_id)
        return booking

    async def _build_doctor_summary(
        self,
        case: IntakeCase,
        patient: PatientInfo,
        use_ai: bool = True,
    ) -> str:
        fallback = (
            f"Người bệnh: {patient.relationship_to_customer}, {patient.age_or_birth_year} tuổi. "
            f"Triệu chứng chính: {case.main_symptom}. Thời gian: {case.duration}. "
            f"Mức độ: {case.severity}. Red flag: {case.red_flag_status}. "
            f"Chuyên khoa gợi ý: {case.suggested_specialty}. "
            f"Cơ sở: {case.preferred_hospital}. Giờ khám: {case.preferred_time_detail if case.preferred_time_detail != 'unknown' else case.preferred_time}. "
            f"Trạng thái: {case.case_status}. "
            f"Nguồn tham khảo: {self.response_builder._format_sources(case.sources)}"
        )
        if not self.llm or not use_ai:
            return fallback
        prompt = (
            "Pha: doctor_summary.\n"
            "Tạo tóm tắt bàn giao cho bác sĩ/CSKH bằng tiếng Việt, 5-8 câu, ngắn gọn nhưng đủ chi tiết.\n"
            "Không chẩn đoán bệnh, không kê thuốc.\n"
            "Bắt buộc nhắc: quan hệ người bệnh, tuổi, triệu chứng chính, thời gian, mức độ, trạng thái red flag, "
            "ưu tiên khám, chuyên khoa gợi ý, cơ sở/giờ khám nếu có, và nguồn tham khảo đã dùng.\n"
            "Create doctor handoff summary in Vietnamese for Vinmec CSKH/doctor dashboard.\n"
            f"Patient: {patient.model_dump()}\n"
            f"Case: {case.model_dump()}\n"
        )
        try:
            return await self.llm.complete(prompt)
        except Exception:
            return fallback

    async def _classify_with_ai(self, case: IntakeCase, patient: PatientInfo) -> IntakeCase:
        fallback_level = case.priority
        case.ai_triage_level = fallback_level
        case.ai_triage_reason = (
            f"{fallback_level}: phân loại sơ bộ dựa trên thời gian, mức độ và dấu hiệu nguy hiểm đã kiểm tra."
        )
        if not self.llm:
            return case
        prompt = (
            "Pha: triage_classification.\n"
            "Chỉ phân loại nguy cơ sơ bộ thành low/medium/high dựa trên triệu chứng, thời gian, mức độ và ngữ cảnh đã tìm kiếm.\n"
            "Không chẩn đoán bệnh, không bỏ qua hardcoded red flags, không kê thuốc.\n"
            "Trả về đúng 1 dòng theo dạng '<low|medium|high>: reason'.\n"
            "Classify preliminary risk for a Vinmec intake case in Vietnamese.\n"
            f"Patient: {patient.model_dump()}\n"
            f"Case: {case.model_dump()}\n"
            f"Evidence context: {case.evidence_context}\n"
        )
        try:
            result = await self.llm.complete(prompt)
        except Exception:
            return case
        normalized = _normalize_text(result)
        if normalized.startswith("high"):
            case.ai_triage_level = "high"
        elif normalized.startswith("low"):
            case.ai_triage_level = "low"
        else:
            case.ai_triage_level = "medium"
        case.ai_triage_reason = result
        if case.ai_triage_level == "high":
            case.priority = "high"
        return case

    def _log(self, case_id: str, event: str, detail: str) -> None:
        self.audit_logs.setdefault(case_id, []).append(AuditLog(case_id=case_id, event=event, detail=detail))
