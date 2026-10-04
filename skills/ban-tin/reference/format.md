# Format bản tin JSON

```json
{
  "type": "digest",
  "output": "anh",
  "date": "2026-10-03",
  "region": "Quy Nhơn",
  "province": "Gia Lai",
  "brand": ["TIN", "QUY NHƠN"],
  "chip": "",
  "cover": {
    "kicker": "BẢN TIN",
    "title": "Tin tức Quy Nhơn",
    "subtitle": "Ngày 3/10/2026",
    "teaser": "Taxi 'chặt chém' 70.000 đồng cho 2 km bị phạt 88 triệu đồng",
    "icon": "pin"
  },
  "items": [
    {
      "category": "khu-vuc",
      "text": "Hợp tác xã vận tải bị phạt 88 triệu đồng, tước phù hiệu 22 xe trong 2 tháng sau vụ tài xế thu 70.000 đồng cho cuốc xe 2 km ở Quy Nhơn.",
      "ai_prompt": "a taxi parked on a coastal city street in Vietnam, daytime",
      "image_credit": "",
      "source": "https://...",
      "source_name": "VietNamNet",
      "published": "2026-10-03T09:54:52+07:00",
      "from_user": false
    }
  ],
  "outro": "Follow để 11h mai xem tiếp tin Quy Nhơn",
  "outro_question": "Bạn thấy phạt 88 triệu có đủ răn đe không?",
  "pin_comment": "Tin nào làm bạn bất ngờ nhất? Ghi số 1–8 👇",
  "caption": {"tiktok": "...", "youtube": "...", "facebook": "..."},
  "hashtags": ["#quynhon", "#tintuc", "#gialai"],
  "needs_review": []
}
```

## Trường

| Trường | Bắt buộc | Ghi chú |
|---|---|---|
| `type` | ✔ | luôn `"digest"` |
| `output` | | `"anh"` hoặc `"video"`; bỏ trống = `default_output` trong `config/ban-tin.json` |
| `date` | ✔ | `YYYY-MM-DD` |
| `region` | ✔ | tên khu vực, dùng cho nhãn "Tin <region>" |
| `province` | | tên tỉnh, dùng cho nhãn "Tin <province>" (category `tinh`) |
| `brand` | | 2 phần tên kênh trên thanh trên, phần 2 tô màu nhấn. Mặc định lấy từ `config/ban-tin.json` |
| `chip` | | nhãn nhỏ góc phải (vd. `"DEMO"`), để trống nếu không cần |
| `colors` | | `{"dark","mid","light","accent"}` mã màu hex, mặc định navy + vàng |
| `cover.title` / `cover.subtitle` | ✔ | tiêu đề bìa + ngày |
| `cover.kicker` / `cover.teaser` | | nhãn nhỏ, 1 câu hé lộ tin hot |
| `cover.image` | | mặc định `item:1` = ảnh tin 1 làm nền bìa; `item:N` = ảnh tin N; `icon` = không dùng ảnh (nền + icon `cover.icon`) |
| `items[]` | ✔ | 1–30 tin (khuyến nghị 10–12) |
| `items[].category` | ✔ | `khu-vuc` · `tinh` · `trong-nuoc` · `the-gioi` – **chỉ được dùng loại có trong `allowed_categories` của `config/ban-tin.json`** (hiện tại chỉ `khu-vuc`) |
| `items[].label` | | ghi đè nhãn chuyên mục |
| `items[].text` | ✔ | 20–260 ký tự (nên 80–200) |
| `items[].image` | | mặc định `press:auto` = **ảnh thật bài gốc (ưu tiên 1)**; xem bảng dưới |
| `items[].ai_prompt` | nên có | mô tả cảnh tiếng Anh cho ảnh AI – chỉ dùng khi không lấy được ảnh thật |
| `items[].image_credit` | | tên báo/tác giả ảnh (mặc định = `source_name`) |
| `items[].source` | ✔ | link bài gốc |
| `items[].source_name` | ✔ | tên báo, hiện dưới ảnh "Nguồn: ..." |
| `items[].published` | ✔ | thời điểm đăng bài gốc, lấy bằng `ban_tin.py meta` (vd. `2026-10-03T09:54:52+07:00`); **phải cùng ngày với `date`** (trừ `from_user`) |
| `items[].from_user` | | `true` = tin người dùng gửi (không được loại) |
| `outro` | ✔ | câu ở trang cuối (kêu gọi follow) |
| `outro_question` | nên có | câu hỏi kéo bình luận, hiện trên thẻ vàng ở trang cuối |
| `pin_comment` | nên có | bình luận ghim, ghi vào `caption.txt` |
| `caption.tiktok/youtube/facebook` | ✔ | caption từng nền tảng |
| `hashtags` | | 3–5 hashtag |
| `needs_review` | | điều AI chưa chắc, người dùng cần duyệt |

## Giá trị `image`

| Dạng | Ý nghĩa |
|---|---|
| `input:<tên file>` | ảnh trong thư mục `input/` (ưu tiên) |
| `ai:<mô tả tiếng Anh>` | ảnh minh hoạ AI tạo miễn phí (Pollinations), ghi "Ảnh minh hoạ AI"; chỉ cảnh chung, không người thật/logo/chữ |
| `press:auto` | ảnh đại diện (og:image) của bài ở `source`; hoặc `press:<link ảnh>`; cần duyệt bản quyền |
| `pexels:<từ khoá tiếng Anh>` | tự tìm ảnh Pexels (cần `PEXELS_API_KEY` trong `config/secrets.env`); thiếu key → icon |
| `icon:<tên>` | hình minh hoạ vẽ sẵn |
| `text:<chữ ngắn>` | thẻ chữ to (số liệu, ngày) |
| `map:<địa điểm>` | (chưa hỗ trợ bản đồ – tạm dùng icon ghim) |

Icon có sẵn: `pin` (địa điểm) · `globe` (thế giới) · `flag` (Việt Nam) · `money` (tiền, giá, phạt) · `bolt` (điện, năng lượng) · `car` (giao thông, xe) · `shield` (công an, an ninh) · `school` (giáo dục) · `warning` (thiên tai, sạt lở, ngập) · `leaf` (môi trường, khí hậu) · `walk` (vỉa hè, đô thị) · `chart` (kinh tế, tăng trưởng) · `ship` (biển, cảng, du lịch biển) · `home` (nhà ở, dân cư) · `mic` (sự kiện, hội nghị)

## Thời lượng (script tự tính)
Bìa 2,5 giây · mỗi tin min(5 giây, 53,5 ÷ số tin) · kết 3 giây → tổng ≤ 59 giây (YouTube Shorts có nhạc bản quyền cần ≤ 60 giây).

## Cấu hình `config/ban-tin.json`
| Trường | Ý nghĩa |
|---|---|
| `region`, `province`, `region_scope` | khu vực, tỉnh, địa bàn cụ thể được tính là "trong khu vực" |
| `allowed_categories` | chuyên mục được phép (script báo lỗi tin ngoài phạm vi) |
| `default_output`, `brand` | chế độ mặc định, tên kênh |
| `sources` | trang để lệnh `scan` lấy bài: `name`, `url`, `pattern` (regex link bài, nhóm 1 = mã bài), `max`, `region_search` |
| `region_keywords` | từ khoá đánh dấu ✓ khi `scan` |
| `preview_music` | nhạc chỉ để xem thử nội bộ (`file`, `start`) |
