#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
colab_run.py - Quy trình tự động 1-Click trên Google Colab
1. Quét tin tức 24h từ 20 nguồn uy tín (kèm link người dùng gửi nếu có)
2. Dùng Gemini Flash API tự động viết kịch bản chuẩn phong cách Quy Nhơn 24h Qua
3. Kiểm tra tính hợp lệ và xuất kịch bản ra inbox/YYYYMMDD-quy-nhon.json
4. Gọi HyperFrames render video dọc 9:16 chuẩn TikTok (54s)
5. Tự động lưu video và caption sang thư mục Google Drive của người dùng
"""

import sys
import os
import json
import re
import time
import argparse
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Reconfigure utf-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Cấu hình Puppeteer/Chromium cho môi trường Linux/Colab chạy quyền root
os.environ["PUPPETEER_ARGS"] = "--no-sandbox --disable-setuid-sandbox"

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
SKILL_DIR = ROOT_DIR / "skills" / "ban-tin"
SCRIPTS_DIR = SKILL_DIR / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))
import ban_tin

VN_TZ = timezone(timedelta(hours=7))

def call_gemini(api_key: str, prompt: str, system_prompt: str = "") -> str:
    """Gọi Gemini API bằng REST API không phụ thuộc thư viện ngoài"""
    models = ["gemini-2.5-flash", "gemini-1.5-flash"]
    last_err = None

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        body = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt}]}
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        }
        if system_prompt:
            body["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            last_err = f"HTTP {e.code}: {err_body}"
            print(f"  ⚠ Lỗi gọi model {model}: {last_err}, thử model khác...")
            continue
        except Exception as e:
            last_err = str(e)
            print(f"  ⚠ Lỗi kết nối {model}: {last_err}, thử model khác...")
            continue

    raise RuntimeError(f"Không thể gọi Gemini API: {last_err}")


def fetch_article_snippet(url: str) -> str:
    """Đọc tóm tắt 300 từ đầu bài báo gốc để lấy số liệu thực tế"""
    try:
        _, html = ban_tin.fetch_html(url)
        # Bỏ script, style
        html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # Lấy các thẻ p
        pars = re.findall(r'<p[^>]*>(.*?)</p>', html, flags=re.DOTALL | re.IGNORECASE)
        clean_pars = []
        for p in pars:
            txt = re.sub(r'<[^>]+>', '', p).strip()
            txt = ban_tin.unescape(txt)
            if len(txt) > 30 and "bản quyền" not in txt.lower():
                clean_pars.append(txt)
        return "\n".join(clean_pars[:3])[:800]
    except Exception:
        return ""


def run_pipeline(api_key: str, user_link: str = "", drive_dir: str = "", session_type: str = ""):
    now_vn = datetime.now(VN_TZ)
    date_str = now_vn.strftime("%Y-%m-%d")
    hour = now_vn.hour
    
    if not session_type:
        session_type = "chieu" if hour >= 13 else "sang"
    
    session_title = "Chiều" if session_type == "chieu" else "Sáng"
    date_display = now_vn.strftime("%d/%m/%Y")

    print("=" * 60)
    print(f"🚀 BẮT ĐẦU TẠO BẢN TIN QUY NHƠN 24H QUA - {session_title.upper()} {date_display}")
    print("=" * 60)

    # 1. QUÉT TIN
    print("\n🔍 1/5 Đang quét tin tức 24h qua...")
    scan_json = ROOT_DIR / "data" / "scanned" / f"scan_{now_vn.strftime('%Y%m%d_%H%M%S')}.json"
    
    # Tạm thêm link người dùng nếu có
    cfg = ban_tin.load_config()
    orig_user_links = cfg.get("user_links", [])
    if user_link and user_link.strip().startswith("http"):
        cfg["user_links"] = [user_link.strip()] + orig_user_links

    ban_tin.scan(date_str, scan_json)

    if not scan_json.exists():
        raise RuntimeError("Quét tin thất bại, không có file dữ liệu.")

    candidates = json.loads(scan_json.read_text(encoding="utf-8"))
    print(f"  ✓ Đã tìm thấy {len(candidates)} bài viết tiềm năng.")

    # Lọc bài phù hợp
    matched = [c for c in candidates if c.get("from_user") or c.get("region_match")]
    if len(matched) < 4:
        matched = candidates[:15]
    else:
        matched = matched[:15]

    print(f"  ✓ Lựa chọn {len(matched)} bài nổi bật nhất để lấy nội dung chi tiết...")
    for idx, c in enumerate(matched, 1):
        print(f"    · ({idx}) {c['source']}: {c['title'][:70]}")
        snippet = fetch_article_snippet(c["url"])
        c["snippet"] = snippet

    # 2. GỌI GEMINI VIẾT KỊCH BẢN
    print("\n✍️ 2/5 Gemini AI đang phân tích và viết kịch bản chuẩn format...")
    
    prompt = f"""
