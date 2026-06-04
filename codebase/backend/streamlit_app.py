import os
from typing import Any

import httpx
import streamlit as st


DEFAULT_BACKEND_URL = os.getenv("DAY6_BACKEND_URL", "http://127.0.0.1:8000")


def api_request(method: str, base_url: str, path: str, json: dict | None = None) -> Any:
    url = f"{base_url.rstrip('/')}{path}"
    with httpx.Client(timeout=10.0) as client:
        response = client.request(method, url, json=json)
        response.raise_for_status()
        return response.json()


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
    response = send_message(base_url, session["session_id"], content)
    st.session_state.last_response = response
    st.session_state.chat_messages.append(
        {
            "role": "assistant",
            "content": response["assistant_text"],
            "response_type": response["response_type"],
        }
    )


def run_normal_booking_flow(base_url: str) -> dict:
    session = api_request("POST", base_url, "/chat/session")
    steps = [
        "Toi dau da day, day hoi kho tieu 2 tuan nay.",
        "Me toi 58 tuoi, dau vua.",
        "Dat lich kham ao",
        "Times City, sang mai",
        "Xac nhan",
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
    response = send_message(base_url, session["session_id"], "Toi dau nguc va kho tho.")
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

st.title("Vinmec Smart Intake Assistant")
st.caption("Chat intake, AI guidance, red-flag handoff, booking draft, and doctor dashboard.")

with st.sidebar:
    backend_url = st.text_input("Backend URL", value=DEFAULT_BACKEND_URL)
    col_health, col_reset = st.columns(2)
    if col_health.button("Health"):
        try:
            st.success(api_request("GET", backend_url, "/health"))
        except Exception as exc:
            st.error(f"Backend error: {exc}")
    if col_reset.button("New chat"):
        reset_chat(backend_url)
        st.rerun()

tab_chat, tab_dashboard, tab_flows = st.tabs(["Chat", "Dashboard", "Flow tests"])

with tab_chat:
    try:
        session = get_or_create_session(backend_url)
        st.markdown(
            f"""
            <span class="status-pill">Session: {session["session_id"]}</span>
            <span class="status-pill">Case: {session["case_id"]}</span>
            """,
            unsafe_allow_html=True,
        )
    except Exception as exc:
        st.error(f"Cannot connect to backend: {exc}")
        st.stop()

    if not st.session_state.chat_messages:
        with st.chat_message("assistant"):
            st.write(
                "Chao ban. Hay mo ta trieu chung, minh se hoi them thong tin can thiet, "
                "kiem tra dau hieu nguy hiem va ho tro tao lich kham ao neu phu hop."
            )

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message["role"] == "assistant" and message.get("response_type"):
                st.caption(f"response_type: {message['response_type']}")

    if st.session_state.last_response:
        replies = st.session_state.last_response.get("quick_replies", [])
        if replies:
            st.caption("Quick replies")
            cols = st.columns(min(len(replies), 4))
            for index, reply in enumerate(replies):
                if cols[index % len(cols)].button(reply, key=f"reply-{len(st.session_state.chat_messages)}-{index}"):
                    submit_chat_message(backend_url, reply)
                    st.rerun()

    prompt = st.chat_input("Nhap trieu chung hoac phan hoi cua ban...")
    if prompt:
        submit_chat_message(backend_url, prompt)
        st.rerun()

    with st.expander("Current case data", expanded=False):
        if st.session_state.last_response:
            st.json(
                {
                    "case": st.session_state.last_response.get("case"),
                    "patient": st.session_state.last_response.get("patient"),
                    "booking": st.session_state.last_response.get("booking"),
                    "sources": st.session_state.last_response.get("sources"),
                }
            )
        else:
            st.info("Send a message to create case data.")

with tab_flows:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Flow 1: normal case + booking")
        if st.button("Run normal booking flow"):
            result = run_normal_booking_flow(backend_url)
            last = result["responses"][-1]
            st.metric("Final response", last["response_type"])
            st.metric("Booking status", last["booking"]["booking_status"] if last["booking"] else "none")
            st.json(result)
    with col_b:
        st.subheader("Flow 2: red flag")
        if st.button("Run red flag flow"):
            result = run_red_flag_flow(backend_url)
            st.metric("Response", result["response"]["response_type"])
            st.metric("Priority", result["response"]["case"]["priority"])
            st.json(result)

with tab_dashboard:
    if st.button("Refresh doctor cases"):
        st.session_state.doctor_cases = api_request("GET", backend_url, "/doctor/cases")
    doctor_cases = st.session_state.get("doctor_cases", [])
    st.dataframe(doctor_cases, use_container_width=True)
    selected_case = st.text_input(
        "Case ID",
        value=doctor_cases[0]["case_id"] if doctor_cases else "",
    )
    if st.button("Load case detail") and selected_case:
        detail = api_request("GET", backend_url, f"/doctor/cases/{selected_case}")
        logs = api_request("GET", backend_url, f"/debug/cases/{selected_case}/logs")
        st.subheader("Case detail")
        st.json(detail)
        st.subheader("Evidence and sources")
        st.json({"evidence_context": detail.get("evidence_context"), "sources": detail.get("sources")})
        st.subheader("Audit logs")
        st.json(logs)
