---
name: ban-tin
description: Làm bản tin tức tổng hợp khu vực dạng ẢNH LƯỚT hoặc VIDEO dọc 9:16 (TikTok, YouTube Shorts, Facebook Reels) theo mẫu kênh 23h59s. Dùng khi người dùng nói "làm bản tin", "bản tin hôm nay", "bản tin video", "tin <khu vực>", hoặc gửi link tin để làm bài. Thu tin → chọn 10–12 tin → viết mỗi tin 1 câu → lưu JSON → chạy script dựng ảnh/video.
---

# Skill: bản tin (ảnh lướt / video)

Skill này dùng được cho **mọi AI** (Claude Code, Gemini / Antigravity, ChatGPT / Codex, ...).
Phần AI làm = đọc tin + viết JSON. Phần dựng = **1 lệnh Python**, không phụ thuộc công cụ riêng của AI nào.

- Format JSON đầy đủ + ví dụ: [`reference/format.md`](reference/format.md)
- Quy tắc nội dung chung của dự án: `AGENTS.md` (mục *Quy tắc nội dung*)
- Mẫu thiết kế: `template/index.html` (không sửa khi không được yêu cầu)
- Script dựng: `scripts/ban_tin.py`

## Yêu cầu máy
Python 3.10+, Node.js (có `npx`), ffmpeg. Không cần cài thư viện Python nào.

## Quy trình (làm đúng thứ tự)

### 1. Xác định yêu cầu
- **Đọc `config/ban-tin.json` trước**: khu vực (`region`), địa bàn cụ thể (`region_scope`), **phạm vi tin được phép** (`allowed_categories`), tên kênh (`brand`).
  Hiện tại: **chỉ tin trong khu vực** (`["khu-vuc"]`) – không lấy tin tỉnh khác/trong nước/thế giới. Script sẽ báo lỗi nếu có tin ngoài phạm vi.
- **Khu vực** (`region`): theo cấu hình; người dùng nói khu vực khác thì làm theo người dùng. Ghi thêm `province` nếu tin cấp tỉnh (vd. Quy Nhơn → tỉnh Gia Lai, vì từ 1/7/2025 Bình Định đã sáp nhập vào Gia Lai).
- **Chế độ** (`output`): mặc định là `"video"` (chỉ render video dọc 9:16 bằng HyperFrames; tạm không render ảnh lướt).
- **Ngày**: hôm nay. Bìa ghi "Ngày D/M/YYYY".

### 2. Thu tin – chạy `scan` trước (đỡ tốn token, không sai ngày)
```bash
python skills/ban-tin/scripts/ban_tin.py scan --date YYYY-MM-DD
```
Lệnh đọc các trang nguồn trong `config/ban-tin.json` (`sources`), lấy giờ đăng thật của từng bài, **chỉ in tin đăng trong 24 giờ tính lùi từ lúc quét** (quét ngày cũ thì tính lùi từ 23:59 ngày đó), gộp tin trùng giữa các nguồn, đánh dấu ✓ tin có từ khoá khu vực (`region_keywords`), báo bài nào không có ảnh. Kết quả lưu `data/scan/<ngày>.json`.
Sau đó:
1. Link / nội dung / file người dùng gửi (chat hoặc thư mục `input/`) → **luôn đưa vào** (`"from_user": true`)
2. Chọn từ danh sách `scan` (ưu tiên dòng ✓); `scan` lỗi hoặc thiếu tin → tự tìm thêm trên báo địa phương
3. Muốn thêm nguồn → thêm vào `sources` trong `config/ban-tin.json` (không sửa script)

**Bản tin chỉ lấy tin ĐĂNG TRONG 24 GIỜ QUA**, tính lùi từ lúc làm bản tin (giờ Việt Nam). Ví dụ làm lúc 12h ngày 4/10 → lấy tin từ 12h ngày 3/10 đến 12h ngày 4/10; tin ngày hôm trước vẫn lấy nếu còn trong 24h.
Không lặp tin đã đưa ở bản tin trước (xem `inbox/` các bản gần nhất). Không đủ tin → làm ít tin hơn (tối thiểu 3) và báo người dùng; không "độn" tin cũ hơn 24h.
Ngoại lệ duy nhất: tin người dùng tự gửi.

