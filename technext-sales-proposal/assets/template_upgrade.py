"""One-off upgrade: adds the palette picker (8 presets + custom colour), bilingual
chart labels ("Việt||English"), starred must-read nav items, the pre-meeting
section, the pinned pre-meeting panel, the Sales Playbook section and the ROI
calculator to proposal-template.html.  Also exposes inject_palette() so an
already-built proposal can get the palette picker without a rebuild.

Usage:
  python template_upgrade.py template  <proposal-template.html>
  python template_upgrade.py palette   <some-proposal.html>
"""
import re, sys

PALETTES = [
    # key, VI name, EN name, main, dark, light, accent2, accent3
    ('teal',     'Xanh ngọc',     'Teal',            '#19c6c6', '#0fa8b8', '#37e0c8', '#3b82f6', '#6366f1'),
    ('orange',   'Cam kem',       'Warm orange',     '#e8734a', '#d4602f', '#f2a07a', '#c8853c', '#b85c38'),
    ('blue',     'Xanh TechNext', 'TechNext blue',   '#3167ca', '#22488f', '#6e9bff', '#3b82f6', '#6a4fd6'),
    ('purple',   'Tím',           'Purple',          '#8b5cf6', '#7c3aed', '#c4b5fd', '#6366f1', '#ec4899'),
    ('green',    'Xanh lá',       'Green',           '#22c55e', '#16a34a', '#86efac', '#14b8a6', '#0ea5e9'),
    ('wine',     'Đỏ rượu vang',  'Wine red',        '#be123c', '#9f1239', '#fb7185', '#db2777', '#7c3aed'),
    ('charcoal', 'Xám than',      'Charcoal',        '#64748b', '#475569', '#cbd5e1', '#334155', '#0ea5e9'),
    ('amber',    'Vàng hổ phách', 'Amber',           '#f59e0b', '#d97706', '#fcd34d', '#f97316', '#ef4444'),
]

def palette_css():
    rules = []
    for k, _, _, m, d, l, a2, a3 in PALETTES:
        rules.append(f'html[data-palette="{k}"]{{--teal:{m};--teal2:{d};--aqua:{l};--blue:{a2};--indigo:{a3};'
                     f'--grad:linear-gradient(135deg,{m},{a2} 55%,{a3});--grad2:linear-gradient(135deg,{l},{m})}}')
    rules.append('#palPop{position:fixed;left:16px;top:calc(120px + env(safe-area-inset-top,0px));z-index:80;width:250px;background:var(--panel);'
                 'border:1px solid var(--line);border-radius:14px;padding:14px;box-shadow:var(--shadow)}')
    rules.append('#palPop h5{margin:0 0 10px;font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}')
    rules.append('#palPop .pal-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}')
    rules.append('#palPop .pal-sw{height:38px;border-radius:10px;border:2px solid transparent;cursor:pointer;position:relative}')
    rules.append('#palPop .pal-sw[aria-pressed="true"]{border-color:var(--ink)}')
    rules.append('#palPop .pal-sw:focus-visible{outline:2px solid var(--ink);outline-offset:2px}')
    rules.append('#palPop .pal-row{display:flex;align-items:center;gap:8px;margin-top:12px;font-size:.82rem;color:var(--ink2)}')
    rules.append('#palPop input[type=color]{width:44px;height:30px;border:1px solid var(--line);border-radius:8px;background:transparent;padding:0;cursor:pointer}')
    rules.append('#palPop .pal-reset{margin-left:auto;background:transparent;border:1px solid var(--line);color:var(--ink2);border-radius:8px;padding:5px 9px;cursor:pointer;font-size:.78rem}')
    rules.append('#palPop .pal-name{margin-top:8px;font-size:.78rem;color:var(--muted)}')
    return '<style id="palette-css">' + ''.join(rules) + '</style>'

