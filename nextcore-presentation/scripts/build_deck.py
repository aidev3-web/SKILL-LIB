# -*- coding: utf-8 -*-
"""NextCore presentation builder: client-profile.json -> deck.json (the words, editable) -> ONE self-contained HTML.

    python -I -X utf8 build_deck.py <client dir | client-profile.json> [--out DIR] [--regen] [--rev 1.0] [--status Draft]

  1. Reads the NextCore profile (client, short_name, industry, city, contact, pain_points, odoo_apps, users, brand{logo,colour}).
  2. Writes <client dir>/deck.json the first time (or with --regen): every word on the six slides, made from the profile
     with the mapping in reference/mapping.md. Edit deck.json to change copy; the build never overwrites it otherwise.
  3. Renders template/deck.html.j2 into <out>/presentation.html: fonts, logos, Odoo icons and the booking QR are inlined,
     so the file opens anywhere with no internet and no other files.
  4. Runs check_deck.py (house content rules + other clients' names). Exit code 1 if a check fails.
Nothing is sent anywhere.
"""
import argparse, base64, colorsys, datetime as dt, hashlib, html, json, math, os, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent
ASSETS = SKILL / 'assets'
BOOKING = 'https://technext.odoo.com/book/c82cf8a9'
WORDS = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten']

# ------------------------------------------------------------------ copy libraries (see reference/mapping.md)
# pain point keyword -> (hypothesis line, preferred apps, how Odoo answers it). Odoo 20 behaviour only; no promises.
PAIN_LIB = [
    (r'\bbir\b|\btax|\bcas\b|\bvat\b|\bgst\b|\biras\b|complian',
     'Tax books and returns prepared by hand.', ['Accounting', 'Invoicing'],
     '{TAX_LINE}'),
    (r'appointment|booking|schedul|reservation|front desk',
     'Bookings kept on paper or in chats, so the day\u2019s schedule is pieced together by hand.', ['Appointments', 'Planning', 'Field Service'],
     'Clients book online, and the calendar updates for the whole team.'),
    (r'\bpos\b|cashier|counter sales|\bstore\b|retail|branch sales',
     'Counter sales recorded apart from stock and the books.', ['Point of Sale'],
     'Each sale at the counter moves stock and posts to the books.'),
    (r'excel|spreadsheet|\bbooks?\b|ledger|month.?end|closing|journal',
     'Books kept in spreadsheets, so month-end waits on copying and checking by hand.', ['Accounting', 'Invoicing'],
     'Invoices, bills and payments post to the books as they happen. Month-end starts from live figures.'),
    (r'stock|inventor|warehouse|cycle count',
     'Stock counted and reconciled by hand, so the numbers drift between counts.', ['Inventory'],
     'Every receipt and delivery moves stock as it happens. A count is checked against what Odoo expects.'),
    (r'quot|sales order|order entry|price ?list|pricing',
     'Quotations and orders typed up apart from stock and billing.', ['Sales'],
     'A quotation becomes the order, the delivery and the invoice, with nothing typed twice.'),
    (r'invoic|billing|receivable|collect',
     'Invoices prepared by hand and chased one by one.', ['Accounting', 'Invoicing', 'Sales'],
     'Invoices come from the confirmed order, and payments are matched to them in the bank.'),
    (r'purchas|supplier|vendor|reorder|procure|buying',
     'Buying decided from memory or a spreadsheet, not from stock levels.', ['Purchase', 'Inventory'],
     'Reordering rules propose purchases, and bills are checked against what arrived.'),
    (r'lead|crm|pipeline|follow',
     'Leads and follow-ups kept in inboxes and notebooks.', ['CRM'],
     'Every lead, call and follow-up sits in one pipeline the whole team sees.'),
    (r'payroll|salar|attendance|leave|\bhr\b',
     'Payroll and leave worked out in spreadsheets.', ['Payroll', 'Time Off', 'Attendances', 'Employees'],
     'Attendance and approved leave feed the payslips.'),
    (r'production|manufactur|\bbom\b|bill of material',
     'Production planned on paper.', ['Manufacturing'],
     'Bills of materials and work orders reserve components and track each run.'),
    (r'report|visibility|dashboard|real.?time',
     'Reports built by exporting and merging files.', [],
     'Reports read the same live records the team works in.'),
]
# the order a record travels through the apps, and the sample record each app creates (doc, id, status)
FLOW_ORDER = ['Website Builder', 'Email Marketing', 'Events', 'CRM', 'Appointments', 'Sales', 'Point of Sale', 'eCommerce', 'Subscriptions', 'Rental', 'Purchase', 'Inventory', 'Manufacturing',
              'Quality', 'Maintenance', 'Project', 'Field Service', 'Helpdesk', 'Timesheets', 'Planning', 'Invoicing', 'Accounting',
              'Expenses', 'Documents', 'Sign', 'Employees', 'Recruitment', 'Time Off', 'Attendances', 'Payroll']