**Chưa đăng bản nào từ hôm qua** (người dùng nói rõ) → lấy tin từ **đầu ngày hôm qua đến hiện tại**: `scan --since YYYY-MM-DD` (ngày hôm qua). Nói chung mốc bắt đầu = lúc đăng bản tin trước; `--since` nhận cả giờ, vd. `--since 2026-10-04T12:00`.
**Bản tối**: quét lại, liệt kê lại toàn bộ danh sách (kể cả tin chưa chọn ban trưa) + **thêm tin chiều → tối**; đánh dấu tin đã đăng bản trưa (nếu người dùng đã đăng) để không lặp.

### 3. Kiểm tra từng tin – BẮT BUỘC
- **Kiểm tra ngày đăng bằng lệnh** (đọc `article:published_time` trong trang, chính xác hơn công cụ đọc web/tìm kiếm):
  ```bash
  python skills/ban-tin/scripts/ban_tin.py meta <link1> <link2> ...
  ```
  Ngày ≠ D → loại. Lệnh cũng in `ảnh:` (ảnh đại diện bài gốc) để dùng với `press:auto`.
- **Mở bài gốc** để lấy số liệu, tên địa danh. **Không** viết từ đoạn tóm tắt của công cụ tìm kiếm (hay sai ngày, sai địa danh, lẫn tin năm cũ).
- Ghi `source` (link bài gốc) + `source_name` (tên báo).
- Điều chưa chắc → ghi vào `needs_review`, không đoán.

### 4. Trình danh sách tin để người dùng chọn/duyệt (BẮT BUỘC trước khi tạo kịch bản & render)
- Sau khi scan và lọc được các tin hợp lệ, AI **phải liệt kê danh sách tin ứng viên tìm được** (kèm số thứ tự 1, 2, 3..., tóm tắt 1 câu, giờ đăng, nguồn báo) để người dùng duyệt.
- **Chỉ đưa vào danh sách những tin AI ĐÃ MỞ VÀ ĐỌC BÀI GỐC**, đã xác thực địa bàn, số liệu, thời gian (vd. lịch còn hiệu lực). Tin chưa đọc / bài chỉ có video / không rõ địa bàn → **không đưa vào checkbox** (chỉ ghi 1 dòng "đã loại vì…" nếu cần). Người dùng không chấp nhận tin chưa xác thực.
- **Trình dạng checkbox** (công cụ hỏi nhiều lựa chọn, cho chọn nhiều) nếu AI có công cụ đó; không có thì liệt kê `- [ ]` để người dùng trả lời bằng số.
- **Sắp xếp danh sách theo độ hấp dẫn với người xem TikTok** (AI đóng vai chuyên gia nội dung, đặt mình vào vị trí người xem): **ưu tiên giới trẻ 18–30 trước** (an toàn – sự cố gần mình, ở trọ/sinh viên, việc làm, công nghệ/AI, du lịch – bay – ăn chơi, công trình "check-in", giá cả, sự kiện cuối tuần), **rồi tới người trưởng thành** (con cái – trường học – sách vở, sức khoẻ, giao thông – đường sá, đô thị, chính sách tiền bạc). Tin hành chính/hội nghị/lễ ký kết xếp cuối. Ghi 1 dòng lý do ngắn cho nhóm tin đầu.
- Dừng lại hỏi người dùng: người dùng có thể chọn số lượng (ví dụ tìm được 10 tin nhưng chỉ chọn 5 tin), chọn theo số thứ tự, đổi thứ tự ưu tiên, hoặc gửi thêm tin riêng.
- **Tuyệt đối không tự ý render trước khi người dùng xác nhận danh sách tin muốn làm.**
- Chỉ sau khi người dùng chốt danh sách tin, AI mới tiến hành viết kịch bản chi tiết (Bước 5) và dựng (Bước 8).
- Nếu người dùng chủ động nói "tự chọn và làm luôn" hoặc tương đương, AI mới tự chọn 5–6 tin nổi bật nhất rồi dựng.