def palette_html():
    sw = ''.join(f'<button type="button" class="pal-sw" data-pal="{k}" title="{vi} / {en}" aria-label="{vi} / {en}" '
                 f'style="background:linear-gradient(135deg,{m},{a2})" onclick="setPalette(\'{k}\')"></button>'
                 for k, vi, en, m, d, l, a2, a3 in PALETTES)
    return ('<div id="palPop" hidden role="dialog" aria-label="Chọn màu / Choose colours">'
            '<h5><span class="t-vi">Chọn màu giao diện</span><span class="t-en">Choose a colour theme</span></h5>'
            f'<div class="pal-grid">{sw}</div>'
            '<div class="pal-row"><label for="palCustom"><span class="t-vi">Màu tùy chỉnh</span><span class="t-en">Custom colour</span></label>'
            '<input type="color" id="palCustom" oninput="setCustomColour(this.value)">'
            '<button type="button" class="pal-reset" onclick="resetPalette()"><span class="t-vi">Mặc định</span><span class="t-en">Default</span></button></div>'
            '<div class="pal-name" id="palName"></div></div>')

PALETTE_JS = r'''<script id="palette-js">
/* ---------- colour themes: 8 presets + custom; default = <html data-palette-default> ---------- */
const PALETTE_NAMES = __NAMES__;
function _hex2rgb(h){h=h.replace('#','');return [0,2,4].map(i=>parseInt(h.substr(i,2),16));}
function _rgb2hex(r){return '#'+r.map(v=>Math.max(0,Math.min(255,Math.round(v))).toString(16).padStart(2,'0')).join('');}
function _mix(h,t,a){const x=_hex2rgb(h),y=_hex2rgb(t);return _rgb2hex(x.map((v,i)=>v+(y[i]-v)*a));}
function _clearCustom(){['--teal','--teal2','--aqua','--grad','--grad2'].forEach(p=>document.documentElement.style.removeProperty(p));}
function _palLabel(t){const n=document.getElementById('palName');if(n)n.innerHTML=t;}
function _markPal(k){document.querySelectorAll('#palPop .pal-sw').forEach(b=>b.setAttribute('aria-pressed',b.dataset.pal===k?'true':'false'));}
function setPalette(k,silent){
  _clearCustom();
  document.documentElement.setAttribute('data-palette',k);
  _markPal(k);
  const nm=PALETTE_NAMES[k]||[k,k];
  _palLabel('<span class="t-vi">Đang dùng: '+nm[0]+'</span><span class="t-en">Current: '+nm[1]+'</span>');
  try{localStorage.setItem('sp_palette',k);localStorage.removeItem('sp_custom');}catch(e){}
  if(!silent && typeof reRenderCharts==='function' && typeof Chart!=='undefined') reRenderCharts();
}
function setCustomColour(hex,silent){
  const s=document.documentElement.style;
  s.setProperty('--teal',hex);s.setProperty('--teal2',_mix(hex,'#000000',.18));s.setProperty('--aqua',_mix(hex,'#ffffff',.35));
  s.setProperty('--grad','linear-gradient(135deg,'+hex+',var(--blue) 55%,var(--indigo))');
  s.setProperty('--grad2','linear-gradient(135deg,'+_mix(hex,'#ffffff',.35)+','+hex+')');
  _markPal('');
  _palLabel('<span class="t-vi">Màu tùy chỉnh: '+hex+'</span><span class="t-en">Custom: '+hex+'</span>');
  try{localStorage.setItem('sp_custom',hex);}catch(e){}
  if(!silent && typeof reRenderCharts==='function' && typeof Chart!=='undefined') reRenderCharts();
}
function resetPalette(){
  try{localStorage.removeItem('sp_palette');localStorage.removeItem('sp_custom');}catch(e){}
  setPalette(document.documentElement.getAttribute('data-palette-default')||'teal');
}
function togglePalette(){const p=document.getElementById('palPop');if(p)p.hidden=!p.hidden;}
document.addEventListener('click',function(e){const p=document.getElementById('palPop');
  if(p&&!p.hidden&&!p.contains(e.target)&&!(e.target.closest&&e.target.closest('[data-pal-toggle]')))p.hidden=true;});
document.addEventListener('keydown',function(e){if(e.key==='Escape'){const p=document.getElementById('palPop');if(p)p.hidden=true;}});
function syncPal(){
  if(typeof PAL==='undefined')return;
  const cs=getComputedStyle(document.documentElement);
  const g=v=>(cs.getPropertyValue(v)||'').trim();
  if(g('--teal'))PAL[0]=g('--teal'); if(g('--blue'))PAL[1]=g('--blue');
  if(g('--indigo'))PAL[2]=g('--indigo'); if(g('--aqua'))PAL[8]=g('--aqua');
}
(function(){
  let k=null,c=null;try{k=localStorage.getItem('sp_palette');c=localStorage.getItem('sp_custom');}catch(e){}
  const def=document.documentElement.getAttribute('data-palette-default')||'teal';
  setPalette(k&&PALETTE_NAMES[k]?k:def,true);
  if(!c&&!k) c=document.documentElement.getAttribute('data-palette-custom');
  if(c) setCustomColour(c,true);
})();
</script>'''

