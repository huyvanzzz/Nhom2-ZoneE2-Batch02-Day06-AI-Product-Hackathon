# Bao cao tinh trang du an Day 6

Du an hien tai da co MVP backend-first cho **Vinmec Smart Intake Assistant** theo `plan_day6.txt`. Muc tieu demo la intake chat, red-flag override, booking ao, luu case, dashboard bac si/CSKH va audit log.

## Tom tat tien do

Trang thai tong quan: **backend MVP da chay duoc 4 flow bat buoc trong plan**.

| Hang muc theo plan | Trang thai | Bang chung hien co |
|---|---:|---|
| Chat intake | Hoan thanh MVP | `POST /chat/session`, `POST /chat/message`, chat history |
| Intake extractor | Hoan thanh MVP | Trich xuat relation, tuoi, trieu chung, thoi gian, muc do, booking intent |
| Medical context search | Hoan thanh MVP | `MedicalContextSearchTool` goi Tavily/Firecrawl khi app runtime co env; fallback deterministic neu tool loi |
| Triage so bo | Hoan thanh MVP | Priority low/medium/high dua tren severity/duration |
| Hardcoded red flag override | Hoan thanh | Dau nguc, kho tho, sot 40, chay mau, dau bung du doi, non ra mau, phan den, ngat/lo mo/co giat, sung moi/mat/luoi |
| Safe guidance | Hoan thanh MVP | Response `safe_guidance` cho ca khong nguy hiem |
| Specialty suggestion | Hoan thanh MVP | Dang map trieu chung tieu hoa sang `Noi Tieu hoa` |
| Booking ao trong chat | Hoan thanh MVP | Hoi co so/thoi gian, xac nhan, tao `booking_status=draft` |
| Patient info | Hoan thanh MVP | Luu `patient_id`, relation, age, default unknown fields |
| Chat history | Hoan thanh | Luu user/assistant messages theo session |
| Doctor summary | Hoan thanh MVP | Tao summary text gan voi case |
| Doctor dashboard | Hoan thanh MVP | `GET /doctor/cases`, `GET /doctor/cases/{case_id}` |
| Doctor notes/status | Hoan thanh MVP | `POST /doctor/cases/{case_id}/notes`, `PATCH /doctor/cases/{case_id}/status` |
| Audit log | Hoan thanh MVP | `GET /debug/cases/{case_id}/logs` |
| Streamlit test UI | Hoan thanh trong dot nay | `codebase/backend/streamlit_app.py` |
| Chat response bang AI | Hoan thanh MVP | `SmartIntakeService` dung OpenAI-compatible gateway trong safe-guidance branch; red flag khong goi AI |

## API hien co

- `GET /health`
- `POST /chat/session`
- `POST /chat/message`
- `GET /chat/session/{session_id}/messages`
- `GET /cases/{case_id}`
- `PATCH /cases/{case_id}`
- `POST /booking/draft`
- `GET /booking/{booking_id}`
- `PATCH /booking/{booking_id}`
- `GET /doctor/cases`
- `GET /doctor/cases/{case_id}`
- `POST /doctor/cases/{case_id}/notes`
- `PATCH /doctor/cases/{case_id}/status`
- `GET /debug/cases/{case_id}/logs`
- `POST /v1/assist` van duoc giu lai cho backend v1 cu.

## 4 flow trong plan

1. **Ca thuong + dat lich:** Da pass bang automated test. Flow tao session, hoi tuoi/muc do, goi y `Noi Tieu hoa`, hoi booking, xac nhan, tao booking draft va hien tren dashboard.
2. **Ca nguy hiem:** Da pass bang automated test va runtime smoke. Input `Toi dau nguc va kho tho.` tra `emergency_handoff`, priority `high`, red flag `confirmed`, khong tao booking thuong.
3. **User hoi thay nguoi than:** Da cover trong flow thuong. Input `Me toi 58 tuoi...` luu `patient_relation=mother` va age `58`.
4. **Dashboard bac si:** Da pass bang automated test. Dashboard list/detail hien case, patient fields, priority, specialty, booking status, summary, chat/log endpoints.

## Gioi han hien tai

- Intake flow dang in-memory, restart server se mat case/session/booking.
- Medical context trong `SmartIntakeService` da gan Tavily/Firecrawl qua `main.py`; neu external tool loi thi fallback deterministic de demo khong crash.
- AI chat response da gan OpenAI-compatible gateway theo `ENVIRONMENT.md`; neu gateway loi thi fallback text deterministic.
- Chua co database, auth, frontend production, booking that, payment, EMR sync, real-time doctor call.
- Text response dang de ASCII de tranh loi encoding trong PowerShell/repo hien tai.

## Lenh test va demo

```powershell
cd codebase/backend
..\..\.venv\Scripts\python.exe -m pip install -e ".[dev]"
..\..\.venv\Scripts\python.exe -m pytest -v
..\..\.venv\Scripts\python.exe -m uvicorn vinm_backend.main:app --reload
```

Streamlit test UI:

```powershell
cd codebase/backend
..\..\.venv\Scripts\python.exe -m streamlit run streamlit_app.py --server.port 8501
```

## Ket luan

Tinh den hien tai, backend da du de demo Day 6 theo `plan_day6.txt`: co chat intake, AI safe-guidance response, Tavily/Firecrawl search context, red flag safety, booking draft, dashboard va audit. Phan can lam tiep neu muon nang cap la them database, auth, va UI production thay cho Streamlit test harness.
