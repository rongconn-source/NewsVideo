# Hướng dẫn cho AI – dự án NewsVideo

> File này dùng chung cho **mọi AI** (Claude, Gemini / Antigravity, ChatGPT / Codex, ...).
> `CLAUDE.md` và `GEMINI.md` chỉ trỏ về đây. Sửa quy tắc thì **chỉ sửa file này**.
> Tổng quan dự án: `PLAN.md`. Phân tích kênh mẫu: `skills/ban-tin/reference/23h59s/PHAN-TICH.md`.

## 1. Dự án làm gì
Bản tin tức tổng hợp của một khu vực, dạng **ảnh lướt 9:16 (Photo Mode - mặc định chỉ tạo bộ ảnh lướt `anh/*.png`, tạm thời không render file video `.mp4` trừ khi người dùng yêu cầu rõ làm video)**, đăng TikTok / YouTube Shorts / Facebook Reels. Kênh chính thức: [@quynhon24hqua](https://www.tiktok.com/@quynhon24hqua). Học theo mô hình kênh TikTok @tinchuan23h59s.

## 2. Việc của AI → dùng skills tương ứng
- **Khi làm bản tin**: người dùng nói "làm bản tin", "bản tin hôm nay", "bản tin trưa/tối", "tin <khu vực>", hoặc gửi link tin:
  **đọc và làm đúng theo `skills/ban-tin/SKILL.md`.**
  Tóm tắt (Tự động hóa 100% - Run skill là ra thành phẩm): kiểm tra các bài tăng view gần nhất trên kênh để bắt sóng chủ đề hot (Follow-up) → chạy `ban_tin.py scan` lấy tin **đăng trong 24 giờ qua** từ 20+ nguồn có sẵn trong `skills/ban-tin/config.json` (+ link người dùng nếu có) → AI tự động chọn lọc **8–12 tin mạnh nhất (hơn 7 tin)** theo 6 nhóm lĩnh vực ưu tiên và kiểm tra bài gốc → tự viết kịch bản lưu `skills/ban-tin/inbox/YYYYMMDD-<khu-vuc>-<buoi>.json` (`"output": "anh"`) → tự chạy `python skills/ban-tin/scripts/ban_tin.py render skills/ban-tin/inbox/<file>.json --mode anh` → xuất bộ **ảnh lướt `anh/01.png…`** + `caption.txt` (không tạo file `.mp4` trừ khi người dùng bảo làm video) + **luôn kèm theo "List All Tin 24h qua"** để người dùng dễ đổi tin nếu muốn. AI không ghi được file (chat trên web): dùng `skills/ban-tin/prompts/viet-kich-ban.md`, trả về 1 khối JSON.

- **Khi chứng thực & trả lời bình luận khán giả**: người dùng nói "trả lời bình luận", "chứng thực bình luận", "check cmt", "soạn trả lời cmt", "bình luận này trả lời sao", hoặc gửi nội dung bình luận của khán giả:
  **đọc và làm đúng theo `skills/tra-loi-binh-luan/SKILL.md`.**
  Tóm tắt: chạy `python skills/tra-loi-binh-luan/scripts/kiem_tra_binh_luan.py "<nội dung cmt>"` để rà soát rủi ro pháp lý & Tiêu chuẩn Cộng đồng TikTok → đối chiếu bài báo gốc đã lưu trong `skills/ban-tin/inbox/` → đưa ra 3 phương án trả lời chuẩn mực (Ngắn gọn / Đầy đủ căn cứ pháp lý / Thân thiện) và tư vấn từ khóa chặn trên TikTok nếu phát hiện bình luận bôi nhọ/thông tin sai lệch.


## 3. Quy tắc nội dung & xuất bản (bắt buộc)
- **Định dạng mặc định**: Chỉ tạo **chế độ ảnh lướt (`--mode anh`, xuất bộ ảnh `anh/01.png…` + `caption.txt`)**, **tạm thời không render file video `.mp4`** trừ khi người dùng yêu cầu rõ "làm video".
- **Số lượng tin & nhịp**:
  - **Chế độ Ảnh cuộn (`--mode anh`, mặc định)**: Chọn **hơn 7 tin (đề xuất 8–12 tin mạnh/bản)** theo chuẩn kênh mẫu `@tinchuan23h59s` để tối ưu thời gian đọc & lướt ảnh trên TikTok Photo Mode (nếu 24h qua ít tin thật sự chất lượng hơn thì lấy tối đa số tin tốt hiện có, không độn tin rác).
  - **Chế độ Video (`--mode video`, khi được yêu cầu)**: Mỗi tin hiện **7 giây**; video ≤ 59 giây nên tối đa 7 tin/bản.
- **Thứ tự 6 nhóm lĩnh vực ưu tiên khi chọn lọc tin (đã chốt)**:
  1. 🔥 **Chuỗi tin đang tăng view trên kênh (Follow-up)**: Diễn biến mới của các vụ việc khán giả đang ngóng (như vụ trốn trại, đại dự án Thị Nại Eco Bay, kiểm tra tiệm vàng...).
  2. 🚨 **An ninh – Pháp luật – Cứu hộ**: Vụ việc nóng, cảnh báo an toàn, giao thông, tàu cá.
  3. 🏗️ **Quy hoạch – Hạ tầng – Đại dự án**: Sân bay Phù Cát, cao tốc Quy Nhơn – Pleiku, công viên biển, giải phóng mặt bằng, khu đô thị.
  4. 🌦️ **Dân sinh – Thời tiết – Y tế**: Mưa lũ, sạt lở, lịch cúp điện/nước, dịch bệnh, khám chữa bệnh.
  5. 🏖️ **Du lịch – Văn hóa – Sự kiện – Thể thao**: Sự kiện cuối tuần ở Quảng trường Nguyễn Tất Thành, giải chạy, bắn pháo hoa, điểm check-in mới.
  6. 💼 **Kinh tế – Việc làm – Giáo dục**: Giá cả, chính sách hỗ trợ, trường đại học/học sinh.
- **Bố cục mỗi trang tin (đã chốt)**: **ảnh 55% phía trên – chữ 45% phía dưới** (`object-fit: contain` + nền mờ `.photo-blur` để không bị cắt mất chi tiết ngang của ảnh báo); **không có thanh header**, tên kênh "QUY NHƠN 24H QUA" nằm thẳng trên ảnh (góc trên trái); tự động **tô vàng có gạch chân (`.hl`) các con số/địa danh trọng điểm** (hoặc cụm từ được đánh dấu `**...**` trong JSON) kèm nút **`Lướt xem tiếp ➔`** ở góc dưới phải.
- **Chiến lược tăng lượt Lưu bài (Save-bait hợp lệ) & Kiếm tiền (Tỷ lệ 9:1)**: Khuyến khích chọn **1–2 tin dạng "Cẩm nang cần lưu"** (lịch cúp điện/nước, lịch sự kiện cuối tuần, lịch bay/tàu, thủ tục hành chính mới, cảnh báo thời tiết/an toàn) ở nửa cuối bản tin và nhắc khán giả *"Bấm LƯU bài để tiện tra cứu"* trong `pin_comment` nhằm tối ưu chỉ số Save/Bookmark. Duy trì **Tỷ lệ 9:1** đối với thương mại: 9 bài điểm tin hoàn toàn không gắn giỏ hàng để tối đa hóa view tự nhiên (hướng khách vào kệ Trưng bày Đặc sản Quy Nhơn – Gia Lai trên trang cá nhân) + 1 bài chuyên đề Du lịch/Ẩm thực/Dân sinh gắn sản phẩm hợp ngữ cảnh.
- **Trang cuối**: logo + "Follow để nắm bắt tin tức Quy Nhơn nhé" + dòng vàng **"Nhà bạn có tin? Nhắn kênh, kênh đưa!"** (script tự thêm).
- **Hashtags BẮT BUỘC luôn đầy đủ 6 thẻ**: `#quynhon #tinquynhon #gialai #binhdinh #tintuc #quynhon24hqua` (trong mọi caption TikTok, YouTube, Facebook).
- **Tuân thủ tuyệt đối Điều khoản Dịch vụ TikTok**: Đọc và áp dụng nghiêm ngặt theo `skills/ban-tin/reference/tiktok-terms-compliance.md` (không nhúng nhạc có bản quyền vào file đăng, luôn trích nguồn ảnh/báo rõ ràng, không tiết lộ thông tin cá nhân PII của nạn nhân, không giật gân bạo lực, 100% tin thật).
- **Liên tục tìm kiếm nguồn mới**: Chủ động cập nhật và tìm nguồn báo chính thống, chất lượng cao, phản ánh sát đời sống Quy Nhơn & Gia Lai (Báo Gia Lai, Báo Mới, VnExpress, Tuổi Trẻ, Thanh Niên...).
- **BẮT BUỘC phân tích kênh & Bám sát chuỗi tin tăng view (Follow-up Trending Topics) mỗi lần làm bản tin**:
  1. Mỗi lần render video hoặc chuẩn bị kịch bản, AI phải chủ động theo dõi kênh chính [@quynhon24hqua](https://www.tiktok.com/@quynhon24hqua), cập nhật số liệu (Followers, Likes, số video, lượt xem từng bài), đánh giá phản ứng và bình luận của người xem; đồng thời theo dõi các kênh tin địa phương cùng khu vực gồm [@hong.hot.quy.nhon](https://www.tiktok.com/@hong.hot.quy.nhon) và [@hong.hot.quy.nhon.bd](https://www.tiktok.com/@hong.hot.quy.nhon.bd) để nắm bắt xu hướng.
  2. **Nguyên tắc "Video tăng view = Chủ đề khán giả đang ngóng"**: Khi thấy bất kỳ video nào gần đây tăng view đột biến (vd. vụ việc an ninh, kiểm tra tiệm vàng, đại dự án quy hoạch như Thị Nại Eco Bay, công viên biển, sạt lở núi Một...), ở bản tin kế tiếp AI **phải chủ động tìm kiếm xem các chủ đề/vụ việc đó có diễn biến mới, thông báo mới hay kết quả điều tra mới trong 24h qua không**. Nếu có tình tiết mới (không lặp lại thông tin cũ), **bắt buộc ưu tiên đưa vào bản tin mới (đặt ở Tin 1 làm Hook hoặc Tin 2)** để tạo hiệu ứng chuỗi tin (Series Follow-up) giữ chân khán giả.
- **Không bịa**: mọi con số, tên, thời gian phải có trong bài gốc. Không viết từ tóm tắt của công cụ tìm kiếm. Chưa chắc → `needs_review`.
- **Luôn có nguồn**: `source` (link) + `source_name` (tên báo) cho từng tin; nguồn hiện trên ảnh và trong caption.
- **Viết lại bằng lời mình**, không chép nguyên tít báo; mỗi tin 80–200 ký tự, đủ ý.
- **Tin chưa xác minh** (chỉ là bài đăng cá nhân/tin đồn) không viết thành sự thật; chỉ đưa khi người dùng đồng ý và ghi "theo thông tin trên mạng xã hội".
- **Tin người dùng gửi luôn giữ** (`from_user: true`); không đủ căn cứ thì ghi `needs_review`.
- **Tai nạn, án hình sự**: không nêu tên đầy đủ (chỉ viết tắt/tuổi), không dùng ảnh nạn nhân, không giật gân, không từ lóng.
- Từ lóng nhẹ chỉ dùng cho tin đời sống nhẹ nhàng.
- Chính trị, tôn giáo, dân tộc: chỉ đưa theo nguồn chính thống, không bình luận.
- **Đưa tin quy hoạch, di dời, dự án, doanh nghiệp (BẮT BUỘC đầy đủ bối cảnh)**: Khi đưa tin về di dời, tháo dỡ công trình, giải tỏa mặt bằng, thu hồi đất, quy hoạch: **phải nêu rõ lý do chính thức từ chính quyền/bài báo gốc** (vd: *"theo quy hoạch mở rộng không gian công viên biển phục vụ cộng đồng"*, *"hết hạn thuê đất theo hợp đồng"*), tuyệt đối không để khuyết thông tin khiến khán giả suy đoán sai lệch làm tổn hại uy tín doanh nghiệp (như suy diễn *"kinh doanh kém nên bị dẹp"*).
- **Câu hỏi tương tác & Pinned comment an toàn, chuẩn mực**: Câu hỏi ở cuối video và bình luận ghim phải mang tính xây dựng, tích cực, hướng đến lợi ích cộng đồng; tuyệt đối không đặt câu hỏi mở mơ hồ tạo kẽ hở kích động tranh cãi, bôi nhọ doanh nghiệp/cá nhân, hoặc dùng từ ngữ dễ bị bot TikTok quét là spam/chèo kéo tin nhắn off-platform (như *"nhắn kênh, kênh đưa"*).
- **Phạm vi tin theo `skills/ban-tin/config.json`** (hiện tại: **ưu tiên tin Quy Nhơn, được lấy tin toàn tỉnh Gia Lai**; không lấy tin tỉnh khác / trong nước / thế giới). Nguồn nào cũng được, **miễn bài có nhắc tới Quy Nhơn hoặc Gia Lai** và sự việc xảy ra trên địa bàn.
- **Bản tin chỉ có tin đăng trong 24 giờ qua**, tính lùi từ lúc làm bản tin (vd. làm lúc 12h ngày 4 → lấy tin từ 12h ngày 3; tin ngày hôm trước vẫn lấy). Trừ tin người dùng tự gửi. Không lặp tin đã đưa ở bản tin trước. Thiếu tin thì làm ít tin hơn, không độn tin cũ.
- **Ảnh**: mỗi tin phải có ảnh – **ảnh thật của bài báo gốc là ưu tiên số 1** (mặc định, ghi "Ảnh: <báo>") hoặc ảnh người dùng đưa → không có mới dùng ảnh minh hoạ AI (`ai_prompt`, chỉ cảnh chung, không người thật/logo/chữ, ghi rõ "Ảnh minh hoạ AI") → icon.
- **Lưu vết pháp lý (BẮT BUỘC)**: Mọi bản tin sau khi tạo xong phải **luôn lưu file JSON kịch bản vào `skills/ban-tin/inbox/YYYYMMDD-<khu-vuc>-<session>.json`** (đầy đủ nguồn báo gốc, URL, thời gian đăng, trích dẫn số liệu thực tế) và **BẮT BUỘC commit & push lên Git** để tracking, làm căn cứ đối soát chứng cứ pháp lý nếu cơ quan chức năng hoặc công an điều tra kiểm tra. File video đầu ra (`data/output/`) rất nặng nên **không cần push lên Git**.
- Địa giới: từ 1/7/2025 nhiều tỉnh đã sáp nhập (vd. Bình Định → Gia Lai; Quy Nhơn nay là các phường thuộc tỉnh Gia Lai). Dùng tên đơn vị hành chính mới như bài báo gốc.

## 4. AI không được
- Đăng bài hoặc gọi API đăng.
- Nhúng nhạc có bản quyền vào file để đăng (nhạc chung được gắn trong app mỗi nền tảng khi đăng).
- Sửa `config/secrets.env`, token, `data/` (trừ thư mục kết quả do script tạo).
- Sửa `skills/ban-tin/template/` hoặc `scripts/` khi người dùng không yêu cầu.
