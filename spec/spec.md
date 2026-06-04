# SPEC sản phẩm - AI Smart Intake Assistant cho Vinmec

## 1. Bằng chứng

**Track:** Healthcare  
**App tham chiếu:** Vinmec / MyVinmec / VinmecCare  
**Tên prototype:** AI Smart Intake Assistant

AI Smart Intake Assistant là một hệ thống AI tiếp nhận sơ bộ trước khám, hoạt động trực tiếp trong luồng chat. Sản phẩm dành cho bệnh nhân lần đầu hoặc người nhà chưa biết mô tả triệu chứng thế nào cho đủ và chưa biết nên chọn chuyên khoa nào khi đặt lịch khám tại Vinmec.

Mục tiêu không phải là tạo chatbot y tế tổng quát. Mục tiêu là tạo một **intake engine** giúp người dùng mô tả triệu chứng dễ hơn, AI hỏi thêm thông tin cần thiết, phát hiện dấu hiệu nguy hiểm, gợi ý chuyên khoa phù hợp, tạo lịch khám ảo nháp trong chat và lưu tóm tắt ca bệnh cho bác sĩ/CSKH.

Prototype **không chẩn đoán bệnh, không kê đơn thuốc, không đưa liều thuốc và không thay thế bác sĩ**. Vai trò của AI là hỗ trợ định hướng tiếp nhận trước khám một cách an toàn.

### 1.1. Quan sát trực tiếp từ nhóm

Qua phần test VinmecCare/MyVinmec ban đầu, nhóm ghi nhận một số điểm yếu:

- Bot có lúc lặp lại yêu cầu tuổi hoặc năm sinh thay vì hỏi tiếp về triệu chứng theo ngữ cảnh.
- Khi người dùng mô tả triệu chứng tự nhiên hoặc mơ hồ, bot có lúc trả lời rằng chưa có câu trả lời phù hợp.
- Với một số tình huống có thể nguy hiểm như sốt cao hoặc chảy máu, bot vẫn có xu hướng trả lời theo hướng tư vấn chung trước khi kiểm tra red flag thật rõ.
- Flow hiện tại có thể đưa người dùng về phiếu hỗ trợ hoặc hotline, nhưng chưa tạo tóm tắt ca bệnh để bác sĩ/CSKH nắm được ngữ cảnh.
- MyVinmec đã có các năng lực liên quan như đặt lịch, quản lý lịch khám cho gia đình và CSKH trực tuyến; vì vậy cơ hội tốt nhất không phải là tạo chatbot y tế mở, mà là cải tiến khâu intake trước khi đặt lịch.

### 1.2. Evidence self-use đã có trong repo

- Ảnh chụp màn hình test VinmecCare/MyVinmec trong `02-group-spec/assets/`.
- Evidence Pack nhóm: `02-group-spec/evidence-pack.md`.
- Thin SPEC Day 05: `02-group-spec/thin-spec.md`.
- Synthesis Decision: `02-group-spec/synthesis-decision.md`.

Các quan sát cụ thể đã được ghi trong Evidence Pack:

| Evidence | Nguồn | Điều học được |
|---|---|---|
| User nhập câu mơ hồ/không thực tế như "sốt 90 độ", bot báo hệ tri thức chưa có câu trả lời. | `02-group-spec/evidence-pack.md`, Evidence 01 | Khi không hiểu, bot cần hỏi lại hoặc hướng dẫn user sửa thông tin thay vì chỉ fallback. |
| User nhập "đau dạ dày, đầy hơi, khó tiêu 2 tuần", bot chỉ hỏi tuổi/năm sinh. | `02-group-spec/evidence-pack.md`, Evidence 02 | Bot cần khai thác thêm mức độ, vị trí, triệu chứng đi kèm và red flag, không chỉ hỏi tuổi. |
| User nhập "sốt 40 độ" hoặc "chảy máu", bot vẫn có xu hướng đưa tư vấn chung. | `02-group-spec/evidence-pack.md`, Evidence 05 và 08 | Red flag phải được kiểm tra trước khi đưa hướng dẫn chăm sóc thông thường. |
| Handoff/hotline có xuất hiện nhưng thiếu bản tóm tắt thông tin user đã nhập. | `02-group-spec/evidence-pack.md`, Evidence 03 và 07 | Khi chuyển sang người thật, hệ thống cần tạo summary có cấu trúc. |

