# Day06-LớpC401-Nhóm E2-nhóm2

## Thành viên

| Mã HV | Họ và tên | Vai trò dự kiến |
|---|---|---|
| 2A202600869 | Lã Duy Anh | SPEC / report, test case demo |
| 2A202600686 | Dương Quang Minh | UI |
| 2A202600679 | Trần Quốc Khánh | Backend |
| 2A202600773 | Nguyễn Anh Kiệt | AI tools |
| 2A202600677 | Nguyễn Văn Huy | Repo / merge code, xây prompt |

## Sản phẩm

**AI Smart Intake Assistant cho Vinmec**

Prototype đề xuất một trợ lý AI intake thông minh cho người dùng Vinmec/MyVinmec. Thay vì chatbot hỏi cộc lốc hoặc trả lời rỗng khi người dùng mô tả triệu chứng tự nhiên, sản phẩm sẽ hỏi làm rõ theo ngữ cảnh, phát hiện dấu hiệu nguy hiểm, gợi ý chuyên khoa/cơ sở phù hợp, dẫn sang đặt lịch khám ảo và lưu tóm tắt ban đầu cho bác sĩ hoặc CSKH.

Prototype không chẩn đoán bệnh, không kê đơn thuốc và không thay thế bác sĩ. AI chỉ hỗ trợ tiếp nhận thông tin, định hướng chuyên khoa và tạo tóm tắt trước khám.

## Track

Healthcare - ứng dụng tham chiếu: Vinmec / MyVinmec / VinmecCare.

## Tài liệu

- SPEC sản phẩm: [spec/spec.md](spec/spec.md)
- Hướng dẫn SPEC gốc: [spec/README.md](spec/README.md)
- Code prototype: [codebase/](codebase/)
- Luật hackathon: [hackathon-rules.md](hackathon-rules.md)
- Evidence Pack Day 5: [02-group-spec/evidence-pack.md](02-group-spec/evidence-pack.md)
- Thin SPEC Day 5: [02-group-spec/thin-spec.md](02-group-spec/thin-spec.md)

## Cách chạy prototype

Backend:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".\codebase\backend[dev]"
cd codebase\backend
..\..\.venv\Scripts\python.exe -m uvicorn vinm_backend.main:app --reload
```

Frontend:

```powershell
cd codebase\frontend
python -m http.server 4173
```

Sau đó mở `http://localhost:4173`. Backend chạy ở `http://127.0.0.1:8000`.

## Công nghệ / API

- Frontend: HTML5, CSS3, Vanilla JavaScript.
- Backend: FastAPI, Pydantic, Uvicorn.
- Storage: SQLite cho case snapshot và audit logs.
- AI: OpenAI-compatible Chat Completions API qua `OpenAIGatewayClient`.
- Search context: Tavily + Firecrawl, ưu tiên Vinmec/trusted medical domains.
- API chính: `/chat/session`, `/chat/message`, `/doctor/cases`, `/booking/draft`, `/doctor/dashboard/stats`.
- Fallback: rule-based extractor/red flag/summary khi AI hoặc search external lỗi.

## Phân công

| Vai trò | Việc chính | Owner |
|---|---|---|
| Report + test case demo | Viết SPEC/report, cập nhật theo codebase, chuẩn bị bộ test case demo và expected result cho 4 flow | Lã Duy Anh |
| UI | Thiết kế và build giao diện chat intake, quick replies, màn hình kết quả/gợi ý chuyên khoa, booking draft và dashboard hiển thị | Dương Quang Minh |
| Backend | Xây API, lưu session/case/message/booking, xử lý orchestration và kết nối dashboard | Trần Quốc Khánh |
| AI tools | Xây tools, extractor, search context, triage logic và red-flag rule phối hợp với backend | Nguyễn Anh Kiệt |
| Repo / merge code, xây prompt | Quản lý repo, review/merge code, xử lý conflict, kiểm tra cấu trúc nộp bài và hướng dẫn chạy | Nguyễn Văn Huy |
