"""Đẩy bộ ảnh bản tin lên TikTok Studio bằng Playwright – DỪNG trước nút Đăng.

Script chỉ: mở TikTok Studio (tab Ảnh) → tải ảnh 01…NN → điền Tiêu đề + Caption + 6 hashtag
→ mở mục chọn nhạc → để nguyên cửa sổ cho người dùng tự chọn nhạc và tự bấm Đăng.
Script KHÔNG BAO GIỜ bấm nút Post / Đăng.

Cách dùng:
  # Lần đầu: mở cửa sổ để tự đăng nhập TikTok (phiên lưu ở data/browser-profile/)
  python skills/ban-tin/scripts/tiktok_upload.py --login

  # Đẩy bản tin (truyền thư mục kết quả hoặc file JSON trong inbox)
  python skills/ban-tin/scripts/tiktok_upload.py data/output/20261125-quy-nhon-trua-anh
  python skills/ban-tin/scripts/tiktok_upload.py skills/ban-tin/inbox/20261125-quy-nhon-trua.json

Cài đặt (1 lần): pip install playwright  (dùng Chrome có sẵn; không có thì: playwright install chromium)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[3]
PROFILE_DIR = ROOT / "data" / "browser-profile"
OUTPUT_DIR = ROOT / "data" / "output"
UPLOAD_URL = "https://www.tiktok.com/tiktokstudio/upload?tab=photo"
HASHTAGS = "#quynhon #tinquynhon #gialai #binhdinh #tintuc #quynhon24hqua"
TITLE_MAX = 90


def resolve_output(arg: str) -> tuple[Path, dict | None]:
    """Nhận thư mục kết quả hoặc file JSON kịch bản → (thư mục kết quả, dữ liệu JSON nếu có)."""
    p = Path(arg)
    if not p.is_absolute():
        p = (ROOT / p) if not p.exists() else p.resolve()
    if p.suffix == ".json":
        data = json.loads(p.read_text(encoding="utf-8"))
        out = OUTPUT_DIR / f"{p.stem}-anh"
        return out, data
    data = None
    inbox = ROOT / "skills" / "ban-tin" / "inbox" / (p.name.removesuffix("-anh") + ".json")
    if inbox.exists():
        data = json.loads(inbox.read_text(encoding="utf-8"))
    return p, data


def read_tiktok_caption(out: Path) -> str:
    """Lấy phần === TIKTOK === trong caption.txt (gồm cả dòng hashtag)."""
    text = (out / "caption.txt").read_text(encoding="utf-8")
    m = re.search(r"=== TIKTOK ===\s*\n(.*?)(?:\n\s*\n|\n===|\Z)", text, re.S)
    if not m:
        sys.exit("Không tìm thấy phần '=== TIKTOK ===' trong caption.txt")
    caption = m.group(1).strip()
    if HASHTAGS not in caption:
        caption = caption.rstrip() + "\n" + HASHTAGS
    return caption


def make_title(data: dict | None, caption: str) -> str:
    """Tiêu đề ≤ 90 ký tự: ưu tiên trường tiktok_title, rồi title, rồi câu đầu caption."""
    raw = ""
    if data:
        raw = data.get("tiktok_title") or data.get("title") or ""
    if not raw:
        raw = re.split(r"(?<=[!?.])\s", caption, maxsplit=1)[0]
    raw = re.sub(r"\s+", " ", raw).strip()
    if len(raw) <= TITLE_MAX:
        return raw
    cut = raw[:TITLE_MAX]
    cut = cut[: cut.rfind(" ")] if " " in cut else cut
    return cut.rstrip(" ,;:–-")


def is_login_page(url: str) -> bool:
    return "login" in urlparse(url).path


def first_visible(page, selectors: list[str], timeout_ms: int = 120_000):
    """Chờ tới khi 1 trong các selector hiện ra; trả về locator đầu tiên tìm thấy."""
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        for sel in selectors:
            loc = page.locator(sel)
            for i in range(loc.count()):
                if loc.nth(i).is_visible():
                    return loc.nth(i)
        page.wait_for_timeout(500)
    return None


def launch(pw):
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    opts = dict(user_data_dir=str(PROFILE_DIR), headless=False, viewport=None,
                args=["--start-maximized"], locale="vi-VN")
    try:
        return pw.chromium.launch_persistent_context(channel="chrome", **opts)
    except Exception:
        return pw.chromium.launch_persistent_context(**opts)


def wait_until_closed(ctx):
    print("\n→ Cửa sổ để nguyên cho bạn. Đóng cửa sổ trình duyệt khi xong để kết thúc script.")
    try:
        while ctx.pages:
            ctx.pages[0].wait_for_timeout(1000)
    except Exception:
        pass


def do_login(pw):
    ctx = launch(pw)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://www.tiktok.com/login")
    print("Hãy tự đăng nhập TikTok trong cửa sổ vừa mở (script không nhập mật khẩu).")
    wait_until_closed(ctx)


def do_upload(pw, out: Path, data: dict | None, title_override: str | None):
    images = sorted(out.joinpath("anh").glob("*.png")) or sorted(out.joinpath("anh").glob("*.jpg"))
    if not images:
        sys.exit(f"Không thấy ảnh trong {out / 'anh'}")
    if len(images) > 35:
        sys.exit(f"{len(images)} ảnh – TikTok chỉ nhận tối đa 35 ảnh/bài")
    caption = read_tiktok_caption(out)
    title = title_override or make_title(data, caption)
    print(f"Ảnh: {len(images)} file ({images[0].name} → {images[-1].name})")
    print(f"Tiêu đề ({len(title)} ký tự): {title}")

    ctx = launch(pw)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto(UPLOAD_URL)

    # Chưa đăng nhập → TikTok chuyển sang trang login (URL login có chứa "tiktokstudio" trong
    # tham số redirect nên phải xét phần path, không xét cả URL)
    page.wait_for_timeout(3000)
    if is_login_page(page.url):
        print("Chưa đăng nhập. Hãy đăng nhập trong cửa sổ, script tự chạy tiếp khi vào được TikTok Studio…")
        while is_login_page(page.url) or not urlparse(page.url).path.startswith("/tiktokstudio"):
            page.wait_for_timeout(2000)
        print("✓ Đã đăng nhập.")
        page.goto(UPLOAD_URL)
        page.wait_for_timeout(3000)

    # Đảm bảo đang ở tab Ảnh
    tab = page.get_by_role("tab", name=re.compile(r"^(Photos|Ảnh)$", re.I))
    try:
        tab.first.click(timeout=15_000)
    except Exception:
        pass

    file_input = page.locator('input[type="file"][accept*="image"]')
    try:
        file_input.first.wait_for(state="attached", timeout=30_000)
    except Exception:
        file_input = page.locator('input[type="file"]')
        try:
            file_input.first.wait_for(state="attached", timeout=30_000)
        except Exception:
            print(f"⚠ Không thấy ô tải ảnh (trang hiện tại: {page.url}). Kiểm tra cửa sổ – có thể cần đăng nhập/xác minh.")
            wait_until_closed(ctx)
            return
    print("Đang tải ảnh lên…")
    file_input.first.set_input_files([str(p) for p in images])

    # Chờ form chi tiết hiện ra (ô tiêu đề / ô mô tả)
    title_box = first_visible(page, [
        'input[placeholder*="title" i]',
        'input[placeholder*="tiêu đề" i]',
        'input[placeholder*="catchy" i]',
    ])
    desc_box = first_visible(page, [
        '.public-DraftEditor-content[contenteditable="true"]',
        '[contenteditable="true"][role="combobox"]',
        '[contenteditable="true"]',
    ])
    if desc_box is None:
        print("⚠ Không tìm thấy ô mô tả – kiểm tra cửa sổ, ảnh có thể chưa tải xong.")
        wait_until_closed(ctx)
        return
    page.wait_for_timeout(2000)

    if title_box is not None:
        title_box.click()
        title_box.fill("")
        title_box.type(title, delay=20)
    else:
        print("⚠ Không thấy ô tiêu đề – bỏ qua, bạn tự điền nếu cần.")

    # Ô mô tả là editor kiểu Draft.js → gõ phím như người, xuống dòng bằng Shift+Enter
    desc_box.click()
    page.keyboard.press("Control+A")
    page.keyboard.press("Delete")
    for i, line in enumerate(caption.split("\n")):
        if i:
            page.keyboard.press("Shift+Enter")
        for word in re.split(r"(\s+)", line):
            if not word:
                continue
            page.keyboard.type(word, delay=15)
            if word.startswith("#"):
                page.wait_for_timeout(400)  # để popup gợi ý hashtag hiện rồi đóng bằng dấu cách
    page.keyboard.press("Escape")

    # Mở mục chọn nhạc rồi DỪNG – không bấm Post/Đăng
    sound = page.get_by_role("button", name=re.compile(r"Add sound|Thêm âm thanh|Thêm nhạc", re.I))
    try:
        sound.first.click(timeout=10_000)
        print("✓ Đã mở mục chọn nhạc.")
    except Exception:
        print("⚠ Không thấy nút chọn nhạc – bạn tự bấm 'Add sound'.")

    print("✓ Xong phần tự động. Bạn tự chọn nhạc 'Em Nên Dừng Lại' và tự bấm Đăng.")
    if data and data.get("pin_comment"):
        print(f"\nBình luận ghim sau khi đăng:\n  {data['pin_comment']}")
    wait_until_closed(ctx)


def main():
    ap = argparse.ArgumentParser(description="Đẩy bộ ảnh bản tin lên TikTok Studio (dừng trước nút Đăng)")
    ap.add_argument("target", nargs="?", help="thư mục data/output/<tên>-anh hoặc file JSON trong inbox")
    ap.add_argument("--login", action="store_true", help="chỉ mở cửa sổ để đăng nhập TikTok lần đầu")
    ap.add_argument("--title", help="tiêu đề tự đặt (≤ 90 ký tự)")
    a = ap.parse_args()
    if not a.login and not a.target:
        ap.error("cần truyền thư mục kết quả / file JSON, hoặc --login")

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        if a.login:
            do_login(pw)
        else:
            out, data = resolve_output(a.target)
            if not out.exists():
                sys.exit(f"Không thấy thư mục kết quả: {out} (chạy render trước)")
            do_upload(pw, out, data, a.title)


if __name__ == "__main__":
    main()