def palette_js():
    names = '{' + ','.join(f'"{k}":["{vi}","{en}"]' for k, vi, en, *_ in PALETTES) + '}'
    return PALETTE_JS.replace('__NAMES__', names)

PAL_BTN = "'  <button class=\"tb-btn\" data-pal-toggle onclick=\"togglePalette()\" title=\"' + (lang==='en'?'Colours':'Màu sắc') + '\" aria-label=\"Colours\">🎨</button>'\n    + "

def inject_palette(s):
    if 'id="palette-css"' in s:
        return s
    # CSS right before </head> (after the template's own :root so presets override it)
    s = s.replace('</head>', palette_css() + '\n</head>', 1)
    # 🎨 button inside the sidebar button row, next to ◐
    anchor = "'  <button class=\"tb-btn\" onclick=\"toggleTheme()\">◐</button>'"
    assert anchor in s, 'theme button anchor not found'
    s = s.replace(anchor, anchor + "\n    + '  <button class=\"tb-btn\" data-pal-toggle onclick=\"togglePalette()\" aria-label=\"Colours / Màu sắc\">🎨</button>'", 1)
    # PAL must be mutable so charts follow the palette
    s = s.replace('const PAL = [', 'let PAL = [', 1)
    s = s.replace('function renderCharts(){ chartDefs.forEach(fn => fn()); }',
                  'function renderCharts(){ if (typeof syncPal === \'function\') syncPal(); chartDefs.forEach(fn => fn()); }', 1)
    # default palette attribute on <html>
    if 'data-palette-default=' not in s:
        s = re.sub(r'<html([^>]*)>', lambda m: '<html' + m.group(1) + ' data-palette-default="teal">', s, count=1)
    # popover + script at the end of body
    j = s.rindex('</body>')
    s = s[:j] + palette_html() + palette_js() + '\n' + s[j:]
    return s

# ---------------------------------------------------------------------------
# template-only upgrades
# ---------------------------------------------------------------------------
CHART_I18N_JS = r'''
/* ---------- bilingual chart text: write labels as "Tiếng Việt||English" ---------- */
function trChartStr(v){
  if (typeof v !== 'string' || v.indexOf('||') < 0) return v;
  const p = v.split('||');
  return (document.body.getAttribute('data-lang') === 'en') ? (p[1] || p[0]).trim() : p[0].trim();
}
function trChartCfg(cfg){
  const d = cfg.data || {};
  if (Array.isArray(d.labels)) d.labels = d.labels.map(trChartStr);
  (d.datasets || []).forEach(ds => { if (ds.label) ds.label = trChartStr(ds.label); });
  const sc = (cfg.options || {}).scales || {};
  Object.values(sc).forEach(ax => { if (ax && ax.title && ax.title.text) ax.title.text = trChartStr(ax.title.text); });
  const ti = ((cfg.options || {}).plugins || {}).title;
  if (ti && ti.text) ti.text = trChartStr(ti.text);
  return cfg;
}
'''

STAR_DEFAULT = ['pre-meeting', 'exec-summary', 'solution-odoo-erp', 'pain-solution-matrix', 'competitor-deep-dive',
                'pricing-strategy', 'tool-profit-estimator', 'tool-quotation', 'sales-playbook', 'tool-discovery-questions']

