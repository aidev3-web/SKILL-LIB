import os
import sys
import pymupdf

def create_pdf_report(md_report_path, output_pdf_path=None):
    if not os.path.exists(md_report_path):
        print(f"Error: Khong tim thay file {md_report_path}")
        return False

    if output_pdf_path is None:
        output_pdf_path = os.path.splitext(md_report_path)[0] + ".pdf"

    with open(md_report_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842) # A4 size

    font_regular = r"C:\Windows\Fonts\arial.ttf"
    font_bold = r"C:\Windows\Fonts\arialbd.ttf"

    page.insert_font(fontname="Arial", fontfile=font_regular)
    page.insert_font(fontname="Arial-Bold", fontfile=font_bold)

    # Header decoration banner
    shape = page.new_shape()
    shape.draw_rect(pymupdf.Rect(0, 0, 595, 75))
    shape.finish(color=None, fill=(0.08, 0.38, 0.86))
    shape.commit()

    # Header Title
    page.insert_text((40, 46), "HTML AUDIT & QUALITY REPORT", fontname="Arial-Bold", fontsize=18, color=(1, 1, 1))

    y = 105
    lines = md_text.splitlines()

    for line in lines:
        line_str = line.strip()
        if not line_str:
            y += 6
            continue

        if y > 780:
            page = doc.new_page(width=595, height=842)
            page.insert_font(fontname="Arial", fontfile=font_regular)
            page.insert_font(fontname="Arial-Bold", fontfile=font_bold)
            y = 50

        if line_str.startswith("# "):
            title = line_str.replace("# ", "").replace("📋", "").strip()
            page.insert_text((40, y), title, fontname="Arial-Bold", fontsize=14, color=(0.1, 0.1, 0.1))
            y += 22
        elif line_str.startswith("## "):
            heading = line_str.replace("## ", "").strip()
            shape = page.new_shape()
            shape.draw_rect(pymupdf.Rect(40, y - 11, 555, y + 5))
            shape.finish(color=None, fill=(0.93, 0.96, 0.99))
            shape.commit()
            page.insert_text((48, y), heading, fontname="Arial-Bold", fontsize=11, color=(0.08, 0.35, 0.75))
            y += 18
        elif line_str.startswith("### "):
            sub = line_str.replace("### ", "").strip()
            page.insert_text((45, y), sub, fontname="Arial-Bold", fontsize=10.5, color=(0.18, 0.18, 0.18))
            y += 16
        elif line_str.startswith("- "):
            bullet = "- " + line_str[2:].replace("**", "").replace("`", "")
            page.insert_text((55, y), bullet, fontname="Arial", fontsize=9, color=(0.25, 0.25, 0.25))
            y += 14
        elif line_str.startswith("|"):
            if "---" in line_str:
                continue
            cells = [c.strip() for c in line_str.split("|")[1:-1]]
            text = "   |   ".join(cells).replace("**", "")
            is_hdr = "Mức độ" in text or "Critical" in text
            fn = "Arial-Bold" if is_hdr else "Arial"
            page.insert_text((55, y), text, fontname=fn, fontsize=9, color=(0.2, 0.2, 0.2))
            y += 14
        elif line_str.startswith("> "):
            quote = line_str.replace("> ", "").replace("**", "")
            shape = page.new_shape()
            shape.draw_rect(pymupdf.Rect(45, y - 9, 550, y + 7))
            shape.finish(color=(0.2, 0.7, 0.3), fill=(0.95, 0.99, 0.95), width=1)
            shape.commit()
            page.insert_text((52, y), quote, fontname="Arial-Bold", fontsize=9, color=(0.1, 0.5, 0.2))
            y += 20
        elif line_str.startswith("**") and ":" in line_str:
            clean = line_str.replace("**", "").replace("`", "")
            page.insert_text((40, y), clean, fontname="Arial", fontsize=9, color=(0.3, 0.3, 0.3))
            y += 14
        elif not line_str.startswith("```"):
            clean = line_str.replace("**", "").replace("`", "")
            page.insert_text((45, y), clean, fontname="Arial", fontsize=8.5, color=(0.35, 0.35, 0.35))
            y += 13

    doc.save(output_pdf_path)
    print(f"PDF generated: {output_pdf_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        md_file = sys.argv[1]
        out_file = sys.argv[2] if len(sys.argv) > 2 else None
        create_pdf_report(md_file, out_file)
    else:
        sample = r"C:\Users\nguye\OneDrive\Máy tính\test_Skill-lib\Trung_mcp-skill-bridge-tools_audit_report.md"
        create_pdf_report(sample)
