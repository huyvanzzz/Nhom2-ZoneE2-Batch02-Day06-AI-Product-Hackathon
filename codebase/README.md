# Vinmec Smart Intake Assistant Frontend

Prototype frontend cho flow hackathon healthcare: mô phỏng một website Vinmec có AI agent nổi ở góc phải dưới để intake triệu chứng, phát hiện red flag, gợi ý chuyên khoa và tạo booking draft ngay trong chat.

## Chạy prototype

### Cách nhanh nhất

Mở trực tiếp file `index.html` trong trình duyệt.

### Nếu muốn chạy bằng local server

Từ thư mục `codebase`, chạy:

```powershell
python -m http.server 4173
```

Sau đó truy cập `http://localhost:4173`.

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
- Local mock intake engine để frontend có thể demo độc lập trước khi nối backend/API AI thật
- Public visual assets loaded from `vinmec.com` to make the background feel closer to the real English homepage during demo

## File chính

- `index.html`: cấu trúc landing page + widget chat
- `styles.css`: visual system, responsive layout, motion
- `app.js`: state machine cho intake flow, red flag và booking draft

## Gợi ý nối backend sau đó

Điểm phù hợp để thay thế local mock là hàm `handleUserInput` trong `app.js`.
Team backend có thể đổi sang flow:

1. Frontend gửi message lên `POST /chat/message`
2. Backend trả về:
   - assistant text
   - quick replies
   - case snapshot
   - doctor summary
3. Frontend chỉ render lại widget và dashboard preview

## Phân công

Bạn có thể cập nhật thêm phần tên thành viên và trách nhiệm cụ thể của nhóm trước khi nộp repo.
