---
name: html-audit
description: >-
  Kiem tra loi cu phap va chat luong cua file HTML, sau do tu dong xuat bao cao
  ra file Markdown (.md) va file PDF (.pdf) cung thu muc. Dung khi nguoi dung
  muon audit, review, kiem tra loi, sua loi HTML, xuat bao cao PDF, hoac noi:
  kiem tra file html, check html, audit html, sua loi html, html report, bao cao pdf.
---

# HTML Audit Skill

Kiem tra toan dien mot file HTML: phat hien loi cu phap, van de cau truc,
thieu thuoc tinh accessibility, SEO co ban, va tu dong ghi ket qua ra
**file Markdown (.md)** va **file PDF (.pdf)** chuyen nghiep.

---

## Quy trinh thuc hien

### Buoc 1 — Xac dinh file HTML can audit

- Lay duong dan tuyet doi cua file HTML tu active document hoac nguoi dung cung cap.
- Ghi nho `<html_dir>` (thu muc chua file) va `<html_basename>` (ten file khong duoi).
- File Markdown: `<html_dir>/<html_basename>_audit_report.md`
- File PDF: `<html_dir>/<html_basename>_audit_report.pdf`

### Buoc 2 — Doc toan bo noi dung file HTML

- Dung `view_file` hoac doc bang script de kiem tra toan bo file HTML.
- Ghi nho tong so dong de xac nhan da doc het.

### Buoc 3 — Phan tich loi va van de

Kiem tra theo thu tu uu tien va ghi nhan so dong cu the cho moi van de:

#### Critical — Loi nghiem trong
- Tag khong dong hoac dong sai thu tu (vi du: `<` thieu ten tag, `<div>` thieu `</div>`)
- Attribute khong co gia tri hoac gia tri khong co dau ngoac kep
- Ky tu dac biet chua duoc escape (`&`, `<`, `>` trong text content)
- Thieu `<!DOCTYPE html>`
- Thieu `<html>`, `<head>`, hoac `<body>` tag
- Encoding khong khai bao (`<meta charset>` bi thieu)

#### Warning — Canh bao
- Thieu `<title>` hoac title rong
- Thieu `<meta name="description">`
- `<img>` thieu thuoc tinh `alt`
- `<a>` thieu `href` hoac `href="#"` ma khong co purpose
- ID bi trung lap trong cung document
- Inline style qua nhieu (>10 element dung `style=""`)
- `<b>`, `<i>` thay vi `<strong>`, `<em>` (semantic HTML)

#### Info — Goi y cai thien
- Thieu `lang` attribute tren `<html>` tag
- `<meta viewport>` bi thieu (responsive)
- Heading hierarchy bi nhay cap (h1 sang h3 bo qua h2)
- `<table>` thieu `<caption>` hoac `scope` tren `<th>`
- Form khong co `label` cho input

### Buoc 4 — Sua loi (neu duoc yeu cau)

- Neu nguoi dung yeu cau sua luon: tien hanh sua loi Critical truoc, sau do Warning.
- Moi lan sua phai ghi ro dong goc -> dong sau sua vao bao cao.
- Khong sua phan logic JavaScript hay CSS design, chi sua cu phap HTML.

### Buoc 5 — Viet bao cao Markdown (.md)

Tao file `<html_basename>_audit_report.md` tai cung thu muc voi HTML theo template chuan:

  # HTML Audit Report - <ten file>.html

  **Ngay kiem tra:** YYYY-MM-DD HH:MM
  **File:** <duong dan tuyet doi>
  **Tong so dong:** N
  **Cong cu:** Antigravity HTML Audit Skill

  ---

  ## Tom tat

  | Muc do   | So luong |
  |----------|----------|
  | Critical | N        |
  | Warning  | N        |
  | Info     | N        |
  | **Tong** | **N**    |

  > Danh gia tong the: [Tot / Can cai thien / Co van de nghiem trong]

  ---

  ## Critical — Loi nghiem trong
  ...

  ## Warning — Canh bao
  ...

  ## Info — Goi y cai thien
  ...

  ## Cac thanh phan da dat chuan
  ...

### Buoc 6 — Xuat bao cao PDF (.pdf)

Sau khi tao xong file Markdown, goi script xuat PDF di kem skill:

```bash
python "<skill_dir>/scripts/generate_pdf_report.py" "<html_dir>/<html_basename>_audit_report.md"
```

Script se tu dong:
- Su dung thu vien `pymupdf` da co san trong moi truong
- Su dung font he thong Windows Arial de ho tro tieng Viet co dau 100%
- Format giao dien chuan bao cao chuyen nghiep voi header banner mau xanh, section cards, bullet points va bang tong ket.
- Xuat ra file `<html_dir>/<html_basename>_audit_report.pdf`.

### Buoc 7 — Thong bao ket qua cho nguoi dung

Bao cao cho nguoi dung:
- So luong loi theo tung muc do
- Link den ca 2 file:
  - File Markdown: `[<ten_file>_audit_report.md](file://...)`
  - File PDF: `[<ten_file>_audit_report.pdf](file://...)`
