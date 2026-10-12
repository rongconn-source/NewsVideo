@echo off
chcp 65001 >nul
title Đăng nhập TikTok Studio - Lưu phiên
echo ============================================================
echo ĐANG MỞ TRÌNH DUYỆT ĐĂNG NHẬP TIKTOK...
echo ============================================================
python skills\ban-tin\scripts\ban_tin.py login
echo.
pause
