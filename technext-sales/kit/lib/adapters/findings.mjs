// audited-findings.json (technext-sales-proposal, source-auditor output) -> lead facts. Pure functions, no I/O.
// Findings are free-text claims grouped by proposal section, not by FACT_KEYS, so picking which claim answers
// "industry" or "current_system" is a judgment step done by the AI. The split:
//   usableFindings(audited)            -> {usable, dropped}   code: number the findings, drop what must not become a fact
//   factsFromPicks(audited, picks, o)  -> {facts, errors}     code: turn the AI's picks into facts for appendFacts
// The AI only returns picks: [{key, value, from: [n, ...]}], n = the finding's index in audited.findings.
// It never sets grade or source: both come from the findings it points at, so it cannot upgrade a guess or invent a URL.
//   grade  confirmed only when every cited finding is graded Confirmed (said by the client on a call/meeting);
//          otherwise assumed, with source.ref = the https source_url of the first cited web finding.
//   at     audited_at, else as_of, else opts.at (YYYY-MM-DD).
// Dropped findings (cannot be cited): grade D, downgraded_to/grade_audited assess or D, bind_check not bound,
// web grades without an https source_url, and anything holding a phone number or email.
import { FACT_KEYS } from "../lead/lead.mjs";
import { hasContact } from "../journey/journey.mjs";
import { pricingValueError, factValue } from "../lead/notes.mjs";

// sections where each key's answer usually sits; only a hint for the prompt, never enforced
export const SECTION_HINTS = {
  industry: ["due-diligence", "company-profile", "market-industry", "overview"],
  size: ["staff-org", "company-profile", "due-diligence"],
  location: ["company-profile", "due-diligence", "regional-expansion"],
  regulatory: ["tool-accounting-overhaul", "market-industry", "pain-solution-matrix"],
  risks: ["pain-solution-matrix", "strategic-analysis", "recommendations"],
  current_system: ["current-tools-saas", "current-operations", "due-diligence"],
  users: ["staff-org", "current-operations", "meeting-minutes"],
  departments: ["department-workflows", "staff-org"],
  client_words: ["meeting-minutes", "pre-meeting", "due-diligence"],
  next_step: ["meeting-minutes", "recommendations"],
  decision_maker: ["founders-leadership", "meeting-minutes"],
  modules: ["solution-odoo-erp", "tool-odoo-platform", "pain-solution-matrix"],
  package: [], // never from research: Neil decides
  addons: ["solution-odoo-erp"],
};

const DATE = /^\d{4}-\d{2}-\d{2}$/;
const isConfirmed = (g) => typeof g === "string" && g.toLowerCase() === "confirmed";
const texts = (x) => (typeof x === "string" || typeof x === "number" ? [String(x)] : x && typeof x === "object" ? Object.values(x).flatMap(texts) : []);

function dropReason(f) {
  if (!f || typeof f !== "object") return "không phải object";
  if (texts(f).some(hasContact)) return "có thông tin liên hệ";
  const g = String(f.grade_audited ?? f.grade ?? "");
  if (g === "D" || f.downgraded_to === "assess" || /assess/i.test(g)) return "bị hạ xuống D/assess";
  if (f.bind_check && f.bind_check !== "bound") return `bind_check ${f.bind_check}`;
  if (!isConfirmed(g)) {
    const url = f.source_url_audited ?? f.source_url;
    if (typeof url !== "string" || !url.startsWith("https://")) return "nguồn web thiếu URL https";
  }
  return null;
}

export function usableFindings(audited) {
  // older runs (kitchen-arena, casa-escondida) store the findings array as the whole file
  const list = Array.isArray(audited) ? audited : Array.isArray(audited?.findings) ? audited.findings : [];
  const usable = [], dropped = [];
  list.forEach((f, n) => {
    const why = dropReason(f);
    if (why) return dropped.push({ n, reason: why });
    usable.push({ n, claim: f.claim, section: f.section, grade: f.grade_audited ?? f.grade, url: f.source_url_audited ?? f.source_url ?? null, excerpt: f.excerpt });
  });
  return { usable, dropped };
}

// opts: {by, at?, noteId?, confirmedKind?: "call" | "meeting", matrixModules?: string[] (price matrix column 0)}
// A token may send grade confirmed only when source.ref is the id of a portal note of the lead (POST /facts rule). So Confirmed
// findings become confirmed facts only with opts.noteId (the note holding the call transcript); without it they are assumed,
// citing the research run. Web findings are always assumed.
export function factsFromPicks(audited, picks, opts = {}) {
  const errors = [];
  const at = [audited?.audited_at, audited?.as_of, opts.at].find((d) => typeof d === "string" && DATE.test(d));
  if (!at) errors.push("thiếu ngày: audited_at, as_of hoặc opts.at dạng YYYY-MM-DD");
  if (typeof opts.by !== "string" || !opts.by.trim()) errors.push("thiếu opts.by (người chạy adapter)");
  if (!Array.isArray(picks)) return { facts: [], errors: [...errors, "picks phải là mảng"] };
  const ok = new Map(usableFindings(audited).usable.map((u) => [u.n, u]));
  const facts = [];
  picks.forEach((p, i) => {
    const w = `pick #${i} (${p?.key})`;
    if (!FACT_KEYS.includes(p?.key)) return errors.push(`${w}: key lạ`);
    const arr = p?.key === "modules";
    if (arr ? !Array.isArray(p.value) || !p.value.length : p?.key === "users" ? p.value == null || p.value === "" : typeof p.value !== "string" || !p.value.trim()) return errors.push(`${w}: value rỗng`);
    if (hasContact(arr ? p.value.join(", ") : String(p.value))) return errors.push(`${w}: value có thông tin liên hệ`);
    // package is Neil's decision, confirmed on a call or by Neil: research never sets it
    if (p.key === "package") return errors.push(`${w}: package không lấy từ research (Neil chọn)`);
    const format = pricingValueError(p.key, p.value, { matrixModules: opts.matrixModules });
    if (format) return errors.push(`${w}: ${format}`);
    if (!Array.isArray(p.from) || !p.from.length) return errors.push(`${w}: thiếu from (số thứ tự finding)`);
    const cited = p.from.map((n) => ok.get(n));
    const bad = p.from.filter((n, j) => !cited[j]);
    if (bad.length) return errors.push(`${w}: finding ${bad.join(", ")} không có hoặc đã bị loại`);
    const web = cited.find((c) => !isConfirmed(c.grade));
    const source = web
      ? { kind: "web", ref: web.url, at }
      : opts.noteId ? { kind: opts.confirmedKind ?? "call", ref: opts.noteId, at } : { kind: "call", ref: `research ${at} (call transcript, no note)`, at };
    const grade = !web && opts.noteId ? "confirmed" : "assumed";
    facts.push({ key: p.key, value: factValue(p.value), grade, source, by: opts.by });
  });
  return { facts: errors.length ? [] : facts, errors };
}
