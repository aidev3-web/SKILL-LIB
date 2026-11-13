// Lead record contract as pure functions (no I/O): facts, the profile projection and staleness of generated outputs.
// The shared shape every generator (journey, proposal, quote) reads. Error messages are Vietnamese; tests look them up by keyword.
//   checkRecord(rec)                      -> string[]                       [] means the record is valid
//   appendFacts(rec, newFacts)            -> {record, errors}               the one way to add facts; rec is not changed
//   profileOf(facts)                      -> {key: {v, s, src, at, id}}     confirmed beats assumed, later beats earlier, superseded ignored
//   leadProfile(facts)                    -> {key: {v, s, src, at}}         profileOf without id: what lead.json.profile holds
//   staleOutputs(rec, {playbook, matrix}) -> kind[]                         only kinds present in rec.outputs
//
// appendFacts keeps an optional `via` ("ui" | "agent") and `at` (ISO time) on a new fact as given; the server stamps both
// (lib/lead/fact-rules.mjs), checkRecord only scans them for contacts. Without them a fact is as before.
//
// Record (journey/leads/<slug>/record.json):
//   {slug, version, owner, sa, runner?, company: {name, short, website, country}, facts: Fact[], outputs: {kind: Output}}
//   version  integer >= 0, bumped once per batch of facts (appendFacts); 0 = no facts yet.
//   facts    append-only by convention: a wrong fact is never edited or removed, a new fact supersedes it.
//            checkRecord sees one snapshot, not the history, so it cannot enforce this; appendFacts never rewrites old facts.
// Fact: {id, key, value, grade, ver, source: {kind, ref, at}, by, supersedes?}
//   id         "f<n>", unique, given by appendFacts.          key    one of FACT_KEYS.
//   grade      confirmed | assumed (GRADE_MAP gives the ADR-001 name).
//   ver        the record version that added the fact (1..version). An output whose inputs.lead < ver has not seen it.
//   source     kind in SOURCE_KINDS; ref is an https:// URL or a plain label with no scheme ("meeting 2026-11-10",
//              "brief · verify"), required when assumed; at is a YYYY-MM-DD string.
//   supersedes id of an earlier fact with the same key; that fact drops out of profileOf.
//   No string anywhere in a fact, nor owner, sa, runner or company.*, may hold a phone number or an email.
// Output: {version, status, inputs: {lead, playbook?, matrix?, research?}, url?}; kind in OUTPUT_KINDS, status in OUTPUT_STATUS.
//
// Stable error keywords: "hồ sơ" (not an object), "facts", "version", "object" (a fact that is not an object), "trùng" (id),
// "key", "grade", "kind", "nguồn" (assumed without ref), "https" (ref with another scheme), "source.at", "supersedes"
// ("chính nó", "đứng sau", other key, unknown id), "liên hệ", "ver", "status".
import { badLink, hasContact } from "../journey/journey.mjs";

export const FACT_KEYS = ["industry", "size", "location", "regulatory", "risks", "current_system", "users", "departments", "client_words", "next_step", "decision_maker", "modules", "package", "addons"];
export const SOURCE_KINDS = ["form", "web", "call", "meeting", "neil"];
export const OUTPUT_KINDS = ["research", "proposal", "journey", "quote"];
export const OUTPUT_STATUS = ["draft", "reviewed", "approved", "published", "stale", "failed"];   // reviewed: a person cleared "AI · not reviewed"
export const READS = {
  journey: ["industry", "regulatory", "risks", "size", "location"],
  proposal: ["industry", "regulatory", "risks", "current_system", "modules", "client_words", "next_step", "decision_maker"],
  quote: ["modules", "users", "package", "current_system"],
};
export const GRADE_MAP = { confirmed: "VERIFIED", assumed: "AI_INFERRED" };

const blank = (v) => typeof v !== "string" || !v.trim();
const isObj = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
// every string and number inside x, so a phone number split over an array or stored as a number is still seen
const texts = (x) => (typeof x === "string" || typeof x === "number" ? [String(x)] : x && typeof x === "object" ? Object.values(x).flatMap(texts) : []);
const supersededIds = (facts) => new Set(facts.map((f) => f?.supersedes).filter(Boolean));