**Gợi ý chọn tin (để người xem ở lại tới ảnh cuối):**
- Mặc định đề xuất **5–6 tin mạnh** (mỗi tin hiện **8 giây** để người xem kịp đọc + xem ảnh; video ≤ 59 giây nên **tối đa 6 tin**) – tỉ lệ xem hết quan trọng hơn số tin.
- Ưu tiên tin **chạm đời sống người dân**: giao thông / cấm đường / công trình, giá cả – điện nước, thời tiết – bão, cảnh báo lừa đảo, an ninh trật tự, sự kiện – lễ hội cuối tuần, du lịch – ăn uống, chuyện lạ / cảm động.
- Xếp cuối hoặc bỏ: hội nghị, bế giảng, khai giảng, tin lễ tân (ít người quan tâm). Khi trình danh sách, đánh dấu ⭐ tin mạnh, ▫ tin yếu để người dùng dễ chọn.
- Thứ tự: tin hot nhất ở **tin 1** (cũng là ảnh bìa) → tin hot thứ 2 đặt **giữa bài** để giữ người xem → tin nhẹ/vui để cuối.

### 5. Viết
- Mỗi tin **1–2 câu, 80–200 ký tự**, đủ ý không cần đọc thêm, viết lại bằng lời mình (không chép tít).
- Có số liệu cụ thể, địa danh (phường/xã), mốc thời gian.
- Án hình sự / tai nạn: không nêu tên đầy đủ, không giật gân, không từ lóng.
- `cover.teaser` = **câu gây tò mò** của tin 1 (≤ 70 ký tự), hiện to trên bìa. Gây tò mò bằng sự thật, chừa kết quả để người xem lướt tiếp, vd. *"53 tài xế Quy Nhơn bị test ma túy bất ngờ – kết quả?"*. **Cấm** tít sai sự thật, thổi phồng; tin tai nạn/hình sự không giật gân.
- Bìa mặc định **lấy ảnh tin 1 làm nền** (không cần ghi). Muốn bìa chỉ có icon: `"cover": {"image": "icon"}`; dùng ảnh tin khác: `"image": "item:N"`.
- **Trang cuối chỉ có logo + lời follow**: `outro` = *"Follow để nắm bắt tin tức Quy Nhơn nhé"*. **Không** dùng `outro_question` (người dùng không thích thẻ câu hỏi ở trang cuối).
- `pin_comment`: bình luận kênh tự đăng rồi ghim – **câu hỏi về chủ đề của tin số 1**, dễ trả lời, + "Nhà bạn có tin? Nhắn kênh, kênh đưa!". Tin 1 là tai nạn/hình sự thì hỏi hướng an toàn/phòng tránh, không hỏi chi tiết vụ việc, không phán xét người liên quan. Không hỏi chính trị/tôn giáo/gây tranh cãi vùng miền.
- Caption Facebook kết bằng chính câu hỏi trong `pin_comment`.
- Caption riêng cho TikTok / YouTube / Facebook, **mở đầu bằng 1 câu hỏi hoặc câu gây tò mò**, rồi liệt kê tin + nguồn.
- **Hashtags BẮT BUỘC luôn là 6 thẻ**: `#quynhon #tinquynhon #gialai #binhdinh #tintuc #quynhon24hqua`.

### 6. Ảnh cho từng tin – mỗi tin PHẢI có ảnh
Script tự thử theo thứ tự, AI chỉ cần điền đúng trường:
1. **Ảnh thật của bài báo gốc** – mặc định (không ghi `image` = `press:auto`, script lấy ảnh đại diện của link `source`, ghi "Ảnh: <tên báo>"). **Ưu tiên số 1.**
   Người dùng gửi ảnh riêng → `"image": "input:<file>"`.
2. **Ảnh minh hoạ AI** – chỉ dùng khi bài gốc không có ảnh: luôn điền `"ai_prompt"` (tiếng Anh, mô tả cảnh chung đúng nội dung tin, bối cảnh Việt Nam) làm dự phòng.
   Cấm: người thật có tên, logo, chữ trên ảnh, cảnh máu me, "ảnh hiện trường" giả. Trên ảnh tự ghi "Ảnh minh hoạ AI".
