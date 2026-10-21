---
name: tra-loi-binh-luan
description: Chứng thực sự thật và soạn thảo câu trả lời bình luận cộng đồng chuẩn chỉ, đúng pháp luật, bảo vệ uy tín doanh nghiệp & chính quyền địa phương cho kênh Quy Nhơn 24h Qua (@quynhon24hqua). Dùng khi người dùng nói "trả lời bình luận", "chứng thực bình luận", "check cmt", "soạn trả lời cmt", "bình luận này trả lời sao", hoặc gửi nội dung bình luận của khán giả.
---

# Skill Trả lời & Chứng thực Bình luận Cộng đồng

> **Mục tiêu**: Giúp chủ kênh **[@quynhon24hqua](https://www.tiktok.com/@quynhon24hqua)** phản hồi các bình luận của khán giả một cách **chuẩn mực · 100% đúng sự thật báo chí · đúng pháp luật (Luật An ninh mạng, Nghị định 147/2024/NĐ-CP) · tuân thủ tuyệt đối Tiêu chuẩn Cộng đồng TikTok · bảo vệ uy tín tổ chức/doanh nghiệp · dập tắt tin đồn sai lệch**.

---

## 1. Khi nào dùng skill này
- Khi người dùng gửi một hoặc nhiều bình luận của khán giả trên TikTok/Facebook/YouTube và hỏi:
  - *"Bình luận này trả lời sao?"*
  - *"Check cmt này xem đúng không"*
  - *"Bình luận bị gắn cờ / vi phạm"*
  - *"Soạn câu trả lời chuẩn chỉ đúng luật cho cmt này"*
- Hoặc khi chủ kênh yêu cầu rà soát bình luận của một video vừa đăng xem có bình luận nào cần đính chính, ẩn hoặc lọc từ khóa hay không.

---

## 2. Quy trình 4 bước xử lý bình luận

### Bước 1: Phân loại bình luận & Đánh giá rủi ro
Phân loại bình luận vào 1 trong 4 nhóm:
1. **Nhóm 1 – Hiểu lầm / Suy đoán sai bản chất sự việc (Rủi ro cao bị gắn cờ)**:
   - Ví dụ: *"Chắc KS Bình Dương làm ăn ko hiệu quả nên bị dẹp"*, *"Dẹp để bán đất vàng cho sân sau"*.
   - **Rủi ro**: Vi phạm chính sách Thông tin sai lệch (Misinformation) & Bôi nhọ uy tín thương mại doanh nghiệp (Defamation). Rất dễ bị người xem khác hoặc doanh nghiệp bấm Report làm video bị gắn cờ.
   - **Hành động**: BẮT BUỘC trả lời đính chính ngay bằng sự thật quy hoạch công ích / văn bản nhà nước.
2. **Nhóm 2 – Thắc mắc thông tin / Hỏi vị trí, tiến độ, chi tiết**:
   - Ví dụ: *"Bệnh viện quốc tế xây khúc nào Tây Sơn ad?"*, *"Bao giờ xong đường Phù Cát?"*.
   - **Hành động**: Trả lời rõ ràng, chính xác kèm địa chỉ/mốc thời gian từ bài báo gốc.
3. **Nhóm 3 – Công kích, chửi bới, vu khống, xúc phạm cán bộ / cá nhân**:
   - Ví dụ: Chửi bới thô tục, vu khống chạy chức, chèn ép tiêu cực khi nói về giáo viên/cán bộ.
   - **Hành động**: **KHÔNG tranh cãi tay đôi**. Khuyên chủ kênh **Ẩn bình luận (Hide)**, **Báo cáo (Report)** với TikTok nếu vi phạm nghiêm trọng, và **thêm từ khóa vào danh sách Lọc từ khóa của kênh**.
4. **Nhóm 4 – Tích cực, khen ngợi, thả icon, góp ý xây dựng**:
   - **Hành động**: Thả tim, cảm ơn thân thiện, gia tăng gắn kết cộng đồng.

---

### Bước 2: Đối chiếu chứng cứ gốc & Sự thật pháp lý
AI chạy công cụ hoặc trực tiếp tra cứu:
```bash
python skills/tra-loi-binh-luan/scripts/kiem_tra_binh_luan.py "<nội dung bình luận>"
```
Hoặc tra cứu trong kho kịch bản `skills/ban-tin/inbox/*.json`:
- Xác định bài báo gốc (`source`, `source_name`).
- Trích dẫn câu văn gốc chứng minh sự thật.
- Kiểm tra các quy định pháp luật liên quan (Luật An ninh mạng 2018 Điều 8, 16; Tiêu chuẩn Cộng đồng TikTok về Quấy rối và Bắt nạt, Thông tin sai lệch).

---

### Bước 3: Soạn thảo câu trả lời chuẩn mực
Luôn cung cấp cho người dùng **3 phương án phản hồi**:
1. **Phương án 1 (Ngắn gọn - Tối ưu cho TikTok Comment ≤ 150 ký tự)**: Nhã nhặn, đi thẳng vào bản chất sự thật, dễ đọc trên điện thoại.
2. **Phương án 2 (Đầy đủ căn cứ & Pháp lý)**: Trích dẫn rõ chủ trương quy hoạch của tỉnh, tên cơ quan chức năng hoặc văn bản pháp lý.
3. **Phương án 3 (Thân thiện, gần gũi địa phương)**: Dùng cách xưng hô thân mật (*"bạn ơi", "bà con mình", "dạ không phải đâu nè"*), xoa dịu tranh cãi, giữ chân người xem.

---

### Bước 4: Khuyến nghị Cài đặt & Quản trị bình luận (Settings)
- Nếu bình luận chứa các từ suy đoán bôi nhọ nguy hiểm: Đề xuất chủ kênh thêm ngay từ khóa đó vào **Cài đặt Lọc từ khóa (Filter Keywords)** trong app TikTok.
- Nếu bình luận bị người xem report nhầm: Hướng dẫn chủ kênh vào mục **"Xem lại bình luận bị lọc"** để bấm Phê duyệt (Approve) hoặc Khiếu nại (Appeal).

---

## 3. Quy tắc cốt lõi khi trả lời (BẮT BUỘC)
1. **Không đôi co, không xúc phạm người xem**: Luôn dùng thái độ khách quan, tôn trọng, cầu thị.
2. **Không bình luận chính trị, không suy diễn vượt quá bài báo gốc**: Chỉ trả lời đúng những gì văn bản chính thức hoặc báo chí chính thống đã xác nhận.
3. **Bảo vệ uy tín doanh nghiệp và cộng đồng**: Khi nhắc đến doanh nghiệp địa phương (khách sạn, khu du lịch, nhà máy, công ty), tuyệt đối không để người xem hiểu sai là bị phạt, thua lỗ hay vi phạm trừ khi có kết luận pháp luật bằng văn bản.
4. **Không dẫn dụ ra ngoài nền tảng**: Không nhắn *"nhắn tin riêng cho kênh"*, *"inbox riêng"* trong phần trả lời bình luận để tránh bot TikTok quét phạt spam.

---

## 4. Tài liệu tham khảo đi kèm
- File tra cứu từ khóa & rủi ro: [reference/bo-tu-khoa-nhay-cam.json](file:///f:/NewsVideo/skills/tra-loi-binh-luan/reference/bo-tu-khoa-nhay-cam.json)
- Kịch bản mẫu cho các vụ việc nóng: [reference/kich-ban-mau-tra-loi.md](file:///f:/NewsVideo/skills/tra-loi-binh-luan/reference/kich-ban-mau-tra-loi.md)
- Script phân tích & gợi ý: [scripts/kiem_tra_binh_luan.py](file:///f:/NewsVideo/skills/tra-loi-binh-luan/scripts/kiem_tra_binh_luan.py)