export function checkRecord(rec) {
  if (!isObj(rec)) return ["hồ sơ phải là object"];
  const errs = [];
  if (!Number.isInteger(rec.version) || rec.version < 0) errs.push(`version hồ sơ phải là số nguyên >= 0, đang là ${JSON.stringify(rec.version)}`);
  if (!Array.isArray(rec.facts)) errs.push("facts phải là mảng");
  for (const k of ["owner", "sa", "runner", "company"]) {
    if (texts(rec[k]).some(hasContact)) errs.push(`${k}: có thông tin liên hệ (SĐT hoặc email)`);
  }
  const facts = Array.isArray(rec.facts) ? rec.facts : [];
  const pos = new Map();
  facts.forEach((f, i) => { if (isObj(f) && !pos.has(f.id)) pos.set(f.id, i); });
  const seen = new Set();
  facts.forEach((f, i) => {
    if (!isObj(f)) return errs.push(`fact #${i}: phải là object`);
    const w = `fact ${f.id ?? `#${i}`}`;
    if (seen.has(f.id)) errs.push(`${w}: id trùng`);
    seen.add(f.id);
    if (!FACT_KEYS.includes(f.key)) errs.push(`${w}: key lạ "${f.key}"`);
    if (!Object.hasOwn(GRADE_MAP, f.grade)) errs.push(`${w}: grade lạ "${f.grade}" (chỉ confirmed hoặc assumed)`);
    if (!SOURCE_KINDS.includes(f.source?.kind)) errs.push(`${w}: source.kind lạ "${f.source?.kind}"`);
    const ref = f.source?.ref;
    if (f.grade === "assumed" && blank(ref)) errs.push(`${w}: assumed mà thiếu nguồn (source.ref rỗng)`);
    if (badLink(ref)) errs.push(`${w}: nguồn là URL thì phải bắt đầu bằng https://`);
    if (typeof f.source?.at !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(f.source.at)) errs.push(`${w}: source.at phải là ngày dạng YYYY-MM-DD`);
    if (f.supersedes != null) {
      const j = pos.get(f.supersedes);
      if (f.supersedes === f.id) errs.push(`${w}: supersedes trỏ tới chính nó`);
      else if (j === undefined) errs.push(`${w}: supersedes trỏ tới id không có "${f.supersedes}"`);
      else if (j > i) errs.push(`${w}: supersedes trỏ tới fact đứng sau "${f.supersedes}"`);
      else if (facts[j].key !== f.key) errs.push(`${w}: supersedes trỏ tới fact khác key (${facts[j].key})`);
    }
    for (const [k, v] of Object.entries(f)) if (texts(v).some(hasContact)) errs.push(`${w}: có thông tin liên hệ (SĐT hoặc email) trong ${k}`);
    if (!Number.isInteger(f.ver) || f.ver > rec.version) errs.push(`${w}: ver ${f.ver} phải là số nguyên, không lớn hơn version hồ sơ ${rec.version}`);
  });
  for (const [kind, o] of Object.entries(isObj(rec.outputs) ? rec.outputs : {})) {
    if (!OUTPUT_KINDS.includes(kind)) errs.push(`output ${kind}: kind lạ`);
    if (!OUTPUT_STATUS.includes(o?.status)) errs.push(`output ${kind}: status lạ "${o?.status}"`);
  }
  return errs;
}

export function appendFacts(rec, newFacts) {
  if (!Array.isArray(newFacts) || !newFacts.length) return { record: rec, errors: ["facts mới phải là mảng không rỗng"] };
  const before = checkRecord(rec);
  if (before.length) return { record: rec, errors: before };
  const ver = rec.version + 1;
  let n = Math.max(0, ...rec.facts.map((f) => Number(/^f(\d+)$/.exec(f.id)?.[1] ?? 0)));
  const added = newFacts.map((f) => (isObj(f)
    ? { id: `f${++n}`, key: f.key, value: f.value, grade: f.grade, ver, source: f.source, by: f.by, ...(f.via != null && { via: f.via }), ...(f.at != null && { at: f.at }), ...(f.supersedes != null && { supersedes: f.supersedes }) }
    : f));
  const record = { ...rec, version: ver, facts: [...rec.facts, ...added] };
  return { record, errors: checkRecord(record) };
}

export function profileOf(facts) {
  const dead = supersededIds(facts);
  const out = {};
  for (const f of facts) {
    if (dead.has(f.id)) continue;
    const cur = out[f.key];
    // equal grade: the later fact wins; confirmed never loses to assumed
    if (cur && cur.s === "confirmed" && f.grade !== "confirmed") continue;
    out[f.key] = { v: f.value, s: f.grade, src: f.source?.ref, at: f.source?.at, id: f.id };
  }
  return out;
}

export const leadProfile = (facts) => Object.fromEntries(Object.entries(profileOf(facts)).map(([k, { id, ...p }]) => [k, p]));

export function staleOutputs(rec, versions) {
  const outs = rec.outputs ?? {};
  const facts = rec.facts ?? [];
  return Object.keys(outs).filter((kind) => {
    const inp = outs[kind].inputs ?? {};
    const reads = READS[kind];
    if (!reads) return false;
    if (facts.some((f) => reads.includes(f.key) && f.ver > (inp.lead ?? 0))) return true;
    if (kind === "journey" && versions.playbook > (inp.playbook ?? 0)) return true;
    if (kind === "quote" && versions.matrix > (inp.matrix ?? 0)) return true;
    return kind === "proposal" && outs.research && outs.research.version > (inp.research ?? 0);
  });
}
