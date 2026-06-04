# Synthesis Decision - Từ Evidence Đến Build Slice

## 1. Gom evidence thành cụm

- `Bot hỏi chưa đủ linh hoạt khi user mô tả triệu chứng`
- `User không biết cần cung cấp thông tin nào`
- `Red flag chưa được xử lý nhất quán`
- `Handoff có nhưng chưa đủ ngữ cảnh`
- `Analog tốt có disclaimer và red flag guidance`

## 2. Insight

```text
User bệnh nhân/người nhà lần đầu muốn khám từ xa không chỉ cần chatbot trả lời câu hỏi y tế.
Họ cần một flow tiếp nhận giúp họ mô tả triệu chứng đúng cách,
biết khi nào cần đi khám/handoff,
và biến đoạn chat thành thông tin có cấu trúc cho bác sĩ,
vì evidence cho thấy user thường nhập triệu chứng thiếu dữ kiện,
bot hiện tại hỏi chưa linh hoạt,
và các case red flag chưa được xử lý nhất quán.
```

## 3. Opportunity

```text
Cơ hội là dùng AI để augment bước tiếp nhận trước khám:
AI kiểm tra thông tin còn thiếu,
hỏi thêm tối đa 3 câu bằng ngôn ngữ đồng cảm kèm quick replies,
phát hiện red flag trước mỗi lượt phản hồi,
gợi ý chuyên khoa/luồng khám từ xa ở mức tham khảo,
và tạo bản tóm tắt triệu chứng nháp.

Điều này giúp user được điều hướng an toàn hơn,
bác sĩ/nhân viên nhận được ngữ cảnh rõ hơn,
trong khi vẫn giữ quyền quyết định cuối cùng cho user và bác sĩ.
```

## 4. Chọn build slice

| Câu hỏi | Đánh giá của nhóm |
|---|---|
| User cụ thể chưa? | Đạt. User là bệnh nhân/người nhà lần đầu muốn khám từ xa, chưa biết chọn chuyên khoa và chưa biết mô tả triệu chứng đủ rõ. |
| Task đủ hẹp chưa? | Đạt nếu chỉ làm intake từ một triệu chứng ngắn đến summary + routing. Demo được trong 3-5 phút. |
| AI decision rõ chưa? | Đạt. AI quyết định: đủ thông tin để route chưa, thiếu slot nào cần hỏi tiếp, có red flag không. |
| Failure path rõ chưa? | Đạt. Failure path chính là user có red flag nhưng AI vẫn tư vấn thường hoặc gợi ý khám từ xa không khẩn cấp. |
| Có evidence không? | Có self-use screenshots. Cần bổ sung thêm 1 nguồn ngoài nhóm/phỏng vấn nhanh nếu kịp. |

### Build slice cuối

```text
Cho bệnh nhân/người nhà lần đầu muốn khám từ xa nhưng chỉ mô tả triệu chứng rất ngắn,
prototype dùng AI để hỏi thêm tối đa 3 câu theo khung thông tin tối thiểu,
kiểm tra red flag trước mỗi lượt phản hồi,
sau đó gợi ý 1-2 chuyên khoa/luồng khám từ xa phù hợp
và tạo bản tóm tắt triệu chứng nháp cho bác sĩ.
```

## 5. Quyết định scope

### Quyết định: giữ domain, giảm scope

Domain vẫn là Healthcare / Telehealth, nhưng không làm "chatbot y tế tổng quát".

Build trong Day 06:

- Chat intake UI.
- Slot-filling: tuổi/đối tượng, thời gian, mức độ, triệu chứng đi kèm.
- Quick replies.
- Red flag checker rule-based.
- Gợi ý 1-2 chuyên khoa mức tham khảo.
- Draft medical summary.
- 4 test paths.

Không build trong Day 06:

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

Lý do:

- Ý tưởng chatbot y tế tổng quát quá rộng và rủi ro cao.
- Evidence cho thấy pain cụ thể nằm ở intake và handoff.
- Slice intake + routing + summary có thể demo được trong 3-5 phút.
- Red flag rule giúp prototype có trust rõ hơn.

## 6. Câu chốt cuối

```text
Dựa trên evidence rằng user thường nhập triệu chứng thiếu dữ kiện,
VinmecCare hiện tại hỏi chưa linh hoạt và red flag chưa được xử lý nhất quán,
nhóm sẽ build prototype AI Smart Intake Assistant
cho bệnh nhân/người nhà lần đầu muốn khám từ xa,
để giải quyết pain mô tả triệu chứng mơ hồ, chọn chuyên khoa khó và handoff thiếu ngữ cảnh,
bằng cách AI hỗ trợ hỏi thêm thông tin còn thiếu,
phát hiện red flag,
gợi ý chuyên khoa ở mức tham khảo
và tạo bản tóm tắt triệu chứng nháp,
đồng thời test failure path khi user có dấu hiệu nguy hiểm nhưng AI phải dừng flow để Emergency Handoff.
```

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
