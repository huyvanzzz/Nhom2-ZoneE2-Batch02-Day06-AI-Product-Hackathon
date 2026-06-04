# Synthesis & Decide Toolkit — Vinmec Smart Intake

Dùng sau khi nhóm đã có evidence. Mục tiêu là chốt một build slice đủ nhỏ cho Day 06.

## 1. Gom evidence thành cụm

Nhóm gom theo workflow/pain, không gom theo tên feature.

### Cụm 1: Bot hỏi chưa đủ linh hoạt khi user mô tả triệu chứng

Evidence:
- User nhập “Tôi thấy đau dạ dày đầy hơi khó tiêu 2 tuần nay”, VinmecCare chỉ hỏi tuổi/năm sinh.
- User nhập “Đau bụng thì phải làm sao”, bot vẫn hỏi tuổi/năm sinh.
- User nhập “Đau bụng âm ỉ nhiều ngày rồi hãy tư vấn cho tôi”, bot tiếp tục hỏi tuổi/năm sinh.

Pain:
User đã cung cấp một phần triệu chứng, nhưng bot chưa khai thác tiếp theo triệu chứng đó. Flow hiện tại giống form cứng hơn là intake thông minh.

---

### Cụm 2: User không biết cần cung cấp thông tin nào

Evidence:
- Các input như “Tôi đang bị sốt vậy tôi phải làm gì”, “Tôi bị chảy máu tôi phải làm sao” còn thiếu tuổi, thời gian, mức độ, triệu chứng đi kèm.
- Bot có lúc trả lời dài, có lúc chuyển hotline, nhưng chưa hướng dẫn user bổ sung thông tin theo từng bước.

Pain:
User cần được dẫn dắt bằng câu hỏi ngắn và dễ trả lời, thay vì phải tự biết mô tả triệu chứng theo cấu trúc y khoa.

---

### Cụm 3: Red flag chưa được xử lý nhất quán

Evidence:
- “Tôi đang bị sốt 40 độ” được trả lời bằng hướng dẫn tự chăm sóc như uống thuốc hạ sốt, bù nước, nghỉ ngơi.
- “Tôi bị chảy máu tôi phải làm sao” được trả lời bằng hướng dẫn xử lý tại nhà trước khi làm rõ mức độ/vị trí.
- Một số trường hợp khác lại chuyển hotline/phiếu hỗ trợ.

Pain:
Trong y tế, trust phụ thuộc vào việc AI biết khi nào không nên tư vấn tiếp. Các dấu hiệu nguy hiểm cần được check trước mỗi lượt phản hồi.

---

### Cụm 4: Handoff có nhưng chưa đủ ngữ cảnh

Evidence:
- VinmecCare có thể chuyển sang “Phiếu yêu cầu hỗ trợ” hoặc hotline.
- Tuy nhiên, bot không tạo bản tóm tắt: triệu chứng chính, thời gian, mức độ, thông tin đã hỏi, red flag status.

Pain:
Nếu chuyển người thật mà không có summary, nhân viên/bác sĩ vẫn phải hỏi lại từ đầu. Giá trị của AI chưa đi hết workflow.

---

### Cụm 5: Analog tốt có disclaimer và red flag guidance

Evidence:
- Chatbot sức khỏe tham khảo nêu “khi nào cần đi khám bác sĩ”, có danh sách dấu hiệu cảnh báo và disclaimer không chẩn đoán.
- Khi user hỏi muốn gặp bác sĩ, chatbot gợi ý chuyên khoa Nội Tiêu hóa.

Pain / pattern học được:
AI có thể hỗ trợ định hướng, nhưng phải nói rõ không thay thế bác sĩ, và phải có cơ chế an toàn khi triệu chứng kéo dài/nguy hiểm.

---

## 2. Viết insight

```text
User bệnh nhân/người nhà lần đầu muốn khám từ xa không chỉ cần chatbot trả lời câu hỏi y tế.
Họ thật ra cần một flow tiếp nhận giúp họ mô tả triệu chứng đúng cách, biết khi nào cần đi khám/handoff, và biến đoạn chat thành thông tin có cấu trúc cho bác sĩ,
vì evidence cho thấy user thường nhập triệu chứng thiếu dữ kiện, bot hiện tại hỏi chưa linh hoạt, và các case red flag chưa được xử lý nhất quán.
```

---

## 3. Viết opportunity

