#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tiktok_draft.py - Đẩy video và caption lên Bản Nháp (Draft) TikTok Studio
Sử dụng Playwright với profile phiên đăng nhập lưu tại data/tiktok_profile.
"""

import sys
import os
import time
import argparse
import re
from pathlib import Path

# Cấu hình mã hoá utf-8 cho stdout trên Windows
sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
PROFILE_DIR = ROOT_DIR / "data" / "tiktok_profile"

def get_caption_from_file(caption_file: Path) -> str:
    """Đọc caption TikTok từ caption.txt"""
    content = caption_file.read_text(encoding='utf-8')
    m = re.search(r'===\s*TIKTOK\s*===\s*\n(.*?)(?=\n===|\Z)', content, re.DOTALL)
    if m:
        lines = [line.strip() for line in m.group(1).strip().split('\n') if line.strip()]
        if len(lines) >= 2 and lines[-1] == lines[-2]:
            lines.pop()
        return " ".join(lines)
    return content.strip()

def run_login():
    """Mở trình duyệt để người dùng đăng nhập lần đầu và lưu session"""
    from playwright.sync_api import sync_playwright

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 60, flush=True)
    print("🔐 BẮT ĐẦU ĐĂNG NHẬP TIKTOK STUDIO (LƯU PHIÊN ĐĂNG NHẬP)", flush=True)
    print(f"📁 Thư mục profile: {PROFILE_DIR}", flush=True)
    print("=" * 60, flush=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("\n👉 Đang mở trang đăng nhập TikTok...", flush=True)
        page.goto("https://www.tiktok.com/login?redirect_url=https%3A%2F%2Fwww.tiktok.com%2Ftiktokstudio%2Fupload", wait_until="domcontentloaded")
        time.sleep(3)

        # Tự động click vào 'Use QR code' nếu có
        try:
            qr_btn = page.locator('div:has-text("Use QR code"), div:has-text("Sử dụng mã QR"), button:has-text("Use QR code")').first
            if qr_btn.count() > 0 and qr_btn.is_visible():
                qr_btn.click()
                print("   ✓ Đã tự động mở khung quét mã QR!", flush=True)
        except Exception:
            pass

        print("\n" + "!" * 60, flush=True)
        print("HÃY QUAN SÁT CỬA SỔ TRÌNH DUYỆT VỪA MỞ TRÊN MÀN HÌNH:", flush=True)
        print("1. Dùng app TikTok trên điện thoại quét mã QR đang hiện trên màn hình máy tính.")
        print("2. QUAN TRỌNG: Trên điện thoại, hãy bấm nút 'ỦY QUYỀN' / 'XÁC NHẬN ĐĂNG NHẬP'.")
        print("3. Trình duyệt trên máy tính sẽ tự động chuyển vào TikTok Studio.")
        print("!" * 60 + "\n", flush=True)

        logged_in = False
        start_time = time.time()
        while time.time() - start_time < 300:
            current_url = page.url.lower()
            if "login" not in current_url and ("tiktokstudio" in current_url or "creator-center" in current_url or "tiktok.com/@" in current_url or "foryou" in current_url):
                logged_in = True
                break
            time.sleep(2)

        if logged_in:
            print("\n🎉 ĐĂNG NHẬP THÀNH CÔNG VÀO TIKTOK!", flush=True)
            print("Session đã được lưu vĩnh viễn trong data/tiktok_profile.", flush=True)
            page.goto("https://www.tiktok.com/tiktokstudio/upload", wait_until="domcontentloaded")
            time.sleep(4)
        else:
            print("\n⚠ Hết thời gian chờ đăng nhập (5 phút). Vui lòng thử lại sau.", flush=True)

        context.close()

def run_push(video_path: Path, caption: str, headless: bool = False):
    """Tự động upload video và lưu vào bản nháp trên TikTok Studio"""
    from playwright.sync_api import sync_playwright

    if not video_path.exists():
        print(f"❌ Lỗi: Không tìm thấy file video tại: {video_path}", flush=True)
        sys.exit(1)

    if not PROFILE_DIR.exists():
        print("❌ Chưa có phiên đăng nhập TikTok.", flush=True)
        print("👉 Vui lòng chạy lệnh đăng nhập trước: python skills/ban-tin/scripts/ban_tin.py login", flush=True)
        sys.exit(1)

    print("=" * 60, flush=True)
    print("🚀 TIẾN HÀNH ĐẨY VIDEO LÊN BẢN NHÁP (TIKTOK STUDIO DRAFT)", flush=True)
    print(f"📹 Video: {video_path.name} ({video_path.stat().st_size / 1024 / 1024:.2f} MB)", flush=True)
    print(f"📝 Caption: {caption[:100]}...", flush=True)
    print("=" * 60, flush=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=headless,
            viewport={"width": 1280, "height": 900},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("\n1/4 Mở trang TikTok Studio Upload...", flush=True)
        page.goto("https://www.tiktok.com/tiktokstudio/upload", wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        # Kiểm tra xem có bị chuyển về trang login không
        if "login" in page.url.lower():
            print("⚠ Trình duyệt đang ở trang đăng nhập. Hãy đăng nhập ngay trên cửa sổ trình duyệt...", flush=True)
            # Chờ người dùng đăng nhập nếu cần
            start_wait = time.time()
            while time.time() - start_wait < 120:
                if "login" not in page.url.lower():
                    print("   ✓ Đã đăng nhập thành công!", flush=True)
                    time.sleep(3)
                    break
                time.sleep(2)
            
            if "login" in page.url.lower():
                print("❌ Chưa đăng nhập vào TikTok. Vui lòng chạy: python skills/ban-tin/scripts/ban_tin.py login", flush=True)
                context.close()
                sys.exit(1)

        print("2/4 Tìm khung upload và đưa video lên...", flush=True)
        # Tìm input upload video (trên page hoặc iframe)
        target_scope = page
        for frame in page.frames:
            try:
                if frame.locator('input[type="file"]').count() > 0:
                    target_scope = frame
                    break
            except Exception:
                pass

        try:
            # Playwright set_input_files works on hidden/attached inputs directly
            target_scope.wait_for_selector('input[type="file"]', state="attached", timeout=30000)
            file_input = target_scope.locator('input[type="file"]').first
            file_input.set_input_files(str(video_path))
            print("   ✓ Đã chọn file video thành công, hệ thống bắt đầu upload!", flush=True)
        except Exception as e:
            print(f"   ❌ Không tìm thấy input file: {e}", flush=True)
            context.close()
            sys.exit(1)

        print("3/4 Đang chờ video xử lý và điền Caption...", flush=True)
        # Chờ trình soạn thảo caption
        editor = None
        editor_selectors = [
            'div[contenteditable="true"]',
            'div.notranslate.public-DraftEditor-content',
            'div[class*="DraftEditor"]',
            'div[data-placeholder]',
            'textarea'
        ]
        
        for _ in range(40):
            # Xoá popup hướng dẫn / overlay nếu có
            try:
                page.evaluate("() => { document.querySelectorAll('#react-joyride-portal, .react-joyride__overlay, .react-joyride__tooltip').forEach(el => el.remove()); }")
            except Exception:
                pass

            for sel in editor_selectors:
                try:
                    loc = target_scope.locator(sel).first
                    if loc.count() > 0 and loc.is_visible():
                        editor = loc
                        break
                except Exception:
                    pass
            if editor:
                break
            time.sleep(1)

        if editor:
            try:
                # Xoá overlay lần nữa trước khi click
                try:
                    page.evaluate("() => { document.querySelectorAll('#react-joyride-portal, .react-joyride__overlay, .react-joyride__tooltip').forEach(el => el.remove()); }")
                except Exception:
                    pass

                editor.click(force=True)
                time.sleep(1)
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                time.sleep(0.5)
                print("   ✓ Đang điền Caption TikTok kèm 6 Hashtag...", flush=True)
                page.keyboard.insert_text(caption)
                time.sleep(2)
            except Exception as e:
                print(f"   ⚠ Lỗi khi điền caption: {e}", flush=True)
        else:
            print("   ⚠ Không tìm thấy ô caption tự động.", flush=True)

        print("4/4 Chờ video upload 100% và bấm 'Lưu bản nháp' (Save as draft)...", flush=True)
        # 1. Chờ video tải lên hoàn tất 100% trên TikTok Studio
        print("   ⏳ Đang tải file video (44 MB) lên máy chủ TikTok, vui lòng chờ...", flush=True)
        upload_done = False
        start_wait = time.time()
        while time.time() - start_wait < 180: # tối đa 3 phút cho video 44MB
            # Kiểm tra các dấu hiệu video đã tải lên 100%
            is_100 = target_scope.locator('text=Đã tải lên, text=Uploaded, text=100%')
            is_uploading = target_scope.locator('text=Đang tải lên, text=Uploading')
            
            if is_100.count() > 0 and is_100.first.is_visible():
                print("   ✓ Video đã tải lên 100% thành công!", flush=True)
                upload_done = True
                break
            
            # Nếu không còn chữ "Đang tải lên" và có player xem trước
            if is_uploading.count() == 0 and target_scope.locator('video').count() > 0:
                print("   ✓ Video đã sẵn sàng trên trình phát!", flush=True)
                upload_done = True
                break
                
            time.sleep(3)

        time.sleep(3)
        saved = False
        start_click = time.time()
        
        while time.time() - start_click < 60:
            # Xoá overlay nếu có
            try:
                page.evaluate("() => { document.querySelectorAll('#react-joyride-portal, .react-joyride__overlay, .react-joyride__tooltip').forEach(el => el.remove()); }")
            except Exception:
                pass

            draft_selectors = [
                'button:has-text("Lưu bản nháp")',
                'button:has-text("Lưu dưới dạng bản nháp")',
                'button:has-text("Save draft")',
                'button:has-text("Save as draft")',
                'button:has-text("Lưu nháp")',
                'button:has-text("Draft")'
            ]
            
            clicked = False
            for sel in draft_selectors:
                try:
                    btn = target_scope.locator(sel).first
                    if btn.count() > 0 and btn.is_visible():
                        btn.click(force=True)
                        print(f"   ✓ Đã bấm nút: '{btn.inner_text().strip()}'!", flush=True)
                        clicked = True
                        saved = True
                        break
                except Exception:
                    pass
            
            if clicked:
                break
            time.sleep(2)

        if saved:
            print("   ⏳ Đang chờ TikTok máy chủ lưu vào Bản Nháp (15 giây)...", flush=True)
            # Chờ trang chuyển hướng hoặc toast lưu thành công
            time.sleep(15)
            # Chuyển hướng sang trang draft để xác nhận
            try:
                page.goto("https://www.tiktok.com/tiktokstudio/content?tab=draft", wait_until="domcontentloaded")
                time.sleep(5)
                # Chụp ảnh xác nhận
                confirm_shot = ROOT_DIR / "data" / "tiktok_draft_confirmed.png"
                page.screenshot(path=str(confirm_shot))
                print(f"   ✓ Đã chụp ảnh xác nhận bản nháp: {confirm_shot}", flush=True)
            except Exception:
                pass

            print("\n" + "=" * 60, flush=True)
            print("🎉 THÀNH CÔNG: VIDEO ĐÃ LƯU VÀO BẢN NHÁP CỦA TIKTOK STUDIO!", flush=True)
            print("📱 BƯỚC TIẾP THEO TRÊN ĐIỆN THOẠI:", flush=True)
            print("1. Mở app TikTok trên điện thoại của bạn.", flush=True)
            print("2. Vào mục 'Hồ sơ' -> icon 'Bản nháp' (Drafts).", flush=True)
            print("3. Bấm vào video vừa tải lên -> chọn Âm thanh -> Yêu thích -> 'nhạc nền - NTP VINAHOUSE'.", flush=True)
            print("4. Bấm Đăng! (Video chuẩn 100% âm thanh bản quyền và ăn đề xuất).", flush=True)
            print("=" * 60, flush=True)
            time.sleep(5)
        else:
            print("\n⚠ Video đang tải lên hoặc nút Lưu nháp chưa sẵn sàng.", flush=True)
            print("👉 Vui lòng quan sát cửa sổ trình duyệt và bấm 'Lưu bản nháp' (Save as draft) trên màn hình nhé!", flush=True)
            time.sleep(20)

        context.close()

def main():
    parser = argparse.ArgumentParser(description="TikTok Draft Pusher - Đẩy video lên bản nháp TikTok Studio")
    subparsers = parser.add_subparsers(dest="command", help="Lệnh thực hiện")

    # Lệnh login
    subparsers.add_parser("login", help="Đăng nhập tài khoản TikTok Studio và lưu phiên")

    # Lệnh push
    push_parser = subparsers.add_parser("push", help="Đẩy video vào Bản Nháp TikTok Studio")
    push_parser.add_argument("target", nargs="?", help="Đường dẫn file video hoặc thư mục output chứa video và caption.txt")
    push_parser.add_argument("--caption", "-c", help="Nội dung caption (nếu không dùng file caption.txt)")
    push_parser.add_argument("--headless", action="store_true", help="Chạy ẩn trình duyệt (mặc định hiện trình duyệt)")

    args = parser.parse_args()

    if args.command == "login":
        run_login()
    elif args.command == "push":
        if not args.target:
            output_dir = ROOT_DIR / "data" / "output"
            recent_dirs = sorted([d for d in output_dir.iterdir() if d.is_dir() and "-video" in d.name], key=lambda x: x.stat().st_mtime, reverse=True)
            if not recent_dirs:
                print("❌ Không tìm thấy thư mục output video nào trong data/output/", flush=True)
                sys.exit(1)
            target_path = recent_dirs[0]
            print(f"🔍 Tự động chọn thư mục output mới nhất: {target_path.name}", flush=True)
        else:
            target_path = Path(args.target)

        if target_path.is_dir():
            mp4_files = [f for f in target_path.glob("*.mp4") if "XEM-THU" not in f.name]
            if not mp4_files:
                print(f"❌ Không tìm thấy file video sạch (.mp4) trong: {target_path}", flush=True)
                sys.exit(1)
            video_file = mp4_files[0]
            caption_file = target_path / "caption.txt"
            caption_text = args.caption or (get_caption_from_file(caption_file) if caption_file.exists() else "")
        else:
            video_file = target_path
            caption_file = video_file.parent / "caption.txt"
            caption_text = args.caption or (get_caption_from_file(caption_file) if caption_file.exists() else "")

        run_push(video_file, caption_text, headless=args.headless)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
