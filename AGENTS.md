# Hướng dẫn cho AI – dự án NewsVideo

> File này dùng chung cho **mọi AI** (Claude, Gemini / Antigravity, ChatGPT / Codex, ...).
> `CLAUDE.md` và `GEMINI.md` chỉ trỏ về đây. Sửa quy tắc thì **chỉ sửa file này**.
> Tổng quan dự án: `PLAN.md`. Phân tích kênh mẫu: `reference/23h59s/PHAN-TICH.md`.

## 1. Dự án làm gì
Bản tin tức tổng hợp của một khu vực, dạng **video dọc 9:16** (mặc định chỉ render video, tạm không render ảnh lướt trừ khi người dùng yêu cầu), đăng TikTok / YouTube Shorts / Facebook Reels. Kênh chính thức: [@quynhon24hqua](https://www.tiktok.com/@quynhon24hqua). Học theo mô hình kênh TikTok @tinchuan23h59s.

## 2. Việc của AI → dùng skill `ban-tin`
Khi người dùng nói "làm bản tin", "bản tin hôm nay", "bản tin video", "tin <khu vực>", hoặc gửi link tin:
**đọc và làm đúng theo `skills/ban-tin/SKILL.md`.**

Tóm tắt: chạy `ban_tin.py scan` lấy tin **đăng trong 24 giờ qua** (+ link người dùng) → mở bài gốc kiểm tra → **trình danh sách tin tìm được cho người dùng chọn/duyệt số lượng & tin muốn làm** → người dùng xác nhận xong mới viết mỗi tin 1 câu → lưu `inbox/YYYYMMDD-<khu-vuc>.json` → chạy `python skills/ban-tin/scripts/ban_tin.py render inbox/<file>.json --mode video`.

AI không ghi được file (chat trên web): dùng `prompts/viet-kich-ban.md`, trả về 1 khối JSON.

## 3. Quy tắc nội dung & xuất bản (bắt buộc)
- **Định dạng mặc định**: Chỉ render **video** (dùng HyperFrames), tạm không render ảnh lướt.
- **Hashtags BẮT BUỘC luôn đầy đủ 6 thẻ**: `#quynhon #tinquynhon #gialai #binhdinh #tintuc #quynhon24hqua` (trong mọi caption TikTok, YouTube, Facebook).
- **Tuân thủ tuyệt đối Điều khoản Dịch vụ TikTok**: Đọc và áp dụng nghiêm ngặt theo `reference/tiktok-terms-compliance.md` (không nhúng nhạc có bản quyền vào file đăng, luôn trích nguồn ảnh/báo rõ ràng, không tiết lộ thông tin cá nhân PII của nạn nhân, không giật gân bạo lực, 100% tin thật).
- **Liên tục tìm kiếm nguồn mới**: Chủ động cập nhật và tìm nguồn báo chính thống, chất lượng cao, phản ánh sát đời sống Quy Nhơn & Gia Lai (Báo Gia Lai, Báo Mới, VnExpress, Tuổi Trẻ, Thanh Niên...).
- **BẮT BUỘC phân tích kênh mỗi lần render**: Mỗi lần render video hoặc chuẩn bị kịch bản, AI phải chủ động theo dõi kênh [@quynhon24hqua](https://www.tiktok.com/@quynhon24hqua), cập nhật số liệu (Followers, Likes, số video), đánh giá phản ứng của người xem và đưa ra định hướng chiến lược nội dung cụ thể cho video kế tiếp.
- **Không bịa**: mọi con số, tên, thời gian phải có trong bài gốc. Không viết từ tóm tắt của công cụ tìm kiếm. Chưa chắc → `needs_review`.
- **Luôn có nguồn**: `source` (link) + `source_name` (tên báo) cho từng tin; nguồn hiện trên ảnh và trong caption.
- **Viết lại bằng lời mình**, không chép nguyên tít báo; mỗi tin 80–200 ký tự, đủ ý.
- **Tin chưa xác minh** (chỉ là bài đăng cá nhân/tin đồn) không viết thành sự thật; chỉ đưa khi người dùng đồng ý và ghi "theo thông tin trên mạng xã hội".
- **Tin người dùng gửi luôn giữ** (`from_user: true`); không đủ căn cứ thì ghi `needs_review`.
- **Tai nạn, án hình sự**: không nêu tên đầy đủ (chỉ viết tắt/tuổi), không dùng ảnh nạn nhân, không giật gân, không từ lóng.
- Từ lóng nhẹ chỉ dùng cho tin đời sống nhẹ nhàng.
- Chính trị, tôn giáo, dân tộc: chỉ đưa theo nguồn chính thống, không bình luận.
- **Phạm vi tin theo `config/ban-tin.json`** (hiện tại: **ưu tiên tin Quy Nhơn, được lấy tin toàn tỉnh Gia Lai**; không lấy tin tỉnh khác / trong nước / thế giới).
- **Bản tin chỉ có tin đăng trong 24 giờ qua**, tính lùi từ lúc làm bản tin (vd. làm lúc 12h ngày 4 → lấy tin từ 12h ngày 3; tin ngày hôm trước vẫn lấy). Trừ tin người dùng tự gửi. Không lặp tin đã đưa ở bản tin trước. Thiếu tin thì làm ít tin hơn, không độn tin cũ.
- **Ảnh**: mỗi tin phải có ảnh – **ảnh thật của bài báo gốc là ưu tiên số 1** (mặc định, ghi "Ảnh: <báo>") hoặc ảnh người dùng đưa → không có mới dùng ảnh minh hoạ AI (`ai_prompt`, chỉ cảnh chung, không người thật/logo/chữ, ghi rõ "Ảnh minh hoạ AI") → icon.
- Địa giới: từ 1/7/2025 nhiều tỉnh đã sáp nhập (vd. Bình Định → Gia Lai; Quy Nhơn nay là các phường thuộc tỉnh Gia Lai). Dùng tên đơn vị hành chính mới như bài báo gốc.

## 4. AI không được
- Đăng bài hoặc gọi API đăng.
- Nhúng nhạc có bản quyền vào file để đăng (nhạc chung được gắn trong app mỗi nền tảng khi đăng).
- Sửa `config/secrets.env`, token, `data/` (trừ thư mục kết quả do script tạo).
- Sửa `skills/ban-tin/template/` hoặc `scripts/` khi người dùng không yêu cầu.
