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
- **Đọc `skills/ban-tin/config.json` trước**: khu vực (`region`), địa bàn cụ thể (`region_scope`), **phạm vi tin được phép** (`allowed_categories`), tên kênh (`brand`).
  Hiện tại: **ưu tiên tin Quy Nhơn** (`khu-vuc`), **được lấy tin toàn tỉnh Gia Lai** (`tinh`) – không lấy tin tỉnh khác/trong nước/thế giới. Bài nguồn chỉ cần **có nhắc Quy Nhơn hoặc Gia Lai** và sự việc xảy ra trên địa bàn. Script sẽ báo lỗi nếu có tin ngoài phạm vi.
- **Khu vực** (`region`): theo cấu hình; người dùng nói khu vực khác thì làm theo người dùng. Ghi thêm `province` nếu tin cấp tỉnh (vd. Quy Nhơn → tỉnh Gia Lai, vì từ 1/7/2025 Bình Định đã sáp nhập vào Gia Lai).
- **Chế độ** (`output`): mặc định là `"anh"` (**chỉ chụp bộ ảnh lướt 9:16 `anh/01.png…09.png` + `caption.txt`, tạm thời không tạo file video `.mp4`** trừ khi người dùng yêu cầu rõ "làm video").
- **Ngày**: hôm nay. Bìa ghi "Ngày D/M/YYYY".

### 2. Thu tin – Kiểm tra chủ đề đang tăng view & chạy `scan` trước (đỡ tốn token, không sai ngày)
- **Bước 2.1 – Bám sát các chủ đề đang tăng view trên kênh (Follow-up Trending Topics)**:
  - Trước hoặc song song lúc quét tin, kiểm tra các video gần đây trên kênh `@quynhon24hqua` xem **video nào đang tăng view đột biến hoặc có nhiều bình luận quan tâm** (ví dụ: vụ nữ sinh ĐH Quy Nhơn, kiểm tra tiệm vàng, cháy nhà Vĩnh Thịnh, dự án Thị Nại Eco Bay, công viên biển khách sạn Bình Dương, sạt lở núi Một, truy bắt phạm nhân...).
  - **Nguyên tắc**: Video tăng view nghĩa là chủ đề đó đang được khán giả địa phương ngóng chờ → **video tiếp theo BẮT BUỘC phải chủ động tìm kiếm xem các vụ việc/dự án đó có diễn biến mới, thông báo mới hay kết quả điều tra mới trong 24h qua không**. Nếu có tình tiết mới (không lặp lại thông tin cũ), **ưu tiên đưa ngay vào bản tin mới (đặt ở Tin 1 làm Hook hoặc Tin 2)** để tạo chuỗi tin (Series Follow-up) giữ chân người xem.
- **Bước 2.2 – Chạy lệnh `scan`**:
```bash
python skills/ban-tin/scripts/ban_tin.py scan --date YYYY-MM-DD
```
Lệnh đọc các trang nguồn trong `skills/ban-tin/config.json` (`sources` và `user_links`), lấy giờ đăng thật của từng bài, **chỉ in tin đăng trong 24 giờ tính lùi từ lúc quét** (quét ngày cũ thì tính lùi từ 23:59 ngày đó), gộp tin trùng giữa các nguồn, đánh dấu ✓ tin có từ khoá khu vực (`region_keywords`), báo bài nào không có ảnh. Kết quả lưu `data/scan/<ngày>.json`.
Sau đó:
1. Link bài người dùng dán trong `user_links` (`skills/ban-tin/config.json`) hoặc gửi qua chat / thư mục `input/` → **luôn đưa vào** (`"from_user": true`)
2. Chọn từ danh sách `scan` (ưu tiên dòng ✓); `scan` lỗi hoặc thiếu tin → tự tìm thêm trên báo địa phương
3. Muốn thêm nguồn quét tự động → thêm vào `sources` trong `skills/ban-tin/config.json` (không sửa script)

**Bản tin chỉ lấy tin ĐĂNG TRONG 24 GIỜ QUA**, tính lùi từ lúc làm bản tin (giờ Việt Nam). Ví dụ làm lúc 12h ngày 4/10 → lấy tin từ 12h ngày 3/10 đến 12h ngày 4/10; tin ngày hôm trước vẫn lấy nếu còn trong 24h.
Không lặp tin đã đưa ở bản tin trước (xem `skills/ban-tin/inbox/` các bản gần nhất). Không đủ tin → làm ít tin hơn (tối thiểu 3) và báo người dùng; không "độn" tin cũ hơn 24h.
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