### 1.3. Evidence ngoài nhóm / analog

Nguồn ngoài nhóm hiện ở mức analog/public evidence, chưa phải phỏng vấn người dùng thật. Vì vậy các kết luận bên dưới được dùng như bằng chứng hỗ trợ, không trình bày như kết luận định lượng:

| Evidence ngoài nhóm | Nguồn | Điều học được |
|---|---|---|
| Các luồng đặt khám online thường yêu cầu user chọn chuyên khoa hoặc loại dịch vụ trước khi hoàn tất đặt lịch. | Analog từ app/website đặt khám và luồng VinmecCare đã quan sát | Người dùng chỉ biết triệu chứng có thể bị kẹt ở bước chọn chuyên khoa. |
| Form tiền khám thường thu thông tin có cấu trúc như tuổi, triệu chứng chính, thời gian, mức độ và triệu chứng đi kèm. | Analog từ pre-consultation form | Chat tự nhiên cần được chuyển thành slot có cấu trúc để giảm việc hỏi lại. |
| Chatbot sức khỏe tham khảo có disclaimer, red flag guidance và gợi ý khi nào nên gặp bác sĩ. | Analog screenshot trong `02-group-spec/assets/` | Prototype phải có disclaimer rõ, không chẩn đoán và ưu tiên handoff khi có dấu hiệu nguy hiểm. |

Nếu có thêm thời gian, nhóm nên kiểm chứng bằng phỏng vấn nhanh 1-2 người từng đặt lịch khám online để thay thế hoặc bổ sung phần analog evidence này.

### 1.4. Insight từ evidence

User không chỉ cần một chatbot trả lời câu hỏi y tế. Họ cần một trợ lý tiếp nhận an toàn, biết biến mô tả triệu chứng mơ hồ thành thông tin có cấu trúc, biết dừng khi có dấu hiệu nguy hiểm, biết gợi ý bước tiếp theo và biết chuyển thông tin sạch sang người thật.

Nhận định cần kiểm chứng thêm sau khi demo:

- Người dùng thật có gặp khó khi chọn chuyên khoa không.
- Người dùng có tin tưởng hơn nếu AI giải thích lý do gợi ý chuyên khoa không.
- Bác sĩ/CSKH có giảm thời gian hỏi lại thông tin ban đầu khi có tóm tắt intake không.

## 2. Lát cắt để build

Lát cắt demo nhỏ nhất:

**Một người dùng nhập triệu chứng tự nhiên cho bản thân hoặc người thân; AI hỏi bổ sung tối đa vài thông tin còn thiếu, kiểm tra red flag, nếu không nguy hiểm thì gợi ý chuyên khoa phù hợp, hỏi đặt lịch khám ảo, tạo booking draft và lưu tóm tắt ca bệnh cho bác sĩ/CSKH.**

Trong lát cắt này:

- **User:** bệnh nhân lần đầu hoặc người nhà đang muốn đặt lịch khám từ xa.
- **Công việc:** mô tả triệu chứng, hiểu mức độ cần xử lý, chọn chuyên khoa phù hợp và tạo lịch khám nháp.
- **Quyết định AI đưa ra:** còn thiếu thông tin nào, có red flag không, nên tiếp tục hỏi hay handoff khẩn cấp, chuyên khoa nào phù hợp.
- **Kết quả trả về:** câu hỏi tiếp theo, cảnh báo an toàn nếu cần, gợi ý chuyên khoa, booking draft và tóm tắt intake.

### 2.1. Scope đã build trong prototype

Đã build trong Day 06:

- Frontend website demo Vinmec với AI chat widget nổi.
- Chat intake song ngữ Việt/Anh.
- Backend FastAPI cho session, message, case, booking và dashboard.
- Slot extraction cho người bệnh, tuổi, triệu chứng, thời gian, mức độ, cơ sở và thời gian khám.
- Search context qua Tavily/Firecrawl, ưu tiên Vinmec và trusted medical domains, có fallback khi API lỗi.
- Triage sơ bộ kết hợp AI gateway và rule-based fallback.
- Hardcoded red flag override chạy trước khi tiếp tục flow tư vấn thường.
- Safe guidance và specialty suggestion.
- Booking draft trong chat.
- Patient info, chat history, doctor summary và audit logs.
- SQLite persistence cho case snapshot và log.
- Doctor/CSKH dashboard endpoints, dashboard stats và doctor login demo.

Không build trong Day 06:

- Chẩn đoán bệnh.
- Kê đơn thuốc.
- Liều thuốc.
- Đặt lịch thật trên hệ thống Vinmec.
- Thanh toán.
- Gọi bác sĩ realtime.
- Đồng bộ EMR thật.
- Dashboard bác sĩ đầy đủ như sản phẩm production.

## 3. AI Product Canvas

| Ô | Câu trả lời của nhóm |
|---|---|
| **Value - Giá trị** | Sản phẩm dành cho bệnh nhân lần đầu hoặc người nhà chưa biết chọn chuyên khoa. AI giúp biến mô tả triệu chứng tự nhiên thành thông tin có cấu trúc, định hướng chuyên khoa và giảm việc bác sĩ/CSKH phải hỏi lại từ đầu. |
| **Trust - Niềm tin** | AI không chẩn đoán và không kê thuốc. Mọi gợi ý đều ở mức định hướng, có lý do ngắn. Nếu có red flag, hardcoded safety rules được ưu tiên cao hơn nhận định AI và flow chuyển sang cảnh báo khẩn cấp/handoff. User có thể sửa thông tin trước khi tạo booking draft. |
| **Feasibility - Tính khả thi** | Prototype đã build được bằng frontend HTML/CSS/JS, backend FastAPI, SQLite store, OpenAI-compatible gateway, Tavily/Firecrawl context search, rule-based red flag checker, booking draft và dashboard endpoints. Chi phí được kiểm soát bằng cách chỉ gọi AI ở bước cần suy luận, lưu slot đã extract trong session, giới hạn context search top-k nhỏ, dùng prompt ngắn/output JSON và để hardcoded red flag rules xử lý trước/sau AI. Độ trễ demo được giảm bằng fallback rule-based khi AI/search external lỗi. Ngưỡng dừng: AI không được chẩn đoán/kê thuốc; nếu red flag xuất hiện thì dừng flow thường và handoff. Phần đặt lịch thật, hồ sơ bệnh án thật, thanh toán và gọi bác sĩ realtime không nằm trong scope. |
| **Tín hiệu học** | Khi user sửa tuổi, người bệnh, triệu chứng, mức độ hoặc chọn chuyên khoa khác, hệ thống lưu log để cải thiện prompt/rule và bộ test. Trong prototype, dữ liệu này dùng để đánh giá và chỉnh prompt, không dùng để train tự động. |

## 4. Tăng năng lực hay tự động hóa

Prototype chọn hướng **augment - tăng năng lực** là chính.

AI không tự động chẩn đoán, không tự động quyết định điều trị và không tự động đặt lịch thật thay người dùng. AI chỉ:

- Hỏi làm rõ thông tin còn thiếu.
- Trích xuất thông tin vào intake case.
- Tìm context y tế liên quan để hỗ trợ định hướng an toàn.
- Phát hiện red flag bằng kết hợp AI và hardcoded rules.
- Gợi ý chuyên khoa/cơ sở ở mức tham khảo.
- Tạo tóm tắt ca bệnh và booking draft để người dùng xác nhận.

Con người giữ quyền quyết định ở các bước:

- Người dùng xác nhận hoặc sửa thông tin người bệnh.
- Người dùng quyết định có tạo lịch khám ảo nháp hay không.
- Bác sĩ/CSKH đọc lại tóm tắt và xử lý ca bệnh.
- Bác sĩ là người chẩn đoán và tư vấn y tế cuối cùng.