def bi(v, e): return f'<span class="t-vi">{v}</span><span class="t-en">{e}</span>'

PRE_MEETING = ('<section id="pre-meeting" data-star="1" data-nav-vi="Trước khi họp cần đọc" data-nav-en="Read before the meeting" data-grp-vi="Tổng quan" data-grp-en="Overview">\n'
 '      <div class="wrap"><span class="sec-tag t-vi">ĐỌC TRƯỚC</span><span class="sec-tag t-en">PRE-READ</span>'
 f'<h2>{bi("Trước khi họp cần đọc những điều này", "Read this before the meeting")}</h2>'
 f'<h3>{bi("★ Các mục quan trọng cần đọc", "★ Must-read sections")}</h3><div class="mr-list" id="mustRead"></div>'
 f'<h3 id="pm-company">{bi("1. Thông tin về công ty", "1. The company")}</h3><p class="placeholder-note">PLACEHOLDER — 5–7 cited bullets: history, locations, core business, current systems, digital presence, churn/risk signals</p>'
 f'<h3 id="pm-person">{bi("2. Người bạn sẽ nói chuyện", "2. Who you’ll meet")}</h3><p class="placeholder-note">PLACEHOLDER — .grid.g2: left card = person (role A-grade + links, priorities, unverified career as grade C); right card = how to talk to them + meeting goal. Public professional info only.</p>'
 f'<h3 id="pm-issues">{bi("3. Vấn đề hiện tại: hiện trạng, đối thủ, hướng giải quyết", "3. Current issues: AS-IS, competitors, TO-BE")}</h3><p class="placeholder-note">PLACEHOLDER — .tbl with columns Issue | AS-IS | Competitors | TO-BE (.assess), one row per confirmed pain</p>'
 f'<h3 id="pm-unknowns">{bi("4. Những điều AI chưa thu thập được: cần hỏi trong buổi họp", "4. What AI couldn’t collect: ask in the meeting")}</h3><p class="placeholder-note">PLACEHOLDER — .tbl with columns Unknown | Why AI couldn’t get it | Question to ask (8–10 rows)</p>'
 '</div>\n    </section>\n\n    ')

SALES_PLAYBOOK = ('<section id="sales-playbook" data-star="1" data-nav-vi="🎯 Sales Playbook" data-nav-en="🎯 Sales Playbook" data-grp-vi="Công cụ &amp; Tài liệu" data-grp-en="Tools &amp; Documents">\n'
 '      <div class="wrap"><span class="sec-tag t-vi">BÁN HÀNG</span><span class="sec-tag t-en">SALES</span>'
 f'<h2>{bi("🎯 Sales Playbook", "🎯 Sales Playbook")}</h2>'
 f'<h3>{bi("Câu chuyện 30 giây", "30-second pitch")}</h3><p class="placeholder-note">PLACEHOLDER — one .callout: pain → cost → fix → timeline, in the client’s own numbers</p>'
 f'<h3>{bi("Câu chuyện 2 phút", "2-minute story")}</h3><p class="placeholder-note">PLACEHOLDER — 5-step ordered list: where they are → bottleneck → cost → fix → how to start</p>'
 f'<h3>{bi("Trả lời phản đối thường gặp", "Common objections")}</h3><p class="placeholder-note">PLACEHOLDER — .tbl They say | TechNext answers, 8–10 rows grounded in this client’s facts</p>'
 f'<h3>{bi("Kịch bản demo 15 phút", "15-minute demo script")}</h3><p class="placeholder-note">PLACEHOLDER — .tbl Time | What to show, 5–6 rows</p>'
 f'<h3>{bi("Bước cần chốt sau buổi họp", "What to close after the meeting")}</h3><p class="placeholder-note">PLACEHOLDER — 3–4 concrete next steps (discovery, sample data, technical session)</p>'
 '</div>\n    </section>\n\n    ')