RECORD = {
    'CRM': ('Opportunity', 'Sample deal', 'Won'), 'Sales': ('Sales order', 'S00042', 'Confirmed'),
    'Point of Sale': ('POS order', 'Shop/0042', 'Paid'), 'eCommerce': ('Online order', 'S00042', 'Confirmed'),
    'Subscriptions': ('Subscription', 'S00042', 'In progress'), 'Rental': ('Rental order', 'S00042', 'Picked up'),
    'Purchase': ('Purchase order', 'P00017', 'Received'), 'Inventory': ('Delivery', 'WH/OUT/00042', 'Done'),
    'Manufacturing': ('Manufacturing order', 'WH/MO/00008', 'Done'), 'Quality': ('Quality check', 'QC/00012', 'Passed'),
    'Maintenance': ('Maintenance request', 'Request 12', 'Repaired'), 'Project': ('Task', 'Task 42', 'Done'),
    'Field Service': ('Field task', 'Task 42', 'Done'), 'Helpdesk': ('Ticket', 'Ticket 42', 'Solved'),
    'Timesheets': ('Timesheet', '8.00 hours', 'Approved'), 'Planning': ('Shift', 'Shift 42', 'Published'),
    'Invoicing': ('Customer invoice', 'INV/2026/00042', 'Paid'), 'Accounting': ('Customer invoice', 'INV/2026/00042', 'Posted'),
    'Expenses': ('Expense report', 'Report 12', 'Approved'), 'Documents': ('Document', 'Filed', 'Done'),
    'Sign': ('Signature request', 'Agreement', 'Signed'), 'Employees': ('Employee', 'Employee file', 'Active'),
    'Recruitment': ('Applicant', 'Applicant 12', 'Hired'), 'Time Off': ('Time off', 'Request 12', 'Approved'),
    'Attendances': ('Attendance', 'Check-in', 'Recorded'), 'Payroll': ('Payslip', 'SLIP/042', 'Done'),
    'Appointments': ('Appointment', 'Booking 42', 'Booked'), 'Website Builder': ('Web page', 'Contact us', 'Published'),
    'Email Marketing': ('Mailing', 'Newsletter 12', 'Sent'), 'Events': ('Event', 'Open day', 'Announced'),
    'Fleet': ('Vehicle', 'Van 12', 'Active'), 'Knowledge': ('Article', 'How we ship', 'Published'), 'Approvals': ('Request', 'Request 12', 'Approved'),
}
ALIAS = {'point of sale': 'Point of Sale \u2014 Shop', 'pos': 'Point of Sale \u2014 Shop', 'pos shop': 'Point of Sale \u2014 Shop',
         'pos restaurant': 'Point of Sale \u2014 Restaurant', 'restaurant': 'Point of Sale \u2014 Restaurant', 'appointment': 'Appointments',
         'accounts': 'Accounting', 'accounting': 'Accounting', 'invoicing': 'Invoicing', 'inventory': 'Inventory', 'stock': 'Inventory',
         'sales': 'Sales', 'sale': 'Sales', 'crm': 'CRM', 'purchase': 'Purchase', 'purchasing': 'Purchase', 'pos': 'Point of Sale',
         'manufacturing': 'Manufacturing', 'mrp': 'Manufacturing', 'payroll': 'Payroll',
         'hr': 'Employees', 'employees': 'Employees', 'ecommerce': 'eCommerce', 'e-commerce': 'eCommerce', 'website': 'Website Builder',
         'helpdesk': 'Helpdesk', 'project': 'Project', 'field service': 'Field Service', 'timesheets': 'Timesheets'}