Bạn là biên tập viên tin tức video của kênh TikTok "@quynhon24hqua" (Kênh chính thức: Quy Nhơn 24h Qua).
Hôm nay là: {session_title} ngày {date_display} ({date_str}).

Dưới đây là danh sách các tin tức trong 24 giờ qua:
{json.dumps(matched, ensure_ascii=False, indent=2)}

YÊU CẦU NỘI DUNG & BIÊN TẬP (BẮT BUỘC TUÂN THỦ 100%):
1. Chọn đúng 6 đến 7 tin mạnh nhất, ưu tiên tin thành phố Quy Nhơn và tỉnh Gia Lai. Tin có "from_user": true BẮT BUỘC giữ.
2. Không bịa số liệu, tên, thời gian. Mọi chi tiết phải lấy từ bài gốc hoặc snippet.
3. Không nêu thông tin cá nhân (PII) của nạn nhân, người liên quan vụ việc hình sự/tai nạn (chỉ viết tắt tên vd: N.Y., 14 tuổi, hoặc tài xế N.).
4. Mỗi tin ("text") viết lại súc tích, hấp dẫn, dễ hiểu trong khoảng 90 đến 180 ký tự (chuẩn đọc trong 7 giây).
5. "cover": kicker là "BẢN TIN {session_title.upper()}", title là "Tin tức Quy Nhơn", subtitle là "{session_title} {date_display}", teaser tóm tắt 2 tin nổi bật nhất cách nhau bằng dấu chấm phẩy.
6. "caption":
   - "tiktok": tóm tắt giật tít 2 tin đầu; liệt kê ngắn các tin còn lại; trích tên các báo; BẮT BUỘC kết thúc bằng đúng 6 hashtag: #quynhon #tinquynhon #gialai #binhdinh #tintuc #quynhon24hqua
7. Hashtags BẮT BUỘC đúng 6 thẻ:
   ["#quynhon", "#tinquynhon", "#gialai", "#binhdinh", "#tintuc", "#quynhon24hqua"]
8. Xuất ra ĐÚNG 1 ĐỐI TƯỢNG JSON theo cấu trúc sau (không kèm giải thích markdown ngoài json):

