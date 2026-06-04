# Reflection Cá Nhân — Day 05 / Day 06 AI Product Lab

> Ghi chú: phần này được điền sẵn theo lát cắt `MoMo - AI gợi ý danh mục cho khoản chi mơ hồ`. Những chỗ cần dữ liệu cá nhân thật được để dưới dạng placeholder rất ngắn để bạn sửa nhanh.

## 1. Vai trò của tôi

- Họ tên: `[Điền họ tên]`
- Mã học viên: `[Điền mã học viên]`
- Vai trò chính trong nhóm: `Research + product framing`
- Track: `Fintech / personal finance`

## 2. Tôi đã làm gì

- Đọc yêu cầu repo Day 05 và tách rõ hai phần cần nộp: artifact cá nhân và artifact nhóm.
- Mổ app MoMo ở góc nhìn AI product thay vì chỉ nhìn UI.
- Gom evidence từ trang public của MoMo, App Store review, và nguồn thảo luận công khai.
- Cắt scope từ ý tưởng quá rộng "AI quản lý tài chính" xuống một build slice nhỏ, test được trong 1 ngày:
  `AI gợi ý 2-3 danh mục cho khoản chi mơ hồ ngoài MoMo, có confidence + correction`.
- Viết lại finding theo ngôn ngữ product decision: user nào, task nào, failure nào, mitigation nào.

## 3. AI đã hỗ trợ tôi như thế nào

- AI giúp tôi đọc nhanh README và bóc tách thành checklist artifact cụ thể.
- AI hỗ trợ tổng hợp evidence từ nhiều nguồn thành một insight xuyên suốt thay vì để thông tin rời rạc.
- AI giúp chuyển nhận xét cảm tính như "app nhiều thứ quá" thành một phát biểu product có thể build và test.
- AI cũng giúp biến problem rộng thành thin SPEC có đủ: user, build slice, auto/aug decision, four paths và failure mode.

## 4. Điều tôi học được

- Một app AI không thất bại chỉ vì model sai; nó còn thất bại khi không có recovery path rõ cho lúc model không chắc.
- "Nhiều tính năng" không đồng nghĩa với "nhiều giá trị". Với sản phẩm tài chính, trust và khả năng sửa nhanh quan trọng hơn cảm giác thông minh.
- Scope đúng cho prototype không phải là "làm AI assistant cho tài chính", mà là chọn đúng một quyết định nhỏ mà AI hỗ trợ tốt hơn flow hiện tại.
- Evidence tốt không cần quá nhiều, nhưng phải đủ để buộc nhóm đổi SPEC ở một điểm cụ thể.

## 5. Đóng góp cụ thể vào repo

- Hoàn thiện `01-invidual-workshop/app-teardown.md`
- Soạn `02-group-spec/evidence-pack.md`
- Soạn `02-group-spec/synthesis-decision.md`
- Soạn `02-group-spec/thin-spec.md`

## 6. Cập nhật sau demo

> Phần này cần bạn điền bằng trải nghiệm thật sau khi nhóm demo, vì mình không nên bịa kết quả demo thay bạn.

- Demo có đi đúng lát cắt đã chọn không? `[Có / Không + 1 câu giải thích]`
- User/giảng viên phản hồi mạnh nhất ở đâu? `[Điền 1-2 ý]`
- Failure path có lộ ra như dự đoán không? `[Điền]`
- Nếu làm lại trong 1 vòng nữa, tôi sẽ đổi điều gì đầu tiên? `[Điền]`
