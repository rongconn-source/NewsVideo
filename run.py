#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run.py - Chạy tạo bản tin tự động trên Laptop/PC
Chỉ cần gõ: python run.py
(Hoặc nhấp đúp file chay_ban_tin.bat)
"""

import sys
from pathlib import Path

# Cấu hình utf-8 cho console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT_DIR / "skills" / "ban-tin" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import colab_run

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Tạo bản tin Quy Nhơn 24h tự động trên máy tính")
    parser.add_argument("--link", default="", help="Link bài báo nóng muốn đưa thêm (tuỳ chọn)")
    parser.add_argument("--session", default="", choices=["", "chieu", "sang"], help="Buổi sáng hoặc chiều")

    args = parser.parse_args()
    colab_run.run_pipeline(
        api_key=colab_run.DEFAULT_KEY,
        user_link=args.link,
        session_type=args.session
    )
