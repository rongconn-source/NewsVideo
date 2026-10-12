#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zalo_send.py - Tự động gửi video và caption vào 'Cloud của tôi' (My Cloud) trên Zalo Web.
Sử dụng Playwright với profile lưu tại data/zalo_profile.
"""

import sys
import os
import time
import argparse
import re
from pathlib import Path

# Cấu hình utf-8 cho stdout trên Windows
sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
PROFILE_DIR = ROOT_DIR / "data" / "zalo_profile"

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
    """Mở trình duyệt để người dùng quét mã QR đăng nhập Zalo lần đầu"""
    from playwright.sync_api import sync_playwright

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 60, flush=True)
    print("🔐 BẮT ĐẦU ĐĂNG NHẬP ZALO WEB (LƯU PHIÊN ĐĂNG NHẬP)", flush=True)
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

        print("\n👉 Đang mở Zalo Web (https://chat.zalo.me)...", flush=True)
        page.goto("https://chat.zalo.me", wait_until="domcontentloaded")

        print("\n" + "=" * 60, flush=True)
        print("📌 VUI LÒNG DÙNG APP ZALO TRÊN ĐIỆN THOẠI QUÉT MÃ QR ĐỂ ĐĂNG NHẬP!", flush=True)
        print("   (Sau khi quét xong và xác nhận trên điện thoại, Zalo sẽ vào giao diện chat)", flush=True)
        print("=" * 60 + "\n", flush=True)

        # Chờ đăng nhập thành công
        max_wait = 300  # 5 phút
        start_time = time.time()
        logged_in = False

        while time.time() - start_time < max_wait:
            time.sleep(3)
            # Kiểm tra xem đã vào giao diện chat chưa
            # Zalo Web khi đăng nhập thành công thường có nav-bar, main-tab hoặc ô tìm kiếm
            has_nav = page.locator('#main-tab, .nav-tabs, .chat-box, div[data-id="div_MainTab"]').count() > 0
            has_cloud = page.locator('text="Cloud của tôi", [title*="Cloud của tôi"]').count() > 0
            has_search = page.locator('input[placeholder*="Tìm kiếm"]').count() > 0

            if has_nav or has_cloud or has_search:
                print("🎉 ĐĂNG NHẬP ZALO THÀNH CÔNG!", flush=True)
                logged_in = True
                time.sleep(5)
                break

        if not logged_in:
            print("⚠️ Hết thời gian chờ đăng nhập (5 phút). Vui lòng thử lại sau.", flush=True)
        else:
            print("✅ Phiên đăng nhập Zalo đã được lưu tại:", PROFILE_DIR, flush=True)

        context.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zalo Web Automation")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("login", help="Đăng nhập Zalo Web và lưu phiên")
    subparsers.add_parser("send", help="Gửi video và caption vào Cloud của tôi")

    args = parser.parse_args()
    if args.command == "login":
        run_login()
    else:
        parser.print_help()
