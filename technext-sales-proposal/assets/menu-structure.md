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

- `overview` — Tổng quan / Overview
- `why-ai` — Vì sao AI quan trọng / Why AI is Important
- `exec-summary` — Tóm tắt điều hành / Executive Summary

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
- `digital-web` — Hiện diện số & Website / Digital & Web Presence
- `reviews-reputation` — Đánh giá & Uy tín / Reviews & Reputation

## Strategic Analysis

- `strategic-analysis` — Phân tích chiến lược / Strategic Analysis
- `pestle` — Phân tích PESTLE / PESTLE Analysis
- `swot-tows` — SWOT & TOWS / SWOT & TOWS
- `porter-5-forces` — Mô hình 5 Áp lực của Porter / Porter's Five Forces
- `competitor-deep-dive` — Phân tích sâu đối thủ / Competitor Deep-Dive
- `market-industry` — Thị trường & Ngành / Market & Industry
- `customer-personas` — Hồ sơ khách hàng mục tiêu / Customer Personas

## Operations

- `operations` — Vận hành / Operations
- `stakeholder-perspectives` — Góc nhìn các bên liên quan / Stakeholder Perspectives
- `department-workflows` — Quy trình phòng ban / Department Workflows
- `pain-solution-matrix` — Ma trận Vấn đề → Giải pháp / Pain → Solution Matrix
- `bpmn-blueprint-uml` — BPMN · Blueprint · UML / BPMN · Blueprint · UML

## Technology

- `ai-automation-catalog` — Danh mục AI & Tự động hoá / AI & Automation Catalog
- `ai-in-action` — AI trong thực tế — Câu chuyện điển hình / AI in Action — Peer Story
- `odoo-architecture` — Kiến trúc Odoo 19 / Odoo 19 Architecture
- `data-migration` — Di chuyển dữ liệu / Data Migration
- `social-media-architecture` — Kiến trúc & Công cụ Marketing mạng xã hội / Social Media Marketing Architecture & Tools

## Delivery

- `implementation-roadmap` — Lộ trình triển khai / Implementation Roadmap
- `change-management` — Quản lý thay đổi / Change Management
- `hypercare-support` — Hỗ trợ Hypercare / Hypercare & Support
- `risk-register-raci` — Bảng rủi ro & RACI / Risk Register & RACI
- `kpis-benefits` — KPI & Lợi ích / KPIs & Benefits

## Competitive Intel

- `competitive-intel` — Thông tin cạnh tranh / Competitive Intel
- `top3-competitor-deep-dive` — Phân tích sâu Top 3 đối thủ / Top-3 Competitor Deep-Dive

## Growth & Strategy

- `pricing-strategy` — Chiến lược giá / Pricing Strategy
- `regional-expansion` — Chiến lược mở rộng vùng / Regional Expansion Strategy
- `modern-alternative-services` — Dịch vụ thay thế hiện đại / Modern Alternative Services
- `advisory` — Tư vấn / Advisory
- `appendix-sources` — Phụ lục & Nguồn tham khảo / Appendix & Sources

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
- `tool-discovery-questions` — 📋 Câu hỏi khám phá / Discovery Questions
- `tool-content-calendar` — 📅 Lịch nội dung mạng xã hội / Social Media Content Calendar

## Notes on operations appearing twice

`prompt.txt` lists a group called "Operations" twice (once under Delivery-adjacent
content near line 36, once again near line 58 right before "Modern Alternative
Services"). Treat the second occurrence as the same `operations` group already covered
above — don't create a duplicate sidebar entry; if the client's research has
operations-related content that didn't fit the first pass, add it to the existing
`operations`/`department-workflows` sections instead.