### 4. Chọn lọc tin & Tự động dựng (Mặc định: Tự động hóa 100% - Run skill là ra luôn thành phẩm)
- **Chế độ mặc định (Tự động 100%)**: AI tự động chọn ra **8–12 tin mạnh nhất, nóng nhất (hơn 7 tin)** ở chế độ Ảnh cuộn (`--mode anh`) từ danh sách đã quét (hoặc từ `user_links` người dùng đưa), kiểm tra bài gốc chuẩn xác, tự động viết kịch bản và tự động render bộ ảnh lướt ngay lập tức. (Chỉ khi người dùng yêu cầu làm `--mode video` mới rút gọn còn 6–7 tin để video ≤ 59 giây).
- **Thứ tự 6 nhóm lĩnh vực ưu tiên chọn lọc tin (đã chốt với người dùng)**:
  1. 🔥 **Chuỗi tin đang tăng view trên kênh (Follow-up)**: Diễn biến mới của các vụ việc khán giả đang ngóng (như vụ trốn trại, đại dự án Thị Nại Eco Bay, kiểm tra tiệm vàng...).
  2. 🚨 **An ninh – Pháp luật – Cứu hộ**: Vụ việc nóng, cảnh báo an toàn, giao thông, tàu cá.
  3. 🏗️ **Quy hoạch – Hạ tầng – Đại dự án**: Sân bay Phù Cát, cao tốc Quy Nhơn – Pleiku, công viên biển, giải phóng mặt bằng, khu đô thị.
  4. 🌦️ **Dân sinh – Thời tiết – Y tế**: Mưa lũ, sạt lở, lịch cúp điện/nước, dịch bệnh, khám chữa bệnh.
  5. 🏖️ **Du lịch – Văn hóa – Sự kiện – Thể thao**: Sự kiện cuối tuần ở Quảng trường Nguyễn Tất Thành, giải chạy, bắn pháo hoa, điểm check-in mới.
  6. 💼 **Kinh tế – Việc làm – Giáo dục**: Giá cả, chính sách hỗ trợ, trường đại học/học sinh.
- **Cách sắp xếp thứ tự trong bản tin**: Tin hot nhất đặt ở **tin 1** (làm ảnh bìa + hook teaser), tin hot thứ 2 đặt ở **giữa bài (tin 4–5)** để giữ chân người xem lướt tiếp, các tin sự kiện/văn hóa nhẹ nhàng đặt ở cuối.
- **Chế độ duyệt thủ công (chỉ bật khi người dùng yêu cầu)**: Nếu người dùng nói "cho tôi chọn tin trước" hoặc "duyệt tin trước khi render", AI mới dừng lại liệt kê danh sách checkbox để người dùng chọn trước khi viết và render.

**Gợi ý chọn tin (để người xem ở lại tới ảnh cuối):**
- Mặc định ở **chế độ Ảnh cuộn (`anh`)**: chọn **8–12 tin mạnh (hơn 7 tin)** giống công thức kênh mẫu `@tinchuan23h59s` (nếu 24h qua ít tin thật sự chất lượng thì lấy tối đa số tin tốt hiện có, không độn tin hội nghị/lễ tân nhạt).
- Xếp cuối hoặc bỏ: hội nghị, bế giảng, khai giảng, tin lễ tân (ít người quan tâm). Khi trình danh sách `List All Tin`, đánh dấu ⭐ tin mạnh, ▫ tin yếu để người dùng dễ đổi tin nếu muốn.