3. Icon theo chuyên mục – dự phòng cuối cùng (script tự dùng).
Kiểm tra trước bằng `ban_tin.py meta <link>`: dòng `ảnh:` trống → bài không có ảnh → sẽ dùng AI.

### 7. Lưu JSON
`inbox/YYYYMMDD-<khu-vuc-khong-dau>.json`, UTF-8, đúng format `reference/format.md`.
AI chat trên web (không ghi được file): trả về 1 khối ```json để người dùng dán vào app.

### 8. Kiểm tra + dựng
```bash
python skills/ban-tin/scripts/ban_tin.py check  inbox/<file>.json
python skills/ban-tin/scripts/ban_tin.py render inbox/<file>.json            # theo "output" trong JSON
python skills/ban-tin/scripts/ban_tin.py render inbox/<file>.json --mode video
```
- `check` báo lỗi → sửa JSON rồi chạy lại.
- Kết quả ở `data/output/<tên>-<chế độ>/`: `ban-tin.mp4` (không nhạc – nhạc gắn trong app khi đăng), `anh/01.png…` (chế độ ảnh), `caption.txt`.
- Xem thử có nhạc (chỉ nội bộ): thêm `--preview-music <file.mp3> --music-start <giây>`.
- AI xem được ảnh → mở vài file `anh/*.png` (hoặc vài khung video) kiểm tra chữ đủ dấu, không tràn khung.

### 9. Báo lại người dùng
Danh sách tin (1 dòng/tin + nguồn), đường dẫn file kết quả, thời lượng, các mục `needs_review`, cảnh báo ảnh báo (`press:`), caption chuẩn với đầy đủ 6 hashtag: `#quynhon #tinquynhon #gialai #binhdinh #tintuc #quynhon24hqua`.

### 10. Phân tích kênh & tư vấn chiến lược (BẮT BUỘC mỗi lần làm tin / render)
- Truy cập / kiểm tra kênh TikTok [@quynhon24hqua](https://www.tiktok.com/@quynhon24hqua):
  - Số liệu hiện tại: Followers, số video, lượt Thích tổng, tương tác.
  - Phân tích hiệu ứng nội dung: Chủ đề nào đang thu hút tương tác tốt (vd. đời sống, an ninh, giao thông, chuyện lạ).
  - Đề xuất định hướng chiến lược: Khung giờ đăng tốt nhất, cách đặt câu hỏi ghim bình luận để kích thích tranh luận/chia sẻ, và điều chỉnh pacing/teaser cho video tiếp theo.

## Lỗi hay gặp (đã gặp khi test – tránh lặp lại)
- **Công cụ đọc web / tìm kiếm của AI hay sai ngày đăng** (cùng 1 bài lúc ghi 2/10, lúc ghi 3/10) và lẫn tin năm cũ → ngày đăng **chỉ tin lệnh `meta` / `scan`**.
- **Tóm tắt của công cụ đọc web có thể sai địa danh** (vd. "phường Quy Nhơn, thành phố Pleiku") → thông tin mâu thuẫn thì bỏ tin hoặc ghi `needs_review`.
- **Tin chung nhiều địa phương** (vd. 2 trạm dừng nghỉ ở 2 tỉnh) → chỉ viết phần thuộc khu vực, ghi chú vào `needs_review`.
- **Trang tìm kiếm khu vực vẫn lẫn tin nơi khác** (vì bài chỉ nhắc tên khu vực) → dấu ✓ chỉ là gợi ý, phải đọc bài xác nhận địa bàn.
- **Tin hình sự**: bài gốc có thể ghi tên đầy đủ – khi viết chỉ dùng viết tắt/tuổi.
- Dịch vụ ảnh AI miễn phí giới hạn ~1 ảnh/30 giây → script tự chờ; vì vậy luôn ưu tiên ảnh thật bài gốc.

## Không được làm
- Không đăng bài, không gọi API đăng.
- Không nhúng nhạc có bản quyền vào file để đăng (nhạc chung "Em Nên Dừng Lại" được gắn trong app mỗi nền tảng).
- Không bịa số liệu; không bỏ tin người dùng gửi.
- Không sửa `template/` hoặc `scripts/` khi không được yêu cầu.
