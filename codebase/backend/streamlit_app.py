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


st.set_page_config(page_title="Vinmec Smart Intake Test", layout="wide")
st.title("Vinmec Smart Intake Assistant")

with st.sidebar:
    backend_url = st.text_input("Backend URL", value=DEFAULT_BACKEND_URL)
    if st.button("Check health"):
        try:
            st.success(api_request("GET", backend_url, "/health"))
        except Exception as exc:
            st.error(f"Backend error: {exc}")

tab_chat, tab_flows, tab_dashboard = st.tabs(["Manual chat", "Flow tests", "Dashboard"])

with tab_chat:
    if "session" not in st.session_state:
        st.session_state.session = None
    if st.button("Create chat session"):
        st.session_state.session = api_request("POST", backend_url, "/chat/session")
    st.json(st.session_state.session)

    content = st.text_input("User message", value="Toi dau da day, day hoi kho tieu 2 tuan nay.")
    if st.button("Send message") and st.session_state.session:
        result = send_message(backend_url, st.session_state.session["session_id"], content)
        st.json(result)

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
    st.dataframe(st.session_state.get("doctor_cases", []), use_container_width=True)