### 5. Viết
- Mỗi tin **1–2 câu, 80–200 ký tự**, đủ ý không cần đọc thêm, viết lại bằng lời mình (không chép tít).
- Có số liệu cụ thể, địa danh (phường/xã), mốc thời gian.
- **Tin quy hoạch, di dời, giải tỏa, dự án**: BẮT BUỘC nêu rõ lý do chính thức từ cơ quan nhà nước (vd: *"theo quy hoạch mở rộng không gian bờ biển ngắm cảnh cho cộng đồng"*, *"hết hạn thuê đất theo hợp đồng"*), không để khuyết thông tin khiến người xem suy đoán tiêu cực, bôi nhọ uy tín doanh nghiệp (như đồn đoán *"kinh doanh kém nên bị dẹp"*).
- Án hình sự / tai nạn: không nêu tên đầy đủ, không giật gân, không từ lóng.
- `cover.teaser` = **câu gây tò mò** của tin 1 (≤ 70 ký tự), hiện to trên bìa. Gây tò mò bằng sự thật, chừa kết quả để người xem lướt tiếp, vd. *"53 tài xế Quy Nhơn bị test ma túy bất ngờ – kết quả?"*. **Cấm** tít sai sự thật, thổi phồng; tin tai nạn/hình sự không giật gân.
- Bìa mặc định **lấy ảnh tin 1 làm nền** (không cần ghi). Muốn bìa chỉ có icon: `"cover": {"image": "icon"}`; dùng ảnh tin khác: `"image": "item:N"`.
- **Trang cuối = logo + lời follow + dòng mời gửi tin**: `outro` = *"Follow để nắm bắt tin tức Quy Nhơn nhé"*; dòng thứ 2 `outro_sub` mặc định *"Nhà bạn có tin? Nhắn kênh, kênh đưa!"* (script tự thêm, không cần ghi). **Không** dùng `outro_question` (người dùng không thích thẻ câu hỏi ở trang cuối).
- `pin_comment`: bình luận kênh tự đăng rồi ghim – **câu hỏi tích cực, văn minh về chủ đề của tin số 1**, hướng đến tiện ích cộng đồng (vd: *"Bà con có mong chờ công viên ngắm biển mới này không? Chia sẻ cảm nghĩ nhé!"*). **Tuyệt đối KHÔNG** đặt câu hỏi mở mơ hồ tạo kẽ hở kích động đồn đoán thất thiệt, không hỏi chi tiết phán xét người liên quan hay doanh nghiệp. **Không** chèn câu kéo tin nhắn ngoài nền tảng (*"Nhắn kênh, kênh đưa!"*) vào bình luận để tránh bị TikTok gắn cờ spam.
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
`skills/ban-tin/inbox/YYYYMMDD-<khu-vuc-khong-dau>.json`, UTF-8, đúng format `reference/format.md`.
AI chat trên web (không ghi được file): trả về 1 khối ```json để người dùng dán vào app.

### 8. Kiểm tra + dựng
```bash
python skills/ban-tin/scripts/ban_tin.py check  skills/ban-tin/inbox/<file>.json
python skills/ban-tin/scripts/ban_tin.py render skills/ban-tin/inbox/<file>.json --mode anh   # mặc định: chỉ tạo bộ ảnh lướt anh/01.png...09.png + caption.txt
python skills/ban-tin/scripts/ban_tin.py render skills/ban-tin/inbox/<file>.json --mode video # chỉ chạy khi người dùng yêu cầu làm video
```
- `check` báo lỗi → sửa JSON rồi chạy lại.
- Kết quả ở `data/output/<tên>-anh/`: `anh/01.png…09.png` (chế độ ảnh lướt mặc định) + `caption.txt`. (Tạm thời không tạo file `.mp4` ở chế độ ảnh để chạy cực nhanh; chỉ tạo `.mp4` khi dùng `--mode video`).
- AI xem được ảnh → mở vài file `anh/*.png` kiểm tra chữ đủ dấu, không tràn khung.

### 9. Báo lại người dùng (BẮT BUỘC kèm "List All Tin")
1. **Thành phẩm bản tin**: Danh sách **8–12 tin đã chọn (hơn 7 tin)** (1 dòng/tin + nguồn), đường dẫn thư mục ảnh `anh/`, caption chuẩn với đầy đủ 6 hashtag (`#quynhon #tinquynhon #gialai #binhdinh #tintuc #quynhon24hqua`) và bình luận ghim (`pin_comment`).
2. **List All Tin trong 24h qua**: Luôn liệt kê toàn bộ danh sách các tin khu vực quét được trong 24h qua (chia nhóm: *Đã chọn / Tin dự phòng tốt / Tin đã đăng bản trước / Tin hội nghị hoặc ngoài địa bàn*) để người dùng dễ dàng yêu cầu đổi thứ tự hoặc thay tin ngay lập tức.

### 10. Phân tích kênh & tư vấn chiến lược (BẮT BUỘC mỗi lần làm tin / render)
- Truy cập / kiểm tra kênh TikTok chính [@quynhon24hqua](https://www.tiktok.com/@quynhon24hqua):
  - Số liệu hiện tại: Followers, số video, lượt Thích tổng, tương tác.
  - Phân tích hiệu ứng nội dung & **Theo dõi chuỗi tin tăng view (Series Follow-up)**: Xác định các video tăng view mạnh gần đây (chủ đề được quan tâm cao) → chủ động săn lùng diễn biến mới của các chủ đề đó cho bản tin kế tiếp.
  - Đề xuất định hướng chiến lược: Khung giờ đăng tốt nhất, cách đặt câu hỏi ghim bình luận để kích thích tranh luận/chia sẻ, và điều chỉnh pacing/teaser cho video tiếp theo.
- Theo dõi các kênh tin tức đối thủ / benchmark tại địa phương:
  - [@hong.hot.quy.nhon](https://www.tiktok.com/@hong.hot.quy.nhon) & [@hong.hot.quy.nhon.bd](https://www.tiktok.com/@hong.hot.quy.nhon.bd): Quan sát chủ đề tin giật gân, chuyện dân sinh Quy Nhơn đang lên xu hướng và cách họ đặt tiêu đề/hook để học hỏi và đón đầu.

## Mẫu hiển thị (đã chốt với người dùng – script/template tự làm, AI không cần chỉnh)
| Phần | Quy định |
|---|---|
| Số tin & Nhịp | **Ảnh cuộn (`anh` - mặc định)**: **8–12 tin/bản (hơn 7 tin)**. **Video (`video`)**: Bìa 2,5s · mỗi tin 7s · kết 3s · video ≤ 59s → tối đa 7 tin |
| Trang tin | **Ảnh 55% phía trên** (sát mép trên) – **chữ 45% phía dưới**: nguồn ảnh → nhãn chuyên mục + số thứ tự → câu tin |
| Tên kênh | **Không có thanh header**; "QUY NHƠN 24H QUA" nằm trên ảnh, góc trên trái, có lớp mờ tối nhẹ để đọc rõ |
| Bìa | Ảnh tin 1 làm nền (mặc định) + nhãn bản tin + tiêu đề + ngày + `cover.teaser` |
| Trang cuối | Logo + khung "Follow để nắm bắt tin tức Quy Nhơn nhé" + dòng vàng "Nhà bạn có tin? Nhắn kênh, kênh đưa!" (`outro_sub`) |
| Nhạc | Không nhúng – gắn "Em Nên Dừng Lại" trong app khi đăng; bản `XEM-THU-co-nhac` chỉ để xem nội bộ |
Người dùng muốn đổi nhịp/bố cục → sửa `scripts/ban_tin.py` (hằng số thời gian) hoặc `template/index.html`, rồi cập nhật bảng này + `AGENTS.md`.

## Lỗi hay gặp (đã gặp khi test – tránh lặp lại)
- **Công cụ đọc web / tìm kiếm của AI hay sai ngày đăng** (cùng 1 bài lúc ghi 2/10, lúc ghi 3/10) và lẫn tin năm cũ → ngày đăng **chỉ tin lệnh `meta` / `scan`**.
- **Tóm tắt của công cụ đọc web có thể sai địa danh** (vd. "phường Quy Nhơn, thành phố Pleiku") → thông tin mâu thuẫn thì bỏ tin hoặc ghi `needs_review`.
- **Tin chung nhiều địa phương** (vd. 2 trạm dừng nghỉ ở 2 tỉnh) → chỉ viết phần thuộc khu vực, ghi chú vào `needs_review`.
- **Trang tìm kiếm khu vực vẫn lẫn tin nơi khác** (vì bài chỉ nhắc tên khu vực) → dấu ✓ chỉ là gợi ý, phải đọc bài xác nhận địa bàn.
- **Tiêu chí nhận bài**: bài có nhắc **Quy Nhơn hoặc Gia Lai** là được (kể cả khi chỉ nhắc trong bài); trang nguồn không lọc theo khu vực (vd. VTC tiêu điểm) để `region_search: false` → chỉ ✓ khi tiêu đề/mô tả có từ khoá.
- **Tin hình sự**: bài gốc có thể ghi tên đầy đủ – khi viết chỉ dùng viết tắt/tuổi.
- Dịch vụ ảnh AI miễn phí giới hạn ~1 ảnh/30 giây → script tự chờ; vì vậy luôn ưu tiên ảnh thật bài gốc.

## Không được làm
- Không đăng bài, không gọi API đăng.
- Không nhúng nhạc có bản quyền vào file để đăng (nhạc chung "Em Nên Dừng Lại" được gắn trong app mỗi nền tảng).
- Không bịa số liệu; không bỏ tin người dùng gửi.
- Không sửa `template/` hoặc `scripts/` khi không được yêu cầu.
