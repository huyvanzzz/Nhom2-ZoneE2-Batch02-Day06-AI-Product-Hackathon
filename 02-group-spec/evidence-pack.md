# Evidence Pack - Vinmec Smart Intake & Telehealth Router

Nộp kèm Thin SPEC cuối Day 05.

## 1. Nhóm và track

**Tên nhóm:** VinM

**Track:** Healthcare / Telehealth / Patient Intake

**Product/app đã chọn:** Trợ lý ảo VinmecCare và luồng hỏi đáp sức khỏe/đặt lịch khám từ xa.

**Build slice đang nghĩ:**

AI Smart Intake Assistant: trợ lý tiếp nhận triệu chứng ban đầu, hỏi thêm thông tin còn thiếu, phát hiện dấu hiệu nguy hiểm, gợi ý chuyên khoa/luồng khám từ xa phù hợp và tạo bản tóm tắt triệu chứng nháp cho bác sĩ.

## 2. Self-use evidence

Nhóm tự dùng Trợ lý ảo VinmecCare và một chatbot sức khỏe tham khảo để quan sát điểm gãy trong workflow.

| Observation | Screenshot/link | Path liên quan | Điều học được |
|---|---|---|---|
| Khi user nhập câu rất mơ hồ/không thực tế như "sốt 90 độ", VinmecCare trả lời rằng hệ tri thức chưa có câu trả lời. | ![Evidence 01](assets/z7896607630360_e3a20e3a6a34bfaa1355b1cad50e12aa.jpg) | Failure / Low-confidence | Bot có fallback, nhưng fallback chưa hướng dẫn user sửa câu hỏi, chưa hỏi lại dữ kiện tối thiểu, chưa giúp user recover. |
| Khi user mô tả triệu chứng khá rõ như "đau dạ dày, đầy hơi, khó tiêu 2 tuần nay", VinmecCare chỉ hỏi tuổi/năm sinh. | ![Evidence 02](assets/z7896607636913_7888656377b674b5bd0e49de9888968c.jpg) | Happy / Low-confidence | Bot bắt đầu intake bằng tuổi là hợp lý, nhưng chưa khai thác tiếp các slot quan trọng như mức độ đau, vị trí, triệu chứng đi kèm, red flag. |
| Với triệu chứng "đau chân 3 ngày nay, chân sưng rất nhiều", VinmecCare chuyển sang phiếu yêu cầu hỗ trợ/hotline. | ![Evidence 03](assets/z7896607636913_7888656377b674b5bd0e49de9888968c.jpg) | Failure / Handoff | Có handoff, nhưng chưa giải thích rõ vì sao cần handoff, chưa tóm tắt thông tin cho chuyên viên/bác sĩ. |
| Khi user hỏi "Đau bụng thì phải làm sao" hoặc "Đau bụng âm ỉ nhiều ngày rồi hãy tư vấn cho tôi", VinmecCare tiếp tục yêu cầu tuổi/năm sinh giống nhau. | ![Evidence 04](assets/z7896607628945_18619563927a18a013c6b6eab8daf01c.jpg) | Low-confidence | Bot đang dùng form cứng theo tuổi, chưa thể hiện khả năng hỏi động theo triệu chứng và mức độ thiếu thông tin. |
| Với câu "Tôi đang bị sốt 40 độ", VinmecCare đưa hướng dẫn tự chăm sóc như uống thuốc hạ sốt, bù nước, nghỉ ngơi. | ![Evidence 05](assets/z7896607662162_6ce8c49e91a4f700ab242ef5b4aaba96.jpg) | Failure | Sốt 40 độ là tình huống cần được xử lý thận trọng. Bot nên ưu tiên red flag/handoff hoặc hỏi nhanh dấu hiệu nguy hiểm thay vì đưa lời khuyên chăm sóc chung. |
| Với câu "Tôi đang bị sốt vậy tôi phải làm gì", VinmecCare trả lời khá dài, mang tính thông tin chung. | ![Evidence 06](assets/z7896607666171_69348ea30957527d192aef5de6737f7a.jpg) | Low-confidence | Khi thông tin còn thiếu nhiệt độ, tuổi, thời gian sốt, triệu chứng đi kèm, bot nên hỏi thêm trước khi tư vấn. |
| Với câu "Lúc này tôi đang bị tình trạng như thế nào", VinmecCare chuyển sang phiếu hỗ trợ và hotline. | ![Evidence 07](assets/z7896607657393_7628b992f69f75025e356b3f623f4777.jpg) | Low-confidence / Handoff | Handoff có tồn tại, nhưng thiếu cơ chế summary để nhân viên/bác sĩ biết user đã nói gì trước đó. |
| Với câu "Tôi bị chảy máu tôi phải làm sao", VinmecCare đưa hướng dẫn xử lý tại nhà trước khi làm rõ loại chảy máu/mức độ. | ![Evidence 08](assets/z7896607705865_88d2d3f8b44f90a5817df515dccc6332.jpg) | Failure | "Chảy máu" là nhóm triệu chứng cần hỏi rõ vị trí, lượng máu, nguyên nhân, tình trạng toàn thân. Bot cần red flag check trước khi tư vấn. |

## 3. User / review / social evidence

Nguồn ngoài nhóm hiện dùng ở mức analog/public evidence để tránh chỉ dựa vào self-use. Nếu nhóm kịp phỏng vấn nhanh trước M1, phần này có thể thay bằng quote thật từ 1-2 người từng đặt lịch khám online.

