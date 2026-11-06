// Sales Journey validation as pure functions (no I/O): a port of journey/tools/validate.py, same checks, same order,
// same Vietnamese messages. Skills and tests look errors up by keyword, so do not reword them.
//   checkPlaybook(pb)                      -> string[]
//   checkLead(ld, pb, {slug?, pageIds?})   -> string[]   pageIds = ids already used by the template (see pageIdsOf)
//   pageIdsOf(templateHtml)                -> string[]
// Shared vectors: tests/vectors/journey.json.
import { RULES, W_CLASS as W } from "./journey-rules.mjs";

const SLUG = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const KINDS = new Set(["step", "script", "checklist", "qa", "recipe", "framework", "rule", "prompt", "holiday"]);
const VAR = new RegExp(`\\{(${W}+)\\}`, "gu");
const SCHEME = /^[A-Za-z][\p{L}\p{N}_+.-]*:/u;
const IDS = new RegExp(`(?<!${W})id="([^"]+)"`, "gu");
const LINK = new RegExp(`(?<!${W})(wa\\.me|zalo\\.me)/\\+?\\p{Nd}|(?<!${W})tel:|(?<!${W})mailto:`, "iu");
const URLS = /https?:\/\/\S+/giu;

const py = (x) => (x == null ? "None" : String(x)); // how Python's f-string shows a value
const cut = (t, n) => Array.from(String(t)).slice(0, n).join(""); // Python slices by code point, JS by UTF-16 unit
const isStr = (v) => typeof v === "string";
const blank = (v) => !isStr(v) || !v.trim();
const inRange = (n, [lo, hi]) => lo <= n && n <= hi;
const has = (o, k) => Object.prototype.hasOwnProperty.call(o, k);

function strings(x, out = []) {
  if (isStr(x)) out.push(x);
  else if (Array.isArray(x)) x.forEach((v) => strings(v, out));
  else if (x && typeof x === "object") Object.values(x).forEach((v) => strings(v, out));
  return out;
}

export const hasContact = (t) => LINK.test(t) || RULES.contact.test(t.replace(URLS, " ")); // shared with lib/lead.mjs
// A src or source.ref is an https:// URL or a plain label with no scheme ("brief · verify"); shared with lib/lead.mjs.
export const badLink = (u) => SCHEME.test(String(u || "").trim()) && !String(u).startsWith("https://");

const daypart = (texts, where) => texts.filter((t) => RULES.no_daypart.test(t)).map((t) => `chào theo buổi ở ${where}: ${cut(t, 60)}`);

export function pageIdsOf(templateHtml) {
  return [...new Set([...templateHtml.matchAll(IDS)].map((m) => m[1]))];
}

export function checkPlaybook(pb) {
  const errs = [], keys = new Set(), items = pb.items ?? [];
  if (!Number.isInteger(pb.version)) errs.push("playbook.version phải là số nguyên");
  items.forEach((it, i) => {
    for (const f of ["key", "kind", "version", "status", "body"]) if (!has(it, f)) errs.push(`items[${i}] thiếu ${f}`);
    if (!KINDS.has(it.kind)) errs.push(`items[${i}] kind sai: ${py(it.kind)}`);
    if (keys.has(it.key)) errs.push(`key trùng: ${py(it.key)}`);
    keys.add(it.key);
  });
  return errs.concat(daypart(strings(items.map((it) => it.body)), "playbook"));
}

