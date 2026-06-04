# Vinmec Smart Intake Assistant Frontend

Prototype frontend cho flow hackathon healthcare: mô phỏng một website Vinmec có AI agent nổi ở góc phải dưới để intake triệu chứng, phát hiện red flag, gợi ý chuyên khoa và tạo booking draft ngay trong chat.

## Chạy prototype

### Chạy nối backend Day 6

1. Start backend ở port mặc định `8000`:

```powershell
cd codebase/backend
..\..\.venv\Scripts\python.exe -m uvicorn vinm_backend.main:app --reload
```

2. Serve frontend từ thư mục `codebase/frontend`:

```powershell
cd codebase/frontend
python -m http.server 4173
```

3. Truy cập `http://localhost:4173`.

Frontend mặc định gọi backend tại `http://127.0.0.1:8000`. Nếu cần đổi, đặt trước khi load `app.js`:

```html
<script>
  window.VINMEC_API_BASE_URL = "http://127.0.0.1:8000";
</script>
```

Nếu backend chưa chạy, widget sẽ fallback về local mock intake engine để vẫn demo được giao diện.

## Những gì prototype đang demo

- Landing page phong cách Vinmec, phù hợp để đặt AI assistant ngay trên web.
- Chuyển ngôn ngữ `Tiếng Việt / English` cho cả homepage và widget AI.
- Chat widget nổi với lời chào: `Tôi có thể giúp gì cho bạn hôm nay?`
- Luồng intake thường:
  - mô tả triệu chứng
  - hỏi relation
  - hỏi tuổi
  - hỏi mức độ
  - gợi ý chuyên khoa + safe guidance
  - tạo booking draft
- Luồng red flag:
  - phát hiện các tín hiệu như `đau ngực`, `khó thở`, `nôn ra máu`, `phân đen`
  - chặn tư vấn tiếp và chuyển sang emergency handoff
- Dashboard preview đồng bộ live theo hội thoại để demo handoff cho bác sĩ/CSKH.

## Stack sử dụng

- HTML5
- CSS3
- Vanilla JavaScript
- Backend-first API client gọi `POST /chat/session` và `POST /chat/message`
- Local mock intake engine làm fallback khi backend chưa chạy
- Public visual assets loaded from `vinmec.com` to make the background feel closer to the real English homepage during demo

## File chính

- `index.html`: cấu trúc landing page + widget chat
- `styles.css`: visual system, responsive layout, motion
- `app.js`: state machine cho intake flow, red flag và booking draft

## Gợi ý nối backend sau đó

Hiện tại `handleUserInput` đã ưu tiên backend trước. Response backend được map vào widget và dashboard preview gồm assistant text, quick replies, case snapshot, patient fields, booking draft và doctor summary.

## Phân công

| Vai trò | Owner | Phần liên quan frontend |
|---|---|---|
| Report + test case demo | Lã Duy Anh | Đối chiếu frontend với SPEC, chuẩn bị flow demo |
| UI | Dương Quang Minh | Homepage, chat widget, responsive layout, dashboard preview |
| Backend | Trần Quốc Khánh | API contract để frontend gọi backend |
| AI tools | Nguyễn Anh Kiệt | Response shape, quick replies, summary/triage data cho frontend render |
| Repo / merge code, xây prompt | Nguyễn Văn Huy | Merge frontend với backend, kiểm tra cấu trúc nộp bài |