| Quote / review / observation | Nguồn | User là ai? | Pain/failure mode |
|---|---|---|---|
| Luồng đặt khám online thường yêu cầu user chọn chuyên khoa hoặc loại dịch vụ trước khi hoàn tất đặt lịch. | Analog từ các app/website đặt khám và luồng VinmecCare quan sát được trong self-use | Bệnh nhân lần đầu đặt khám | Nếu user chỉ biết triệu chứng chung, bước chọn chuyên khoa dễ trở thành điểm nghẽn. |
| Form tiền khám/pre-consultation form thường thu thông tin có cấu trúc như tuổi, triệu chứng chính, thời gian, mức độ và triệu chứng đi kèm. | Analog từ form tiền khám / pre-consultation form | Bệnh nhân/người nhà bệnh nhân, bác sĩ/nhân viên tiếp nhận | Chat tự nhiên cần được chuyển thành slot có cấu trúc để giảm việc hỏi lại từ đầu. |
| Chatbot sức khỏe tham khảo có disclaimer, red flag guidance và gợi ý khi nào nên gặp bác sĩ. | Analog screenshot trong mục 4 | Bệnh nhân hỏi thông tin sức khỏe online | Prototype cần disclaimer rõ, không chẩn đoán, và phải ưu tiên handoff khi có dấu hiệu nguy hiểm. |

## 4. Competitor / analog evidence

| App / mô hình tham khảo | Họ xử lý task này thế nào? | Pattern học được | Có áp dụng trong 1 ngày không? |
|---|---|---|---|
| Chatbot sức khỏe tham khảo có reasoning/citation | Khi user mô tả "đau dạ dày, đầy hơi, khó tiêu 2 tuần", chatbot phân tích nguyên nhân phổ biến, nêu khi nào cần đi khám và có disclaimer không chẩn đoán. | Trả lời y tế cần có disclaimer, cảnh báo red flag và khuyến nghị đi khám khi kéo dài. | Có, nhưng chỉ áp dụng pattern an toàn; không build chatbot chẩn đoán. |
| Chatbot sức khỏe tham khảo | Khi user hỏi muốn gặp bác sĩ, chatbot gợi ý chuyên khoa Nội Tiêu hóa và bệnh viện phù hợp. | AI có thể hỗ trợ routing sang chuyên khoa, nhưng phải tránh gợi ý quá rộng hoặc quá tự tin. | Có. Prototype chỉ gợi ý 1-2 chuyên khoa mức tham khảo. |
| Form tiền khám / pre-consultation form | Thu thập thông tin theo các trường cố định trước buổi khám. | Chat tự nhiên nên được chuyển thành slot có cấu trúc: tuổi, thời gian, mức độ, triệu chứng đi kèm, red flag. | Có. Build được bằng slot-filling đơn giản. |
| Chatbot CSKH dùng quick replies | Dẫn user trả lời nhanh bằng nút bấm thay vì gõ dài. | Quick replies giảm công gõ và giúp dữ liệu vào sạch hơn. | Có. Prototype dùng quick replies cho 2-3 câu hỏi intake. |

Ảnh minh chứng analog:

- ![Analog 01](assets/z7896607638142_4dac4b6d70b12d58c21726396f7ae716.jpg)
- ![Analog 02](assets/z7896607644500_db0c41f3c7c9b231a876363273f4d2a7.jpg)
- ![Analog 03](assets/z7896607647447_b980330209b43195f69f359b9dda65a7.jpg)
- ![Analog 04](assets/z7896607657028_2fbbcaf728ca6a1415cb33bf8938efff.jpg)

## 5. Evidence -> Insight

```text
Evidence nổi bật nhất:
VinmecCare có thể hỏi tuổi/năm sinh, fallback hoặc chuyển hotline,
nhưng chưa thể hiện rõ một flow intake thông minh:
hỏi đúng thông tin còn thiếu theo triệu chứng,
phát hiện red flag trước khi tư vấn,
cho user sửa ngữ cảnh,
và tạo bản tóm tắt có cấu trúc cho bác sĩ.

Insight:
User không chỉ cần một chatbot trả lời câu hỏi y tế.
Thật ra họ cần một trợ lý tiếp nhận an toàn,
biết biến mô tả triệu chứng mơ hồ thành thông tin có cấu trúc,
biết dừng khi có dấu hiệu nguy hiểm,
và biết chuyển thông tin sạch sang người thật.

Opportunity:
AI có thể giúp bằng cách augment bước tiếp nhận trước khám:
kiểm tra slot còn thiếu, hỏi thêm bằng câu hỏi ngắn kèm quick replies,
phát hiện red flag, gợi ý chuyên khoa ở mức tham khảo,
và tạo draft summary cho bác sĩ.
```

## 6. Evidence đổi SPEC như thế nào?

- [x] Đổi user chính.
- [x] Đổi pain statement.
- [x] Đổi build slice.
- [x] Đổi Auto/Aug decision.
- [x] Đổi 4 paths.
- [x] Đổi failure mode.
- [x] Đổi owner/test plan.

Ghi rõ thay đổi quan trọng:

```text
Trước evidence, nhóm định làm chatbot y tế hỏi đáp chung cho Vinmec.

Sau evidence, nhóm đổi thành AI Smart Intake Assistant cho bước tiếp nhận trước khám từ xa.

Lý do:
Chatbot y tế tổng quát quá rộng, rủi ro cao và khó demo trong 1 ngày.
Evidence cho thấy pain rõ hơn nằm ở bước user mô tả triệu chứng thiếu dữ kiện,
bot hỏi chưa đủ linh hoạt, có case red flag cần xử lý an toàn,
và khi handoff vẫn thiếu bản tóm tắt cho người thật.
```