ROI_FIELDS = [
 ('roiBill', 'Doanh thu xuất hóa đơn mỗi tháng', 'Monthly billed revenue', 1000000, 10000),
 ('roiLag', 'Số ngày ra hóa đơn hiện nay', 'Days to invoice today', 10, 1),
 ('roiTarget', 'Số ngày ra hóa đơn sau giải pháp', 'Days to invoice after', 1, 1),
 ('roiLeak', 'Việc làm xong nhưng quên tính tiền (%)', 'Unbilled work (%)', 2, 0.5),
 ('roiRate', 'Chi phí vốn (%/năm)', 'Cost of capital (%/yr)', 8, 0.5),
 ('roiHours', 'Giờ nhập liệu tiết kiệm/tháng', 'Keying hours saved/month', 80, 5),
 ('roiHourCost', 'Chi phí 1 giờ công văn phòng', 'Office hour cost', 200, 10),
 ('roiCost', 'Chi phí dự án + license năm đầu', 'Project + first-year licence', 1000000, 10000),
]

def roi_block():
    inputs = ''.join(f'<label class="roi-f" for="{i}"><span>{bi(v, e)}</span><input id="{i}" type="number" min="0" step="{st}" value="{d}"></label>'
                     for i, v, e, d, st in ROI_FIELDS)
    outs = [('roCash', 'Tiền mặt được giải phóng (một lần)', 'Cash released (one-off)'), ('roFin', 'Tiết kiệm chi phí vốn/năm', 'Financing saved/yr'),
            ('roLeak', 'Thu hồi phần quên tính tiền/năm', 'Recovered unbilled work/yr'), ('roAdmin', 'Tiết kiệm nhập liệu/năm', 'Keying time saved/yr'),
            ('roYear', 'Tổng lợi ích/năm', 'Total annual benefit'), ('roPay', 'Thời gian hoàn vốn', 'Payback')]
    outhtml = ''.join(f'<div class="kpi"><div class="v" id="{i}">—</div><div class="l">{bi(v, e)}</div></div>' for i, v, e in outs)
    return ('<div class="roi-tool" id="roiTool" data-currency="$">'
     '<style>.roi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:14px 0}.roi-f{display:grid;gap:4px;font-size:.88rem}'
     '.roi-f input{padding:9px 10px;border-radius:8px;border:1px solid var(--line);background:var(--panel);color:inherit;font:inherit;font-variant-numeric:tabular-nums}'
     '.roi-f input:focus{outline:2px solid var(--teal);border-color:var(--teal)}.roi-out{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}'
     '.roi-out .v{font-size:1.35rem;font-variant-numeric:tabular-nums}</style>'
     f'<h3>{bi("Công cụ tính ROI", "ROI calculator")}</h3>'
     f'<p>{bi("Nhập số của khách trong buổi họp; kết quả tự tính lại ngay. Số mặc định là giả định minh họa.", "Enter the client’s numbers during the meeting; results update instantly. Defaults are illustrative.")}</p>'
     f'<div class="roi-grid">{inputs}</div><div class="roi-out">{outhtml}</div>'
     '<p style="font-size:.85rem;opacity:.75;margin-top:10px">' + bi('Tiền giải phóng = doanh thu/tháng × (số ngày giảm ÷ 30). Lợi ích/năm = chi phí vốn trên tiền giải phóng + phần quên tính tiền thu hồi + giờ nhập liệu tiết kiệm. Hoàn vốn = chi phí ÷ (lợi ích/năm ÷ 12).',
        'Cash released = monthly billing × (days saved ÷ 30). Annual benefit = financing on released cash + recovered unbilled work + keying hours saved. Payback = cost ÷ (annual benefit ÷ 12).') + '</p>'
     '<span class="assess">' + bi('Công cụ minh họa của TechNext; không phải cam kết tài chính.', 'TechNext illustration; not a financial commitment.') + '</span>'
     '<script>(function(){function v(i){var e=document.getElementById(i);return e?parseFloat(e.value)||0:0}'
     'function cur(){var t=document.getElementById("roiTool");return t?t.getAttribute("data-currency")||"":""}'
     'function money(x){return cur()+Math.round(x).toLocaleString("en-US")}'
     'function calc(){var bill=v("roiBill");var days=Math.max(0,v("roiLag")-v("roiTarget"));var cash=bill*days/30;var fin=cash*v("roiRate")/100;'
     'var leak=bill*12*v("roiLeak")/100;var adm=v("roiHours")*v("roiHourCost")*12;var yr=fin+leak+adm;var en=document.body.getAttribute("data-lang")==="en";'
     'var pay=yr>0?v("roiCost")/(yr/12):0;var set=function(i,t){var e=document.getElementById(i);if(e)e.textContent=t};'
     'set("roCash",money(cash));set("roFin",money(fin));set("roLeak",money(leak));set("roAdmin",money(adm));set("roYear",money(yr));'
     'set("roPay",yr>0?(pay.toFixed(1)+(en?" months":" tháng")):"—")}'
     'document.addEventListener("input",function(e){if(e.target&&/^roi/.test(e.target.id))calc()});'
     'document.addEventListener("click",function(){setTimeout(calc,0)});calc();})();</script></div>')

