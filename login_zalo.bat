@echo off
chcp 65001 >nul
title Đăng nhập Zalo Web - Lưu phiên
echo ============================================================
echo ĐANG MỞ ZALO WEB ĐỂ QUÉT MÃ QR...
echo ============================================================
python skills\ban-tin\scripts\zalo_send.py login
echo.
pause
