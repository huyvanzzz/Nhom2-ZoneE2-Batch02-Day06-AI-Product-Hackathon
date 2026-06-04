import os
from typing import Any

import httpx
import streamlit as st


DEFAULT_BACKEND_URL = os.getenv("DAY6_BACKEND_URL", "http://127.0.0.1:8000")
DEFAULT_API_TIMEOUT_SECONDS = float(os.getenv("DAY6_API_TIMEOUT_SECONDS", "90"))


def api_request(method: str, base_url: str, path: str, json: dict | None = None) -> Any:
    url = f"{base_url.rstrip('/')}{path}"
    timeout = httpx.Timeout(DEFAULT_API_TIMEOUT_SECONDS, connect=5.0)
    with httpx.Client(timeout=timeout) as client:
        response = client.request(method, url, json=json)
        response.raise_for_status()
        return response.json()


def _fetch_facilities(base_url: str) -> list[dict]:
    try:
        return api_request("GET", base_url, "/vinmec/facilities")
    except Exception:
        return []


def send_message(base_url: str, session_id: str, content: str) -> dict:
    return api_request(
        "POST",
        base_url,
        "/chat/message",
        {"session_id": session_id, "content": content},
    )


def get_or_create_session(base_url: str) -> dict:
    if "session" not in st.session_state or st.session_state.session is None:
        st.session_state.session = api_request("POST", base_url, "/chat/session")
        st.session_state.chat_messages = []
        st.session_state.last_response = None
    return st.session_state.session


def reset_chat(base_url: str) -> None:
    st.session_state.session = api_request("POST", base_url, "/chat/session")
    st.session_state.chat_messages = []
    st.session_state.last_response = None


def submit_chat_message(base_url: str, content: str) -> None:
    session = get_or_create_session(base_url)
    st.session_state.chat_messages.append({"role": "user", "content": content})
    try:
        with st.spinner("Đang kiểm tra triệu chứng, ngữ cảnh y tế và đề xuất phù hợp..."):
            response = send_message(base_url, session["session_id"], content)
        st.session_state.last_response = response
        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": response["assistant_text"],
            }
        )
    except httpx.TimeoutException:
        st.session_state.last_response = None
        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": (
                    "Mình đang xử lý lâu hơn bình thường. Bạn vui lòng thử lại sau vài giây "
                    "hoặc kiểm tra backend và AI gateway đã chạy chưa."
                ),
            }
        )
    except httpx.RequestError as exc:
        st.session_state.last_response = None
        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": f"Không kết nối được tới backend. Chi tiết: {exc}",
            }
        )


def is_emergency_locked() -> bool:
    return bool(
        st.session_state.get("last_response")
        and st.session_state.last_response.get("response_type") == "emergency_handoff"
    )


def _pretty_specialty(value: str) -> str:
    mapping = {
        "Noi Tong quat": "Nội tổng quát",
        "Noi Tieu hoa": "Nội tiêu hoá",
        "Cap cuu": "Cấp cứu",
        "Noi Tim mach": "Nội tim mạch",
        "Noi Than kinh": "Nội thần kinh",
        "San phu khoa": "Sản phụ khoa",
        "Tai mui hong": "Tai mũi họng",
        "Da lieu": "Da liễu",
        "Chan thuong chinh hinh": "Chấn thương chỉnh hình",
    }
    return mapping.get(value, value)


def _preview_logs(logs: list[dict]) -> list[dict]:
    compact = []
    for log in logs[-8:]:
        compact.append(
            {
                "time": log.get("created_at", "")[:19].replace("T", " "),
                "event": log.get("event", ""),
                "detail": log.get("detail", ""),
            }
        )
    return compact


def run_normal_booking_flow(base_url: str) -> dict:
    session = api_request("POST", base_url, "/chat/session")
    steps = [
        "Tôi đau dạ dày, đầy hơi khó tiêu 2 tuần nay.",
        "Mẹ tôi 58 tuổi, đau vừa.",
        "Đặt lịch khám nháp",
        "Times City, sáng mai",
        "Xác nhận",
    ]
    responses = [send_message(base_url, session["session_id"], step) for step in steps]
    messages = api_request("GET", base_url, f"/chat/session/{session['session_id']}/messages")
    case_detail = api_request("GET", base_url, f"/doctor/cases/{session['case_id']}")
    doctor_cases = api_request("GET", base_url, "/doctor/cases")
    logs = api_request("GET", base_url, f"/debug/cases/{session['case_id']}/logs")
    return {
        "session": session,
        "responses": responses,
        "messages": messages,
        "case_detail": case_detail,
        "doctor_cases": doctor_cases,
        "logs": logs,
    }


