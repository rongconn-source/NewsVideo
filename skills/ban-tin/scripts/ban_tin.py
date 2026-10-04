#!/usr/bin/env python3
"""Dựng bản tin (ảnh lướt hoặc video) từ 1 file JSON.

Dùng được với mọi AI / mọi người: chỉ cần Python 3.10+, Node.js (npx) và ffmpeg.

    python skills/ban-tin/scripts/ban_tin.py check  inbox/20261003-quy-nhon.json
    python skills/ban-tin/scripts/ban_tin.py render inbox/20261003-quy-nhon.json
    python skills/ban-tin/scripts/ban_tin.py render inbox/x.json --mode video --preview-music nhac.mp3

Kết quả nằm ở data/output/<tên file JSON>-<chế độ>/
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

HF_VERSION = "0.8.114"
SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = SKILL_DIR / "template"
REPO_DIR = SKILL_DIR.parent.parent
INPUT_DIR = REPO_DIR / "input"
OUTPUT_DIR = REPO_DIR / "data" / "output"

CATEGORIES = {"khu-vuc", "tinh", "trong-nuoc", "the-gioi"}
IMAGE_PREFIXES = ("input:", "press:", "ai:", "pexels:", "icon:", "text:", "map:")
ICON_NAMES = {"pin", "globe", "flag", "money", "bolt", "car", "shield", "school", "warning",
              "leaf", "walk", "chart", "ship", "home", "mic"}
COVER_SECONDS, OUTRO_SECONDS, MAX_ITEM_SECONDS, MAX_TOTAL_SECONDS = 2.5, 3.0, 5.0, 59.0
DEFAULT_COLORS = {"dark": "#061633", "mid": "#0a2350", "light": "#1a4c8f", "accent": "#f6b93b"}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------- kiểm tra
def load_config() -> dict:
    f = REPO_DIR / "config" / "ban-tin.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def validate(d: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    cfg = load_config()
    allowed = set(cfg.get("allowed_categories") or CATEGORIES)

    def need(cond, msg):
        if not cond:
            errors.append(msg)

    need(d.get("type") == "digest", '"type" phải là "digest"')
    need(d.get("output", "anh") in ("anh", "video"), '"output" phải là "anh" hoặc "video"')
    need(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(d.get("date", ""))), '"date" phải dạng YYYY-MM-DD')
    need(isinstance(d.get("region"), str) and d["region"].strip(), 'thiếu "region" (vd. "Quy Nhơn")')
    if cfg.get("region") and d.get("region") and cfg["region"] != d["region"]:
        warnings.append(f"region \"{d['region']}\" khác cấu hình \"{cfg['region']}\" (config/ban-tin.json)")
    cover = d.get("cover") or {}
    need(cover.get("title"), 'thiếu "cover.title"')
    need(cover.get("subtitle"), 'thiếu "cover.subtitle" (vd. "Ngày 3/10/2026")')
    need(d.get("outro"), 'thiếu "outro"')
    items = d.get("items")
    need(isinstance(items, list) and 1 <= len(items or []) <= 30, '"items" phải có 1–30 tin')
    for i, it in enumerate(items or [], 1):
        p = f"tin {i}"
        if not isinstance(it, dict):
            errors.append(f"{p}: phải là object")
            continue
        text = str(it.get("text", ""))
        need(20 <= len(text) <= 260, f"{p}: \"text\" dài {len(text)} ký tự (cần 20–260)")
        need(it.get("category") in CATEGORIES, f"{p}: \"category\" phải là 1 trong {sorted(CATEGORIES)}")
        if it.get("category") in CATEGORIES and it.get("category") not in allowed and not it.get("from_user"):
            errors.append(f"{p}: chuyên mục \"{it.get('category')}\" nằm ngoài phạm vi cấu hình {sorted(allowed)} "
                          f"(config/ban-tin.json) – chỉ lấy tin {cfg.get('region', 'khu vực')}")
        need(str(it.get("source", "")).startswith("http"), f"{p}: thiếu \"source\" (link nguồn)")
        need(it.get("source_name"), f"{p}: thiếu \"source_name\" (vd. \"Báo Gia Lai\")")
        pub = str(it.get("published", ""))[:10]
        if not it.get("from_user") and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(d.get("date", ""))):
            import datetime as _dt
            day = _dt.date.fromisoformat(d["date"])
            ok_days = {day.isoformat(), (day - _dt.timedelta(days=1)).isoformat()}
            need(pub in ok_days, f"{p}: \"published\" = \"{pub or 'trống'}\" ngoài 24h qua của bản tin {d.get('date')} "
                 f"(lấy bằng lệnh meta; chỉ lấy tin đăng trong 24 giờ tính lùi từ lúc làm bản tin)")
        img = str(it.get("image") or "press:auto")
        need(img.startswith(IMAGE_PREFIXES), f"{p}: \"image\" phải bắt đầu bằng {IMAGE_PREFIXES}")
        if img.startswith("press:"):
            pass  # ảnh thật bài gốc: mặc định, ghi "Ảnh: <báo>" trên ảnh
        if (img.startswith("ai:") and len(img) < 15) or (it.get("ai_prompt") is not None and len(str(it["ai_prompt"])) < 12):
            errors.append(f"{p}: \"ai:\" cần mô tả cảnh bằng tiếng Anh, vd. ai:busy coastal street at sunset")
        if img.startswith("icon:") and img[5:] and img[5:] not in ICON_NAMES:
            warnings.append(f"{p}: icon \"{img[5:]}\" không có, dùng icon mặc định. Có: {sorted(ICON_NAMES)}")
        if len(text) > 210:
            warnings.append(f"{p}: tin dài {len(text)} ký tự – chữ sẽ nhỏ, nên rút gọn")
    cap = d.get("caption") or {}
    for k in ("tiktok", "youtube", "facebook"):
        need(cap.get(k), f'thiếu "caption.{k}"')
    for r in d.get("needs_review") or []:
        warnings.append(f"cần duyệt: {r}")
    if not d.get("pin_comment"):
        warnings.append('thiếu "pin_comment" (bình luận ghim sau khi đăng)')
    return errors, warnings


# ---------------------------------------------------------------- ảnh
def slugify(s: str) -> str:
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "ban-tin"


def download(url: str, dest: Path) -> Path:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
        ctype = r.headers.get("Content-Type", "")
    ext = ".png" if "png" in ctype else ".webp" if "webp" in ctype else ".jpg"
    out = dest.with_suffix(ext)
    out.write_bytes(data)
    return out


def pexels(query: str, dest: Path) -> tuple[Path, str] | None:
    key = secret("PEXELS_API_KEY")
    if not key:
        return None
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({"query": query, "per_page": 1, "orientation": "landscape"})
    req = urllib.request.Request(url, headers={"Authorization": key, "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        photos = json.load(r).get("photos") or []
    if not photos:
        return None
    p = photos[0]
    return download(p["src"]["large2x"], dest), f"Pexels/{p.get('photographer', '')}"


def resolve_one(kind: str, val: str, it: dict, i: int, img_dir: Path) -> None:
    """Gắn 1 nguồn ảnh cho tin; lỗi thì raise để thử nguồn kế tiếp."""
    src_credit = f"Nguồn: {it['source_name']}"
    if kind == "input":
        f = next((p for p in [INPUT_DIR / val, *INPUT_DIR.rglob(val)] if p.is_file()), None)
        if not f:
            raise FileNotFoundError(f"không thấy input/{val}")
        out = img_dir / f"{i:02d}{f.suffix.lower()}"
        shutil.copy2(f, out)
        it["_img"] = f"assets/img/{out.name}"
        it["_credit"] = f"Ảnh: {it['image_credit']} · {src_credit}" if it.get("image_credit") else src_credit
    elif kind == "press":
        url = resolve_visuals_press_auto(it) if val in ("", "auto") else val
        out = download(url, img_dir / f"{i:02d}")
        if out.stat().st_size < 15_000:
            raise ValueError("ảnh bài gốc quá nhỏ (có thể là logo)")
        it["_img"] = f"assets/img/{out.name}"
        it["_credit"] = f"Ảnh: {it.get('image_credit') or it['source_name']}"
    elif kind == "ai":
        out = ai_image(val, img_dir / f"{i:02d}", seed=1000 + i)
        it["_img"] = f"assets/img/{out.name}"
        it["_ai"] = True
        it["_credit"] = f"Ảnh minh hoạ AI · {src_credit}"
    elif kind == "pexels":
        got = pexels(val, img_dir / f"{i:02d}")
        if not got:
            raise ValueError("chưa có PEXELS_API_KEY hoặc không tìm thấy ảnh")
        it["_img"] = f"assets/img/{got[0].name}"
        it["_credit"] = f"Ảnh: {got[1]} · {src_credit}"
    elif kind == "text":
        it["_text"], it["_credit"] = val, src_credit
    else:  # icon / map
        it["_icon"], it["_credit"] = ("pin" if kind == "map" else val), src_credit


def resolve_visuals(d: dict, img_dir: Path) -> list[str]:
    """Thứ tự thử ảnh mỗi tin: image (mặc định press:auto = ảnh thật bài gốc) → ai_prompt → icon theo chuyên mục."""
    notes = []
    for i, it in enumerate(d["items"], 1):
        chain = [str(it.get("image") or "press:auto")]
        if it.get("ai_prompt"):
            chain.append("ai:" + it["ai_prompt"])
        chain.append("icon:")
        for k, cand in enumerate(chain):
            kind, _, val = cand.partition(":")
            try:
                resolve_one(kind, val, it, i, img_dir)
                if k:
                    notes.append(f"tin {i}: dùng nguồn ảnh dự phòng → {cand[:60]}")
                break
            except Exception as e:
                notes.append(f"tin {i}: {cand[:40]} lỗi ({e})")
                for key in ("_img", "_ai", "_text", "_icon"):
                    it.pop(key, None)
    return notes


# ---------------------------------------------------------------- dựng
def timing(n: int) -> dict:
    item = min(MAX_ITEM_SECONDS, round((MAX_TOTAL_SECONDS - COVER_SECONDS - OUTRO_SECONDS) / n, 2))
    total = round(COVER_SECONDS + n * item + OUTRO_SECONDS, 2)
    return {"cover": COVER_SECONDS, "item": item, "outro": OUTRO_SECONDS, "total": total}


def build_project(d: dict, proj: Path) -> dict:
    if proj.exists():
        shutil.rmtree(proj)
    (proj / "assets" / "img").mkdir(parents=True)
    shutil.copytree(TEMPLATE_DIR / "fonts", proj / "assets" / "fonts")
    notes = resolve_visuals(d, proj / "assets" / "img")
    cover = dict(d["cover"])
    pick = str(cover.get("image", "item:1"))  # mặc định: ảnh tin 1 làm nền bìa; "icon" = không dùng ảnh
    if pick.startswith("item:"):
        k = int(pick[5:] or 1)
        src = d["items"][k - 1] if 1 <= k <= len(d["items"]) else {}
        if not src.get("_img"):  # tin chỉ định không có ảnh → lấy ảnh thật đầu tiên
            src = next((it for it in d["items"] if it.get("_img")), {})
        if src.get("_img"):
            cover["_img"] = src["_img"]
    t = timing(len(d["items"]))
    colors = {**DEFAULT_COLORS, **(d.get("colors") or {})}
    cfg = load_config()
    logo = ""
    logo_src = REPO_DIR / cfg["logo"] if cfg.get("logo") else None
    if logo_src and logo_src.is_file():
        shutil.copy2(logo_src, proj / "assets" / f"logo{logo_src.suffix.lower()}")
        logo = f"assets/logo{logo_src.suffix.lower()}"
    data = {
        "region": d["region"], "province": d.get("province", ""), "brand": d.get("brand") or cfg.get("brand") or ["NEWS", "VIDEO"],
        "chip": d.get("chip", ""), "cover": cover, "outro": d["outro"], "outro_question": d.get("outro_question", ""),
        "logo": logo, "timing": t,
        "items": [{k: v for k, v in it.items() if k in ("category", "label", "text", "_img", "_ai", "_text", "_icon", "_credit")}
                  for it in d["items"]],
    }
    html = (TEMPLATE_DIR / "index.html").read_text(encoding="utf-8")
    html = (html.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
                .replace("__DURATION__", str(t["total"]))
                .replace("__C_DARK__", colors["dark"]).replace("__C_MID__", colors["mid"])
                .replace("__C_LIGHT__", colors["light"]).replace("__C_ACCENT__", colors["accent"]))
    (proj / "index.html").write_text(html, encoding="utf-8")
    (proj / "hyperframes.json").write_text(json.dumps({"paths": {"assets": "assets"}, "media": {"autoProxy": True}}, indent=2), encoding="utf-8")
    (proj / "meta.json").write_text(json.dumps({"id": proj.parent.name, "name": proj.parent.name}), encoding="utf-8")
    for n in notes:
        print("  ·", n)
    return t


def run(cmd: list[str], cwd: Path) -> None:
    print("  $", " ".join(cmd[1:] if cmd[0].lower().endswith(("npx.cmd", "npx")) else cmd)[:160])
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(r.stdout[-3000:], r.stderr[-3000:], sep="\n")
        raise SystemExit(f"Lỗi khi chạy: {cmd[1:4]}")


def hf(*args: str) -> list[str]:
    cmd = shutil.which("hyperframes")
    if cmd:
        return [cmd, *args]
    npx = shutil.which("npx")
    if not npx:
        raise SystemExit("Không thấy hyperframes hoặc npx – cần cài Node.js (https://nodejs.org)")
    return [npx, "--yes", f"hyperframes@{HF_VERSION}", *args]


def ffmpeg() -> str:
    f = shutil.which("ffmpeg")
    if not f:
        raise SystemExit("Không thấy ffmpeg – cần cài ffmpeg")
    return f


def slide_times(n: int, t: dict) -> list[float]:
    ts = [t["cover"] - 0.3]
    ts += [round(t["cover"] + i * t["item"] + t["item"] - 0.3, 2) for i in range(n)]
    ts.append(round(t["total"] - 1.0, 2))
    return ts


def render_slides(proj: Path, out: Path, n: int, t: dict) -> list[Path]:
    snap = proj / "snapshots"
    times = slide_times(n, t)
    run(hf("snapshot", "--at", ",".join(map(str, times)), "--no-end", "-o", str(snap), "--describe", "false", "."), proj)
    shots = sorted(snap.glob("frame-*.png"), key=lambda p: int(re.search(r"frame-(\d+)", p.name).group(1)))
    slides_dir = out / "anh"
    if slides_dir.exists():
        shutil.rmtree(slides_dir)  # xoá ảnh cũ của lần dựng trước
    slides_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for k, s in enumerate(shots, 1):
        dest = slides_dir / f"{k:02d}.png"
        shutil.copy2(s, dest)
        files.append(dest)
    return files


def slideshow(files: list[Path], t: dict, mp4: Path) -> None:
    durs = [t["cover"]] + [t["item"]] * (len(files) - 2) + [t["outro"]]
    lst = mp4.with_suffix(".txt")
    lines = []
    for f, du in zip(files, durs):
        lines += [f"file '{f.as_posix()}'", f"duration {du}"]
    lines.append(f"file '{files[-1].as_posix()}'")
    lst.write_text("\n".join(lines), encoding="utf-8")
    run([ffmpeg(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-threads", "0", "-crf", "20", "-c:a", "aac", "-t", str(t["total"]), str(mp4)], mp4.parent)
    lst.unlink()


def add_music(video: Path, music: Path, start: float, total: float, out: Path) -> None:
    fade_at = max(0.0, total - 2.5)
    run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(video), "-ss", str(start), "-stream_loop", "-1", "-i", str(music),
         "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-af", f"afade=t=in:d=0.6,afade=t=out:st={fade_at}:d=2.5,volume=0.8", "-c:a", "aac", "-t", str(total), str(out)], out.parent)


def write_caption(d: dict, out: Path) -> None:
    tags = " ".join(d.get("hashtags") or [])
    src = "\n".join(f"- {it['source_name']}: {it['source']}" for it in d["items"])
    cap = d["caption"]
    txt = (f"=== TIKTOK ===\n{cap['tiktok']}\n{tags}\n\n=== YOUTUBE SHORTS ===\n{cap['youtube']}\n{tags}\n\n"
           f"=== FACEBOOK ===\n{cap['facebook']}\n{tags}\n\n=== NGUỒN ===\n{src}\n")
    if d.get("pin_comment"):
        txt += f"\n=== BÌNH LUẬN GHIM (đăng xong tự bình luận rồi ghim) ===\n{d['pin_comment']}\n"
    if d.get("needs_review"):
        txt += "\n=== CẦN DUYỆT ===\n" + "\n".join(f"- {r}" for r in d["needs_review"]) + "\n"
    (out / "caption.txt").write_text(txt, encoding="utf-8")


# ---------------------------------------------------------------- meta (ngày đăng, ảnh bài gốc)
def fetch_html(url: str) -> tuple[str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/140.0",
                                               "Accept-Language": "vi-VN,vi;q=0.9"})
    with urllib.request.urlopen(req, timeout=12) as r:
        raw, final = r.read(), r.geturl()
    if raw[:2] == bytes([0x1F, 0x8B]):  # gzip
        raw = gzip.decompress(raw)
    return final, raw.decode("utf-8", errors="replace")


def page_meta(url: str) -> dict:
    final, html = fetch_html(url)

    def meta(*names):
        for n in names:
            m = re.search(rf'<meta[^>]+(?:property|name|itemprop)=["\']{re.escape(n)}["\'][^>]*content=["\']([^"\']+)', html, re.I) \
                or re.search(rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]*(?:property|name|itemprop)=["\']{re.escape(n)}["\']', html, re.I)
            if m:
                return m.group(1).strip()
        return ""

    published = meta("article:published_time", "datePublished", "pubdate", "publishdate", "dc.date.issued")
    if not published:
        m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', html)
        published = m.group(1) if m else ""
    title = meta("og:title") or (re.search(r"<title>(.*?)</title>", html, re.S | re.I) or [None, ""])[1].strip()
    return {"url": final, "published": published, "title": unescape(title), "image": unescape(meta("og:image")),
            "site": unescape(meta("og:site_name")), "description": unescape(meta("og:description", "description"))}


def resolve_visuals_press_auto(it: dict) -> str:
    img = page_meta(it["source"]).get("image")
    if not img:
        raise ValueError("bài gốc không có ảnh đại diện (og:image)")
    return img


def secret(name: str) -> str | None:
    if os.environ.get(name):
        return os.environ[name]
    env = REPO_DIR / "config" / "secrets.env"
    if env.exists():
        m = re.search(rf"^{name}=(.+)$", env.read_text(encoding="utf-8"), re.M)
        return m.group(1).strip() if m else None
    return None


def ai_image(prompt: str, dest: Path, seed: int) -> Path:
    """Ảnh minh hoạ AI miễn phí (Pollinations). Không key: ~1 ảnh/30 giây → tự chờ + thử lại.
    Ảnh đã tạo được lưu ở data/cache/ai/ nên dựng lại không phải tạo lại."""
    import hashlib
    import time
    import urllib.error

    full = prompt + ", photorealistic, natural light, no text, no watermark"
    cache = REPO_DIR / "data" / "cache" / "ai" / (hashlib.sha1(f"{full}|{seed}".encode()).hexdigest()[:16] + ".jpg")
    if cache.exists():
        out = dest.with_suffix(".jpg")
        shutil.copy2(cache, out)
        return out
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(full)}?width=1280&height=1024&nologo=true&seed={seed}"
    headers = {"User-Agent": "Mozilla/5.0"}
    token = secret("POLLINATIONS_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for attempt in range(10):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=180) as r:
                data = r.read()
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_bytes(data)
            out = dest.with_suffix(".jpg")
            out.write_bytes(data)
            return out
        except urllib.error.HTTPError as e:
            if e.code not in (402, 429, 500, 502, 503) or attempt == 9:
                raise
            print(f"    … dịch vụ ảnh AI bận (lỗi {e.code}), chờ 20 giây rồi thử lại ({attempt + 1}/9)", flush=True)
            time.sleep(20)
    raise RuntimeError("không tạo được ảnh AI")



# ---------------------------------------------------------------- scan (thu tin đúng ngày từ nguồn)
def norm(t: str) -> str:
    t = unicodedata.normalize("NFD", t.replace("đ", "d").replace("Đ", "D"))
    return "".join(c for c in t if unicodedata.category(c) != "Mn").lower()


def scan(date: str, out_json: Path | None, since: str | None = None) -> None:
    from concurrent.futures import ThreadPoolExecutor

    cfg = load_config()
    sources = cfg.get("sources") or []
    if not sources:
        raise SystemExit('Chưa có "sources" trong config/ban-tin.json')
    keys = [norm(k) for k in cfg.get("region_keywords") or [cfg.get("region", "")] if k]
    links: dict[str, dict] = {}
    for src in sources:
        try:
            base, html = fetch_html(src["url"])
        except Exception as e:
            print(f"  ✗ không đọc được {src['name']}: {e}")
            continue
        found = []
        for href in re.findall(r'href="([^"#]+)"', html):
            url = urllib.parse.urljoin(base, href)
            m = re.search(src["pattern"], url)
            if m and url not in links:
                found.append((int(m.group(1)), url))
        found = sorted(set(found), reverse=True)[: src.get("max", 40)]
        for _, url in found:
            links[url] = src
        print(f"  · {src['name']}: {len(found)} bài mới nhất")

    def one(url):
        try:
            return url, page_meta(url)
        except Exception:
            return url, None

    import datetime as _dt
    vn = _dt.timezone(_dt.timedelta(hours=7))
    now = _dt.datetime.now(vn)
    end = now if date == now.date().isoformat() else _dt.datetime.fromisoformat(date + "T23:59:59+07:00")
    start = end - _dt.timedelta(hours=24)  # "24h qua" = 24 giờ tính lùi từ lúc quét
    if since:  # người dùng chọn mốc riêng (vd. chưa đăng bản nào từ hôm qua)
        start = _dt.datetime.fromisoformat(since if "T" in since else since + "T00:00")
        if start.tzinfo is None:
            start = start.replace(tzinfo=vn)

    def in_window(pub: str) -> bool:
        try:
            t = _dt.datetime.fromisoformat(pub.strip().replace("Z", "+00:00"))
            if t.tzinfo is None:
                t = t.replace(tzinfo=vn)
            return start <= t <= end
        except ValueError:
            return pub.startswith(date)

    rows = []
    with ThreadPoolExecutor(16) as ex:
        for url, m in ex.map(one, links):
            if not m or not m["published"] or not in_window(m["published"]):
                continue
            src = links[url]
            text = norm(f"{m['title']} {m['description']}")
            match = src.get("region_search", False) or any(k in text for k in keys)
            rows.append({"published": m["published"], "source": src["name"], "title": m["title"], "url": url,
                         "image": m["image"], "description": m["description"], "region_match": match})
    # gộp tin trùng giữa các nguồn (ưu tiên link báo gốc hơn Báo Mới)
    best: dict[str, dict] = {}
    for r in rows:
        key = norm(r["title"])[:70]
        cur = best.get(key)
        if not cur or ("baomoi.com" in cur["url"] and "baomoi.com" not in r["url"]):
            if cur:
                r["region_match"] = r["region_match"] or cur["region_match"]
            best[key] = r
        else:
            cur["region_match"] = cur["region_match"] or r["region_match"]
    rows = list(best.values())
    rows.sort(key=lambda r: (not r["region_match"], r["published"]))
    print()
    print(f"TIN TỪ {start:%d/%m %H:%M} → {end:%d/%m %H:%M}: {len(rows)} bài ({sum(r['region_match'] for r in rows)} có từ khoá khu vực)")
    print()
    for r in rows:
        flag = "✓" if r["region_match"] else " "
        print(f"{flag} {r['published'][8:10]}/{r['published'][5:7]} {r['published'][11:16]} | {r['source'][:14]:14} | {r['title'][:95]}")
        print(f"                           {r['url']}{'' if r['image'] else '   (KHÔNG có ảnh → cần ai_prompt)'}")
    if out_json:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nĐã lưu: {out_json}")
    print("\n✓ = tiêu đề/mô tả có từ khoá khu vực hoặc lấy từ trang tìm kiếm khu vực. Vẫn phải mở bài gốc kiểm tra địa bàn.")

# ---------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser(description="Dựng bản tin ảnh lướt / video từ file JSON")
    ap.add_argument("command", choices=["scan", "check", "render", "meta"])
    ap.add_argument("json", nargs="?", help="file bản tin JSON (check/render)")
    ap.add_argument("urls", nargs="*", help="(meta) các link bài báo cần xem ngày đăng + ảnh")
    ap.add_argument("--mode", choices=["anh", "video"], help="ghi đè trường output trong JSON")
    ap.add_argument("--out", type=Path, help="thư mục kết quả (mặc định data/output/<tên>-<chế độ>)")
    ap.add_argument("--preview-music", type=Path, help="file nhạc chỉ để XEM THỬ (không dùng để đăng)")
    ap.add_argument("--music-start", type=float, help="giây bắt đầu trong file nhạc xem thử")
    ap.add_argument("--no-preview-music", action="store_true", help="không làm bản xem thử có nhạc")
    ap.add_argument("--date", help="(scan) ngày YYYY-MM-DD, mặc định hôm nay")
    ap.add_argument("--since", help="(scan) lấy tin từ mốc này thay vì 24h, vd. 2026-10-03 hoặc 2026-10-04T12:00")
    a = ap.parse_args()
    if a.command == "scan":
        import datetime
        date = a.date or datetime.date.today().isoformat()
        scan(date, REPO_DIR / "data" / "scan" / f"{date}.json", a.since)
        return
    if a.command == "meta":
        for u in [str(a.json), *a.urls]:
            try:
                m = page_meta(u)
                print(f"{m['published'] or '?':27} | {m['site'][:16]:16} | {m['title'][:90]}")
                print(f"{'':27}   {m['url']}")
                print(f"{'':27}   ảnh: {m['image'][:110]}")
            except Exception as e:
                print(f"LỖI {u}: {e}")
        return
    if not a.json:
        ap.error("cần đường dẫn file JSON")
    a.json = Path(a.json).resolve()
    pm = load_config().get("preview_music") or {}
    if not a.preview_music and not a.no_preview_music and pm.get("file") and (REPO_DIR / pm["file"]).is_file():
        a.preview_music = REPO_DIR / pm["file"]
    if a.music_start is None:
        a.music_start = float(pm.get("start", 0)) if a.preview_music else 0.0
    if a.preview_music:
        a.preview_music = a.preview_music.resolve()
        if not a.preview_music.is_file():
            raise SystemExit(f"Không thấy file nhạc: {a.preview_music}")
    if a.out:
        a.out = a.out.resolve()

    d = json.loads(a.json.read_text(encoding="utf-8"))
    errors, warnings = validate(d)
    for w in warnings:
        print("  ⚠", w)
    if errors:
        print("JSON CHƯA HỢP LỆ:")
        for e in errors:
            print("  ✗", e)
        raise SystemExit(1)
    mode = a.mode or d.get("output") or load_config().get("default_output", "anh")
    n = len(d["items"])
    t = timing(n)
    print(f"✓ JSON hợp lệ: {n} tin · chế độ {mode} · {t['item']}s/tin · tổng {t['total']}s")
    if a.command == "check":
        return

    out = a.out or OUTPUT_DIR / f"{a.json.stem}-{mode}"
    out.mkdir(parents=True, exist_ok=True)
    proj = out / "_project"
    print("1/3 Chuẩn bị mẫu + ảnh…")
    build_project(d, proj)
    import datetime
    stamp = datetime.datetime.now().strftime("%Hh%M")
    for old in out.glob("*.mp4"):  # xoá video cũ, tránh lẫn bản
        old.unlink()
    mp4 = out / f"{a.json.stem}_{stamp}.mp4"
    if mode == "anh":
        print("2/3 Chụp ảnh từng trang…")
        files = render_slides(proj, out, n, t)
        print("3/3 Ghép ảnh thành video (cho YouTube/Facebook)…")
        slideshow(files, t, mp4)
    else:
        print("2/3 Render video (HyperFrames)…")
        run(hf("render", "-o", str(mp4)), proj)
        print("3/3 Xong render.")
    write_caption(d, out)
    if a.preview_music:
        add_music(mp4, a.preview_music, a.music_start, t["total"], out / f"{a.json.stem}_{stamp}-XEM-THU-co-nhac.mp4")
    print(f"\nKẾT QUẢ: {out}")
    for p in sorted(out.iterdir()):
        if p.name != "_project":
            print("  -", p.name + ("/" if p.is_dir() else ""))


if __name__ == "__main__":
    main()