Lý do chọn augment: y tế là lĩnh vực rủi ro cao. Nếu AI gợi ý sai hoặc bỏ sót red flag, hậu quả có thể nghiêm trọng. Vì vậy AI chỉ nên hỗ trợ tiếp nhận và định hướng, không thay quyền quyết định y khoa.

## 5. Bốn đường đi của trải nghiệm

### 5.1. Đường thuận

Input demo:

```text
Tôi đau dạ dày, đầy hơi khó tiêu 2 tuần nay.
```

AI hỏi thêm tuổi, người bệnh là ai, mức độ đau và dấu hiệu nguy hiểm. Khi đủ thông tin và không có red flag, AI gợi ý Nội Tiêu hóa, đưa hướng chăm sóc ban đầu an toàn, hỏi đặt lịch khám ảo, tạo booking draft và lưu tóm tắt cho dashboard.

Kết quả mong đợi:

- User hiểu vì sao nên khám Nội Tiêu hóa.
- User có thể tạo lịch khám ảo nháp.
- Bác sĩ/CSKH có tóm tắt ca bệnh.

### 5.2. Khi AI không chắc

Input demo:

```text
Tôi mệt, chóng mặt, khó ngủ.
```

AI không đoán bệnh và không gợi ý quá chắc chắn. AI hỏi lại để làm rõ thời gian kéo dài, tuổi, triệu chứng đi kèm, có đau ngực/khó thở/ngất không. Nếu vẫn chưa đủ dữ liệu, AI chuyển sang hướng tư vấn tổng quát hoặc CSKH hỗ trợ thêm, kèm tóm tắt ngắn.

Kết quả mong đợi:

- AI không trả lời như chẩn đoán.
- User được hướng dẫn cung cấp thêm thông tin.
- Nếu chưa đủ dữ kiện, hệ thống có fallback an toàn.

### 5.3. Khi AI sai hoặc có red flag

Input demo:

```text
Tôi đau ngực và khó thở.
```

AI phát hiện red flag, dừng flow đặt lịch thường, hiển thị cảnh báo khẩn cấp, tạo high-priority case và đưa ca lên dashboard bác sĩ/CSKH.

Kết quả mong đợi:

- AI không gợi ý chăm sóc tại nhà.
- AI không hỏi đặt lịch khám thường.
- Dashboard hiện `red_flag_status = confirmed` và `priority = high`.

### 5.4. Khi người dùng sửa

Input demo:

```text
Người khám là mẹ tôi chứ không phải tôi.
```

AI cập nhật người bệnh, quan hệ với người chat, tuổi/năm sinh nếu cần, kiểm tra red flag lại từ đầu và tạo lại summary.

Kết quả mong đợi:

- `patient_relation = mother`.
- Summary ghi đúng người bệnh là mẹ user.
- Các câu hỏi tiếp theo đổi theo ngữ cảnh người thân.

## 6. Những kiểu lỗi đáng lo nhất

| Failure mode | Khi nào xảy ra | Ảnh hưởng | Cách xử lý trong prototype |
|---|---|---|---|
| Bỏ sót red flag | User nhập triệu chứng nguy hiểm nhưng AI vẫn gợi ý đặt lịch thường | Bệnh nhân chậm tiếp cận cấp cứu | Hardcoded red flag rules chạy ở mọi lượt chat và override nhận định AI |
| Gợi ý sai chuyên khoa | Thông tin mơ hồ, thiếu tuổi/thời gian/vị trí hoặc triệu chứng giao nhau | User đặt sai chuyên khoa, mất thời gian | Hỏi lại thông tin tối thiểu, hiện 1-2 gợi ý kèm lý do, cho user sửa |
| AI tạo cảm giác chẩn đoán | Câu trả lời quá chắc chắn hoặc dùng ngôn ngữ như kết luận bệnh | User tin nhầm, tự điều trị | Copy phải nói rõ "gợi ý định hướng", không chẩn đoán, không kê thuốc |
| Search context sai hoặc quá rộng | Nguồn search không phù hợp hoặc bị hiểu sai | Gợi ý thiếu an toàn | Chỉ dùng nguồn ưu tiên, chuẩn hóa context, red flag hardcode luôn kiểm tra lại |