TAX_LINE = {
    'PH': 'Accounting is set up for BIR requirements, with your accountant.',
    'SG': 'Taxes are set up for GST, with your accountant.',
    'VN': 'Taxes are set up for local requirements, with your accountant.',
    'other': 'Taxes are set up for local requirements, with your accountant.'}
DISCLAIMER = ('TechNext is an Odoo Ready Partner. We are not affiliated with, accredited by or acting for the BIR or any '
              'government agency, and we do not file or register on your behalf. This is not tax advice.')


def country_of(prof):
    """PH / SG / VN / other, from an explicit `country` or the city suffix (Pasig City, PH)."""
    c = (prof.get('country') or prof.get('city', '').split(',')[-1]).strip().upper()
    return {'PH': 'PH', 'PHILIPPINES': 'PH', 'SG': 'SG', 'SINGAPORE': 'SG', 'VN': 'VN', 'VIETNAM': 'VN', 'VIET NAM': 'VN'}.get(c, 'other')


def num_word(n):
    return WORDS[n] if 0 <= n < len(WORDS) else str(n)


def and_list(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def safe(s):
    return re.sub(r'[<>:"/\\|?*]', '', s).strip().rstrip('.')


# ------------------------------------------------------------------ colour: the client's colour, made safe to use as text on paper
def _lum(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + .05) / (lb + .05)


def client_ui_colour(hexc):
    """4.5:1 on the paper; ink when it is too close to TechNext blue to tell apart (then the legend still reads)."""
    if not re.match(r'^#[0-9a-fA-F]{6}$', hexc or ''):
        return '#1F1F3D', 'no valid brand colour: ink used'
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    bh, _, _ = colorsys.rgb_to_hls(0x31 / 255, 0x67 / 255, 0xCA / 255)
    if s > .3 and min(abs(h - bh), 1 - abs(h - bh)) * 360 < 22:
        return '#1F1F3D', 'brand colour too close to TechNext blue: ink used'
    note = ''
    while contrast('#%02X%02X%02X' % tuple(round(c * 255) for c in colorsys.hls_to_rgb(h, l, s)), '#FAF9FB') < 4.5 and l > .05:
        l -= .02; note = 'brand colour darkened for 4.5:1 contrast'
    return '#%02X%02X%02X' % tuple(round(c * 255) for c in colorsys.hls_to_rgb(h, l, s)), note


# ------------------------------------------------------------------ assets
def data_uri(path, mime=None):
    p = pathlib.Path(path)
    mime = mime or {'.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}[p.suffix.lower()]
    return f'data:{mime};base64,' + base64.b64encode(p.read_bytes()).decode()


def nameplate_svg(name, colour):
    """No logo file: a plain type nameplate (never a drawn mark)."""
    w = max(240, 22 * len(name))
    t = html.escape(name)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 60" width="{w}" height="60"><text x="0" y="44" '
           f'font-family="Plus Jakarta Sans, Segoe UI, Arial, sans-serif" font-weight="800" font-size="40" fill="{colour}">{t}</text></svg>')
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()


def fonts_css(text):
    """Variable fonts (one file serves every weight). latin-ext only when the deck's text needs it."""
    need_ext = any(ord(ch) > 0xFF and not (0x2000 <= ord(ch) <= 0x206F) and ch not in '€™↑↓−∕→' for ch in text)
    lat = 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD'
    ext = 'U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF'
    out = []
    for fam, base, wt in (('Plus Jakarta Sans', 'plus-jakarta-sans', '500 800'), ('Inter', 'inter', '400 700'), ('Caveat', 'caveat', '400 700')):
        subsets = [('latin', lat)] + ([('latin-ext', ext)] if need_ext and fam != 'Caveat' else [])
        for sub, rng in subsets:
            f = ASSETS / 'fonts' / f'{base}-{sub}.woff2'
            out.append(f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{wt};font-display:block;"
                       f"src:url(data:font/woff2;base64,{base64.b64encode(f.read_bytes()).decode()}) format('woff2');unicode-range:{rng}}}")
    return '\n'.join(out)


def qr_svg(url):
    import segno
    s = segno.make(url, error='m').svg_inline(dark='#1F1F3D', light=None, scale=1, border=0, omitsize=True)
    return s.replace('<svg ', '<svg role="img" aria-label="QR code: book a call with a TechNext adviser" ', 1)


def apps_catalogue():
    cat = {}
    for grp in json.loads((ASSETS / 'apps.json').read_text(encoding='utf-8')):
        for a in grp['apps']:
            cat[a['n'].lower()] = a
    return cat


# ------------------------------------------------------------------ profile -> deck.json (the words)
def load_profile(p):
    p = pathlib.Path(p)
    if p.is_dir():
        p = p / 'client-profile.json'
    prof = json.loads(p.read_text(encoding='utf-8-sig'))
    miss = [k for k in ('client', 'industry', 'city', 'pain_points', 'odoo_apps', 'users') if not prof.get(k)]
    if miss:
        raise SystemExit(f'client-profile.json is missing: {", ".join(miss)}')
    return p, prof


def resolve_apps(names, cat):
    out, unknown = [], []
    for n in names:
        key = ALIAS.get(n.strip().lower(), n.strip())
        a = cat.get(key.lower())
        if not a:
            unknown.append(n); continue
        out.append(dict(app=a['n'].split(' \u2014 ')[0], module=a['m'], desc=a['d']))
    if unknown:
        raise SystemExit(f'unknown Odoo app(s) {unknown}: use the names in assets/apps.json (the technext.asia catalogue)')
    order = {n: i for i, n in enumerate(FLOW_ORDER)}
    return sorted(out, key=lambda a: order.get(a['app'], 50))


def default_deck(prof, cat):
    C = prof['client'].strip()
    short = (prof.get('short_name') or C.split()[0]).strip()
    city = re.sub(r',\s*(PH|SG|VN|Philippines|Singapore|Vietnam)\s*$', '', prof['city'].strip())
    users = int(prof['users'])
    if users < 1:
        raise SystemExit('users must be 1 or more')
    contact = (prof.get('contact') or 'team').strip()
    country = country_of(prof)
    tax_line = TAX_LINE[country]
    nusers = f'{users} user' + ('' if users == 1 else 's')
    apps = resolve_apps(prof['odoo_apps'], cat)
    names = [a['app'] for a in apps]

    # 02 what we heard: at most three pain points, in the profile's order
    rows, used = [], set()
    if len(prof['pain_points']) > 3:
        print(f"NOTE: {len(prof['pain_points'])} pain points; the slide shows the first three. Reorder the profile or edit deck.json.")
    for pp in prof['pain_points'][:3]:
        hit = next((x for x in PAIN_LIB if re.search(x[0], pp, re.I)), None)
        line, prefs, odoo = (hit[1], hit[2], hit[3].replace('{TAX_LINE}', tax_line)) if hit else ('To confirm in discovery.', [], None)
        app = next((n for n in prefs if n in names), None) or next((n for n in names if n not in used), names[0])
        used.add(app)
        a = next(x for x in apps if x['app'] == app)
        rows.append(dict(today=pp.strip()[:1].upper() + pp.strip()[1:], today_line=line, app=app, module=a['module'], odoo_line=odoo or a['desc']))
    n = len(rows)
    heard_title = (f'One thing [[holds {short} back]] today.' if n == 1 else f'{num_word(n)} things [[hold {short} back]] today.')

    # 03 apps: up to six on the rail, the rest named
    rail, also = apps[:6], apps[6:]
    flow = []
    for a in rail:
        doc, rid, st = RECORD.get(a['app'], ('Record', 'Sample', 'Done'))
        flow.append(dict(app=a['app'], module=a['module'], desc=a['desc'], doc=doc, record=rid, status=st))
    k = len(apps)
    apps_title = (f'{num_word(k)} Odoo apps, [[one database]].' if k > 1 else f'One Odoo app, [[set up for {short}]].')
    apps_lead = (f'Sized for {nusers} at {short}. {and_list(names)} share every record, so nothing is typed twice.' if k > 1
                 else f'Sized for {nusers} at {short}, on the same database every app you add later will share.')

    # 04 NextSprint (method shared with the Sales Proposal builder: Agile, Lean, Six Sigma; seven steps)
    sprints = max(1, min(len(apps), 6))
    w_sp_end = 2 + 2 * sprints
    weeks = w_sp_end + 2
    steps = [
        dict(by='tn', g=1, b='Discovery workshop', p='We map how you sell, stock and bill.', em='Week 1'),
        dict(by='cl', g=1, b='Share your data', p='Customers, items, opening stock and balances.', em='Weeks 1–2'),
        dict(by='cl', g=1, b='Sign the scope', p='Your OK sets the scope of record.', em='End of week 2'),
        dict(by='tn', g=2, b='Sprints', p='Two-week sprints, each ending in a demo.', em=f'Weeks 3–{w_sp_end}'),
        dict(by='cl', g=2, b='Test (UAT)', p='Approve or send back each deliverable.', em=f'Week {w_sp_end + 1}'),
        dict(by='tn', g=3, b='Go-live', p=f'Data import and training for your {nusers}.', em=f'Week {weeks}'),
        dict(by='tn', g=3, b='Hypercare', p='Close support after go-live, then a review.', em='30 days'),
    ]
    groups = [dict(name='Lean', span=3, line='Only what adds value: we map first, then you sign the scope.'),
              dict(name='Agile', span=2, line='Short sprints, a demo each time, your approval before the next.'),
              dict(name='Six Sigma', span=2, line='Measured, then controlled: live with checks, then close support.')]

    # 05 plan (indicative; replace with the Sales Proposal's plan when it exists)
    sp_names = [a['app'] for a in apps[:6]] if len(apps) <= 6 else [f'Sprint {i + 1}' for i in range(sprints)]
    plan = [
        dict(label='Discover and scope', sub=f'TechNext with {short}', w0=1, w1=2, kind='', text='Workshop, data, signed scope',
             ms='Scope signed', when='Weeks 1–2',
             detail=f'A discovery workshop maps how {short} sells, stocks and bills. Your team shares the data, then signs the scope of record.'),
        dict(label='Set up in sprints', sub='TechNext', w0=3, w1=w_sp_end, kind='', sprints=sp_names, when=f'Weeks 3–{w_sp_end}',
             detail=f'{num_word(sprints)} two-week sprint{"s" if sprints > 1 else ""}, each ending in a demo your team approves before the next starts.'),
        dict(label='Test (UAT)', sub=short, w0=w_sp_end + 1, w1=w_sp_end + 1, kind='cl', text='Your team tests', when=f'Week {w_sp_end + 1}',
             detail='Your team runs real transactions end to end and approves or sends back each deliverable.'),
        dict(label='Go-live and training', sub='TechNext', w0=weeks, w1=weeks, kind='', text='Import, training', ms='Go-live', when=f'Week {weeks}',
             detail=f'The final data import and training for your {nusers}, then {short} runs on Odoo.'),
        dict(label='Hypercare', sub='TechNext', w0=None, w1=None, kind='hc', text='30 days', when='30 days after go-live',
             detail='Close support while your team settles in, then a review of what to improve next.'),
    ]
    return {
        '_profile_md5': None, '_note': 'The words on every slide. Edit freely, then run build_deck.py again. --regen rebuilds this file from the profile.',
        'rev': '1.0', 'status': 'Draft', 'date': dt.date.today().strftime('%-d %B %Y') if os.name != 'nt' else dt.date.today().strftime('%#d %B %Y'),
        'country': country,
        'client': dict(name=C, short=short, industry=prof['industry'].strip(), city=city, contact=contact, users=users),
        'who': dict(kicker='who we are', title='Your trusted [[expert adviser]] for ERP and compliance.',
                    lead='We advise first, then deliver the whole solution, with our own experts from discovery to hypercare.',
                    partner='Odoo Ready Partner in Singapore', teams='teams in Taguig City and Ho Chi Minh City',
                    plate=[['Industry', prof['industry'].strip()], ['City', city], ['Team on Odoo', nusers]],
                    figures=[dict(n=142, suf='', l='ERP projects'), dict(n=40, suf='+', l='years of excellence'),
                             dict(n=90, suf='+', l='enterprise clients'), dict(n=25, suf='+', l='countries')]),
        'heard': dict(kicker='what we heard', title=heard_title,
                      lead=f'From our first conversation with your {contact}. We confirm each one in discovery, then set Odoo up around it.',
                      col_today='What we heard', col_odoo='With Odoo', rows=rows),
        'apps': dict(kicker='the Odoo apps', title=apps_title, lead=apps_lead, flow=flow,
                     also=(f'+{len(also)} more on the same database: ' + and_list(a['app'] for a in also)) if also else '', users_tag=nusers,
                     licence='Odoo licences are billed by Odoo, per user per month.'),
        'method': dict(kicker='how we work', title='NextSprint: Agile, Lean and Six Sigma in [[seven steps]].',
                       lead=f'The best of three proven disciplines in one method. {short} decides at every gate.',
                       groups=groups, steps=steps, loop_line='A rejected deliverable goes back to step 4 until you approve it.'),
        'plan': dict(kicker='phases and timeline', title=f'Live on Odoo in [[about {weeks} weeks]].',
                     lead=f'Four phases from the first workshop to go-live, then 30 days of hypercare. A sprint moves on only with {short}’s approval.',
                     tag='Indicative plan, confirmed at kick-off', weeks=weeks, rows=plan,
                     rule_t='Select a phase', rule_d='to see who does what in it.'),
        'next': dict(kicker='next step', title='Next: [[agree the scope]], then kick off.',
                     lead=f'Your team reviews the proposal, and an adviser walks {short} through anything still open.',
                     steps=[dict(h='Review the proposal', p='The scope and the plan, sent with this deck.'),
                            dict(h='Settle open points', p='A call with an adviser, who recommends what fits and says why.'),
                            dict(h='Sign, then kick off', p='Week 1 starts with the discovery workshop.')],
                     qr_line='Scan to book a call with an adviser', qr_url_text=BOOKING.replace('https://', ''),
                     email='sales@technext.asia', site='technext.asia',
                     disclaimer=DISCLAIMER if (country == 'PH' and any(re.search(r'\bbir\b|\bcas\b', r['today'] + r['odoo_line'], re.I) for r in rows)) else ''),
    }


# ------------------------------------------------------------------ deck.json -> render data
def layout(D):
    """Pixel values the template needs; computed every build (never stored in deck.json)."""
    S = json.loads(json.dumps(D))
    n = len(S['heard']['rows'])
    S['heard']['row_h'] = {1: 200, 2: 172}.get(n, 128)
    k = len(S['apps']['flow'])
    colw = 1360 / k
    S['apps'].update(n=k, top=356, rail_y=160, card_w=252 if k < 5 else 236, half=round(colw / 2, 1), wire_end=round(1360 - colw / 2, 1))
    S['method']['top'] = 352
    seen = {}
    for st in S['method']['steps']:
        st['who'] = 'TechNext' if st['by'] == 'tn' else S['client']['short']
        st['k'] = seen.get(st['g'], 0); seen[st['g']] = st['k'] + 1   # place within its discipline (cascade order)
    P = S['plan']
    weeks, after_w, track = P['weeks'], 170, 1360 - 300
    wz = track - after_w
    pct = lambda px: round(px / track * 100, 3)
    wx = lambda w: wz * w / weeks
    for r in P['rows']:
        for k_, v_ in (('sprints', None), ('ms', None), ('kind', ''), ('text', '')):
            r.setdefault(k_, v_)
        if r.get('w0') is None:   # hypercare: the after-go-live column
            px = after_w - 24
            r['l'], r['w'] = pct(wz + 12), pct(px)
        else:
            px = wx(r['w1']) - wx(r['w0'] - 1) - 12
            r['l'], r['w'] = pct(wx(r['w0'] - 1) + 6), pct(px)
        if r['text'] and len(r['text']) * 9 + 30 > px:   # a label that would be cut is left off: the row label says it
            r['text'] = ''
        if r['sprints'] and any(len(s) * 9 + 18 > px / len(r['sprints']) for s in r['sprints']):
            r['sprints'] = [f'S{i + 1}' for i in range(len(r['sprints']))]
        if r.get('ms'):
            r['ms'] = dict(label=r['ms'], l=pct(wx(r['w1']) - 6))
    P.update(top=356, after_w=after_w, row_h=76)
    return S


def render(D, prof, prof_dir, out_html):
    import jinja2
    from markupsafe import Markup, escape
    S = layout(D)
    C = dict(S['client'])
    colour = (prof.get('brand') or {}).get('colour', '')
    C['colour_ui'], cnote = client_ui_colour(colour)
    logo = (prof.get('brand') or {}).get('logo')
    lp = (prof_dir / logo) if logo else None
    C['logo_uri'] = data_uri(lp) if lp and lp.exists() else None
    lnote = '' if lp and lp.exists() else 'no logo file: type nameplate used'
    cat = apps_catalogue()
    for r in S['heard']['rows']:
        mod = r.get('module') or (cat.get(ALIAS.get(r['app'].lower(), r['app']).lower()) or {}).get('m')
        if not mod or not (ASSETS / 'odoo' / f'{mod}.svg').exists():
            raise SystemExit(f"slide 2: no Odoo icon for app {r['app']!r}: set heard.rows[].module in deck.json")
        r['icon'] = data_uri(ASSETS / 'odoo' / f'{mod}.svg')
    for f in S['apps']['flow']:
        f['icon'] = data_uri(ASSETS / 'odoo' / f"{f['module']}.svg")
    all_text = json.dumps(D, ensure_ascii=False)
    A = dict(fonts_css=Markup(fonts_css(all_text)), logo=data_uri(ASSETS / 'img/logo-horizontal.png'),
             logo_white=data_uri(ASSETS / 'img/logo-horizontal-white.png'), qr_svg=Markup(qr_svg(BOOKING)),
             favicon='data:image/svg+xml;base64,' + base64.b64encode(b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#3167CA"/><path d="M7 16.5 25 8l-5.5 17-4.2-6.6z" fill="#fff"/></svg>').decode())

    def hl(s):
        s = str(escape(s))
        return Markup(re.sub(r'\[\[(.+?)\]\]', r'<span class="hl">\1</span>', s, count=1).replace('[[', '').replace(']]', ''))

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(SKILL / 'template')), autoescape=True,
                             comment_start_string='{##', comment_end_string='##}', undefined=jinja2.StrictUndefined,
                             trim_blocks=True, lstrip_blocks=True)
    env.filters['hl'] = hl
    J = dict(apps=[dict(app=f['app'], doc=f['doc'], record=f['record'], status=f['status']) for f in S['apps']['flow']],
             plan=[dict(label=r['label'], when=r['when'], detail=r['detail']) for r in S['plan']['rows']],
             plan_rule=dict(t=S['plan']['rule_t'], d=S['plan']['rule_d']))
    meta = (f"TechNext presentation for {C['name']}: who we are, what we heard, the Odoo apps, NextSprint, the plan and the next step.")
    out = env.get_template('deck.html.j2').render(C=C, S=S, A=A, J=J, D=dict(meta_desc=meta), total=6)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(out, encoding='utf-8', newline='\n')
    return [x for x in (cnote, lnote) if x]


def validate_deck(D):
    """Plan-validate-execute: catch a bad hand edit of deck.json with a message that says what is allowed."""
    out = []
    need = {'who': ['kicker', 'title', 'lead', 'figures', 'plate'], 'heard': ['kicker', 'title', 'lead', 'rows'],
            'apps': ['kicker', 'title', 'lead', 'flow'], 'method': ['kicker', 'title', 'lead', 'groups', 'steps'],
            'plan': ['kicker', 'title', 'lead', 'weeks', 'rows'], 'next': ['kicker', 'title', 'lead', 'steps']}
    for sec, keys in need.items():
        for k in keys:
            if k not in D.get(sec, {}):
                out.append(f'{sec}.{k} is missing (run with --regen to see the default)')
        t = D.get(sec, {}).get('title', '')
        if t.count('[[') != 1 or t.count(']]') != 1:
            out.append(f'{sec}.title needs exactly one [[marker phrase]]: {t!r}')
        if len(re.sub(r'\[\[|\]\]', '', t)) > 70:
            out.append(f'{sec}.title is over 70 characters (titles are 2-3 lines at most): shorten it, do not shrink the type')
    if not 1 <= len(D.get('heard', {}).get('rows', [])) <= 3:
        out.append('heard.rows must hold 1 to 3 pain points (split, never shrink: move the rest to the proposal)')
    if not 1 <= len(D.get('apps', {}).get('flow', [])) <= 6:
        out.append('apps.flow must hold 1 to 6 apps (the rest go in apps.also)')
    if len(D.get('method', {}).get('steps', [])) != 7:
        out.append('method.steps must hold the seven NextSprint steps')
    if [g.get('span') for g in D.get('method', {}).get('groups', [])] and sum(g.get('span', 0) for g in D['method']['groups']) != 7:
        out.append('method.groups spans must add up to 7 (Lean 3, Agile 2, Six Sigma 2)')
    for r in D.get('plan', {}).get('rows', []):
        if r.get('w1') and r['w1'] > D['plan'].get('weeks', 0):
            out.append(f"plan row {r.get('label')!r} ends after week {D['plan'].get('weeks')}: raise plan.weeks")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('profile')
    ap.add_argument('--out')
    ap.add_argument('--regen', action='store_true', help='rebuild deck.json from the profile (overwrites edits)')
    ap.add_argument('--rev')
    ap.add_argument('--status')
    a = ap.parse_args()
    ppath, prof = load_profile(a.profile)
    pdir = ppath.parent
    dj = pdir / 'deck.json'
    pmd5 = hashlib.md5(ppath.read_bytes()).hexdigest()
    cat = apps_catalogue()
    if a.regen or not dj.exists():
        D = default_deck(prof, cat)
        D['_profile_md5'] = pmd5
        dj.write_text(json.dumps(D, ensure_ascii=False, indent=2), encoding='utf-8')
        print('wrote', dj)
    else:
        D = json.loads(dj.read_text(encoding='utf-8-sig'))
        if D.get('_profile_md5') != pmd5:
            print('NOTE: client-profile.json changed since deck.json was written. Check the copy, or run with --regen.')
    if a.rev:
        D['rev'] = a.rev
    if a.status:
        D['status'] = a.status
    if a.rev or a.status:
        dj.write_text(json.dumps(D, ensure_ascii=False, indent=2), encoding='utf-8')
    problems = validate_deck(D)
    if problems:
        print('deck.json problems (fix them, then build again):')
        for p_ in problems:
            print('  -', p_)
        sys.exit(1)
    print('storyline (the six headlines must tell the story alone and end on the ask):')
    for k_, sec in enumerate(['who', 'heard', 'apps', 'method', 'plan', 'next'], 1):
        print(f'  {k_}. ' + re.sub(r'\[\[|\]\]', '', D[sec]['title']))
    out = pathlib.Path(a.out) if a.out else pdir / 'out'
    html_path = out / 'presentation.html'
    notes = render(D, prof, pdir, html_path)
    kb = html_path.stat().st_size // 1024
    print(f'built {html_path}  ({kb} KB, 6 slides, rev {D["rev"]} {D["status"]})')
    for n in notes:
        print('  note:', n)
    sys.path.insert(0, str(HERE))
    import check_deck
    ok = check_deck.check(html_path, D)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
