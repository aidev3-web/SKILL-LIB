# Profile to slides: the mapping

`build_deck.py` writes this mapping into `deck.json` on the first build. `deck.json` is the copy of record after that: edit it, never the template, for one client's words.

## The profile (NextCore `client-profile.json`)
```json
{
  "client": "Northgate Trading Corp.",       // legal/display name: chrome label, "Prepared for" card, file name
  "short_name": "Northgate",                 // in sentences and the legend; default = first word of client
  "industry": "Wholesale distribution",      // card row
  "city": "Pasig City, PH",                  // card row (", PH"/", SG"/", VN" dropped)
  "contact": "Finance Manager",              // slide 2 lead ("your Finance Manager")
  "pain_points": ["Excel books", "stock counts"],   // slide 2, max 3, in this order
  "odoo_apps": ["Accounting", "Inventory", "Sales"], // slide 3 rail (max 6, the rest named), slide 5 sprints
  "users": 12,                               // card, slide 3 tag, step 6, go-live detail
  "brand": {"logo": "logo.svg", "colour": "#0F6B5C"}  // logo beside TechNext's; colour = the client's own marks
}
```
Required: client, industry, city, pain_points, odoo_apps, users. Optional: `country` (PH / SG / VN; otherwise read from the city suffix) decides the tax wording and the BIR disclaimer. More than 3 pain points: the first three are used and the build prints a NOTE. `users: 1` reads "1 user". Other fields the profile carries (tin_branch, opening_balances, announce_ok...) are not used by the deck. App names must match the technext.asia catalogue in `assets/apps.json` (aliases: accounts, stock, sale, pos, mrp, hr, e-commerce...); an unknown name stops the build.

## Slide by slide
| # | Slide | From the profile | Fixed house content |
|---|---|---|---|
| 1 | Who TechNext is (navy) | "Prepared for" card: logo, industry, city, `users` users; chrome label = client | Kicker "who we are"; "Your trusted [[expert adviser]] for ERP and compliance."; "We advise first, then deliver the whole solution, with our own experts from discovery to hypercare."; "Odoo Ready Partner in Singapore · teams in Taguig City and Ho Chi Minh City"; the four approved figures counting up |
| 2 | What we heard | `pain_points` (max 3) as the client's own words; `contact` in the lead; count word in the headline ("Two things [[hold Northgate back]] today.") | Each pain point gets a hypothesis line and the app that answers it, from the pain library below. → reveals one answer per press |
| 3 | The Odoo apps | `odoo_apps` sorted into flow order, max 6 on the rail; `users` in the lead and the tag; headline counts the apps ("Three Odoo apps, [[one database]].") | One sample record travels app to app (→ or a click): S00042 → WH/OUT/00042 → INV/2026/00042 ...; app lines from `apps.json`; "Odoo licences are billed by Odoo, per user per month."; "Illustrative · sample records" |
| 4 | NextSprint | `short_name` as the deciding party; `users` in step 6; sprint weeks from the app count | "NextSprint: Agile, Lean and Six Sigma in [[seven steps]]."; Lean over steps 1-3, Agile over 4-5, Six Sigma over 6-7; TechNext steps filled blue, the client's steps ringed in the client colour; "A rejected deliverable goes back to step 4 until you approve it." |
| 5 | Phases and timeline | weeks = 2 (discover) + 2 per app (one sprint each, max 6) + 1 (UAT) + 1 (go-live); sprint bars named by app; `users` in the go-live detail | "Indicative plan, confirmed at kick-off"; Hypercare 30 days after go-live; click a bar for who does what |
| 6 | Next step (navy) | `short_name` in the lead | "Next: [[agree the scope]], then kick off."; review the proposal → settle open points with an adviser → sign, then kick off; booking QR (technext.odoo.com/book/c82cf8a9); sales@technext.asia and technext.asia as plain text |

## The pain library (`PAIN_LIB` in build_deck.py)
A keyword in the pain point picks the hypothesis line, the preferred app (only if the client has it) and how Odoo answers. Odoo 20 behaviour only, no outcomes promised.

| Keyword | Hypothesis (today) | App | With Odoo |
|---|---|---|---|
| BIR, tax, CAS, VAT, GST, IRAS, compliance (checked FIRST) | Tax books and returns prepared by hand. | Accounting / Invoicing | by country: PH "set up for BIR requirements, with your accountant" (+ disclaimer on the close); SG "set up for GST, with your accountant"; else "local requirements" |
| appointment, booking, schedule, reservation, front desk | Bookings kept on paper or in chats, so the day's schedule is pieced together by hand. | Appointments / Planning / Field Service | Clients book online, and the calendar updates for the whole team. |
| POS, cashier, counter sales, store, retail | Counter sales recorded apart from stock and the books. | Point of Sale | Each sale at the counter moves stock and posts to the books. |
| excel, spreadsheet, books (whole word), ledger, month-end | Books kept in spreadsheets, so month-end waits on copying and checking by hand. | Accounting / Invoicing | Invoices, bills and payments post to the books as they happen. Month-end starts from live figures. |
| stock, inventory, warehouse, cycle count (not bare "count") | Stock counted and reconciled by hand, so the numbers drift between counts. | Inventory | Every receipt and delivery moves stock as it happens. A count is checked against what Odoo expects. |
| quotation, sales order, price list | Quotations and orders typed up apart from stock and billing. | Sales | A quotation becomes the order, the delivery and the invoice, with nothing typed twice. |
| invoice, billing, receivable, collect | Invoices prepared by hand and chased one by one. | Accounting / Invoicing / Sales | Invoices come from the confirmed order, and payments are matched to them in the bank. |
| purchase, supplier, reorder | Buying decided from memory or a spreadsheet, not from stock levels. | Purchase / Inventory | Reordering rules propose purchases, and bills are checked against what arrived. |
| lead, CRM, pipeline, follow-up | Leads and follow-ups kept in inboxes and notebooks. | CRM | Every lead, call and follow-up sits in one pipeline the whole team sees. |
| payroll, salary, attendance, leave | Payroll and leave worked out in spreadsheets. | Payroll / Time Off / Attendances | Attendance and approved leave feed the payslips. |
| production, manufacturing, BOM | Production planned on paper. | Manufacturing | Bills of materials and work orders reserve components and track each run. |
| report, visibility, dashboard | Reports built by exporting and merging files. | first unused app | Reports read the same live records the team works in. |
| no match | "To confirm in discovery." | first unused app | the app's catalogue line |

Each pain point is a HYPOTHESIS: the slide 2 lead says "We confirm each one in discovery". Rewrite a hypothesis in deck.json when the profile gives more detail; never add a figure the client did not give.

## When the Sales Proposal exists
The proposal builder (`nextcore-proposal`) owns the plan of record. If it has run for this client, copy its weeks, sprint names and hypercare length into `deck.json` (`plan.weeks`, `plan.rows`, `method.steps[].em`) so the two materials agree. The deck never shows the fee, licence prices or invoice dates.

Order matters: the first matching row wins, and patterns use word boundaries ("notebook" must not match "books"). Every new row needs a case in `tests/cases.json`.
