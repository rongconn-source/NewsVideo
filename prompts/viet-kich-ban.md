# Prompt cho AI dạng chat (ChatGPT, Gemini, ... trên web)

Dùng khi AI **không đọc được thư mục dự án** (không chạy được lệnh, không ghi được file).

**Cách dùng:**
1. Mở chat mới → dán nội dung `AGENTS.md`, `skills/ban-tin/SKILL.md` và `skills/ban-tin/reference/format.md` (hoặc dán 1 lần vào Custom GPT / Project / Gem)
2. Dán đoạn bên dưới, thay phần `<...>`
3. Copy khối JSON AI trả về → lưu thành `inbox/YYYYMMDD-<khu-vuc>.json` (hoặc dán vào app ô "Dán bản tin")
4. Chạy: `python skills/ban-tin/scripts/ban_tin.py render inbox/<file>.json`

---

```
Làm bản tin <ảnh / video> khu vực <khu vực>, ngày <D/M/YYYY>, theo đúng skill ban-tin tôi đã gửi.

Tin tôi gửi (luôn đưa vào):
- <link 1>
- <link 2>
- <hoặc dán nội dung bài>

Yêu cầu:
- Chỉ lấy tin đăng trong 24 giờ qua, có nhắc Quy Nhơn hoặc Gia Lai; mở từng bài gốc để lấy số liệu; chọn 6–7 tin (tối đa 7, tin tôi gửi luôn giữ)
- Chỉ trả về 1 khối ```json đúng format, không giải thích bên trong khối
- Sau khối JSON: liệt kê ngắn từng tin + nguồn, và các điểm cần tôi duyệt
```