Red flag tối thiểu cần chặn:

- đau ngực
- khó thở
- sốt 40 độ
- chảy máu nhiều
- đau bụng dữ dội
- nôn ra máu
- đi ngoài phân đen
- ngất/lơ mơ/co giật
- sưng môi/mặt/lưỡi sau ăn hoặc uống thuốc

Rule quan trọng: **hardcoded red flag rules luôn có quyền ưu tiên cao hơn AI nhận định**.

## 7. Kế hoạch kiểm thử và bằng chứng demo

MVP được coi là chạy được nếu pass các flow kiểm thử chính:

| Flow | Kịch bản | Kết quả mong đợi |
|---|---|---|
| Ca thường + đặt lịch | User: "Tôi đau dạ dày, đầy hơi khó tiêu 2 tuần nay." AI hỏi tuổi/mức độ. User: "Mẹ tôi 58 tuổi, đau vừa." User chọn đặt lịch Times City sáng mai. | AI gợi ý Nội Tiêu hóa, tạo booking draft, lưu dashboard. |
| AI không chắc | User: "Tôi mệt, chóng mặt, khó ngủ." | AI không chẩn đoán, hỏi thêm thời gian kéo dài, tuổi, triệu chứng đi kèm và red flag; nếu thiếu dữ kiện thì fallback an toàn hoặc chuyển CSKH. |
| Ca nguy hiểm | User: "Tôi đau ngực và khó thở." | AI cảnh báo khẩn cấp, tạo high-priority case, dashboard hiện red_flag confirmed. |
| User hỏi thay người thân | User: "Mẹ tôi đau bụng mấy ngày nay." | AI hỏi tuổi mẹ, mức độ, dấu hiệu đi kèm; summary ghi đúng người bệnh là mẹ user. |
| User sửa thông tin | User ban đầu nói "Tôi bị sốt", sau đó sửa "À tôi hỏi cho bé nhà tôi 5 tuổi." | AI cập nhật đối tượng người bệnh, kiểm tra red flag lại từ đầu và tạo summary mới theo ngữ cảnh trẻ em. |
| Dashboard bác sĩ | Doctor mở dashboard. | Doctor thấy danh sách ca, thông tin bệnh nhân, lịch đặt khám, tóm tắt ca, lịch sử chat, red flag/priority. |

Kịch bản demo 5 phút:

| Phần | Nội dung trình bày | Người phụ trách chính |
|---|---|---|
| Problem | Nỗi đau từ evidence: user mô tả triệu chứng thiếu dữ kiện, bot hỏi chưa linh hoạt, red flag chưa được xử lý nhất quán, handoff thiếu summary. | Report + test case demo |
| Solution | AI Smart Intake Assistant: hỏi thêm slot còn thiếu, kiểm tra red flag, gợi ý chuyên khoa, tạo booking draft và doctor summary. | Report + test case demo / UI |
| Augment hay automate | Chọn augment vì y tế rủi ro cao; AI hỗ trợ intake và routing, user/bác sĩ giữ quyền quyết định. | Report + test case demo |
| Live demo | Chạy happy path và một error/red-flag path; nếu live lỗi thì dùng screenshot/video backup. | UI / Backend / AI tools |
| Lessons | Nêu trade-off: không chẩn đoán, dùng rule để chặn red flag, giới hạn scope để demo được trong Day 06. | Repo / merge code, xây prompt |

Bằng chứng cần giữ lại:

- Screenshot trước/sau của flow chat.
- Prompt và response log của AI.
- API request/response mẫu.
- Danh sách test case đã chạy.
- Lỗi AI gặp phải và cách nhóm sửa prompt/rule.
- Video backup nếu demo live lỗi.

Bằng chứng code/test hiện có:

- Frontend: `codebase/frontend/index.html`, `codebase/frontend/styles.css`, `codebase/frontend/app.js`.
- Backend: `codebase/backend/src/vinm_backend/`.
- API chính: `/chat/session`, `/chat/message`, `/doctor/cases`, `/booking/draft`, `/doctor/dashboard/stats`.
- Test backend: `codebase/backend/tests/`, gồm test Day 6 API, smart intake, orchestrator, retrieval adapters, OpenAI gateway và smoke test.
- Lệnh test: `cd codebase/backend` rồi chạy `..\..\.venv\Scripts\python.exe -m pytest`.

Chỉ số có thể đánh giá:

- Số lượt hỏi để đủ thông tin.
- Tỷ lệ phát hiện red flag trong bộ test.
- Tỷ lệ gợi ý đúng chuyên khoa theo kỳ vọng của nhóm.
- Tỷ lệ user đi tiếp sang CTA đặt lịch trong demo.
- Mức độ giảm thông tin bác sĩ/CSKH phải hỏi lại.

## 8. Phân công

| Vai trò | Việc chính | Owner |
|---|---|---|
| Report + test case demo | Viết SPEC/report, cập nhật theo codebase, chuẩn bị bộ test case demo và expected result cho 4 flow: happy path, low-confidence, red flag và correction | Lã Duy Anh |
| UI | Thiết kế và build giao diện chat intake, quick replies, màn hình kết quả/gợi ý chuyên khoa, booking draft và dashboard hiển thị | Dương Quang Minh |
| Backend | Xây API, lưu session/case/message/booking, xử lý orchestration và kết nối dashboard | Trần Quốc Khánh |
| AI tools | Xây tools, extractor, search context, triage logic và red-flag rule phối hợp với backend | Nguyễn Anh Kiệt |
| Repo / merge code, xây prompt | Quản lý repo, review/merge code, xử lý conflict, kiểm tra cấu trúc nộp bài và hướng dẫn chạy | Nguyễn Văn Huy |

## Phụ lục A. Thiết kế prototype backend-first

Phần này bổ sung chi tiết kỹ thuật cho Day 06. Nội dung chính của SPEC vẫn bám theo 8 mục phía trên.

### A.1. Luồng sản phẩm

```text
Người dùng mô tả triệu chứng
-> AI hỏi khai thác thông tin sơ lược
-> AI tìm context y tế liên quan
-> AI nhận định sơ bộ mức độ nguy hiểm
-> Hardcoded safety rules kiểm tra lại red flag
-> Nếu nguy hiểm:
      cảnh báo bệnh nhân
      tạo ca ưu tiên cho bác sĩ/CSKH
      lưu lịch sử chat và thông tin ca bệnh
      hiển thị trên dashboard bác sĩ/CSKH
-> Nếu không nguy hiểm:
      gợi ý chăm sóc ban đầu an toàn
      gợi ý chuyên khoa phù hợp
      hỏi người dùng có muốn đặt lịch khám ảo không
-> Nếu người dùng muốn đặt lịch:
      hỏi cơ sở khám mong muốn
      hỏi thời gian mong muốn
      xác nhận thông tin bệnh nhân
      tạo booking draft trong chat
      lưu booking vào ca bệnh
-> Bác sĩ/CSKH xem dashboard:
      thông tin bệnh nhân
      triệu chứng
      lịch sử chat
      tóm tắt ca bệnh
      mức độ ưu tiên
      chuyên khoa gợi ý
      thông tin đặt lịch
```

### A.2. Công cụ backend tối thiểu

**Intake Extractor Tool:** trích xuất `patient_relation`, `age_or_birth_year`, `main_symptom`, `duration`, `severity`, `location`, `associated_symptoms`, `booking_intent`, `preferred_time`, `preferred_hospital`.

**Medical Context Search Tool:** tìm thông tin y tế liên quan từ nguồn ưu tiên như Vinmec, CDC, NHS, Mayo Clinic, WHO, MedlinePlus. Search chỉ hỗ trợ định hướng an toàn, không dùng để chẩn đoán.

**Triage & Safety Rule Tool:** kết hợp AI context và hardcoded rules để trả về `triage_level`, `red_flag_status`, `priority`, `action`.

