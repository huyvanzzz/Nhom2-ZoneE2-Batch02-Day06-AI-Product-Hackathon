# App Teardown — MoMo Quản Lý Chi Tiêu



## 1. Chọn sản phẩm để dùng thử

| Sản phẩm | AI feature | Cách truy cập |
|---|---|---|
| [MoMo](https://www.momo.vn/) | [Quản Lý Chi Tiêu](https://www.momo.vn/quan-ly-chi-tieu), [Trợ thủ tài chính với AI](https://www.momo.vn/tro-thu-tai-chinh) | Website public + app listing |

## 2. Dùng thử: promise vs reality

### Product hứa gì?

- AI tự động ghi chép và phân loại chi tiêu.
- User có thể xem báo cáo tuần/tháng và nhận gợi ý chi tiêu.
- User có thể nhập khoản chi qua chat để giảm nhập tay.

### User nào được hứa sẽ được giúp?

- Người đã dùng MoMo cho thanh toán hằng ngày.
- Người mới muốn bắt đầu quản lý tiền nhưng ngại ghi chép thủ công.

### Tôi kỳ vọng AI làm được task nào?

- Đọc mô tả ngắn như `ăn trưa 65k` hoặc `cafe với khách 90k`.
- Gợi ý đúng danh mục đủ nhanh để user tin báo cáo chi tiêu.
- Hỗ trợ ghi lại khoản chi ngoài MoMo với ít bước nhất có thể.

### Reality: điểm gãy xuất hiện ở đâu?

- MoMo hứa AI giúp ghi chép nhẹ, nhưng flow giao dịch ngoài MoMo vẫn khá thủ công.
- AI có vẻ phân loại theo lịch sử và ngữ cảnh giao dịch, nhưng không thấy path `AI không chắc`.
- Không có dấu hiệu rõ ràng cho việc giải thích vì sao giao dịch bị gán vào danh mục đó.
- Nếu danh mục bị gán sai, user có thể sửa, nhưng chưa thấy cảm giác hệ thống học tốt hơn từ correction.

## 3. Evidence cụ thể

| Evidence | Quan sát | Link |
|---|---|---|
| Product promise | MoMo mô tả AI có thể ghi chép chi tiêu tự động, phân loại tự động và hỗ trợ qua chat. | [MoMo Quản Lý Chi Tiêu](https://www.momo.vn/quan-ly-chi-tieu) |
| Workflow detail | Với khoản chi ngoài MoMo, user vẫn cần nhập số tiền, chọn danh mục và chọn thời gian. | [MoMo Quản Lý Chi Tiêu](https://www.momo.vn/quan-ly-chi-tieu) |
| Classification logic | MoMo nói AI dựa trên lịch sử phân loại, lời nhắn chuyển tiền và dữ liệu AI, nhưng không nêu confidence hay recovery path. | [MoMo Quản Lý Chi Tiêu](https://www.momo.vn/quan-ly-chi-tieu) |
| User review | Review công khai cho thấy có user chỉ muốn làm tác vụ nhanh nhưng app bị nhiều pop-up và nhiễu. | [App Store MoMo](https://apps.apple.com/us/app/momo-tr%E1%BB%A3-th%E1%BB%A7-t%C3%A0i-ch%C3%ADnh-v%E1%BB%9Bi-ai/id918751511) |
| Public discussion | Một thảo luận công khai nhận xét MoMo có quá nhiều feature, khó tập trung vào một task nhỏ. | [Reddit thread](https://www.reddit.com/r/VietNam/comments/13tvu0k/what_are_your_opinion_on_mobile_payment_apps_like/) |

## 4. Prompt/input nên dùng để test

| Input | Kỳ vọng | Điều cần quan sát |
|---|---|---|
| `Ăn trưa 65k` | AI gợi ý đúng `Ăn uống` | Happy path có đủ nhanh và rõ không |
| `Cafe với khách 90k` | AI gợi ý 2 khả năng như `Ăn uống` hoặc `Công việc` | Có low-confidence path không |
| `Linh tinh 120k` | AI không nên tự tin quá mức | Có yêu cầu user chọn lại không |
| `Thuốc và đồ ăn 280k` | AI dễ sai vì mixed-purpose | Failure path có cho sửa ngay không |

## 5. Vẽ 4 paths

| Path | Hiện trạng | Chỗ gãy / cơ hội sửa |
|---|---|---|
| Happy | Giao dịch rõ nghĩa có thể được AI gán danh mục và đưa vào báo cáo. | Giá trị cốt lõi đúng nếu input rõ. |
| Low-confidence | Chưa thấy public flow cho trường hợp AI không chắc. | Nên hiện 2-3 danh mục gợi ý thay vì auto-gán im lặng. |
| Failure | Khoản chi mơ hồ hoặc mixed-purpose có thể bị gán sai. | Sai báo cáo chi tiêu, sai cảnh báo ngân sách, giảm trust. |
| Correction | User có thể sửa, nhưng chưa thấy correction được dùng để giải thích hoặc cải thiện lần sau. | Thiếu vòng lặp học từ user và thiếu UX recovery rõ. |

## 6. Finding thành quyết định product

```text
Khi user nhập một khoản chi mơ hồ như "linh tinh 120k" hoặc "cafe với khách 90k",
AI có thể gán danh mục quá tự tin dựa trên lịch sử cũ,
hậu quả là báo cáo chi tiêu tháng bị sai nhưng user không nhận ra ngay.
Lỗi nằm ở Intent + UX Recovery.
Nên sửa bằng low-confidence path:
- hiển thị 2-3 danh mục gợi ý,
- nói ngắn vì sao AI gợi ý như vậy,
- cho user sửa 1 chạm,
- và dùng correction đó để cải thiện lần gợi ý tiếp theo.
```

## 7. Sketch as-is / to-be

### As-is

```text
User phát sinh giao dịch
-> MoMo tự ghi hoặc user nhập tay
-> AI gán danh mục
-> Báo cáo tuần/tháng

Điểm gãy:
- Khoản chi ngoài MoMo còn nhiều bước tay
- Khoản chi mơ hồ không có path "AI không chắc"
- User khó hiểu vì sao danh mục bị gán như vậy
```

### To-be

```text
User nhập khoản chi ngắn
-> AI đọc mô tả + lịch sử gần đây
-> Nếu rõ: gợi ý 1 danh mục chính và cho xác nhận nhanh
-> Nếu mơ hồ: hiện 2-3 danh mục + confidence
-> User chọn hoặc sửa 1 chạm
-> Hệ thống lưu correction
-> Báo cáo cập nhật ngay
```

## 8. Câu nói rõ finding này sẽ đổi gì trong SPEC

```text
Finding này đổi scope từ "AI quản lý tài chính cá nhân" rất rộng
thành một build slice nhỏ hơn:
AI gợi ý danh mục cho khoản chi mơ hồ ngoài MoMo,
có confidence và one-tap correction để tăng trust vào báo cáo chi tiêu.
```

## 9. Tự kiểm trước khi nộp

- [x] Có ít nhất 1 observation cụ thể kèm link.
- [x] Có đủ 4 paths.
- [x] Finding được viết thành product decision.
- [x] Có sketch as-is và to-be.
- [x] Có một câu nói rõ finding này đổi gì trong SPEC.
