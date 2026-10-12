#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_colab_notebook.py - Tạo file QuyNhon24h_Video_Generator.ipynb chuẩn để chạy trên Google Colab
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent

notebook = {
    "nbformat": 4,
    "nbformat_minor": 0,
    "metadata": {
        "colab": {
            "name": "QuyNhon24h_Video_Generator.ipynb",
            "provenance": [],
            "include_colab_link": True
        },
        "kernelspec": {
            "name": "python3",
            "display_name": "Python 3"
        },
        "language_info": {
            "name": "python"
        }
    },
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {"id": "header_md"},
            "source": [
                "# 🎬 QUY NHƠN 24H QUA - TẠO BẢN TIN VIDEO TỰ ĐỘNG BẰNG 1-CLICK\n",
                "### 📱 Chạy trực tiếp từ điện thoại hoặc máy tính → Video HD tự động bay vào Google Drive!\n",
                "\n",
                "---\n",
                "**📌 Quy trình hoàn toàn tự động:**\n",
                "1. Bấm nút **Play ▶** bên trái ô chạy bên dưới.\n",
                "2. Chờ ~2 phút: Máy chủ Google tự quét tin tức 24h → AI viết bài → Render video 9:16 HD.\n",
                "3. Video và Caption sẽ **tự động lưu vào thư mục Google Drive: `BanTin_QuyNhon`** của bạn!\n",
                "4. Mở app **Google Drive** trên điện thoại → Tải video về thư viện ảnh → Đăng lên TikTok kèm nhạc nền **NTP VINAHOUSE**."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {
                "cellView": "form",
                "id": "run_pipeline_code"
            },
            "outputs": [],
            "source": [
                "#@title 🚀 BẤM NÚT NÀY ĐỂ TẠO BẢN TIN { display-mode: \"form\" }\n",
                "#@markdown ---\n",
                "#@markdown ### 📰 1. Link bài báo nóng (Tuỳ chọn):\n",
                "LINK_TIN_NONG = \"\" #@param {type:\"string\"}\n",
                "#@markdown *(Dán link bài báo bạn muốn bắt buộc đưa vào bản tin, nếu không có hãy để trống)*\n",
                "\n",
                "#@markdown ---\n",
                "#@markdown ### ☁️ 2. Tự động lưu vào Google Drive:\n",
                "LUU_VAO_GOOGLE_DRIVE = True #@param {type:\"boolean\"}\n",
                "THU_MUC_DRIVE = \"BanTin_QuyNhon\" #@param {type:\"string\"}\n",
                "\n",
                "#@markdown ---\n",
                "#@markdown ### 🔑 3. Google Gemini API Key (Đã gắn sẵn cho kênh, có thể để trống):\n",
                "GEMINI_API_KEY = \"\" #@param {type:\"string\"}\n",
                "#@markdown ---\n",
                "\n",
                "import os, sys, shutil, subprocess, base64\n",
                "from pathlib import Path\n",
                "\n",
                "# 1. Lấy API Key (mặc định đã cấu hình sẵn cho kênh Quy Nhơn 24h Qua)\n",
                "DEFAULT_KEY = base64.b64decode('QVEuQWI4Uk42Slp2SFRCRXd0aXU5TWYwMVpFS1FscjRCVVBzUXppU0lxVXFRcVBNbFFOSnc=').decode()\n",
                "api_key = GEMINI_API_KEY.strip()\n",
                "if not api_key:\n",
                "    try:\n",
                "        from google.colab import userdata\n",
                "        api_key = userdata.get('GEMINI_API_KEY')\n",
                "    except Exception:\n",
                "        pass\n",
                "if not api_key:\n",
                "    api_key = DEFAULT_KEY\n",
                "\n",
                "# 2. Kết nối Google Drive\n",
                "drive_dir_path = \"\"\n",
                "if LUU_VAO_GOOGLE_DRIVE:\n",
                "    print(\"☁️ Đang kết nối Google Drive...\")\n",
                "    try:\n",
                "        from google.colab import drive\n",
                "        drive.mount('/content/drive')\n",
                "        drive_dir_path = f\"/content/drive/MyDrive/{THU_MUC_DRIVE}\"\n",
                "        Path(drive_dir_path).mkdir(parents=True, exist_ok=True)\n",
                "        print(f\"  ✓ Đã kết nối Drive: {drive_dir_path}\")\n",
                "    except Exception as e:\n",
                "        print(f\"  ⚠ Không thể kết nối Drive: {e}. Video sẽ chỉ lưu tạm trong Colab.\")\n",
                "\n",
                "# 3. Tải hoặc cập nhật mã nguồn dự án\n",
                "print(\"\\n📦 Đang chuẩn bị mã nguồn dự án...\")\n",
                "if not Path(\"/content/NewsVideo\").exists():\n",
                "    !git clone https://github.com/rongconn-source/NewsVideo.git /content/NewsVideo\n",
                "else:\n",
                "    !cd /content/NewsVideo && git pull\n",
                "\n",
                "# 4. Cài đặt các thư viện cần thiết & Cập nhật Node.js 22 & Thư viện Chromium\n",
                "print(\"\\n⚙️ Đang chuẩn bị môi trường Node.js 22 & Thư viện Chromium...\")\n",
                "!if [ $(node -v | cut -d'.' -f1 | tr -d 'v') -lt 22 ]; then \\\n",
                "    echo \"  · Đang nâng cấp Node.js lên phiên bản 22 (yêu cầu của HyperFrames)...\"; \\\n",
                "    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - > /dev/null 2>&1; \\\n",
                "    apt-get install -y nodejs > /dev/null 2>&1; \\\n",
                "    ln -sf /usr/bin/node /tools/node/bin/node 2>/dev/null || true; \\\n",
                "    ln -sf /usr/bin/npx /tools/node/bin/npx 2>/dev/null || true; \\\n",
                "    ln -sf /usr/bin/npm /tools/node/bin/npm 2>/dev/null || true; \\\n",
                "    echo \"  ✓ Node.js hiện tại: $(node -v)\"; \\\n",
                "fi\n",
                "print(\"  · Cài đặt thư viện đồ họa hệ thống cho Chromium...\")\n",
                "!apt-get update -qq > /dev/null 2>&1 && apt-get install -y -qq \\\n",
                "    libnss3 libnspr4 libatk1.0-0* libatk-bridge2.0-0* libcups2 libdrm2 \\\n",
                "    libxkbcommon0 libatspi* libxcomposite1 libxdamage1 libxfixes3 \\\n",
                "    libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2* > /dev/null 2>&1\n",
                "!pip install -q requests beautifulsoup4\n",
                "\n",
                "# 5. Chạy pipeline tạo video\n",
                "print(\"\\n🎬 ĐANG TẠO BẢN TIN VÀ RENDER VIDEO HD...\")\n",
                "cmd = [\n",
                "    sys.executable,\n",
                "    \"/content/NewsVideo/skills/ban-tin/scripts/colab_run.py\",\n",
                "    \"--api-key\", api_key\n",
                "]\n",
                "if LINK_TIN_NONG.strip():\n",
                "    cmd.extend([\"--link\", LINK_TIN_NONG.strip()])\n",
                "if drive_dir_path:\n",
                "    cmd.extend([\"--drive-dir\", drive_dir_path])\n",
                "\n",
                "my_env = os.environ.copy()\n",
                "my_env['PATH'] = f\"/usr/bin:/usr/local/bin:{my_env.get('PATH', '')}\"\n",
                "p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=my_env)\n",
                "for line in p.stdout:\n",
                "    print(line, end=\"\")\n",
                "p.wait()\n",
                "\n",
                "if p.returncode != 0:\n",
                "    print(f\"\\n❌ Có lỗi xảy ra trong quá trình chạy (mã lỗi {p.returncode})\")\n",
                "else:\n",
                "    print(\"\\n🎉 HOÀN THÀNH XUẤT SẮC! Video đã nằm trong Google Drive của bạn.\")\n"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {
                "cellView": "form",
                "id": "preview_and_download_code"
            },
            "outputs": [],
            "source": [
                "#@title 📱 XEM TRƯỚC VIDEO & SAO CHÉP CAPTION { display-mode: \"form\" }\n",
                "import os, glob, re\n",
                "from pathlib import Path\n",
                "from IPython.display import HTML, display\n",
                "\n",
                "videos = sorted(glob.glob(\"/content/NewsVideo/data/output/*/*.mp4\"), key=os.path.getmtime, reverse=True)\n",
                "captions = sorted(glob.glob(\"/content/NewsVideo/data/output/*/caption.txt\"), key=os.path.getmtime, reverse=True)\n",
                "\n",
                "if videos:\n",
                "    latest_video = videos[0]\n",
                "    cap_text = Path(captions[0]).read_text(encoding=\"utf-8\") if captions else \"\"\n",
                "    m = re.search(r'===\\s*TIKTOK\\s*===\\s*\\n(.*?)(?=\\n===|\\Z)', cap_text, re.DOTALL)\n",
                "    tiktok_cap = m.group(1).strip() if m else cap_text\n",
                "    file_size_mb = os.path.getsize(latest_video) / 1024 / 1024\n",
                "    \n",
                "    html_code = f\"\"\"\n",
                "    <div style=\"background: #111827; padding: 20px; border-radius: 12px; color: white; max-width: 480px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;\">\n",
                "        <h3 style=\"color: #F59E0B; margin-top: 0;\">🎉 Video Bản Tin Đã Sẵn Sàng!</h3>\n",
                "        <p style=\"font-size: 14px; color: #9CA3AF; margin-bottom: 12px;\">\n",
                "            📁 File: <b style=\"color: #E5E7EB;\">{os.path.basename(latest_video)}</b> ({file_size_mb:.1f} MB)\n",
                "        </p>\n",
                "        <video width=\"100%\" height=\"420\" controls style=\"border-radius: 8px; background: black; margin-bottom: 15px;\">\n",
                "            <source src=\"{latest_video}\" type=\"video/mp4\">\n",
                "            Trình duyệt không hỗ trợ xem trực tiếp.\n",
                "        </video>\n",
                "        <h4 style=\"margin-bottom: 6px; color: #10B981;\">📋 Caption TikTok:</h4>\n",
                "        <textarea id=\"capBox\" style=\"width: 100%; height: 110px; background: #1F2937; color: white; border: 1px solid #374151; border-radius: 6px; padding: 8px; font-size: 13px; resize: none; box-sizing: border-box;\" readonly>{tiktok_cap}</textarea>\n",
                "        <br>\n",
                "        <button onclick=\"navigator.clipboard.writeText(document.getElementById('capBox').value); alert('Đã sao chép Caption TikTok!');\" style=\"margin-top: 10px; background: #2563EB; color: white; border: none; padding: 12px 18px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; font-size: 14px;\">\n",
                "            📋 SAO CHÉP CAPTION TIKTOK\n",
                "        </button>\n",
                "    </div>\n",
                "    \"\"\"\n",
                "    display(HTML(html_code))\n",
                "else:\n",
                "    print(\"Chưa thấy video nào. Hãy chạy ô tạo bản tin ở trên trước nhé!\")\n"
            ]
        }
    ]
}

out_file = ROOT_DIR / "QuyNhon24h_Video_Generator.ipynb"
out_file.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Đã tạo thành công file Colab: {out_file}")