**Chat Response & Case Summary Tool:** sinh phản hồi tiếp theo, hỏi tiếp thông tin còn thiếu, cảnh báo nguy hiểm, gợi ý chuyên khoa, xác nhận booking draft và tạo doctor summary.

### A.3. API backend tối thiểu

```text
POST /chat/session
POST /chat/message
GET /chat/session/{session_id}/messages

GET /cases/{case_id}
PATCH /cases/{case_id}

POST /booking/draft
PATCH /booking/{booking_id}
GET /booking/{booking_id}

GET /doctor/cases
GET /doctor/cases/{case_id}
POST /doctor/cases/{case_id}/notes
PATCH /doctor/cases/{case_id}/status

GET /debug/cases/{case_id}/logs
```

### A.4. Dữ liệu cần lưu

Patient information:

```json
{
  "patient_id": "pat_001",
  "full_name": "unknown",
  "age_or_birth_year": "58",
  "gender": "unknown",
  "relationship_to_customer": "mother",
  "phone": "optional"
}
```

Intake case:

```json
{
  "case_id": "case_001",
  "main_symptom": "đau dạ dày, đầy hơi, khó tiêu",
  "duration": "2 tuần",
  "severity": "vừa",
  "red_flag_status": "none",
  "priority": "medium",
  "suggested_specialty": "Nội Tiêu hóa",
  "case_status": "booking_requested"
}
```

Booking draft:

```json
{
  "booking_id": "book_001",
  "case_id": "case_001",
  "patient_id": "pat_001",
  "specialty": "Nội Tiêu hóa",
  "hospital": "Vinmec Times City",
  "preferred_time": "Sáng mai",
  "booking_status": "draft",
  "doctor_summary_attached": true
}
```

Doctor summary:

```text
Người bệnh: Mẹ của người dùng, 58 tuổi.
Triệu chứng chính: Đau dạ dày, đầy hơi, khó tiêu.
Thời gian: Khoảng 2 tuần.
Mức độ: Vừa.
Red flag: Chưa phát hiện từ thông tin hiện có.
Chuyên khoa gợi ý: Nội Tiêu hóa.
Lý do: Triệu chứng tiêu hóa kéo dài, nên khám chuyên khoa để đánh giá nguyên nhân.
Trạng thái: Người dùng đã yêu cầu đặt lịch khám ảo.
```

## Phụ lục B. Trạng thái codebase thực tế

### B.1. Cấu trúc source code

```text
codebase/
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── README.md
└── backend/
    ├── pyproject.toml
    ├── streamlit_app.py
    ├── src/vinm_backend/
    └── tests/
```

### B.2. Cách chạy local

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

Truy cập `http://localhost:4173`. Backend chạy tại `http://127.0.0.1:8000`.

### B.3. Model/API và search tool

- AI gateway: OpenAI-compatible Chat Completions API qua `OpenAIGatewayClient`.
- Biến môi trường: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`.
- Search context: Tavily + Firecrawl qua `TavilyClient` và `FirecrawlClient`.
- Handoff optional: Telegram adapter.
- Fallback: nếu AI/search external lỗi hoặc thiếu key, backend dùng rule-based extractor, red flag, specialty selection và doctor summary fallback.

### B.4. Endpoint đã implement

```text
GET /health
POST /v1/assist
POST /chat/session
POST /chat/message
GET /chat/session/{session_id}/messages
GET /cases/{case_id}
PATCH /cases/{case_id}
POST /booking/draft
GET /booking/{booking_id}
PATCH /booking/{booking_id}
GET /doctor/cases
POST /doctor/login
GET /doctor/dashboard/stats
GET /doctor/cases/{case_id}
POST /doctor/cases/{case_id}/notes
PATCH /doctor/cases/{case_id}/status
GET /debug/cases/{case_id}/logs
GET /doctor/cases/{case_id}/logs
GET /vinmec/facilities
```

### B.5. Test thực tế cần lưu khi nộp

- Kết quả chạy `pytest` trong `codebase/backend`.
- Screenshot happy path trên frontend.
- Screenshot red flag path.
- Screenshot dashboard/case summary.
- API response mẫu từ `/chat/message`.
