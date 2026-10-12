@echo off
chcp 65001 >nul
title Đẩy video vào Bản Nháp TikTok Studio
echo ============================================================
echo ĐANG ĐẨY VIDEO MỚI NHẤT LÊN BẢN NHÁP TIKTOK STUDIO...
echo ============================================================
python skills\ban-tin\scripts\ban_tin.py push
echo.
pause
