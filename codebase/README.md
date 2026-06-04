# Codebase

Đây là nơi nhóm nộp toàn bộ phần code của prototype. Mục tiêu là để giảng viên và các nhóm khác nhìn được sản phẩm chạy như thế nào, và mỗi thành viên đã đóng góp ra sao.

## Nhóm cần làm

- Đưa mã nguồn của prototype vào folder này. Nếu prototype được deploy hoặc host ở nơi khác, hãy để lại đường link kèm hướng dẫn truy cập.
- Trong file `README.md` của nhóm, ghi rõ ba điều: cách chạy prototype (các bước cài đặt và biến môi trường nếu cần), những công cụ và API đã dùng (model AI, framework, công cụ dựng giao diện…), và phần phân công ai làm gì.
- Mỗi thành viên nên có ít nhất một commit thực chất trong repo — đây là căn cứ để ghi nhận đóng góp của từng người.

## Lưu ý

Đừng commit những thông tin nhạy cảm như API key hay file `.env`. Nếu prototype cần các biến môi trường, hãy dùng một file `.env.example` để mô tả các biến đó thay vì để lộ giá trị thật.

## Backend v1

The backend prototype lives in `codebase/backend`.

### Run

1. Create or activate the root `.venv`.
2. Install backend dependencies:

```powershell
cd codebase/backend
..\..\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

3. Run tests:

```powershell
..\..\.venv\Scripts\python.exe -m pytest -v
```

4. Start the API:

```powershell
..\..\.venv\Scripts\python.exe -m uvicorn vinm_backend.main:app --reload
```

### Demo flow

- `GET /health` returns `{"status":"ok"}`.
- `POST /v1/assist` accepts `{"query":"..."}` and returns a structured answer with sources.
- The flow is: validate request, search Tavily, scrape Firecrawl, answer with the OpenAI-compatible gateway, notify Telegram.
- If the AI gateway fails, the backend returns `status="error"` instead of crashing.

### Day 6 Smart Intake Assistant

The Day 6 agent is an in-memory Vinmec Smart Intake MVP. It supports normal intake, red-flag emergency handoff, virtual booking draft, doctor dashboard, and audit logs.

Core endpoints:

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

Demo payloads:

```powershell
$session = Invoke-RestMethod -Method Post http://127.0.0.1:8000/chat/session

Invoke-RestMethod -Method Post http://127.0.0.1:8000/chat/message `
  -ContentType "application/json" `
  -Body (@{ session_id=$session.session_id; content="Toi dau da day, day hoi kho tieu 2 tuan nay." } | ConvertTo-Json)

Invoke-RestMethod -Method Post http://127.0.0.1:8000/chat/message `
  -ContentType "application/json" `
  -Body (@{ session_id=$session.session_id; content="Me toi 58 tuoi, dau vua." } | ConvertTo-Json)

Invoke-RestMethod http://127.0.0.1:8000/doctor/cases
```