def run_red_flag_flow(base_url: str) -> dict:
    session = api_request("POST", base_url, "/chat/session")
    response = send_message(base_url, session["session_id"], "Tôi đau ngực và khó thở.")
    doctor_cases = api_request("GET", base_url, "/doctor/cases")
    logs = api_request("GET", base_url, f"/debug/cases/{session['case_id']}/logs")
    return {
        "session": session,
        "response": response,
        "doctor_cases": doctor_cases,
        "logs": logs,
    }


st.set_page_config(page_title="Vinmec Smart Intake Assistant", layout="wide")

st.markdown(
    """
    <style>
    .main .block-container { max-width: 1180px; padding-top: 1.5rem; }
    .stChatMessage { border-radius: 8px; }
    .status-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        background: #172033;
        border: 1px solid #30415f;
        color: #d6e2ff;
        font-size: 0.82rem;
        margin-right: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Trợ lý tiếp nhận thông tin khám Vinmec")
st.caption("AI hỏi bổ sung thông tin, kiểm tra dấu hiệu nguy hiểm, tìm ngữ cảnh y tế và hỗ trợ tạo lịch khám nháp.")

with st.sidebar:
    backend_url = st.text_input("Địa chỉ backend", value=DEFAULT_BACKEND_URL)
    facilities = st.session_state.get("vinmec_facilities")
    if facilities is None:
        facilities = _fetch_facilities(backend_url)
        st.session_state.vinmec_facilities = facilities
    col_health, col_reset = st.columns(2)
    if col_health.button("Kiểm tra"):
        try:
            st.success(api_request("GET", backend_url, "/health"))
        except Exception as exc:
            st.error(f"Lỗi backend: {exc}")
    if col_reset.button("Chat mới"):
        reset_chat(backend_url)
        st.rerun()
    with st.expander("Danh sách bệnh viện Vinmec", expanded=False):
        if facilities:
            st.dataframe(
                [
                    {
                        "Tên cơ sở": item.get("short_name") or item.get("name"),
                        "Thành phố": item.get("city", ""),
                        "Điện thoại": item.get("phone", ""),
                    }
                    for item in facilities
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Không tải được danh sách cơ sở.")

tab_chat, tab_dashboard, tab_flows = st.tabs(["Chat", "Dashboard bác sĩ", "Test luồng"])

with tab_chat:
    try:
        session = get_or_create_session(backend_url)
        st.markdown(
            f"""
            <span class="status-pill">Session: {session["session_id"]}</span>
            <span class="status-pill">Ca bệnh: {session["case_id"]}</span>
            """,
            unsafe_allow_html=True,
        )
    except Exception as exc:
        st.error(f"Không kết nối được backend: {exc}")
        st.stop()

    if not st.session_state.chat_messages:
        with st.chat_message("assistant"):
            st.write(
                "Chào bạn. Hãy mô tả triệu chứng, mình sẽ hỏi thêm thông tin cần thiết, "
                "kiểm tra dấu hiệu nguy hiểm và hỗ trợ tạo lịch khám nháp nếu phù hợp."
            )

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if st.session_state.last_response:
        replies = st.session_state.last_response.get("quick_replies", [])
        if replies:
            st.caption("Gợi ý trả lời nhanh")
            cols = st.columns(min(len(replies), 4))
            for index, reply in enumerate(replies):
                if cols[index % len(cols)].button(reply, key=f"reply-{len(st.session_state.chat_messages)}-{index}"):
                    submit_chat_message(backend_url, reply)
                    st.rerun()

    if is_emergency_locked():
        st.error("Ca bệnh đã được khóa ở trạng thái khẩn cấp. Không tiếp tục chat thêm trong phiên này.")
        st.info(
            "Gọi ngay hotline cơ sở Vinmec gần nhất hoặc đến cấp cứu gần nhất. "
            "Nếu đang ở Việt Nam, hãy gọi cấp cứu địa phương ngay khi cần."
        )

    prompt = st.chat_input("Nhập triệu chứng hoặc phản hồi của bạn...", disabled=is_emergency_locked())
    if prompt and not is_emergency_locked():
        submit_chat_message(backend_url, prompt)
        st.rerun()

    with st.expander("Dữ liệu ca hiện tại", expanded=False):
        if st.session_state.last_response:
            case = st.session_state.last_response.get("case") or {}
            patient = st.session_state.last_response.get("patient") or {}
            booking = st.session_state.last_response.get("booking") or {}
            sources = st.session_state.last_response.get("sources") or []
            st.dataframe(
                [
                    {
                        "Mã ca": case.get("case_id", ""),
                        "Người bệnh": patient.get("relationship_to_customer", ""),
                        "Tuổi": patient.get("age_or_birth_year", ""),
                        "Triệu chứng": case.get("main_symptom", ""),
                        "Chuyên khoa": _pretty_specialty(case.get("suggested_specialty", "")),
                        "Cơ sở": case.get("preferred_hospital", ""),
                        "Giờ hẹn": case.get("preferred_time_detail", case.get("preferred_time", "")),
                        "Trạng thái": case.get("case_status", ""),
                        "Ưu tiên": case.get("priority", ""),
                    }
                ],
                use_container_width=True,
                hide_index=True,
            )
            if booking:
                st.write(
                    f"Booking draft: {booking.get('booking_status', 'none')} | "
                    f"{booking.get('hospital', '')} | {booking.get('preferred_time_detail', booking.get('preferred_time', ''))}"
                )
            if sources:
                st.write("Nguồn đã dùng:")
                for source in sources[:2]:
                    st.write(f"- {source.get('title', '')}")
            facilities_hint = st.session_state.last_response.get("facility_candidates") or []
            if facilities_hint:
                st.write("Cơ sở Vinmec gợi ý:")
                st.dataframe(
                    [
                        {
                            "Tên": item.get("short_name") or item.get("name", ""),
                            "Thành phố": item.get("city", ""),
                            "Điện thoại": item.get("phone", ""),
                        }
                        for item in facilities_hint
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.info("Gửi một tin nhắn để tạo dữ liệu ca.")

with tab_flows:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Luồng 1: ca thường + đặt lịch")
        if st.button("Chạy luồng đặt lịch"):
            result = run_normal_booking_flow(backend_url)
            last = result["responses"][-1]
            st.metric("Phản hồi cuối", last["response_type"])
            st.metric("Trạng thái lịch", last["booking"]["booking_status"] if last["booking"] else "none")
            st.json(result)
    with col_b:
        st.subheader("Luồng 2: dấu hiệu nguy hiểm")
        if st.button("Chạy luồng khẩn cấp"):
            result = run_red_flag_flow(backend_url)
            st.metric("Phản hồi", result["response"]["response_type"])
            st.metric("Mức ưu tiên", result["response"]["case"]["priority"])
            st.json(result)

with tab_dashboard:
    if st.button("Tải danh sách ca"):
        st.session_state.doctor_cases = api_request("GET", backend_url, "/doctor/cases")
    doctor_cases = st.session_state.get("doctor_cases", [])
    st.dataframe(doctor_cases, use_container_width=True)
    selected_case = st.text_input(
        "Mã ca",
        value=doctor_cases[0]["case_id"] if doctor_cases else "",
    )
    if st.button("Xem chi tiết ca") and selected_case:
        detail = api_request("GET", backend_url, f"/doctor/cases/{selected_case}")
        logs = api_request("GET", backend_url, f"/debug/cases/{selected_case}/logs")
        st.subheader("Chi tiết ca")
        st.dataframe(
            [
                {
                    "Mã ca": detail.get("case_id", ""),
                    "Người bệnh": detail.get("patient", ""),
                    "Tuổi": detail.get("age_or_birth_year", ""),
                    "Triệu chứng": detail.get("main_symptom", ""),
                    "Chuyên khoa": _pretty_specialty(detail.get("suggested_specialty", "")),
                    "Cơ sở": detail.get("preferred_hospital", ""),
                    "Giờ hẹn": detail.get("preferred_time_detail", ""),
                    "Trạng thái booking": detail.get("booking_status", ""),
                }
            ],
            use_container_width=True,
            hide_index=True,
        )
        if detail.get("doctor_summary"):
            st.subheader("Tóm tắt AI")
            st.write(detail.get("doctor_summary"))
        st.subheader("Nguồn tham khảo và context")
        st.json({"evidence_context": detail.get("evidence_context"), "sources": detail.get("sources")})
        st.subheader("Nhật ký xử lý")
        st.dataframe(_preview_logs(logs), use_container_width=True, hide_index=True)
