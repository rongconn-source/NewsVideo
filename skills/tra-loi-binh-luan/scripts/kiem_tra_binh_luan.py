#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Công cụ Kiểm tra & Soạn thảo câu trả lời bình luận chuẩn pháp lý cho kênh Quy Nhơn 24h Qua (@quynhon24hqua).
Usage:
    python skills/tra-loi-binh-luan/scripts/kiem_tra_binh_luan.py "Chắc KS Bình Dương kinh doanh ko hiệu quả rồi"
    python skills/tra-loi-binh-luan/scripts/kiem_tra_binh_luan.py --recent
"""

import sys
import os
import json
import glob
import re
from pathlib import Path

# Đảm bảo in tiếng Việt & emoji chuẩn trên Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
INBOX_DIR = BASE_DIR / "skills" / "ban-tin" / "inbox"
REF_DIR = Path(__file__).resolve().parent.parent / "reference"
KEYWORDS_FILE = REF_DIR / "bo-tu-khoa-nhay-cam.json"
TEMPLATES_FILE = REF_DIR / "kich-ban-mau-tra-loi.md"

def load_keywords():
    if KEYWORDS_FILE.exists():
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def scan_inbox_for_keywords(keywords):
    matched_articles = []
    json_files = sorted(glob.glob(str(INBOX_DIR / "*.json")), reverse=True)[:10]
    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("items", [])
            for idx, item in enumerate(items):
                content = item.get("text", "") or item.get("body", "")
                text = f"{item.get('title', '')} {content} {item.get('source_name', '')}"
                text_lower = text.lower()
                for kw in keywords:
                    if kw.lower() in text_lower:
                        matched_articles.append({
                            "session": Path(jf).stem,
                            "item_index": idx + 1,
                            "category": item.get("category", ""),
                            "body": content,
                            "source_name": item.get("source_name", ""),
                            "source": item.get("source", ""),
                            "matched_keyword": kw
                        })
                        break
        except Exception:
            continue
    return matched_articles

def analyze_comment(comment_text):
    data = load_keywords()
    nhom_tu_khoa = data.get("nhom_tu_khoa", {})
    found_risks = []
    matched_kws = []

    text_lower = comment_text.lower()

    for category, details in nhom_tu_khoa.items():
        kws = details.get("keywords", [])
        for kw in kws:
            if kw.lower() in text_lower:
                found_risks.append({
                    "category": category,
                    "keyword": kw,
                    "risk": details.get("rui_ro", ""),
                    "solution": details.get("nguyen_tac_xu_ly", "")
                })
                matched_kws.append(kw)

    # Extract potential entity names or subjects
    potential_entities = []
    known_entities = [
        "bình dương", "hải âu", "hoàng yến", "bệnh viện", "quốc tế", "tây sơn",
        "hiệu trưởng", "giáo viên", "quy nhơn nam", "phù cát", "sân bay", "long mỹ", "gò đá trắng"
    ]
    for entity in known_entities:
        if entity in text_lower:
            potential_entities.append(entity)

    # Find evidence in inbox
    search_terms = potential_entities if potential_entities else [comment_text[:20]]
    evidences = scan_inbox_for_keywords(search_terms)

    # Generate suggestions
    suggestions = generate_suggestions(comment_text, found_risks, evidences, potential_entities)

    return {
        "comment": comment_text,
        "risks": found_risks,
        "matched_keywords": list(set(matched_kws)),
        "entities": potential_entities,
        "evidences": evidences[:3],
        "suggestions": suggestions
    }

def generate_suggestions(comment_text, risks, evidences, entities):
    suggs = {}
    lower = comment_text.lower()

    if any(e in lower for e in ["bình dương", "hoàng yến", "hải âu"]):
        suggs["ngan_gon"] = "Dạ không phải đâu bạn ơi! Việc di dời khách sạn là theo Đồ án quy hoạch chung của tỉnh nhằm trả lại toàn bộ không gian biển mở làm công viên công cộng phục vụ người dân và du khách, hoàn toàn không phải do kinh doanh đâu ạ."
        suggs["chi_tiet"] = "Chào bạn, việc tháo dỡ và bàn giao mặt bằng khách sạn Bình Dương là chủ trương lớn của tỉnh theo quy hoạch chỉnh trang bờ biển Quy Nhơn. Toàn bộ khu đất này sẽ làm công viên cây xanh, lối đi dạo ngắm biển cho cộng đồng chứ không liên quan đến tình hình kinh doanh của doanh nghiệp bạn nhé!"
        suggs["than_thien"] = "Dạ không phải đâu nè bạn, khách sạn bàn giao mặt bằng để tỉnh làm công viên biển cho bà con mình dạo mát ngắm biển á, quy hoạch đẹp lắm luôn!"
    elif any(e in lower for e in ["bệnh viện", "tây sơn", "gara"]):
        suggs["ngan_gon"] = "Dạ đúng rồi bạn, dự án Bệnh viện đa khoa quốc tế 200 giường xây tại số 200 đường Tây Sơn (khu Gara Quyền cũ gần BHXH) với vốn hơn 665 tỷ đồng đó ạ."
        suggs["chi_tiet"] = "Chào bạn, theo quyết định chấp thuận chủ trương đầu tư, bệnh viện quốc tế 665 tỷ sẽ xây dựng tại số 200 đường Tây Sơn, P. Quy Nhơn Nam (vị trí Gara Quyền cũ) để nâng cao chất lượng khám chữa bệnh cho người dân tỉnh mình bạn nha."
        suggs["than_thien"] = "Đúng rồi bạn nha, ngay chỗ Gara Quyền cũ trên đường Tây Sơn á, sắp tới có bệnh viện hiện đại phục vụ bà con rồi nè!"
    elif any(e in lower for e in ["hiệu trưởng", "giáo viên", "quy nhơn nam"]):
        suggs["ngan_gon"] = "Chào bạn, hiện UBND tỉnh đã chỉ đạo các cơ quan chức năng vào cuộc tổng kiểm tra, rà soát toàn diện vụ việc để xử lý theo đúng quy định pháp luật và đảm bảo quyền lợi cho các thầy cô. Bà con mình cùng theo dõi kết luận chính thức nhé!"
        suggs["chi_tiet"] = "Chào bạn, vụ việc sắp xếp cán bộ ở P. Quy Nhơn Nam hiện đang được cơ quan thanh tra của tỉnh và ngành giáo dục rà soát kỹ lưỡng. Chúng ta cùng chờ kết luận chính thức từ cơ quan có thẩm quyền để nắm thông tin chuẩn xác nhất nhé!"
        suggs["than_thien"] = "Cảm ơn bạn đã quan tâm! Tỉnh đang cho thanh tra kiểm tra cụ thể rồi, có thông tin mới nhất kênh sẽ cập nhật ngay cho bà con nha."
    else:
        # Generic response
        if evidences:
            ev = evidences[0]
            suggs["ngan_gon"] = f"Chào bạn, theo thông tin chính thức từ {ev['source_name']}: {ev['body'][:120]}... Bạn theo dõi kênh để cập nhật thêm nhé!"
        else:
            suggs["ngan_gon"] = "Cảm ơn bạn đã chia sẻ góc nhìn cùng kênh! Mọi thông tin kênh đưa đều dựa trên nguồn tin báo chí chính thống đã kiểm chứng ạ."
        suggs["than_thien"] = "Cảm ơn bạn đã theo dõi và tương tác cùng Quy Nhơn 24h Qua nhé! Chúc bạn ngày mới tốt lành 🥰"

    return suggs

def main():
    if len(sys.argv) < 2:
        print("Usage: python kiem_tra_binh_luan.py \"<nội dung bình luận>\"")
        sys.exit(0)

    comment = " ".join(sys.argv[1:])
    result = analyze_comment(comment)

    print("=" * 65)
    print("🔎 KẾT QUẢ PHÂN TÍCH & CHỨNG THỰC BÌNH LUẬN")
    print("=" * 65)
    print(f"📝 Nội dung bình luận: \"{result['comment']}\"")
    print("-" * 65)

    if result["risks"]:
        print("⚠️ CẢNH BÁO RỦI RO PHÁP LÝ & TIKTOK POLICY:")
        for r in result["risks"]:
            print(f"  - Từ khóa phát hiện: [{r['keyword']}] (Nhóm: {r['category']})")
            print(f"    Rủi ro: {r['risk']}")
            print(f"    Giải pháp xử lý: {r['solution']}")
    else:
        print("✅ Đánh giá rủi ro: Bình luận an toàn / Chưa phát hiện từ khóa cấm.")

    print("-" * 65)
    if result["evidences"]:
        print("📚 DỮ LIỆU ĐỐI CHIẾU TRONG BẢN TIN GỐC:")
        for ev in result["evidences"]:
            print(f"  • [{ev['session']}] Tin #{ev['item_index']} - Báo: {ev['source_name']}")
            print(f"    Trích dẫn: {ev['body']}")
            print(f"    Link gốc: {ev['source']}")
    else:
        print("ℹ️ Dữ liệu đối chiếu: Không tìm thấy bài báo liên quan trực tiếp trong 10 bản tin gần nhất.")

    print("-" * 65)
    print("💡 GỢI Ý CÂU TRẢ LỜI CHUẨN MỰC CHO KÊNH:")
    suggs = result["suggestions"]
    if "ngan_gon" in suggs:
        print(f"\n1. Phương án Ngắn gọn (Khuyên dùng trên TikTok):\n   👉 \"{suggs['ngan_gon']}\"")
    if "chi_tiet" in suggs:
        print(f"\n2. Phương án Đầy đủ căn cứ pháp lý:\n   👉 \"{suggs['chi_tiet']}\"")
    if "than_thien" in suggs:
        print(f"\n3. Phương án Thân thiện, gần gũi:\n   👉 \"{suggs['than_thien']}\"")

    print("=" * 65)

if __name__ == "__main__":
    main()
