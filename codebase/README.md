# Codebase - AI Smart Intake Assistant cho Vinmec

Thư mục này chứa prototype hoàn chỉnh cho Day 06 gồm:

- `frontend/`: website demo Vinmec + AI chat widget + dashboard preview.
- `backend/`: FastAPI backend cho smart intake, red flag rule, AI orchestration, search context, booking draft, doctor dashboard và audit log.

Prototype chứng minh lát cắt chính của sản phẩm: người dùng nhập triệu chứng tự nhiên, hệ thống hỏi bổ sung thông tin còn thiếu, kiểm tra red flag, gợi ý chuyên khoa, tạo booking draft và lưu tóm tắt ca bệnh cho bác sĩ/CSKH.

## Cách chạy

### 1. Tạo môi trường Python và cài backend

Từ thư mục gốc repo:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".\codebase\backend[dev]"
```

### 2. Tạo file môi trường

Tạo file `.env` ở thư mục gốc repo với các biến sau:

```text
OPENAI_API_KEY=
OPENAI_BASE_URL=
OPENAI_MODEL=
FIRECRAWL_API_KEY=
TAVILY_API_KEY=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Không commit file `.env` thật. Nếu chưa có key thật, backend vẫn có nhiều fallback rule-based để phục vụ demo/test nội bộ, nhưng AI/search external sẽ không chạy đầy đủ.

### 3. Chạy backend

```powershell
cd codebase\backend
..\..\.venv\Scripts\python.exe -m uvicorn vinm_backend.main:app --reload
```

Backend mặc định chạy tại:

```text
http://127.0.0.1:8000
```

### 4. Chạy frontend

Mở một terminal khác:

```powershell
cd codebase\frontend
python -m http.server 4173
```

Sau đó truy cập:

```text
http://localhost:4173
```

Frontend mặc định gọi backend tại `http://127.0.0.1:8000`. Nếu backend chưa chạy, frontend có fallback local mock để vẫn demo được giao diện.

## Cách test

Từ thư mục `codebase/backend`:

```powershell
..\..\.venv\Scripts\python.exe -m pytest
```

Bộ test hiện có trong `codebase/backend/tests/`, bao gồm smoke test, API test, smart intake flow, orchestrator, retrieval adapters, OpenAI gateway và Day 6 API.

## Stack sử dụng

| Lớp | Công nghệ |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | FastAPI, Pydantic, Uvicorn |
| Storage | SQLite qua `SqliteIntakeStore` |
| AI gateway | OpenAI-compatible Chat Completions API |
| Search context | Tavily + Firecrawl, có trusted-domain fallback |
| Dashboard/demo | Frontend dashboard preview + backend doctor endpoints |
| Optional handoff | Telegram adapter |

## API chính

| Method | Endpoint | Mục đích |
|---|---|---|
| `GET` | `/health` | Kiểm tra backend |
| `POST` | `/chat/session` | Tạo intake session |
| `POST` | `/chat/message` | Gửi message và nhận phản hồi AI/intake |
| `GET` | `/chat/session/{session_id}/messages` | Xem lịch sử chat |
| `GET` | `/cases/{case_id}` | Xem intake case |
| `PATCH` | `/cases/{case_id}` | Cập nhật case |
| `POST` | `/booking/draft` | Tạo booking draft |
| `GET` | `/booking/{booking_id}` | Xem booking draft |
| `GET` | `/doctor/cases` | Danh sách case cho bác sĩ/CSKH |
| `GET` | `/doctor/cases/{case_id}` | Chi tiết case |
| `POST` | `/doctor/login` | Login demo bằng mã bác sĩ |
| `GET` | `/doctor/dashboard/stats` | Thống kê dashboard |
| `GET` | `/doctor/cases/{case_id}/logs` | Audit log của case |
| `GET` | `/vinmec/facilities` | Danh sách cơ sở Vinmec demo |

## Những gì đã implement

- Frontend song ngữ Việt/Anh.
- Chat widget nổi trên website demo Vinmec.
- Backend-first API client trên frontend.
- Local frontend fallback khi backend chưa chạy.
- Intake session, message history, case, patient info và booking draft.
- Slot extraction cho người bệnh, tuổi, triệu chứng, thời gian, mức độ, cơ sở và thời gian khám.
- Red flag rule-based gate chạy trước khi tiếp tục tư vấn thường.
- Gợi ý chuyên khoa theo rule và AI fallback.
- Medical context search ưu tiên Vinmec/trusted medical domains.
- Doctor summary bằng AI nếu có key, fallback rule-based nếu AI lỗi.
- SQLite persistence cho case snapshot và audit logs.
- Doctor dashboard endpoints, login demo và dashboard stats.

## Flow demo cần pass

| Flow | Input mẫu | Kết quả mong đợi |
|---|---|---|
| Happy path | `Tôi đau dạ dày, đầy hơi khó tiêu 2 tuần nay.` sau đó `Mẹ tôi 58 tuổi, đau vừa.` | Backend hỏi thêm slot còn thiếu, gợi ý Nội Tiêu hóa, tạo summary và cho phép booking draft. |
| Low-confidence | `Tôi mệt, chóng mặt, khó ngủ.` | Hệ thống không chẩn đoán, hỏi thêm thông tin hoặc fallback an toàn. |
| Red flag | `Tôi đau ngực và khó thở.` | `response_type = emergency_handoff`, priority high, dashboard ghi nhận red flag. |
| Correction | User sửa người bệnh, tuổi hoặc ngữ cảnh sau khi đã nhập triệu chứng. | Case/patient fields được cập nhật, summary và dashboard phản ánh thông tin mới. |
| Dashboard | Bác sĩ/CSKH mở danh sách case. | Thấy case, patient info, red flag status, booking status, doctor summary và audit logs. |

## Giới hạn prototype

- Không chẩn đoán bệnh.
- Không kê đơn thuốc hoặc liều thuốc.
- Không đặt lịch thật vào hệ thống Vinmec production.
- Không đồng bộ EMR/hồ sơ bệnh án thật.
- Không có phân quyền production; `doctor/login` chỉ là demo.
- External AI/search phụ thuộc API key trong `.env`; khi lỗi sẽ dùng fallback rule-based để demo an toàn.

## Phân công liên quan codebase

| Vai trò | Owner | Phần liên quan |
|---|---|---|
| Report + test case demo | Lã Duy Anh | Đối chiếu codebase với SPEC, viết test case demo và bằng chứng |
| UI | Dương Quang Minh | Frontend, chat widget, dashboard preview |
| Backend | Trần Quốc Khánh | FastAPI endpoints, SQLite store, session/case/booking/dashboard |
| AI tools | Nguyễn Anh Kiệt | OpenAI gateway, Tavily/Firecrawl context search, triage/summary |
| Repo / merge code, xây prompt | Nguyễn Văn Huy | Merge code, prompt/rule, cấu trúc nộp bài |