{{
  "type": "digest",
  "output": "video",
  "date": "{date_str}",
  "region": "Quy Nhơn",
  "province": "Gia Lai",
  "chip": "",
  "cover": {{
    "kicker": "BẢN TIN {session_title.upper()}",
    "title": "Tin tức Quy Nhơn",
    "subtitle": "{session_title} {date_display}",
    "teaser": "<tóm tắt 2 tin nóng>",
    "image": "item:1"
  }},
  "items": [
    {{
      "category": "khu-vuc",
      "text": "<nội dung 90-180 ký tự>",
      "ai_prompt": "<mô tả cảnh bằng tiếng Anh phục vụ ảnh minh hoạ nếu thiếu>",
      "source": "<link bài báo gốc>",
      "source_name": "<tên báo>",
      "published": "<ISO 8601 published time từ bài gốc>"
    }}
  ],
  "outro": "Follow để nắm bắt tin tức Quy Nhơn nhé",
  "pin_comment": "<câu hỏi thảo luận tương tác kết thúc bằng: Nhà bạn có tin? Nhắn kênh, kênh đưa!>",
  "caption": {{
    "tiktok": "<caption đầy đủ kèm 6 hashtag>",
    "youtube": "Tin Quy Nhơn {session_title.lower()} {date_display}: ... #Shorts",
    "facebook": "📍 QUY NHƠN 24H QUA – BẢN TIN {session_title.upper()} {date_display}..."
  }},
  "hashtags": [
    "#quynhon",
    "#tinquynhon",
    "#gialai",
    "#binhdinh",
    "#tintuc",
    "#quynhon24hqua"
  ],
  "needs_review": [
    "<danh sách các điểm đã kiểm tra hoặc lưu ý>"
  ]
}}
"""
    raw_json = call_gemini(api_key, prompt)
    
    # Parse json
    # Làm sạch markdown nếu có ```json ... ```
    m = re.search(r'```json\s*(.*?)\s*```', raw_json, re.DOTALL)
    if m:
        raw_json = m.group(1)
    else:
        raw_json = raw_json.strip()

    bulletin_data = json.loads(raw_json)
    
    # Kiểm tra JSON hợp lệ
    errors, warnings = ban_tin.validate(bulletin_data)
    for w in warnings:
        print("  ⚠", w)
    if errors:
        print("  ✗ Một số lỗi validation:", errors)
        # Tự sửa lỗi ngày tháng nếu cần
        bulletin_data["date"] = date_str
        for it in bulletin_data.get("items", []):
            if not it.get("published"):
                it["published"] = f"{date_str}T{hour:02d}:00:00+07:00"

    inbox_file = ROOT_DIR / "inbox" / f"{date_str.replace('-', '')}-quy-nhon-{session_type}.json"
    inbox_file.parent.mkdir(parents=True, exist_ok=True)
    inbox_file.write_text(json.dumps(bulletin_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✓ Kịch bản đã lưu: {inbox_file.name} ({len(bulletin_data['items'])} tin)")

    # 3. RENDER VIDEO
    print("\n🎬 3/5 Đang render video HD 1080x1920 (HyperFrames)...")
    out_dir = ROOT_DIR / "data" / "output" / f"{inbox_file.stem}-video"
    out_dir.mkdir(parents=True, exist_ok=True)
    proj_dir = out_dir / "_project"
    
    ban_tin.build_project(bulletin_data, proj_dir)
    
    stamp = now_vn.strftime("%Hh%M")
    for old in out_dir.glob("*.mp4"):
        old.unlink()
    mp4_file = out_dir / f"{inbox_file.stem}_{stamp}.mp4"
    
    # Gọi HyperFrames render
    cmd = ban_tin.hf("render", "-o", str(mp4_file))
    print(f"  · Chạy: {' '.join(cmd)}")
    ban_tin.run(cmd, proj_dir)
    ban_tin.write_caption(bulletin_data, out_dir)
    
    print(f"  ✓ Render video thành công: {mp4_file.name} ({mp4_file.stat().st_size / 1024 / 1024:.1f} MB)")

    # 4. SAO CHÉP VÀO GOOGLE DRIVE
    print("\n☁️ 4/5 Đang đồng bộ video sang Google Drive...")
    drive_saved_video = None
    if drive_dir:
        drive_path = Path(drive_dir)
        if drive_path.exists():
            dest_video = drive_path / mp4_file.name
            dest_caption = drive_path / f"{inbox_file.stem}_caption.txt"
            
            import shutil
            shutil.copy2(mp4_file, dest_video)
            shutil.copy2(out_dir / "caption.txt", dest_caption)
            drive_saved_video = dest_video
            print(f"  🎉 ĐÃ LƯU THÀNH CÔNG VÀO GOOGLE DRIVE: {dest_video}")
        else:
            print(f"  ⚠ Thư mục Google Drive '{drive_dir}' chưa được mount hoặc không tồn tại.")
    else:
        print("  · Bỏ qua sao chép Drive (không truyền đường dẫn Drive).")

    # 5. HOÀN THÀNH & XUẤT CAPTION
    print("\n" + "=" * 60)
    print("🎉 TẤT CẢ ĐÃ HOÀN TẤT!")
    print(f"📁 Video: {mp4_file}")
    if drive_saved_video:
        print(f"📱 Google Drive: {drive_saved_video}")
    print("=" * 60)
    
    caption_txt = (out_dir / "caption.txt").read_text(encoding="utf-8")
    print("\n📋 CAPTION ĐĂNG TIKTOK:\n")
    m_cap = re.search(r'===\s*TIKTOK\s*===\s*\n(.*?)(?=\n===|\Z)', caption_txt, re.DOTALL)
    final_cap = m_cap.group(1).strip() if m_cap else caption_txt
    print(final_cap)
    print("\n" + "=" * 60)
    
    return {
        "video": str(mp4_file),
        "drive_video": str(drive_saved_video) if drive_saved_video else None,
        "caption": final_cap
    }

import base64
DEFAULT_KEY = base64.b64decode('QVEuQWI4Uk42Slp2SFRCRXd0aXU5TWYwMVpFS1FscjRCVVBzUXppU0lxVXFRcVBNbFFOSnc=').decode()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline tạo bản tin tự động (Colab hoặc Laptop/PC)")
    parser.add_argument("--api-key", default=DEFAULT_KEY, help="Google Gemini API Key (mặc định đã cấu hình sẵn)")
    parser.add_argument("--link", default="", help="Link bài báo nóng cần đưa thêm (tuỳ chọn)")
    parser.add_argument("--drive-dir", default="", help="Thư mục Google Drive để lưu video")
    parser.add_argument("--session", default="", choices=["", "chieu", "sang"], help="Buổi sáng hoặc chiều")

    args = parser.parse_args()
    run_pipeline(
        api_key=args.api_key or DEFAULT_KEY,
        user_link=args.link,
        drive_dir=args.drive_dir,
        session_type=args.session
    )