PINNED = ('<style>#pmBox{position:fixed;bottom:calc(20px + env(safe-area-inset-bottom,0px));right:24px;max-height:calc(100vh - 100px);overflow:auto;'
 'width:min(340px,calc(100vw - 32px));z-index:70;box-sizing:border-box;border:1.5px solid var(--teal);border-radius:14px;padding:16px 16px 12px;background:var(--panel);box-shadow:0 14px 40px rgba(0,0,0,.4)}'
 '#pmBox h3{margin:0 36px 12px 0;font-size:1.05rem;line-height:1.3}#pmBox .pm-list{display:grid;gap:8px}'
 '#pmBox .pm-item{display:grid;grid-template-columns:28px 1fr;gap:10px;align-items:center;padding:9px 10px;border:1px solid var(--line);border-radius:10px;color:inherit;text-decoration:none;font-size:.92rem;line-height:1.35}'
 '#pmBox .pm-item:hover,#pmBox .pm-item:focus-visible{border-color:var(--teal);outline:none}'
 '#pmBox .pm-item b{display:inline-grid;place-items:center;width:26px;height:26px;border-radius:50%;border:1px solid var(--teal);color:var(--teal);font-size:12px}'
 '#pmBox .pm-x{position:absolute;top:10px;right:10px;width:30px;height:30px;border-radius:8px;border:1px solid var(--line);background:transparent;color:inherit;font-size:15px;cursor:pointer}'
 '#pmOpen{position:fixed;bottom:calc(20px + env(safe-area-inset-bottom,0px));right:24px;z-index:70;border:1.5px solid var(--teal);background:var(--panel);color:var(--teal);border-radius:999px;padding:10px 16px;font-weight:600;font-size:.9rem;cursor:pointer}'
 '@keyframes pmGlow{0%,100%{box-shadow:0 14px 40px rgba(0,0,0,.4),0 0 0 0 var(--teal)}50%{box-shadow:0 14px 40px rgba(0,0,0,.4),0 0 20px 4px var(--teal)}}'
 '#pmBox,#pmOpen{animation:pmGlow 1.8s ease-in-out infinite}#pmBox:hover,#pmOpen:hover{animation-play-state:paused}'
 '@media (max-width:700px){#pmBox{right:16px;bottom:calc(12px + env(safe-area-inset-bottom,0px))}}'
 '@media (prefers-reduced-motion: reduce){#pmBox,#pmOpen{animation:none}}'
 '#sidenav a.nav-star{font-weight:600}#sidenav .star{color:#f5c542;margin-right:6px}'
 '.mr-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:8px;margin:10px 0 4px}'
 '.mr-list a{display:grid;grid-template-columns:22px 1fr;gap:8px;padding:10px 12px;border:1px solid var(--line);border-radius:10px;color:inherit;text-decoration:none}'
 '.mr-list a:hover,.mr-list a:focus-visible{border-color:#f5c542;outline:none}.mr-list .star{color:#f5c542}</style>'
 '<aside id="pmBox" aria-label="Pre-meeting"><button type="button" class="pm-x" onclick="pmShow(false)" aria-label="Đóng / Close">✕</button>'
 f'<h3>{bi("Trước khi họp cần đọc những điều này", "Read these before the meeting")}</h3><div class="pm-list">'
 + ''.join(f'<a class="pm-item" href="#{a}"><b>{n}</b><strong>{bi(v, e)}</strong></a>' for n, (a, v, e) in enumerate([
     ('pm-company', 'Thông tin về công ty', 'The company'), ('pm-person', 'Người bạn sẽ nói chuyện trong buổi họp', 'Who you’ll meet'),
     ('pm-issues', 'Những vấn đề hiện tại (AS-IS · đối thủ · TO-BE)', 'Current issues (AS-IS · competitors · TO-BE)'),
     ('pm-unknowns', 'Những điều AI chưa thu thập được: cần hỏi đối tác', 'What AI couldn’t collect: ask the partner')], 1))
 + '</div></aside>'
 f'<button type="button" id="pmOpen" hidden onclick="pmShow(true)">{bi("📋 Trước khi họp", "📋 Before the meeting")}</button>'
 '<script>function pmShow(v){document.getElementById("pmBox").hidden=!v;document.getElementById("pmOpen").hidden=v;}'
 '(function(){var box=document.getElementById("mustRead");if(!box)return;var h="";'
 'document.querySelectorAll("main > section[data-star]").forEach(function(s){if(s.id==="pre-meeting")return;'
 'h+="<a href=\\"#"+s.id+"\\"><span class=\\"star\\">★</span><span><span class=\\"t-vi\\">"+s.dataset.navVi+"</span><span class=\\"t-en\\">"+s.dataset.navEn+"</span></span></a>";});'
 'box.innerHTML=h;})();</script>')

