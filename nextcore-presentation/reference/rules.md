# Rules: what the deck may say and how it must look

Condensed from `technext-presentations` (content-rules.md, design.md, lessons) and the owner's rules in memory. When technext.asia and this file disagree, the live site wins: update this file and tell the user.

## Claims (check_deck.py enforces the starred ones)
- * **Odoo is never "free".** Licences are billed by Odoo, per user per month; TechNext quotes the implementation. No prices of any kind in the deck (fee, licences, discounts): the proposal carries them.
- * **No BIR guarantees.** Never "BIR-ready", "BIR-compliant", "accredited", "certified", "handled", "we confirm". Say "set up for BIR requirements"; the client's accountant or RDO confirms coverage. If a slide mentions BIR at all, the close carries: "TechNext is an Odoo Ready Partner. We are not affiliated with, accredited by or acting for the BIR or any government agency, and we do not file or register on your behalf."
- * **Tax wording follows the client's country** (`country`, or the city suffix): PH = "Accounting is set up for BIR requirements, with your accountant." + the not-affiliated disclaimer on the close (added automatically); SG = "Taxes are set up for GST, with your accountant." (never a GST F5 or IRAS e-filing claim); VN and others = "local requirements". Never BIR in a non-Philippine deck.
- * **"Odoo Ready Partner in Singapore"**, never certified/Gold/Silver, never a partnership in the Philippines. TechNext can say it serves Philippine businesses and has teams in Taguig City and Ho Chi Minh City.
- **Approved figures only:** 142 ERP projects, 40+ years of excellence, 90+ enterprise clients, 25+ countries (and 3 offices, 4 AI disciplines if ever needed). No team size, revenue, founding year or other numbers unless the user gives them. Not ISO 27001 certified.
- * **No other client's name**, sample company or leftover from another deck (Hitachi, GERP, Makati, Kestrel & Pine, Lumen Trading...), in text, alt, aria or data. The check reads `01. Client Folder` for the current client list.
- **Pain points are hypotheses** to confirm in discovery. Only the client's own facts from the profile (or the client's public pages, dated). No job ads, reviews, headcount guesses or internal research.
- **Sample data is labelled** ("Illustrative · sample records"). Record ids are Odoo-style and fictional.
- **Plans are indicative** ("Indicative plan, confirmed at kick-off"). Never a go-live date.
- * **No WhatsApp** link or number. sales@technext.asia is plain text, never a `mailto:` link. Booking: https://technext.odoo.com/book/c82cf8a9 (QR).

## Voice (owner, 20-21 Oct 2026)
- TechNext is a solution provider and expert adviser. Lead line: "Your trusted expert adviser for ERP and compliance." Brand line: "We advise first, then deliver the whole solution." Our OWN experts implement.
- Verbs: advise, recommend, deliver; "solve", not "fix"; "recommend what fits, and say why"; "a call with an adviser".
- * British "adviser", never "advisor". British spelling throughout (organise, customisation, centre). "Odoo", never "ODOO".
- * Never "world-class", "leading", "one-stop shop", "vendor", "reseller", "trusted advisor".
- One idea per slide; the headline makes the point; exactly ONE marker phrase per headline (`[[...]]` in deck.json).
- Kickers: short, lowercase, Caveat ("what we heard", "how we work").

## Design
- **technext.asia branding** (site.css tokens): blue #3167CA (points: the marker, the current step, TechNext's bars), navy #1E4691, sky #6FA0F5, ink #1F1F3D, body #4C4C63, secondary text #5E5E75 (never #8888A0 for text: 3.3:1), line #E7E4E9, paper #FAF9FB, ok #137A4A. Plus Jakarta Sans (display), Inter (body), Caveat (kicker only).
- **Light slides on plain paper**; navy (#0F2350 → #1E4691 → #2D5DB8 at 140°, nothing else on it) only for the opener and the close. No dark mode.
- **No background masking:** no tinted fields, slabs, ovals, bands, radial or linear washes, glows, dot grids with mask fades, blur, or greyed elements behind or over content. A white card holding content (the "Prepared for" plate, the QR card, the record card) is content, not masking. Unreached things are shown smaller or in secondary text colour, never at low opacity.
- **No icon tiles:** line icons bare, in brand colour; official Odoo app icons bare (no tile, never recoloured, never greyed).
- **The client's colour** marks only the client's own things: the client's steps and bars, the "what we heard" column. `build_deck.py` darkens it to 4.5:1 on paper, and swaps it for ink when it is too close to TechNext blue (then the legend still reads). Never a client-colour field.
- **The client's logo:** official file, untouched (never recoloured or redrawn); large on the opener's white "Prepared for" plate; beside TechNext's in the light slides' chrome. No file = a type nameplate.
- **Frame:** 1600 x 900; padding 118 top, 120 sides, 96 bottom; chrome in the top 92px, footer 34px from the bottom; content stays above y 842 (the shots check fails otherwise).
- **Split, never shrink:** content that does not fit is cut, or moved to the proposal; type never goes below the scale. Max 3 pain points, 6 apps on the rail (the rest named), titles 70 characters.
- **A different composition on every slide** (stats + plate / ledger / rail / steps / Gantt / QR): never two alike in a row.
- **Type scale:** opener 92px, close 64px, slide titles 44px, lead 26px, body 18-22px, small 15-17px (nothing meaningful under 15px; secondary text under 18px uses #5E5E75 or darker).

## Motion (motionmaxxing craft, the deck motion kit)
- Slides push: the old slide accelerates out in 0.2 s, the new one lands soft over 0.6 s.
- Arrivals move and decelerate (`[data-in]` rises 36px, opacity is a 0.2 s helper); siblings stagger 60-120 ms; a slide is built by about 1.2-1.5 s.
- Headlines rise word by word (75-105 ms per word); the marker draws after the last word.
- One spring per deck: the close's QR card lands from oversize.
- Each working object moves with meaning: figures count up (slide 1), arrows draw and answers rise (slide 2), the record card travels and changes face (slide 3), the method groups cascade in order (slide 4), phase bars wipe in left to right in time order (slide 5).
- Nothing grows from zero; no blur animation; no infinite decorative loops.
- Reduced motion: fade only, every slide lands finished. Print: every slide finished.
- Review with `find-animation-opportunities` / `improve-animations` before shipping a template change.

## When tempted to bend a rule
Read the rationalisation table in `framework.md` (Stage 4). It lists the excuses that come up and the answer to each.
