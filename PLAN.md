# Plan: App local làm bản tin khu vực (ảnh lướt hoặc video) & đăng 3 nền tảng

## Context
Bạn muốn làm kênh **tin tức ngắn của một khu vực** trên TikTok, YouTube Shorts, Facebook Reels. Cần một app chạy trên máy (miễn phí tối đa) để: thu tin → AI viết bản tin → dựng **ảnh lướt hoặc video** theo mẫu cố định → duyệt → đăng lên 3 nền tảng.

**Kênh tham khảo:** [News23h59 (@tinchuan23h59s)](https://www.tiktok.com/@tinchuan23h59s) – phân tích chi tiết + ảnh mẫu trong `reference\23h59s\PHAN-TICH.md`.
Đã kiểm tra 20/20 bài: **100% là bài ảnh (Photo Mode) + 1 sound**, không có bài video nào. TikTok tự lướt ảnh theo nhạc. Mỗi bài 12–14 ảnh (bìa → 10–12 tin → ảnh kêu gọi follow), chốt 1 bài nhạc cho mọi bài. Trung vị ~44.000 view/bài sau 1 tháng.

**Bản demo đã làm** (03/10/2026): `demo\` (mẫu HyperFrames) → `data\output\demo\ban-tin-mau.mp4` (35s, 1080×1920) + `data\output\demo\slides\01–08.png`. Đây là điểm xuất phát cho cả 2 mẫu.

Đã chốt:
- **2 cách làm, chọn theo từng yêu cầu** (chi tiết ở mục *Hai chế độ đầu ra*):
  - **Ảnh** (mặc định, giống 23h59s): ảnh PNG → TikTok ảnh lướt; YouTube/Facebook ghép ảnh thành video bằng ffmpeg
  - **Video**: video có hiệu ứng dựng bằng HyperFrames → cùng 1 file MP4 đăng cả 3 nơi
- **Nhạc nền chung cho mọi bài:** "Em Nên Dừng Lại" – Kzuy, đoạn từ **5:05** trở đi – **lấy miễn phí, hợp lệ từ kho nhạc trong app của từng nền tảng** (TikTok / YouTube / Facebook), không nhúng file nhạc → app xuất bản **không nhạc**, bạn gắn nhạc lúc đăng
- **Ưu tiên tin Quy Nhơn, được lấy tin toàn tỉnh Gia Lai** (không tin tỉnh khác / trong nước / thế giới) – đổi trong `config/ban-tin.json` (`allowed_categories`)
- **Bản tin chỉ có tin đăng trong 24 giờ qua**, tính lùi từ lúc làm bản tin (làm lúc 12h ngày 4 → lấy tin từ 12h ngày 3; tin hôm trước vẫn lấy). Kiểm tra giờ đăng thật bằng `ban_tin.py meta`; `scan` tự lọc đúng 24h; không lặp tin đã đăng ở bản tin trước
- **AI thu tin 24h qua** từ danh sách nguồn (`config\sources.yaml`, bạn điền sau) + link/file bạn gửi → **chọn 10–12 tin**; tin bạn gửi luôn được ưu tiên
- **Mỗi tin đều có ảnh:** **ảnh thật của bài báo gốc (ưu tiên số 1)** hoặc ảnh bạn đưa → không có mới tạo **ảnh minh hoạ AI** (ghi rõ "Ảnh minh hoạ AI", chỉ cảnh chung) → icon
- **Web app local** (mở trên trình duyệt, chạy bằng `start.bat`)
- **Bản tin do AI viết trong chat** (Claude, Gemini, ChatGPT hay AI bất kỳ – không tốn phí API) → app nhận qua thư mục `inbox\` hoặc ô "Dán bản tin"
- **Hướng dẫn cho AI dùng chung 1 file `AGENTS.md`** (`CLAUDE.md`, `GEMINI.md` chỉ trỏ về đó); quy trình làm bản tin đóng gói thành **skill `ban-tin`**
- **Thư mục:** `F:\NewsVideo`

Chưa chốt (bạn sửa trực tiếp vào plan): xem mục cuối **📝 Phần bạn cần điền**.

---

## Quy trình sử dụng hằng ngày
```
1. Bạn nhắn AI: "làm bản tin hôm nay" (có thể kèm vài link tin bạn muốn có)
   - Muốn video thì nói rõ: "làm bản tin video hôm nay" (không nói gì = ảnh)
   - Link/ảnh/file cũng có thể bỏ sẵn vào F:\NewsVideo\input\
2. AI (theo skill ban-tin):
   - Thu tin 24h qua từ danh sách nguồn (config\sources.yaml) + link bạn gửi
   - Chọn 10–12 tin → kiểm tra nguồn → viết mỗi tin 1 câu → chọn ảnh → lưu bản tin JSON (ghi rõ "output": "anh" | "video")
     · AI ghi được file → tự lưu vào F:\NewsVideo\inbox\
     · AI chat trên web → bạn copy JSON → dán vào ô "Dán bản tin" trong app
   - Đầu vào đã dùng trong input\ chuyển sang input\_done\<ngày>\
   ──────────── từ đây app tự chạy ────────────
3. App thấy file mới → TỰ dựng theo chế độ:
   · Ảnh  → 12–14 ảnh PNG + video ghép ảnh (ffmpeg) cho YouTube/Facebook
   · Video → 1 video MP4 có hiệu ứng (HyperFrames)
4. App báo "Chờ duyệt" → bạn xem, sửa chữ/đổi ảnh nếu cần → bấm "Duyệt" (1 lần bấm)
5. Đến khung giờ đăng → app gửi bộ ảnh/video (không nhạc) + caption sẵn sang điện thoại và nhắc bạn
6. Bạn đăng trên app từng nền tảng: chọn file → gắn sound "Em Nên Dừng Lại" (đã lưu Yêu thích) → dán caption → Đăng (~1–2 phút/nền tảng)
7. Bạn dán link bài đã đăng vào app (hoặc app tự tìm bài mới trên kênh) để lưu lại
```
> Bước 4 (duyệt) có thể tắt bằng `approval: auto` trong `settings.yaml`. Mặc định **bật duyệt**, vì là tin tức nên cần người xem lại trước khi lên sóng.

---

## Hai chế độ đầu ra
Cả 2 dùng **chung 1 file bản tin JSON và chung thiết kế** → AI tốn token như nhau (token chỉ tốn ở khâu AI đọc tin + viết câu, ~7–23 nghìn/bản tin). Khác nhau ở khâu máy dựng (0 token).

| | **Ảnh** (`"output": "anh"`, mặc định) | **Video** (`"output": "video"`) |
|---|---|---|
| Giống | Kênh 23h59s | Bản demo `ban-tin-mau.mp4` |
| Dựng | Mẫu HTML → chụp PNG bằng Playwright (vài giây) | Mẫu HyperFrames → render MP4 (~35–60 giây máy chạy) |
| Hiệu ứng | Không (TikTok tự lướt ảnh) | Trượt ngang giữa trang, zoom nhẹ, chữ hiện dần, mưa/ánh sáng nền |
| TikTok | **Ảnh lướt (Photo Mode)** + gắn sound trong app | Đăng **video** (không nhạc) + gắn sound trong app |
| YouTube / Facebook | ffmpeg ghép PNG thành video **không nhạc** (mỗi ảnh ~5 giây, chuyển cảnh đơn giản) → gắn nhạc trong app | Cùng file MP4 (không nhạc) → gắn nhạc trong app |
| Khi nào dùng | Bản tin hằng ngày | Bản tin đặc biệt, tin nóng cần thu hút, muốn thử nghiệm |

### Mẫu (dùng chung 2 chế độ – học từ 23h59s, đã có bản demo)
| Trang | Kích thước | Nội dung |
|---|---|---|
| Bìa | 1080×1920 | Nền thương hiệu + "Tin tức <khu vực>" + **ngày** + tuỳ chọn 1 dòng hé lộ tin nóng nhất |
| Tin (10–12) | 1080×1920 | Thanh trên (logo) → ảnh tin (1080×860) → `Nguồn/Minh hoạ: ...` → nhãn chuyên mục + số thứ tự (3/12) → 1 câu tin chữ trắng đậm → logo mờ phía dưới |
| Kết | 1080×1920 | "Follow kênh để cập nhật tin tức mới nhất" + logo + ghi công nhạc (nếu cần) |

- Nhãn chuyên mục: `Tin <khu vực> 📍` · `Tin trong nước 🇻🇳` · `Tin thế giới 🌎`
- Thứ tự: tin bạn gửi + tin nóng/ảnh hưởng nhiều nhất đặt **ngay sau bìa**
- Màu, font (hiện tại Be Vietnam Pro), logo lấy từ `brand\` + `settings.yaml` → đổi nhận diện không cần sửa code
- Giới hạn độ dài: video **≤ 59 giây** (YouTube Shorts có nhạc bản quyền nên ≤ 60 giây) → app tự tính giây/tin = min(5, 54 ÷ số tin): 10 tin × 5s, 12 tin × 4,5s; TikTok ảnh lướt tối đa 35 ảnh

### Nhạc nền chung – lấy miễn phí từ kho nhạc của nền tảng
"Em Nên Dừng Lại" (Kzuy, ℗ 2024 COLLAB MUSIC GROUP) là nhạc thương mại → **không có nguồn tải miễn phí hợp lệ**. Cách miễn phí + hợp lệ: gắn trong app, nền tảng đã trả bản quyền.
| Nền tảng | Cách gắn | Lưu ý |
|---|---|---|
| TikTok | Thêm âm thanh → tìm "Em Nên Dừng Lại Kzuy" → chọn đoạn từ ~5:05 (hoặc đoạn TikTok gợi ý) → lưu **Yêu thích** | Tài khoản **Business** chỉ dùng kho nhạc thương mại (thường không có bài này) → dùng tài khoản Cá nhân/Creator |
| YouTube Shorts | App YouTube → tải Short lên → **Thêm âm thanh** → tìm bài → chọn đoạn | Short có nhạc bản quyền nên ≤ 60 giây |
| Facebook Reels | App Facebook → tạo Reel từ file → **Nhạc** → tìm bài | Fanpage có thể bị giới hạn một số bài → thử thực tế ở Giai đoạn 4 |
- Không gắn được nhạc kho qua API/đăng tự động → đây là **bước tay duy nhất** còn lại
- Không có bài trong kho của nền tảng nào → nền tảng đó dùng nhạc miễn phí bản quyền khác (YouTube Audio Library / Meta Sound Collection) hoặc nhạc thịnh hành trong kho
- File `demo\assets\music\em-nen-dung-lai-0505.mp3` (tải từ YouTube) **chỉ dùng xem thử nội bộ**, không dùng để đăng

---

## Công nghệ (Python cho app, Node.js chỉ dùng cho chế độ Video)
| Phần | Dùng |
|---|---|
| Web app | Python **FastAPI** + giao diện HTML đơn giản (Jinja + HTMX) |
| Dữ liệu | **SQLite** (1 file `data/app.db`) |
| Thu tin | **RSS / trang báo** trong `config\sources.yaml`, **trafilatura** (đọc bài báo), **yt-dlp** / **Playwright** (bài FB/TikTok/YouTube), **pypdf** / **python-docx** (file bạn gửi) |
| Chế độ Ảnh | Mẫu **HTML/CSS** trong `slide_templates\` → PNG 1080×1920 bằng **Playwright**; **ffmpeg** ghép PNG + nhạc thành video cho YouTube/Facebook |
| Chế độ Video | **HyperFrames** (HTML + GSAP → MP4), mẫu trong `video_templates\` (gốc từ `demo\`) |
| Ảnh minh hoạ | **Ảnh thật bài gốc** (og:image, ưu tiên 1) / ảnh bạn đưa (`input\`) → **AI tạo ảnh** khi không có (Pollinations, miễn phí ~1 ảnh/30s, có cache) → icon dự phòng |
| Nhạc nền | **Không nhúng** – gắn "Em Nên Dừng Lại" từ kho nhạc trong app TikTok / YouTube / Facebook lúc đăng |
| Giao bài | Chép ảnh/video + `caption.txt` vào thư mục **Google Drive/OneDrive** đồng bộ sang điện thoại; thông báo Windows (+ tuỳ chọn bot Telegram/Zalo) |
| Lưu link bài | Bạn dán link, hoặc **yt-dlp** tự tìm bài mới nhất trên kênh |
| Theo dõi inbox | **watchdog** – có file bản tin mới là tự dựng |
| Hẹn giờ | **APScheduler** chạy trong app – đến khung giờ đăng thì giao bài + nhắc bạn |

---

## Cấu trúc thư mục
```
F:\NewsVideo\
├─ start.bat                 # bấm đúp để chạy app
├─ AGENTS.md                 # hướng dẫn cho MỌI AI: format bản tin, phong cách viết, quy tắc tin tức
├─ CLAUDE.md, GEMINI.md      # chỉ trỏ về AGENTS.md
├─ skills\ban-tin\           # SKILL GỐC (mọi AI): SKILL.md, scripts\ban_tin.py, template\, reference\
├─ .claude\ .agent\ .agents\ # file trỏ skill cho Claude Code / Antigravity (Gemini) / Codex
├─ prompts\                  # prompt dán vào AI chat trên web (ChatGPT, Gemini...)
├─ reference\23h59s\         # phân tích + ảnh mẫu kênh tham khảo
├─ demo\                     # bản demo HyperFrames (03/10/2026) – gốc của 2 mẫu
├─ config\
│   ├─ settings.yaml         # khu vực, chế độ mặc định, kênh đăng, màu, font, khung giờ, giây/ảnh
│   ├─ sources.yaml          # danh sách nguồn tin (RSS, trang báo, page) – bạn điền sau
│   ├─ secrets.env           # token FB, key Pexels (không chia sẻ)
│   ├─ client_secret.json    # OAuth Google (tải từ Google Cloud)
│   └─ youtube_token.json    # app tự tạo sau lần đăng nhập YouTube đầu tiên
├─ brand\                    # logo, font, ảnh nền bìa (nhạc không lưu – gắn trong app nền tảng)
├─ slide_templates\          # mẫu chế độ Ảnh (HTML/CSS): cover, item, outro
├─ video_templates\          # mẫu chế độ Video (HyperFrames)
├─ input\                    # BẠN bỏ thêm: links.txt, ghi chú, ảnh, .pdf/.docx
│   └─ _done\<ngày>\         # đầu vào đã dùng
├─ inbox\                    # AI bỏ bản tin (.json) vào đây
├─ data\  app.db, media\, output\
│   └─ browser_tiktok\       # phiên đăng nhập TikTok riêng của app
└─ app\
    ├─ main.py               # web app
    ├─ fetch\                # thu tin từ nguồn + đọc link/file
    ├─ images\               # chuẩn bị ảnh (input/Pexels/báo), cắt khung, bản đồ, thẻ chữ
    ├─ render\  slides.py (Ảnh), slideshow.py (ffmpeg), video.py (HyperFrames)
    ├─ pipeline\             # theo dõi inbox, hàng đợi, xếp lịch, thử lại
    ├─ handoff\              # chép bài + caption sang thư mục đồng bộ, gửi nhắc, lưu link bài đã đăng
    └─ templates\            # giao diện
```

### Format bản tin (AI viết, app đọc – chi tiết trong `AGENTS.md` / skill)
```json
{
  "type": "digest",
  "output": "anh",
  "date": "2026-10-03",
  "cover": {"title": "Tin tức <khu vực>", "subtitle": "Ngày 3/10/2026", "teaser": "Cấm xe tải qua cầu X giờ cao điểm"},
  "items": [
    {
      "category": "khu-vuc",
      "text": "Từ 15/10, xe tải bị cấm qua cầu X vào giờ cao điểm sáng và chiều, phải đi vòng đường Y.",
      "image": "input:cau-x.jpg",
      "image_credit": "",
      "source": "https://...",
      "from_user": true
    },
    {
      "category": "trong-nuoc",
      "text": "Giá xăng hôm nay tăng hơn 1.400 đồng/lít.",
      "image": "press:https://.../anh.jpg",
      "image_credit": "Tuổi Trẻ",
      "source": "https://..."
    }
  ],
  "outro": "Follow kênh để cập nhật tin tức mới nhất",
  "caption": {"tiktok": "...", "youtube": "...", "facebook": "..."},
  "hashtags": ["#tintuc", "#khuvucX"],
  "needs_review": ["Tin 5: chưa rõ ngày áp dụng"]
}
```
- `output`: `anh` (mặc định) | `video` → app chọn cách dựng
- `category`: `khu-vuc` | `trong-nuoc` | `the-gioi` → app chọn nhãn chuyên mục
- `image`: `input:<file>` (ảnh bạn đưa) · `pexels:<từ khoá>` · `map:<địa điểm>` · `text:<chữ>` · `press:<link ảnh>` (ảnh báo – **bắt buộc** `image_credit`, app tự đánh dấu cần duyệt)
- `from_user`: tin do bạn gửi → luôn giữ, không được loại
- `needs_review`: điều AI chưa chắc → hiện nổi bật ở màn hình duyệt
- App **kiểm tra bản tin** (JSON Schema) khi nhận: sai format → trạng thái Lỗi + báo trường nào sai

---

## Giao bài & đăng (gắn nhạc trong app)

### Luồng
```
inbox\*.json ──(watchdog)──► Mới ──► Đang dựng ──► Chờ duyệt ──(bạn bấm Duyệt)──► Sẵn sàng đăng ──(đến giờ)──► Đã gửi điện thoại ──► Đã đăng
                                         │
                                         ▼
                                       Lỗi (dựng hỏng → nút "Dựng lại")
```
- Bài duyệt xong xếp vào khung giờ đăng (`settings.yaml`); đến giờ app **gửi sang điện thoại** + nhắc bạn
- **Gửi sang điện thoại**: app chép bộ ảnh/video + file `caption.txt` (caption riêng cho TikTok / YouTube / Facebook) vào thư mục đồng bộ (Google Drive hoặc OneDrive) → trên điện thoại mở là thấy
- Nhắc: thông báo Windows + (tuỳ chọn) tin nhắn Telegram/Zalo bot kèm caption để copy nhanh
- Sau khi đăng: bạn dán link vào app, hoặc app tự tìm bài mới nhất trên kênh (yt-dlp) để lưu link + lượt xem

### Cấu hình (`config\settings.yaml`)
```yaml
region: "<khu vực>"
approval: manual            # manual = chờ bạn duyệt
default_output: anh         # anh | video – dùng khi yêu cầu không nói rõ
post_slots: ["11:00"]       # 23h59s đăng ~11h, 1 bài/ngày
digest:
  items: 12                 # số tin mục tiêu (10–12)
  max_video_seconds: 59     # YouTube Shorts có nhạc bản quyền ≤ 60s
music:
  in_app_sound: "Em Nên Dừng Lại – Kzuy (từ 5:05)"   # gắn trong app mỗi nền tảng
handoff:
  sync_folder: "C:/Users/PC/Google Drive/NewsVideo-dang-bai"   # thư mục đồng bộ sang điện thoại
channels:
  youtube:  { enabled: true, channel_url: "https://www.youtube.com/@..." }
  facebook: { enabled: true, page_url: "https://www.facebook.com/..." }
  tiktok:   { enabled: true, username: "@tin..." }
```

### Đăng từng nền tảng (trên điện thoại, ~1–2 phút/nơi)
| Nền tảng | Chế độ Ảnh | Chế độ Video |
|---|---|---|
| TikTok | (+) → chọn 12–14 ảnh → Ảnh → **Thêm âm thanh** (Yêu thích) → dán caption → Đăng | (+) → chọn video → **Thêm âm thanh** → Đăng |
| YouTube Shorts | Chọn video ghép (≤ 59s) → **Thêm âm thanh** → dán tiêu đề → Đăng | Như bên trái |
| Facebook Reels | Tạo Reel từ video ghép → **Nhạc** → dán caption → Chia sẻ | Như bên trái |

**Đăng đúng kênh**: app ghi rõ tên kênh trong file `caption.txt` và thông báo; trên điện thoại kiểm tra đang ở đúng tài khoản/Fanpage trước khi bấm Đăng.

### Việc bạn chuẩn bị 1 lần
1. Tài khoản TikTok **Cá nhân hoặc Creator** (không phải Business, để dùng được bài này), kênh YouTube, Fanpage Facebook
2. Trên cả 3 app: tìm "Em Nên Dừng Lại Kzuy" → lưu Yêu thích / thử gắn vào 1 bài nháp → báo tôi nền tảng nào **không có** bài
3. Cài Google Drive (hoặc OneDrive) trên máy tính + điện thoại cùng 1 tài khoản → tạo thư mục `NewsVideo-dang-bai`
4. Tạo key Pexels (miễn phí, 2 phút)

### Giới hạn cần biết
- Video có nhạc bản quyền: YouTube Shorts ≤ 60 giây → app giữ video ≤ 59 giây
- Facebook Reels 3–90 giây; Fanpage có thể bị giới hạn một số bài nhạc
- TikTok ảnh lướt: tối đa 35 ảnh/bài

### Tự đăng qua API (để dành – Giai đoạn 5)
Chỉ dùng khi bài **không cần nhạc kho** (vd. nhạc miễn phí bản quyền nhúng sẵn): YouTube Data API (OAuth + audit), Facebook Graph API (Page Token), TikTok Content Posting API; kèm `guard.py` kiểm tra đúng kênh trước khi đăng. Hướng dẫn chi tiết sẽ viết khi tới bước này.

---

## Các giai đoạn triển khai

### Giai đoạn 0 – Cài đặt (≈ 1 buổi)
- Cài Python packages, yt-dlp, Playwright (+ Chromium), tạo khung thư mục, `start.bat`
- HyperFrames CLI (đã chạy được qua `npx` khi làm demo)
- Chuyển font từ `demo\assets\` sang `brand\`
- **Bạn làm:** tạo key Pexels (miễn phí, 2 phút); tìm "Em Nên Dừng Lại" trong app TikTok / YouTube / Facebook; cài Google Drive (hoặc OneDrive) trên máy tính + điện thoại
- ✅ Xong khi: mở được `localhost:8000` thấy trang chủ trống

### Giai đoạn 1 – Thu tin + skill viết bản tin (≈ 2 ngày)
- `config\sources.yaml` → app/AI lấy tin 24h qua thành danh sách ngắn
- Đọc link bài báo / FB / TikTok / YouTube (đăng nhập FB/TikTok 1 lần trong Playwright), file .pdf/.docx, ảnh trong `input\`
- ✅ **Đã làm (03/10/2026):** skill `ban-tin` (`skills\ban-tin\`) + `AGENTS.md`, `prompts\` theo format bản tin; test thành công bản tin Quy Nhơn cả 2 chế độ (`data\output\20261003-quy-nhon-*`)
- ✅ Xong khi: nhắn "làm bản tin hôm nay" kèm 2 link → JSON 10–12 tin, có đủ 2 tin bạn gửi, tin nào cũng có nguồn

### Giai đoạn 2 – Dựng 2 chế độ (≈ 3–4 ngày) ⭐ quan trọng nhất
- **Mẫu chung**: tách thiết kế từ `demo\index.html` thành bìa / tin / kết, nhận dữ liệu từ JSON; tự co chữ khi tin dài; tiếng Việt đủ dấu
- **Chế độ Ảnh**: `slide_templates\` → PNG (Playwright) → ffmpeg ghép video **không nhạc** (≤ 59 giây)
- **Chế độ Video**: `video_templates\` (HyperFrames) nhận cùng JSON → MP4 có hiệu ứng như demo, **không nhạc**, ≤ 59 giây
- Xử lý ảnh: lấy từ `input\` / Pexels / ảnh báo, cắt vừa khung 1080×860, bản đồ, thẻ chữ khi không có ảnh
- ✅ Xong khi: cùng 1 file JSON 12 tin → chế độ Ảnh ra 14 PNG + 1 video ghép; chế độ Video ra 1 MP4 ≤ 59 giây; xem ổn trên điện thoại

### Giai đoạn 3 – Pipeline tự động + giao diện duyệt (≈ 2–3 ngày)
- watchdog theo dõi `inbox` → kiểm tra format → tự dựng theo `output`
- Ô **"Dán bản tin"** cho AI chat trên web → kiểm tra → lưu vào `inbox`
- Giao diện duyệt: lướt từng ảnh / xem video → sửa chữ / đổi ảnh / xoá tin / đổi thứ tự / **đổi chế độ Ảnh ↔ Video** → dựng lại → bấm "Duyệt"
- Tin dùng ảnh báo (`press:`) và mục `needs_review` hiện nổi bật
- Trạng thái: Mới / Đang dựng / Chờ duyệt / Sẵn sàng đăng / Đã gửi điện thoại / Đã đăng / Lỗi
- ✅ Xong khi: bỏ 1 file vào `inbox` → không bấm gì → tự dựng xong và nằm ở "Chờ duyệt"

### Giai đoạn 4 – Giao bài sang điện thoại + lưu link (≈ 1–2 ngày)
- **Bạn làm trước**: xem mục *Việc bạn chuẩn bị 1 lần*
- Đến khung giờ: chép bộ ảnh/video + `caption.txt` (3 caption riêng, ghi rõ tên kênh) vào thư mục đồng bộ; thông báo Windows (+ tuỳ chọn bot Telegram/Zalo gửi caption)
- Nút "Đã đăng" + ô dán link; hoặc yt-dlp tự tìm bài mới nhất trên 3 kênh để lưu link + lượt xem
- Tuỳ chọn tự chạy app khi bật máy (Windows Task Scheduler)
- ✅ Xong khi: duyệt 1 bản tin → đến giờ điện thoại có sẵn ảnh/video + caption → bạn gắn nhạc và đăng 3 nơi trong ≤ 5 phút → link được lưu trong app

### Giai đoạn 5 – Mở rộng (làm sau, tùy nhu cầu)
- App tự thu tin theo lịch mỗi sáng → AI chỉ việc chọn + viết
- **Tự đăng qua API** (YouTube / Facebook / TikTok + `guard.py` chống nhầm kênh) cho bài dùng nhạc miễn phí bản quyền nhúng sẵn
- 2 bản tin/ngày (trưa + tối) hoặc bản tin chuyên đề (giao thông, giá cả, thời tiết)
- **Video tin nóng có giọng đọc** (edge-tts + phụ đề) cho tin quan trọng
- Dashboard thống kê view/like từng bài → so sánh Ảnh vs Video, giờ đăng, loại tin
- Nhiều mẫu, nhiều page/kênh

**Tổng giai đoạn 0–4: khoảng 1,5 tuần làm việc** (bỏ phần đăng qua API nên ngắn hơn).

---

## Quy tắc nội dung (chi tiết trong `AGENTS.md`)
- Luôn viết lại bằng lời của mình, mỗi tin 1 câu 15–45 từ, đủ ý không cần đọc thêm; không chép nguyên tít báo
- Mọi tin có link nguồn; tin chưa xác minh / chỉ là bài đăng cá nhân thì không đưa, hoặc ghi rõ "theo thông tin trên mạng xã hội" sau khi bạn đồng ý
- Tin bạn gửi luôn giữ (`from_user`); không đủ căn cứ thì ghi vào `needs_review`. Tin thu từ nguồn thì AI được loại
- Ảnh: ưu tiên ảnh bạn đưa → Pexels / bản đồ / thẻ chữ; ảnh báo chỉ khi cần, luôn ghi nguồn, phải qua duyệt
- Từ lóng nhẹ (kiểu "củ", "tỏi") chỉ cho tin đời sống/nhẹ nhàng; **cấm** với tin tai nạn, án mạng, người chết
- Tai nạn, án hình sự: không nêu tên đầy đủ, không dùng ảnh nạn nhân
- 1 bản tin/ngày giai đoạn đầu, đăng đều đặn đúng giờ

---

## Kiểm tra (verification)
1. Chạy `start.bat` → mở `localhost:8000` không lỗi
2. Nhắn "làm bản tin hôm nay" kèm 2 link → JSON 10–12 tin, có đủ 2 tin bạn gửi, tin nào cũng có nguồn, `output: anh`; nhắn "làm bản tin video" → `output: video`
3. Viết 1 bản tin bằng Claude, 1 bằng Gemini/ChatGPT (dán qua ô "Dán bản tin") → cả 2 đều qua kiểm tra format và dựng được
4. Cùng 1 JSON dựng cả 2 chế độ → so cạnh ảnh mẫu `reference\23h59s\` và bản demo trên điện thoại: chữ rõ, đủ dấu, không tràn khung; video ≤ 59 giây, không có nhạc
5. Tin có ảnh `press:` → hiện cảnh báo ở màn hình duyệt
6. Thử gắn "Em Nên Dừng Lại" trên cả 3 app với 1 bài **riêng tư/nháp** → ghi lại nền tảng nào có/không có bài
7. Duyệt 1 bản tin, đặt khung giờ gần → điện thoại nhận đủ file + caption đúng tên kênh
8. Đăng xong → link 3 bài được lưu trong app

---

## 📝 Phần bạn cần điền / sửa
- [x] Khu vực: Quy Nhơn (tỉnh Gia Lai)
- [x] Tên page/kênh: **Quy Nhơn 24h Qua** – `@quynhon24hqua`; tiểu sử: "📍Chuyện Quy Nhơn 24h qua – gọn trong 1 phút / 📩Nhà bạn có tin? Nhắn kênh, kênh đưa!"; logo `brand\avatar-quy-nhon-24h-qua-1-phut.jpg` (đổi từ kênh cũ @giai.cuu.tin.hoc, ẩn 3 video tin học)
- [x] Link kênh TikTok chính thức: https://www.tiktok.com/@quynhon24hqua
- [x] Đã đăng video đầu tiên trên TikTok: bản tin trưa 4/10/2026 (6 tin, `@quynhon24hqua`)
- [x] Logo kênh, watermark logo nền mờ, quy tắc duyệt bài bằng checkbox đã hoàn thiện
- [x] Nhạc nền: "Em Nên Dừng Lại" – Kzuy, từ 5:05, gắn miễn phí từ kho nhạc trong app mỗi nền tảng
- [x] Số bản tin/ngày + khung giờ vàng đăng: 2 bản/ngày (trưa 11h30–12h30, tối 19h30–20h30)
- [ ] Dùng Google Drive hay OneDrive để chuyển bài sang điện thoại?

---

## 🎯 Định hướng & Chiến lược phát triển kênh (@quynhon24hqua)
1. **Lợi thế nội dung siêu địa phương (Hyper-local):** Người dân và giới trẻ Quy Nhơn/Gia Lai chú ý cao nhất đến địa danh quen thuộc, tin sát vách nhà.
2. **Thử nghiệm A/B dạng bài:**
   - Bản trưa: dạng **Video động** (30–35s).
   - Bản tối: dạng **Bộ ảnh lướt (Photo Carousel)** – người xem tự vuốt đọc, tăng thời gian dừng xem (Dwell Time).
3. **Công thức giữ chân & kéo tương tác:**
   - **Tin 1:** Đóng vai trò móc câu (Hook) gây tò mò, kẹp vấn đề gần gũi (an toàn, giá cả, sự cố, địa điểm mới).
   - **Bình luận ghim:** Tự bình luận ngay 1 câu hỏi mở liên quan tin 1 + "Nhà bạn có tin? Nhắn kênh, kênh đưa!".
4. **Hiệu năng & Tốc độ làm bản tin:**
   - Quét tin tự động 16 luồng (~4s/lần quét).
   - Tự động lọc mốc thời gian từ lần đăng trước đến hiện tại (`--since`).
   - Trình checkbox các tin **đã xác thực bài gốc 100%** để duyệt nhanh trong 1 phút.