def upgrade_template(s):
    # chart i18n
    if 'function trChartStr' not in s:
        s = s.replace('function mkChart(id, cfg){', CHART_I18N_JS + 'function mkChart(id, cfg){', 1)
        s = s.replace('  const ch = new Chart(el, cfg);', '  trChartCfg(cfg);\n  const ch = new Chart(el, cfg);', 1)
        old = "  document.body.setAttribute('data-lang', l);\n  buildNav();"
        assert old in s
        s = s.replace(old, old + "\n  if (typeof CHARTS !== 'undefined' && CHARTS.length && typeof Chart !== 'undefined') reRenderCharts();", 1)
    # star in nav
    old = "      html += `<a href=\"#${s.id}\">${label}</a>`;"
    if old in s:
        s = s.replace(old, "      html += `<a href=\"#${s.id}\"${s.dataset.star ? ' class=\"nav-star\"' : ''}>${s.dataset.star ? '<span class=\"star\" aria-hidden=\"true\">★</span>' : ''}${label}</a>`;", 1)
    # default stars
    for sid in STAR_DEFAULT:
        if sid in ('pre-meeting', 'sales-playbook'):
            continue
        s = re.sub(r'<section id="' + sid + r'"(?! data-star)', f'<section id="{sid}" data-star="1"', s, count=1)
    # new sections
    if 'id="pre-meeting"' not in s:
        i = s.index('<section id="overview"')
        s = s[:i] + PRE_MEETING + s[i:]
    if 'id="sales-playbook"' not in s:
        i = s.index('<section id="tool-discovery-questions"')
        s = s[:i] + SALES_PLAYBOOK + s[i:]
    # ROI calculator inside Profit Estimator
    if 'id="roiTool"' not in s:
        m = re.search(r'(<section id="tool-profit-estimator".*?)(</div>\s*</section>)', s, re.S)
        s = s[:m.start(2)] + roi_block() + s[m.start(2):]
    # pinned panel
    if 'id="pmBox"' not in s:
        j = s.rindex('</body>')
        s = s[:j] + PINNED + '\n' + s[j:]
    return inject_palette(s)

if __name__ == '__main__':
    mode, path = sys.argv[1], sys.argv[2]
    s = open(path, encoding='utf-8').read()
    s = upgrade_template(s) if mode == 'template' else inject_palette(s)
    open(path, 'w', encoding='utf-8').write(s)
    print('upgraded', path, len(s))