```text
Cơ hội là dùng AI để augment bước tiếp nhận trước khám:
AI kiểm tra thông tin còn thiếu, hỏi thêm tối đa 3 câu bằng ngôn ngữ đồng cảm kèm quick replies, phát hiện red flag trước mỗi lượt phản hồi, gợi ý chuyên khoa/luồng khám từ xa ở mức tham khảo, và tạo bản tóm tắt triệu chứng nháp.
Điều này giúp user được điều hướng an toàn hơn, bác sĩ/nhân viên nhận được ngữ cảnh rõ hơn, trong khi vẫn giữ quyền quyết định cuối cùng cho user và bác sĩ.
```

---

## 4. Chọn build slice

Build slice tốt phải qua 5 câu hỏi.

| Câu hỏi | Đánh giá của nhóm |
|---|---|
| User cụ thể chưa? | Đạt. User là bệnh nhân/người nhà lần đầu muốn khám từ xa, chưa biết chọn chuyên khoa và chưa biết mô tả triệu chứng đủ rõ. |
| Task đủ hẹp chưa? | Đạt nếu chỉ làm intake từ một triệu chứng ngắn đến summary + routing. Demo được trong 3-5 phút. |
| AI decision rõ chưa? | Đạt. AI quyết định: đủ thông tin để route chưa, thiếu slot nào cần hỏi tiếp, có red flag không. |
| Failure path rõ chưa? | Đạt. Failure path chính là user có red flag nhưng AI vẫn tư vấn thường hoặc gợi ý khám từ xa không khẩn cấp. |
| Có evidence không? | Có self-use screenshots. Cần bổ sung thêm 1 nguồn ngoài nhóm/phỏng vấn nhanh trước checkpoint M1 Day 06. |

### Build slice cuối

```text
Cho bệnh nhân/người nhà lần đầu muốn khám từ xa nhưng chỉ mô tả triệu chứng rất ngắn,
prototype dùng AI để hỏi thêm tối đa 3 câu theo khung thông tin tối thiểu,
kiểm tra red flag trước mỗi lượt phản hồi,
sau đó gợi ý 1-2 chuyên khoa/luồng khám từ xa phù hợp và tạo bản tóm tắt triệu chứng nháp cho bác sĩ.
```

---

## 5. Quyết định: giữ, giảm scope, hay đổi hướng?

### Quyết định: Giữ domain, giảm scope.

Domain vẫn là Healthcare / Telehealth, nhưng không làm “chatbot y tế tổng quát”.

Build trong Day 06:
- Chat intake UI.
- Slot-filling: tuổi/đối tượng, thời gian, mức độ, triệu chứng đi kèm.
- Quick replies.
- Red flag checker rule-based.
- Gợi ý 1-2 chuyên khoa mức tham khảo.
- Draft medical summary.
- 4 test paths.

Không build trong Day 06:
- Đặt lịch thật với hệ thống Vinmec.
- Chẩn đoán bệnh.
- Kê đơn thuốc.
- Tích hợp hồ sơ bệnh án thật.
- Kết nối bác sĩ thật.
- Thanh toán.

Lý do:
- Ý tưởng chatbot y tế tổng quát quá rộng và rủi ro cao.
- Evidence cho thấy pain cụ thể nằm ở intake và handoff.
- Slice intake + routing + summary có thể demo được trong 3-5 phút.
- Red flag rule giúp prototype có trust rõ hơn.

---

## 6. Câu chốt cuối

```text
Dựa trên evidence rằng user thường nhập triệu chứng thiếu dữ kiện, VinmecCare hiện tại hỏi chưa linh hoạt và red flag chưa được xử lý nhất quán,
nhóm sẽ build prototype AI Smart Intake Assistant,
cho bệnh nhân/người nhà lần đầu muốn khám từ xa,
để giải quyết pain mô tả triệu chứng mơ hồ, chọn chuyên khoa khó và handoff thiếu ngữ cảnh,
bằng cách AI hỗ trợ hỏi thêm thông tin còn thiếu, phát hiện red flag, gợi ý chuyên khoa ở mức tham khảo và tạo bản tóm tắt triệu chứng nháp,
và sẽ test failure path khi user có dấu hiệu nguy hiểm nhưng AI phải dừng flow để Emergency Handoff.
```

---

## 7. Backlog

Những thứ không build trong Day 06:

- Đặt lịch thật trên hệ thống Vinmec.
- Đồng bộ hồ sơ bệnh án thật.
- Dashboard bác sĩ đầy đủ.
- Tích hợp hotline thật.
- Thanh toán.
- Nhận diện người dùng bằng tài khoản thật.
- Cá nhân hóa theo lịch sử khám.
- Chẩn đoán bệnh.
- Kê đơn thuốc.
- Bao phủ toàn bộ triệu chứng y tế.
- Đánh giá mức độ nguy hiểm bằng mô hình y khoa phức tạp.
