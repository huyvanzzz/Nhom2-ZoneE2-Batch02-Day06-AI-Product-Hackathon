from __future__ import annotations

import re
import unicodedata
import json
from datetime import datetime, timezone
from typing import Literal
from urllib.parse import urlparse

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

TRUSTED_MEDICAL_DOMAINS = [
    "vinmec.com",
    "mayoclinic.org",
    "nhs.uk",
    "medlineplus.gov",
    "cdc.gov",
    "who.int",
    "clevelandclinic.org",
    "healthdirect.gov.au",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_text(value: str) -> str:
    lowered = value.lower()
    decomposed = unicodedata.normalize("NFD", lowered)
    ascii_text = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return ascii_text.replace("đ", "d").replace("Đ", "d")


def _contains_term(normalized: str, term: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(term).replace(r"\ ", r"\s+") + r"(?!\w)"
    return re.search(pattern, normalized) is not None


def _contains_any_term(normalized: str, terms: list[str]) -> bool:
    return any(_contains_term(normalized, term) for term in terms)


def _extract_time_label(normalized: str) -> str | None:
    if "sang mai" in normalized:
        return "Sáng mai"
    if "chieu mai" in normalized:
        return "Chiều mai"
    if "toi nay" in normalized:
        return "Tối nay"
    if "cuoi tuan" in normalized:
        return "Cuối tuần"

    clock_match = re.search(r"\b(\d{1,2}):(\d{2})\s*(chieu|toi|sang|trua)?\b", normalized)
    if clock_match:
        hour = int(clock_match.group(1))
        minute = int(clock_match.group(2))
        suffix = clock_match.group(3) or ""
        if suffix in {"chieu", "toi"} and hour < 12:
            hour += 12
        suffix_label = {
            "chieu": "chiá»u",
            "toi": "tá»‘i",
            "sang": "sÃ¡ng",
            "trua": "trÆ°a",
        }.get(suffix, "")
        if suffix_label:
            return f"{hour:02d}:{minute:02d} {suffix_label}".strip()
        return f"{hour:02d}:{minute:02d}"

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
    if "vinmec" in normalized:
        return "Vinmec"
    return None


def _domain_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.lower().removeprefix("www.")


def _is_trusted_domain(url: str, domains: list[str]) -> bool:
    domain = _domain_from_url(url)
    return any(domain == allowed or domain.endswith(f".{allowed}") for allowed in domains)


def _case_search_phrase(case: "IntakeCase") -> str:
    if case.suggested_specialty == "Noi Tieu hoa":
        return "dau da day day hoi kho tieu"
    if case.suggested_specialty == "Cap cuu":
        return "dau nguc kho tho cap cuu"
    if case.suggested_specialty == "Noi Tong quat":
        return "dau dau sot ho"
    if case.main_symptom != "unknown":
        return case.main_symptom
    return case.suggested_specialty


def _display_specialty(value: str) -> str:
    display_map = {
        "Noi Tong quat": "Nội tổng quát",
        "Noi Tieu hoa": "Nội tiêu hoá",
        "Cap cuu": "Cấp cứu",
        "Noi Tim mach": "Nội tim mạch",
        "Noi Than kinh": "Nội thần kinh",
    }
    return display_map.get(value, value.replace("_", " "))


def _normalize_specialty_code(value: str) -> str | None:
    normalized = _normalize_text(value)
    specialty_map = {
        "noi tieu hoa": "Noi Tieu hoa",
        "noi tong quat": "Noi Tong quat",
        "cap cuu": "Cap cuu",
        "noi tim mach": "Noi Tim mach",
        "noi than kinh": "Noi Than kinh",
        "san phu khoa": "San phu khoa",
        "tai mui hong": "Tai mui hong",
        "da lieu": "Da lieu",
        "chan thuong chinh hinh": "Chan thuong chinh hinh",
    }
    for needle, specialty in specialty_map.items():
        if needle in normalized:
            return specialty
    return None


def _specialty_candidates_from_case(case: "IntakeCase") -> list[str]:
    normalized = _normalize_text(" ".join([case.main_symptom, case.duration, case.severity, " ".join(case.red_flags)]))
    candidates = {"Noi Tong quat"}
    symptom_rules = [
        ("Noi Tieu hoa", ["dau bung", "day hoi", "kho tieu", "da day", "non", "tieu chay", "phan den"]),
        ("Cap cuu", ["dau nguc", "kho tho", "ngat", "lo mo", "co giat", "non ra mau", "chay mau"]),
        ("Noi Than kinh", ["dau dau", "chong mat", "te", "yeu nua nguoi", "roi loan y thuc"]),
        ("Tai mui hong", ["ho", "viem hong", "dau hong", "sot nong", "so mui"]),
        ("San phu khoa", ["mang thai", "co bau", "phu khoa", "kinh nguyet", "ra mau am dao"]),
        ("Da lieu", ["ngua", "phat ban", "mun", "di ung", "man da"]),
        ("Chan thuong chinh hinh", ["chan thuong", "gay", "khop", "sung", "nga", "xoay", "trai khop"]),
    ]
    for specialty, terms in symptom_rules:
        if any(term in normalized for term in terms):
            candidates.add(specialty)
    return sorted(candidates)


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
    duration: str = "unknown"
    severity: str = "unknown"
    red_flag_status: str
    priority: str
    suggested_specialty: str
    preferred_hospital: str
    preferred_time_detail: str
    booking_status: str
    created_at: str
    doctor_summary: str = ""


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
    facility_candidates: list[dict] = Field(default_factory=list)


class IntakeExtractorTool:
    def _extract_phone(self, normalized: str) -> str | None:
        phone_match = re.search(
            r"(?:so dien thoai|sdt|dien thoai)\s*[:\-]?\s*([0-9][0-9\s\.-]{5,})",
            normalized,
        )
        if not phone_match:
            return None
        digits = re.sub(r"\D", "", phone_match.group(1))
        return digits if len(digits) >= 7 else None

    def _extract_full_name(self, normalized: str) -> str | None:
        patterns = [
            r"(?:ten nguoi benh|ten benh nhan|ho ten|ten)\s+(.+?)(?=\s*(?:so dien thoai|sdt|dien thoai|co so|dia diem|ngay gio|luc|vao|tai)\b|$)",
            r"(?:nguoi benh)\s+(.+?)(?=\s*(?:so dien thoai|sdt|dien thoai|co so|dia diem|ngay gio|luc|vao|tai)\b|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, normalized)
            if match:
                value = re.sub(r"\s+", " ", match.group(1)).strip(" ,.;:-")
                value = re.sub(r"^(la|ten la)\s+", "", value).strip()
                if value:
                    return " ".join(part.capitalize() for part in value.split())
        return None

    def extract(self, message: str) -> dict:
        normalized = _normalize_text(message)
        slots: dict[str, object] = {}

        if _contains_any_term(normalized, ["me toi", "ma toi"]):
            slots["patient_relation"] = "mother"
        elif _contains_any_term(normalized, ["bo toi", "ba toi"]):
            slots["patient_relation"] = "father"
        elif _contains_any_term(normalized, ["con toi", "be nha toi", "be cua toi", "be toi", "chau nha toi"]):
            slots["patient_relation"] = "child"
        elif _contains_term(normalized, "toi"):
            slots["patient_relation"] = "self"

        age_match = re.search(r"\b(\d{1,3})\s*(tuoi|t)\b", normalized)
        if age_match:
            slots["age_or_birth_year"] = age_match.group(1)

        if _contains_any_term(normalized, ["da day", "day hoi", "kho tieu", "dau bung"]):
            slots["main_symptom"] = "dau da day, day hoi, kho tieu"
            slots["suggested_specialty"] = "Noi Tieu hoa"
        elif _contains_any_term(normalized, ["dau dau", "sot", "sot nong", "ho"]):
            symptoms = []
            if _contains_term(normalized, "dau dau"):
                symptoms.append("dau dau")
            if _contains_any_term(normalized, ["sot", "sot nong"]):
                symptoms.append("sot")
            if _contains_term(normalized, "ho"):
                symptoms.append("ho")
            slots["main_symptom"] = ", ".join(symptoms) or "trieu chung toan than"
            slots["suggested_specialty"] = "Noi Tong quat"
        elif _contains_any_term(normalized, ["dau nguc", "kho tho"]):
            slots["main_symptom"] = "dau nguc, kho tho"
            slots["suggested_specialty"] = "Cap cuu"

        if full_name := self._extract_full_name(normalized):
            slots["full_name"] = full_name
        if phone := self._extract_phone(normalized):
            slots["phone"] = phone

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


class PolicyGuardTool:
    API_SECRET_TERMS = [
        "api key",
        "apikey",
        "openai key",
        "secret key",
        "access token",
        "bearer token",
        "cho toi key",
        "xin key",
    ]
    DISCRIMINATION_TERMS = [
        "da den",
        "nguoi da den",
        "da trang",
        "nguoi da trang",
        "nguoi trang",
        "nguoi chau phi",
        "nguoi chau a",
        "nguoi an do",
        "nguoi trung quoc",
        "nguoi nuoc ngoai",
    ]
    EXCLUSION_TERMS = [
        "khong co",
        "khong gap",
        "khong muon gap",
        "khong kham voi",
        "tranh",
        "loai",
        "cam",
        "chi gap",
        "chi chon",
        "chi muon",
        "uu tien",
    ]

    def classify(self, message: str) -> str | None:
        normalized = _normalize_text(message)
        if any(term in normalized for term in self.API_SECRET_TERMS):
            return "secret_request"
        has_discrimination_term = any(term in normalized for term in self.DISCRIMINATION_TERMS)
        has_exclusion_term = any(term in normalized for term in self.EXCLUSION_TERMS)
        if has_discrimination_term and has_exclusion_term:
            return "discriminatory_request"
        return None


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

        search_plan = self._build_search_plan(case)
        collected_sources: list[SourceRef] = []
        scraped_points: list[str] = []
        try:
            chosen_query = search_plan[0]["query"]
            for plan in search_plan:
                sources = await self.tavily.search(
                    plan["query"],
                    include_domains=plan["include_domains"],
                    exclude_domains=plan.get("exclude_domains"),
                    search_depth="advanced",
                    max_results=5,
                    include_raw_content="markdown",
                    topic="general",
                )
                filtered_sources = [
                    source for source in sources if _is_trusted_domain(source.url, plan["include_domains"])
                ]
                if filtered_sources:
                    collected_sources = self._merge_sources(collected_sources, filtered_sources)
                    chosen_query = plan["query"]
                    break

            if self.firecrawl and collected_sources:
                for source in collected_sources[:2]:
                    try:
                        scraped_points.append(await self.firecrawl.scrape(source.url))
                    except Exception:
                        continue
            context = {
                **fallback_context,
                "search_query": chosen_query,
                "search_plan": search_plan,
                "scraped_context": scraped_points[:2],
            }
            return context, collected_sources[:5] or fallback_sources
        except Exception:
            return fallback_context, fallback_sources

    def list_facility_options(self) -> list[dict]:
        return [
            {
                "facility_id": "vinmec_times_city",
                "name": "Bệnh viện Đa khoa Quốc tế Vinmec Times City",
                "short_name": "Vinmec Times City",
                "city": "Hà Nội",
                "address": "Số 458 Minh Khai, Hà Nội",
                "phone": "024 3974 3556",
            },
            {
                "facility_id": "vinmec_smart_city",
                "name": "Bệnh viện Đa khoa Vinmec Smart City",
                "short_name": "Vinmec Smart City",
                "city": "Hà Nội",
                "address": "Số 2A đường Tây Mỗ, Hà Nội",
                "phone": "024 3208 5678",
            },
            {
                "facility_id": "vinmec_central_park",
                "name": "Bệnh viện Đa khoa Quốc tế Vinmec Central Park",
                "short_name": "Vinmec Central Park",
                "city": "TP. Hồ Chí Minh",
                "address": "720A Điện Biên Phủ, TP. Hồ Chí Minh",
                "phone": "028 3622 1166",
            },
            {
                "facility_id": "vinmec_da_nang",
                "name": "Bệnh viện Đa khoa Vinmec Đà Nẵng",
                "short_name": "Vinmec Đà Nẵng",
                "city": "Đà Nẵng",
                "address": "Đường 30 tháng 4, Đà Nẵng",
                "phone": "0236 3711 111",
            },
            {
                "facility_id": "vinmec_can_tho",
                "name": "Bệnh viện Đa khoa Vinmec Cần Thơ",
                "short_name": "Vinmec Cần Thơ",
                "city": "Cần Thơ",
                "address": "Số 150A Đường 3/2, Cần Thơ",
                "phone": "0292 368 3003",
            },
        ]

    def _build_search_plan(self, case: IntakeCase) -> list[dict]:
        symptom_phrase = _case_search_phrase(case)
        primary_query = f"site:vinmec.com {symptom_phrase} khi nao can kham"
        secondary_query = f"{symptom_phrase} warning signs when to seek care"
        return [
            {
                "label": "vinmec_first",
                "query": primary_query,
                "include_domains": ["vinmec.com"],
                "exclude_domains": ["youtube.com", "m.youtube.com", "facebook.com", "tiktok.com"],
            },
            {
                "label": "trusted_fallback",
                "query": secondary_query,
                "include_domains": [
                    "vinmec.com",
                    "mayoclinic.org",
                    "nhs.uk",
                    "medlineplus.gov",
                    "cdc.gov",
                    "who.int",
                    "clevelandclinic.org",
                    "healthdirect.gov.au",
                ],
                "exclude_domains": ["youtube.com", "m.youtube.com", "facebook.com", "tiktok.com"],
            },
        ]

    def _merge_sources(self, existing: list[SourceRef], new_sources: list[SourceRef]) -> list[SourceRef]:
        seen = {source.url for source in existing}
        merged = list(existing)
        for source in new_sources:
            if source.url not in seen:
                merged.append(source)
                seen.add(source.url)
        return merged


class TriageSafetyRuleTool:
    RED_FLAGS = {
        # Hô hấp / tuần hoàn cấp
        "dau nguc": "dau nguc",
        "tuc nguc": "tuc nguc",
        "dau nguc lan tay": "dau nguc lan tay",
        "dau nguc lan ham": "dau nguc lan ham",
        "dau nguc lan lung": "dau nguc lan lung",
        "kho tho": "kho tho",
        "kho tho tang dan": "kho tho tang dan",
        "moi tim": "moi tim/tim tai",
        "ngat": "ngat",
        "choang vang": "choang vang",
        # Sốt/nhiễm trùng nặng hoặc chảy máu nặng
        "sot 40": "sot 40 do",
        "sot cao khong ha": "sot cao khong ha",
        "ret run": "ret run",
        "chay mau nhieu": "chay mau nhieu",
        "de bam tim": "de bam tim/chay mau bat thuong",
        # Thần kinh cấp
        "dau dau du doi": "dau dau du doi",
        "dau dau dot ngot": "dau dau dot ngot",
        "co gay": "co gay",
        "co giat": "co giat",
        "lo mo": "lo mo/roi loan y thuc",
        "meo mieng": "meo mieng",
        "noi kho": "noi kho",
        "yeu nua nguoi": "yeu/liet nua nguoi",
        "te nua nguoi": "te nua nguoi",
        "mat thi luc dot ngot": "mat thi luc dot ngot",
        # Tiêu hóa cấp / xuất huyết tiêu hóa
        "dau bung du doi": "dau bung du doi",
        "dau bung tang dan": "dau bung tang dan",
        "bung cung": "bung cung",
        "non lien tuc": "non lien tuc",
        "non ra mau": "non ra mau",
        "non mau ca phe": "non mau ca phe",
        "phan den": "di ngoai phan den",
        "di ngoai ra mau": "di ngoai ra mau",
        "tieu chay ra mau": "tieu chay ra mau",
        # Tiết niệu cấp
        "khong tieu duoc": "khong tieu duoc/bi tieu",
        # Dị ứng / phản vệ
        "sung moi": "sung moi",
        "sung mat": "sung mat",
        "sung luoi": "sung luoi",
        "sung hong": "sung hong",
        "phat ban kem kho tho": "phat ban kem kho tho",
        "noi me day toan than": "noi me day toan than",
        "phat ban khong mat mau": "phat ban khong mat mau khi an",
        # Đau lưng nguy cơ chèn ép thần kinh
        "te vung yen ngua": "te vung yen ngua",
        "mat kiem soat tieu tien": "mat kiem soat tieu tien",
        "mat kiem soat dai tien": "mat kiem soat dai tien",
        # Thai sản / trẻ em
        "mang thai ra mau": "mang thai ra mau",
        "mang thai dau bung": "mang thai dau bung",
        "thai may yeu": "thai may yeu/it hon binh thuong",
        "tre li bi": "tre li bi",
        "tre kho danh thuc": "tre kho danh thuc",
        "tre kho tho": "tre kho tho",
        "tre co giat": "tre co giat",
        "tre mat nuoc": "tre co dau hieu mat nuoc",
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
    def __init__(self, llm=None, facility_provider=None):
        self.llm = llm
        self.facility_provider = facility_provider

    def _facility_candidates(self, limit: int = 4) -> list[dict]:
        if not self.facility_provider:
            return []
        return self.facility_provider.list_facility_options()[:limit]

    def _booking_missing_fields(self, case: IntakeCase, patient: PatientInfo) -> list[str]:
        missing = []
        if patient.full_name == "unknown":
            missing.append("tên người bệnh")
        if patient.phone in {None, "", "unknown"}:
            missing.append("số điện thoại")
        if case.preferred_hospital in {"unknown", "Vinmec"}:
            missing.append("cơ sở khám cụ thể")
        if case.preferred_time_detail == "unknown" and case.preferred_time == "unknown":
            missing.append("thời gian ngày giờ")
        return missing

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

        booking_missing = self._booking_missing_fields(case, patient)

        if case.booking_intent and booking_missing:
            facility_candidates = self._facility_candidates()
            quick_replies = [candidate["short_name"] for candidate in facility_candidates[:4]]
            if not quick_replies:
                quick_replies = [
                    "Vinmec Times City",
                    "Vinmec Smart City",
                    "Vinmec Central Park",
                    "Ch?a ch?c",
                ]
            return IntakeResponse(
                response_type="ask_booking_details",
                assistant_text=(
                    "Mình đã ghi nhận nhu cầu đặt lịch. "
                    "Để tạo lịch nháp, mình cần: "
                    + ", ".join(booking_missing)
                    + ". "
                    "Bạn gửi theo mẫu: tên..., số điện thoại..., cơ sở khám..., ngày giờ...."
                ),
                quick_replies=quick_replies,
                case=case,
                patient=patient,
                doctor_summary=case.doctor_summary,
                sources=case.sources,
                facility_candidates=facility_candidates,
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
                facility_candidates=self._facility_candidates(),
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
            f"Dựa trên thông tin bạn vừa chia sẻ, mình tạm xếp ca này ở mức ưu tiên {case.priority}. "
            "Đây là nhận định sơ bộ để định hướng, không phải chẩn đoán y khoa. "
            f"Dựa trên triệu chứng hiện tại và nguồn tham khảo đã kiểm tra{source_text}, "
            f"mình khuyên bạn ưu tiên khám {_display_specialty(case.suggested_specialty)} tại Vinmec sớm hơn nếu triệu chứng kéo dài, lặp lại hoặc nặng lên. "
            "Nếu có sốt cao, khó thở, đau ngực, nôn ra máu, đi ngoài phân đen hoặc lơ mơ, hãy đi cấp cứu ngay. "
            "Nếu bạn muốn, mình có thể tạo lịch khám nháp ngay trong chat."
        )
        if not self.llm:
            return fallback

        prompt = (
            "Pha: safe_guidance.\n"
            "Vai trò: trợ lý tiếp nhận Vinmec, không chẩn đoán bệnh, không kê thuốc, không bỏ qua hardcoded red flags.\n"
            "Giọng văn: thân thiện, tự nhiên, y khoa nhưng không khô cứng; tránh các cụm kiểu 'mình đã kiểm tra ngữ cảnh y tế liên quan'.\n"
            "Mục tiêu: trả lời 4-6 câu bằng tiếng Việt, giống một điều phối viên y tế đang hướng dẫn người bệnh.\n"
            "Bắt buộc gồm 4 phần:\n"
            "1) Mở đầu ngắn gọn bằng sự đồng cảm hoặc xác nhận điều người bệnh vừa chia sẻ.\n"
            "2) Nêu nhận định sơ bộ về mức độ ưu tiên khám bằng ngôn ngữ dễ hiểu.\n"
            "3) Nếu có sources, chỉ nhắc 1-2 nguồn đáng tin và giải thích ngắn vì sao chúng liên quan; không liệt kê dồn dập nhiều nguồn.\n"
            "4) Kết bằng câu hỏi mềm: 'Nếu bạn muốn, mình có thể tạo lịch khám nháp ngay trong chat.'\n"
            "Nếu nguồn chưa đủ thì nói rõ là chỉ đang dựa trên thông tin hiện có và vẫn ưu tiên an toàn.\n"
            f"Patient relation: {patient.relationship_to_customer}\n"
            f"Age or birth year: {patient.age_or_birth_year}\n"
            f"Main symptom: {case.main_symptom}\n"
            f"Duration: {case.duration}\n"
            f"Severity: {case.severity}\n"
            f"Suggested specialty: {case.suggested_specialty}\n"
            f"Priority: {case.priority}\n"
            f"Evidence context: {case.evidence_context}\n"
            f"Sources: {self._format_sources(case.sources)}\n"
            "Return a warm Vietnamese chat reply with safe initial guidance, specialty suggestion, and a booking question.\n"
        )
        try:
            assistant_text = await self.llm.complete(prompt)
            return self._polish_safe_guidance_text(self._enrich_safe_guidance_text(assistant_text, case))
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
            f"Patient relation: {patient.relationship_to_customer}\n"
            "Khong hoi lai quan he nguoi benh neu Patient relation khac unknown va khong nam trong Missing fields.\n"
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
            f"Dựa trên nguồn tham khảo đã kiểm tra{source_text}, mình gợi ý ưu tiên khám {_display_specialty(case.suggested_specialty)} tại Vinmec sớm hơn nếu triệu chứng kéo dài hoặc tăng mức độ.",
            "Nếu bạn muốn, mình có thể tạo lịch khám nháp ngay trong chat và lưu đầy đủ hồ sơ, giờ khám chi tiết, tóm tắt ca bệnh cùng nguồn tham khảo.",
        ]
        return assistant_text.rstrip() + "\n\n" + " ".join(tail)

    def _polish_safe_guidance_text(self, assistant_text: str) -> str:
        replacements = {
            "Mình đã kiểm tra ngữ cảnh y tế liên quan": "Dựa trên thông tin bạn vừa chia sẻ",
            "hiện chưa thấy dấu hiệu khẩn cấp rõ ràng": "mình chưa thấy dấu hiệu khẩn cấp rõ ràng",
            "Noi Tong quat": "Nội tổng quát",
            "Noi Tieu hoa": "Nội tiêu hoá",
            "Cap cuu": "Cấp cứu",
        }
        polished = assistant_text
        for source_text, target_text in replacements.items():
            polished = polished.replace(source_text, target_text)
        return polished


class SmartIntakeService:
    def __init__(self, llm=None, context_search: MedicalContextSearchTool | None = None, store=None):
        self.llm = llm
        self.store = store
        self.extractor = IntakeExtractorTool()
        self.policy_guard = PolicyGuardTool()
        self.context_search = context_search or MedicalContextSearchTool()
        self.triage = TriageSafetyRuleTool()
        self.response_builder = ChatResponseSummaryTool(llm=llm, facility_provider=self.context_search)
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
        self._save_case_snapshot(case_id)
        return session

    async def handle_message(self, session_id: str, content: str) -> IntakeResponse:
        session = self.sessions[session_id]
        case = self.cases[session.case_id]
        patient = self.patients[session.patient_id]
        if case.red_flag_status == "confirmed" or case.case_status == "red_flag_detected":
            self._log(case.case_id, "blocked_user_message", content)
            response = await self.response_builder.build(case, patient, None)
            self._log(case.case_id, "assistant_response", response.response_type)
            self._save_case_snapshot(case.case_id)
            return response

        self.messages[session_id].append(ChatMessage(role="user", content=content))
        self._log(case.case_id, "user_message", content)

        policy_violation = self.policy_guard.classify(content)
        if policy_violation:
            response = self._build_policy_refusal_response(case, patient, policy_violation)
            self.messages[session_id].append(ChatMessage(role="assistant", content=response.assistant_text))
            self._log(case.case_id, "policy_refusal", policy_violation)
            self._log(case.case_id, "assistant_response", response.response_type)
            self._save_case_snapshot(case.case_id)
            return response

        if not self._is_in_scope_message(content):
            response = self._build_out_of_scope_response(case, patient)
            self.messages[session_id].append(ChatMessage(role="assistant", content=response.assistant_text))
            self._log(case.case_id, "out_of_scope_message", content)
            self._log(case.case_id, "assistant_response", response.response_type)
            self._save_case_snapshot(case.case_id)
            return response

        slots = self.extractor.extract(content)
        self._log(case.case_id, "intake_slots_extracted", json.dumps(slots, ensure_ascii=False))
        self._apply_slots(case, patient, slots)
        if case.booking_intent:
            booking_slots = await self._extract_booking_slots(case, patient, content)
            self._log(case.case_id, "booking_slots_extracted", json.dumps(booking_slots, ensure_ascii=False))
            self._apply_slots(case, patient, booking_slots)
        case = self.triage.classify(case, content)
        self._log(
            case.case_id,
            "triage_rule_applied",
            f"priority={case.priority}; red_flag_status={case.red_flag_status}; red_flags={case.red_flags}",
        )
        if self._has_minimum_intake(case, patient) and case.red_flag_status != "confirmed":
            case.evidence_context, case.sources = await self.context_search.search(case)
            self._log(
                case.case_id,
                "medical_context_search",
                json.dumps(
                    {
                        "search_query": case.evidence_context.get("search_query", "fallback"),
                        "source_count": len(case.sources),
                        "sources": [source.title for source in case.sources[:3]],
                    },
                    ensure_ascii=False,
                ),
            )
            case = await self._classify_with_ai(case, patient)
            case = await self._choose_specialty_with_ai(case, patient)
        case.doctor_summary = await self._build_doctor_summary(
            case,
            patient,
            use_ai=case.red_flag_status != "confirmed",
        )
        self.cases[case.case_id] = case

        booking = self.bookings.get(case.booking_id) if case.booking_id else None
        if case.booking_intent:
            booking_missing = self._booking_missing_fields(case, patient)
            self._log(case.case_id, "booking_missing_fields", json.dumps(booking_missing, ensure_ascii=False))
            if booking is None and not booking_missing:
                booking = self._create_booking(case, patient)
                case.booking_id = booking.booking_id
                case.case_status = "booking_requested"
                self.cases[case.case_id] = case

        response = await self.response_builder.build(case, patient, booking)
        self.messages[session_id].append(ChatMessage(role="assistant", content=response.assistant_text))
        self._log(case.case_id, "assistant_response", response.response_type)
        self._save_case_snapshot(case.case_id)
        return response

    def list_messages(self, session_id: str) -> list[ChatMessage]:
        return self.messages[session_id]

    def get_case(self, case_id: str) -> IntakeCase:
        return self.cases[case_id]

    def patch_case(self, case_id: str, patch: dict) -> IntakeCase:
        case = self.cases[case_id].model_copy(update=patch | {"updated_at": _now_iso()})
        self.cases[case_id] = case
        self._log(case_id, "case_patched", str(sorted(patch.keys())))
        self._save_case_snapshot(case_id)
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
        self._save_case_snapshot(case_id)
        return booking

    def get_booking(self, booking_id: str) -> BookingDraft:
        return self.bookings[booking_id]

    def patch_booking(self, booking_id: str, patch: dict) -> BookingDraft:
        booking = self.bookings[booking_id].model_copy(update=patch)
        self.bookings[booking_id] = booking
        self._log(booking.case_id, "booking_patched", str(sorted(patch.keys())))
        self._save_case_snapshot(booking.case_id)
        return booking

    def list_doctor_cases(self) -> list[DoctorCaseRow]:
        stored_rows = self.store.list_doctor_case_rows() if self.store else []
        if stored_rows:
            return [DoctorCaseRow(**row) for row in stored_rows]

        rows = []
        for case in self.cases.values():
            patient = self.patients[case.patient_id]
            booking_status = "none"
            booking = self.bookings.get(case.booking_id) if case.booking_id else None
            if booking:
                booking_status = booking.booking_status
            preferred_hospital = case.preferred_hospital
            if preferred_hospital == "unknown" and booking:
                preferred_hospital = booking.hospital
            preferred_time_detail = case.preferred_time_detail
            if preferred_time_detail == "unknown" and booking:
                preferred_time_detail = booking.preferred_time_detail
            rows.append(
                DoctorCaseRow(
                    case_id=case.case_id,
                    patient=patient.relationship_to_customer,
                    age_or_birth_year=patient.age_or_birth_year,
                    main_symptom=case.main_symptom,
                    duration=case.duration,
                    severity=case.severity,
                    red_flag_status=case.red_flag_status,
                    priority=case.priority,
                    suggested_specialty=case.suggested_specialty,
                    preferred_hospital=preferred_hospital,
                    preferred_time_detail=preferred_time_detail,
                    booking_status=booking_status,
                    created_at=case.created_at,
                    doctor_summary=case.doctor_summary,
                )
            )
        return rows

    def add_doctor_note(self, case_id: str, note: str) -> IntakeCase:
        case = self.cases[case_id]
        case.doctor_notes.append(note)
        case.updated_at = _now_iso()
        self._log(case_id, "doctor_note_added", note)
        self._save_case_snapshot(case_id)
        return case

    def patch_case_status(self, case_id: str, status: str) -> IntakeCase:
        case = self.cases[case_id]
        case.case_status = status
        case.updated_at = _now_iso()
        self._log(case_id, "case_status_updated", status)
        self._save_case_snapshot(case_id)
        return case

    def list_audit_logs(self, case_id: str) -> list[AuditLog]:
        stored_logs = self.store.list_logs(case_id) if self.store else []
        if stored_logs:
            return [AuditLog(**log) for log in stored_logs]
        return self.audit_logs[case_id]

    def dashboard_stats(self) -> dict:
        if self.store:
            return self.store.dashboard_stats()
        rows = self.list_doctor_cases()
        return {
            "date": datetime.now(timezone.utc).date().isoformat(),
            "total_conversations": len(rows),
            "red_flag_cases": sum(1 for row in rows if row.red_flag_status == "confirmed"),
            "booking_drafts": sum(1 for row in rows if row.booking_status == "draft"),
            "priority_counts": {},
            "specialty_counts": {},
        }

    def _build_policy_refusal_response(
        self,
        case: IntakeCase,
        patient: PatientInfo,
        policy_violation: str,
    ) -> IntakeResponse:
        if policy_violation == "secret_request":
            assistant_text = (
                "Mình không thể cung cấp API key, token, mật khẩu hoặc thông tin bí mật hệ thống. "
                "Mình vẫn có thể hỗ trợ tiếp nhận triệu chứng, gợi ý chuyên khoa phù hợp hoặc tạo lịch khám nháp."
            )
            quick_replies = ["Mô tả triệu chứng", "Đặt lịch khám nháp", "Xem handoff cho bác sĩ"]
        elif policy_violation == "discriminatory_request":
            assistant_text = (
                "Mình không thể hỗ trợ chọn hoặc loại trừ nhân sự, bác sĩ hay địa điểm dựa trên chủng tộc, màu da hoặc đặc điểm được bảo vệ. "
                "Nếu bạn muốn đặt lịch, mình có thể hỗ trợ theo nhu cầu y tế, chuyên khoa, cơ sở Vinmec và khung giờ phù hợp."
            )
            quick_replies = ["Chọn cơ sở Vinmec", "Nhập thời gian khám", "Mô tả triệu chứng"]
        else:
            assistant_text = (
                "Mình không thể hỗ trợ yêu cầu đó. "
                "Mình có thể tiếp tục hỗ trợ tiếp nhận triệu chứng, gợi ý chuyên khoa hoặc tạo lịch khám nháp."
            )
            quick_replies = ["Mô tả triệu chứng", "Đặt lịch khám nháp"]
        return IntakeResponse(
            response_type="policy_refusal",
            assistant_text=assistant_text,
            quick_replies=quick_replies,
            case=case,
            patient=patient,
            booking=None,
            doctor_summary=case.doctor_summary,
            sources=case.sources,
            facility_candidates=self.response_builder._facility_candidates(),
        )

    def _is_in_scope_message(self, content: str) -> bool:
        normalized = _normalize_text(content)
        if not normalized.strip():
            return False
        scope_terms = [
            "vinmec",
            "kham",
            "dat lich",
            "lich kham",
            "booking",
            "bac si",
            "chuyen khoa",
            "co so",
            "benh vien",
            "trieu chung",
            "benh",
            "dau",
            "sot",
            "ho",
            "kho tho",
            "dau nguc",
            "da day",
            "day hoi",
            "kho tieu",
            "dau bung",
            "non",
            "tieu chay",
            "chong mat",
            "met",
            "ngua",
            "phat ban",
            "mang thai",
            "co bau",
            "me toi",
            "bo toi",
            "con toi",
            "be nha toi",
            "be cua toi",
            "chau nha toi",
            "tuoi",
            "nam sinh",
            "nhe",
            "vua",
            "nang",
            "rat nang",
            "khong chiu duoc",
            "times city",
            "smart city",
            "central park",
            "da nang",
            "sang mai",
            "chieu mai",
            "toi nay",
            "cuoi tuan",
            "xac nhan",
            "sua thong tin",
            "huy",
            "ten nguoi benh",
            "ten benh nhan",
            "ho ten",
            "so dien thoai",
            "sdt",
            "dien thoai",
        ]
        if _contains_any_term(normalized, scope_terms):
            return True
        if re.search(r"\b\d{1,3}\s*(tuoi|t)\b", normalized):
            return True
        if re.search(r"\b\d{1,2}(:\d{2})?\s*(gio|h|chieu|sang|toi|trua)\b", normalized):
            return True
        if re.search(r"(?:so dien thoai|sdt|dien thoai)\s*[:\-]?\s*[0-9][0-9\s\.-]{5,}", normalized):
            return True
        return False

    def _build_out_of_scope_response(self, case: IntakeCase, patient: PatientInfo) -> IntakeResponse:
        return IntakeResponse(
            response_type="out_of_scope",
            assistant_text=(
                "Câu hỏi này không phù hợp với phạm vi hỗ trợ của Vinmec AI Intake demo. "
                "Mình chỉ hỗ trợ tiếp nhận triệu chứng, phát hiện dấu hiệu nguy hiểm, gợi ý chuyên khoa và tạo lịch khám nháp."
            ),
            quick_replies=["Mô tả triệu chứng", "Đặt lịch khám nháp", "Chọn cơ sở Vinmec"],
            case=case,
            patient=patient,
            booking=None,
            doctor_summary=case.doctor_summary,
            sources=case.sources,
            facility_candidates=self.response_builder._facility_candidates(),
        )

    def _apply_slots(self, case: IntakeCase, patient: PatientInfo, slots: dict) -> None:
        if full_name := slots.get("full_name"):
            patient.full_name = str(full_name)
        if phone := slots.get("phone"):
            patient.phone = str(phone)
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

    def _booking_missing_fields(self, case: IntakeCase, patient: PatientInfo) -> list[str]:
        missing = []
        if patient.full_name == "unknown":
            missing.append("tên người bệnh")
        if patient.phone in {None, "", "unknown"}:
            missing.append("số điện thoại")
        if case.preferred_hospital in {"unknown", "Vinmec"}:
            missing.append("cơ sở khám cụ thể")
        if case.preferred_time_detail == "unknown" and case.preferred_time == "unknown":
            missing.append("thời gian ngày giờ")
        return missing

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

    async def _extract_booking_slots(self, case: IntakeCase, patient: PatientInfo, message: str) -> dict:
        deterministic_slots = self.extractor.extract(message)
        if not self.llm:
            return deterministic_slots

        prompt = (
            "Pha: booking_extraction.\n"
            "Trích xuất các trường đặt lịch từ tin nhắn gần nhất của người dùng.\n"
            "Chỉ trả về JSON hợp lệ, không giải thích, không markdown.\n"
            "Các khóa cho phép: full_name, phone, preferred_hospital, preferred_time, preferred_time_detail, booking_intent.\n"
            "Nếu không chắc, dùng giá trị \"unknown\".\n"
            "Nếu người dùng chỉ nói \"Vinmec\" mà chưa nêu cơ sở cụ thể, preferred_hospital vẫn để \"Vinmec\".\n"
            f"Patient hiện tại: {patient.model_dump()}\n"
            f"Case hiện tại: {case.model_dump()}\n"
            f"Tin nhắn: {message}\n"
        )
        try:
            raw = await self.llm.complete(prompt)
            parsed = json.loads(raw)
        except Exception:
            return deterministic_slots

        slots = dict(deterministic_slots)
        for key in ["full_name", "phone", "preferred_hospital", "preferred_time", "preferred_time_detail"]:
            value = parsed.get(key)
            if isinstance(value, str) and value and value != "unknown":
                slots[key] = value
        if parsed.get("booking_intent") is True:
            slots["booking_intent"] = True
        return slots

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
            self._log(case.case_id, "doctor_summary_fallback", "llm_disabled_or_red_flag")
            return fallback.replace("Noi Tong quat", "Nội tổng quát").replace("Noi Tieu hoa", "Nội tiêu hoá").replace("Cap cuu", "Cấp cứu")
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
            summary = await self.llm.complete(prompt)
            self._log(case.case_id, "doctor_summary_ai", "phase=doctor_summary; status=ok")
            return summary.replace("Noi Tong quat", "Nội tổng quát").replace("Noi Tieu hoa", "Nội tiêu hoá").replace("Cap cuu", "Cấp cứu")
        except Exception:
            self._log(case.case_id, "doctor_summary_fallback", "phase=doctor_summary; status=llm_error")
            return fallback.replace("Noi Tong quat", "Nội tổng quát").replace("Noi Tieu hoa", "Nội tiêu hoá").replace("Cap cuu", "Cấp cứu")

    async def _classify_with_ai(self, case: IntakeCase, patient: PatientInfo) -> IntakeCase:
        fallback_level = case.priority
        case.ai_triage_level = fallback_level
        case.ai_triage_reason = (
            f"{fallback_level}: phân loại sơ bộ dựa trên thời gian, mức độ và dấu hiệu nguy hiểm đã kiểm tra."
        )
        if not self.llm:
            self._log(case.case_id, "ai_triage_fallback", case.ai_triage_reason)
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
            self._log(case.case_id, "ai_triage_fallback", "phase=triage_classification; status=llm_error")
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
        self._log(case.case_id, "ai_triage_result", case.ai_triage_reason)
        return case

    async def _choose_specialty_with_ai(self, case: IntakeCase, patient: PatientInfo) -> IntakeCase:
        if not self.llm:
            self._log(case.case_id, "specialty_selection_fallback", case.suggested_specialty)
            return case

        allowed_candidates = _specialty_candidates_from_case(case)
        prompt = """Pha: specialty_selection.
Select the most appropriate specialty for this intake case.
Only choose one specialty from: Noi Tieu hoa, Noi Tong quat, Cap cuu, Noi Tim mach, Noi Than kinh, San phu khoa, Tai mui hong, Da lieu, Chan thuong chinh hinh.
If there is not enough data, keep the current specialty.
Do not diagnose or prescribe medication.
Return exactly one line in the format '<specialty>: reason'.
Allowed specialties: {allowed_candidates}
Current specialty: {case.suggested_specialty}
Patient: {patient.model_dump()}
Case: {case.model_dump()}
Evidence context: {case.evidence_context}
Sources: {self.response_builder._format_sources(case.sources)}
"""
        try:
            result = await self.llm.complete(prompt)
        except Exception:
            self._log(case.case_id, "specialty_selection_fallback", "phase=specialty_selection; status=llm_error")
            return case

        suggested = _normalize_specialty_code(result or "")
        if suggested and suggested in allowed_candidates:
            case.suggested_specialty = suggested
            self._log(case.case_id, "specialty_selection_result", result)
            return case
        if case.suggested_specialty not in allowed_candidates and "Noi Tong quat" in allowed_candidates:
            case.suggested_specialty = "Noi Tong quat"
        self._log(case.case_id, "specialty_selection_result", result or case.suggested_specialty)
        return case

    def _log(self, case_id: str, event: str, detail: str) -> None:
        normalized = re.sub(r"\s+", " ", detail).strip()
        if len(normalized) > 120:
            normalized = normalized[:117] + "..."
        log = AuditLog(case_id=case_id, event=event, detail=normalized)
        self.audit_logs.setdefault(case_id, []).append(log)
        if self.store:
            self.store.append_log(case_id, event, normalized, log.created_at)

    def _booking_status_for_case(self, case: IntakeCase) -> str:
        booking = self.bookings.get(case.booking_id) if case.booking_id else None
        return booking.booking_status if booking else "none"

    def _save_case_snapshot(self, case_id: str) -> None:
        if not self.store or case_id not in self.cases:
            return
        case = self.cases[case_id]
        patient = self.patients[case.patient_id]
        self.store.save_case_snapshot(case, patient, self._booking_status_for_case(case))
