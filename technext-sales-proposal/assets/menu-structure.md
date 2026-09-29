# Sidebar menu structure — source of truth

Transcribed verbatim from `prompt.txt` (the original hand-typed prompt this skill
packages). This is the fixed sidebar for every proposal this skill produces. Order and
grouping below must not be dropped or reshuffled — `prompt.txt`'s own last line ("Add
more relevant categories") means agents may **add** an extra item inside a group if a
client's research surfaces something that doesn't fit an existing item, never remove or
reorder the ones listed here.

Each entry below is `slug — VI label / EN label`. The slug is the `id` used for the
`<section id="slug">` and the sidebar `<a href="#slug">` in `assets/proposal-template.html`.
Group headers (bold) are non-clickable sidebar section dividers, not their own `<section>`.

## Overview

- `pre-meeting` — Trước khi họp cần đọc / Read before the meeting ★ (written by front-matter-writer; 4 fixed parts: `pm-company`, `pm-person`, `pm-issues`, `pm-unknowns`; the ★ must-read list inside it is auto-built from every section tagged `data-star="1"`)
- `overview` — Tổng quan / Overview
- `exec-summary` — Tóm tắt điều hành / Executive Summary

- `recommendations` — Khuyến nghị / Recommendations

## Proposed Solutions

TechNext sells three service lines, not just Odoo — every proposal pitches all three,
each grounded in this specific client's research, not a generic pitch copy-pasted
across clients.

- `solution-odoo-erp` — Giải pháp Odoo ERP / Odoo ERP Solution
- `solution-ai` — Giải pháp AI / AI Solutions
- `solution-social-media` — Giải pháp Marketing mạng xã hội / Social Media Marketing Solution

## Due Diligence

- `due-diligence` — Rà soát toàn diện / Due Diligence
- `company-profile` — Hồ sơ công ty / Company Profile
- `product-catalog` — Danh mục sản phẩm / Product Catalog
- `founders-leadership` — Nhà sáng lập & Ban lãnh đạo / Founders & Leadership
- `staff-org` — Nhân sự & Cơ cấu tổ chức / Staff & Org Analysis
- `current-operations` — Vận hành hiện tại / Current Operations
- `current-tools-saas` — Công cụ & Phần mềm đang dùng / Current Tools & SaaS
- `digital-web` — Hiện diện số & Website / Digital & Web Presence
- `reviews-reputation` — Đánh giá & Uy tín / Reviews & Reputation

## Strategic Analysis

- `strategic-analysis` — Phân tích chiến lược / Strategic Analysis
- `competitor-deep-dive` — Phân tích sâu đối thủ / Competitor Deep-Dive
- `market-industry` — Thị trường & Ngành / Market & Industry
- `customer-personas` — Hồ sơ khách hàng mục tiêu / Customer Personas

## Operations

- `department-workflows` — Quy trình phòng ban / Department Workflows
- `pain-solution-matrix` — Ma trận Vấn đề → Giải pháp / Pain → Solution Matrix
- `bpmn-blueprint-uml` — BPMN · Blueprint · UML / BPMN · Blueprint · UML

## Competitive Intel

- `competitive-intel` — Thông tin cạnh tranh / Competitive Intel
- `top3-competitor-deep-dive` — Phân tích sâu Top 3 đối thủ / Top-3 Competitor Deep-Dive

## Growth & Strategy

- `pricing-strategy` — Chiến lược giá / Pricing Strategy
- `regional-expansion` — Chiến lược mở rộng vùng / Regional Expansion Strategy
- `advisory` — Tư vấn / Advisory
- `sources-citation` — Nguồn & Trích dẫn / Sources & Citation

## Tools & Documents

- `tool-ai-playbook` — 📘 Sổ tay triển khai AI / AI Build Playbook
- `tool-profit-estimator` — 📊 Công cụ ước tính lợi nhuận / Profit Estimator
- `tool-owner-faq` — 💬 Hỏi đáp cho chủ doanh nghiệp / Owner FAQ
- `tool-odoo-platform` — ⚓ Nền tảng Odoo / Odoo Platform
- `tool-brd` — 📑 Yêu cầu nghiệp vụ (BRD) / Requirements (BRD)
- `tool-quotation` — 🧾 Báo giá / Quotation
- `tool-accounting-overhaul` — 📒 Cải tổ kế toán / Accounting Overhaul
- `tool-demo-walkthrough` — 🧭 Hướng dẫn Demo / Demo Walkthrough
- `tool-staff-guides` — 🛎 Hướng dẫn nhân viên / Staff Guides
- `sales-playbook` — 🎯 Sales Playbook ★ (30-second + 2-minute pitch, objections, 15-minute demo script, what to close)
- `tool-discovery-questions` — 📋 Câu hỏi khám phá / Discovery Questions
- `meeting-minutes` — 🗒 Biên bản họp / Meeting Minutes

## Removed sections — boss feedback 2026-09-23

The following 12 items (and the now-empty "Technology" and "Delivery" groups they
lived in) were removed per direct boss feedback, and must **not** be regenerated:
`operations`, `stakeholder-perspectives`, `ai-automation-catalog`, `ai-in-action`,
`odoo-architecture`, `data-migration`, `social-media-architecture`,
`implementation-roadmap`, `change-management`, `hypercare-support`,
`risk-register-raci`, `kpis-benefits`. Their chart/diagram ownership (`cRisk`, `cKpi`,
`cRoi`, plus 5 of the 9 diagram slots) moved to the new `recommendations` section and
`bpmn-blueprint-uml` — see `SKILL.md`'s "Charts & diagrams" section for the current
manifest. `operations`'s old content (Current Operations/Current Tools & SaaS) already
lives separately under Due Diligence (`current-operations`/`current-tools-saas`) —
unaffected by this removal.