export function checkLead(ld, pb, { slug, pageIds = [] } = {}) {
  const errs = ["slug", "version", "playbook_version", "lead", "profile", "vars", "kit", "versions"].filter((f) => !has(ld, f)).map((f) => `thiếu ${f}`);
  if (errs.length) return errs;
  const PAGE_IDS = new Set(pageIds);
  if (!SLUG.test(ld.slug)) errs.push("slug chỉ gồm a-z, 0-9 và dấu -");
  if (slug != null && ld.slug !== slug) errs.push(`slug ${ld.slug} trong lead.json khác thư mục ${slug}`);
  if (ld.playbook_version !== pb.version) errs.push(`playbook_version ${py(ld.playbook_version)} khác playbook ${py(pb.version)}`);
  for (const [k, f] of Object.entries(ld.profile)) {
    if (!RULES.status.includes(f?.s)) errs.push(`profile.${k}: s phải là assumed hoặc confirmed`);
    if (f?.s === "assumed" && !f.src) errs.push(`profile.${k}: assumed thì phải có src`);
  }
  for (const f of ["company", "owner"]) if (blank(ld.lead[f])) errs.push(`lead.${f} phải là chuỗi không rỗng`);
  if (!["a", "b", "c"].includes(ld.lead.framework)) errs.push("lead.framework phải là a, b hoặc c");
  for (const [k, v] of Object.entries(ld.vars)) {
    if (RULES.builtin_vars.includes(k)) errs.push(`vars.${k} trùng tên biến có sẵn của template`);
    if (blank(v)) errs.push(`vars.${k} phải là chuỗi không rỗng`);
  }
  const kit = ld.kit;
  for (const f of ["kyc", "ask", "qa", "objections", "close_checks", "videos"]) if (!has(kit, f)) errs.push(`kit thiếu ${f}`);
  // Links become href: only https:// is accepted. A src that is not a URL (e.g. "brief · verify") is fine.
  for (const [where, u] of [["lead.deck", ld.lead.deck], ["kit.research_url", kit.research_url]]) {
    if (u && !String(u).startsWith("https://")) errs.push(`${where} phải trống hoặc bắt đầu bằng https://`);
  }
  const kyc = kit.kyc ?? [], videos = kit.videos ?? [], qa = kit.qa ?? [], objections = kit.objections ?? [];
  const srcs = Object.entries(ld.profile).map(([k, f]) => [`profile.${k}`, f?.src]).concat(kyc.map((f, i) => [`kit.kyc[${i}]`, f?.src]));
  for (const [where, u] of srcs) {
    if (badLink(u)) errs.push(`${where}: src là URL thì phải bắt đầu bằng https://`);
  }
  const lim = RULES.limits;
  if (!inRange(videos.length, lim.videos)) errs.push(`kit.videos: cần ${lim.videos[0]}–${lim.videos[1]} video`);
  const ids = videos.map((v) => py(v.id));
  for (const i of ids) {
    // vXxx so it never meets a fixed page id (v1, v2 are tick boxes).
    if (!/^v[A-Z][A-Za-z0-9]*$/.test(i)) errs.push(`kit.videos: id ${i} phải có dạng vXxx, ví dụ vCas`);
    else if (PAGE_IDS.has(i)) errs.push(`kit.videos: id ${i} trùng id có sẵn của trang`);
  }
  if (new Set(ids).size !== ids.length) errs.push("kit.videos: id bị lặp");
  for (const v of videos) if (blank(v.label)) errs.push(`kit.videos: ${py(v.id)} cần label không rỗng`);
  kyc.forEach((f, i) => { if (f.s === "assumed" && !f.src) errs.push(`kit.kyc[${i}]: assumed thì phải có src`); });
  const roles = qa.map((g) => g.role);
  if (!inRange(roles.length, lim.qa_groups)) errs.push(`kit.qa: cần ${lim.qa_groups[0]}–${lim.qa_groups[1]} nhóm`);
  if (new Set(roles).size !== roles.length) errs.push("kit.qa: vai bị lặp");
  for (const g of qa) {
    if (!RULES.roles.includes(g.role)) errs.push(`kit.qa: vai ${py(g.role)} không hợp lệ`);
    if (!inRange((g.q ?? []).length, lim.qa_per_role)) errs.push(`kit.qa.${py(g.role)}: cần ${lim.qa_per_role[0]}–${lim.qa_per_role[1]} câu`);
  }
  if (!inRange(objections.length, lim.objections)) errs.push(`kit.objections: cần ${lim.objections[0]}–${lim.objections[1]} mục`);
  const cc = kit.close_checks ?? [];
  if (!inRange(cc.length, lim.close_checks)) errs.push(`kit.close_checks: cần ${lim.close_checks[0]}–${lim.close_checks[1]} mục`);
  // What the AI writes: no price, no blanks. The client's own words ("if") may carry an amount.
  const aiText = [...strings(ld.vars), ...strings(qa), ...objections.map((o) => o.then ?? ""), ...strings(cc), ...strings(kit.ask ?? [])];
  for (const t of aiText) {
    if (RULES.no_money.test(t)) errs.push(`có số tiền trong phần AI viết: ${cut(t, 60)}`);
    if (RULES.no_placeholder.test(t)) errs.push(`còn chỗ trống: ${cut(t, 60)}`);
  }
  errs.push(...daypart([...strings(kit), ...strings(ld.vars)], "lead"));
  for (const t of [...strings(ld.lead), ...strings(ld.profile), ...strings(kit), ...strings(ld.vars)]) {
    // phone/email links are blocked; other URLs are removed before looking for numbers (long ids in source URLs).
    if (hasContact(t)) errs.push(`có thông tin liên hệ ngoài khối demo: ${cut(t, 40)}`);
  }
  const used = new Set(strings(pb.items?.map((it) => it.body) ?? []).flatMap((t) => [...t.matchAll(VAR)].map((m) => m[1])));
  const missing = [...used].filter((v) => !RULES.builtin_vars.includes(v) && !has(ld.vars, v)).sort();
  if (missing.length) errs.push("thiếu biến trong vars: " + missing.join(", "));
  return errs;
}
