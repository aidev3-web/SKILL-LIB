// ingest_notes helpers (design §5.5 step 2). Pure, no I/O. The AI reads the notes and proposes facts; code strips and checks.
//   stripContacts(text) -> {text, removed}     phones and emails replaced by "[contact removed]"; never survive (re-checked)
//   checkExtractedFacts(facts, {noteId, date, record?, matrixModules?}) -> {facts, errors}
//     source.ref = noteId, the portal note the facts come from ("n1"...): a token may send confirmed only when it cites a note
//     only FACT_KEYS; grade confirmed; source.kind call|meeting; source.at = date;
//     supersedes only an existing fact id of the SAME key (when record is given); no contact; no price for package/modules/addons.
//     Output facts carry no id/ver/by: appendFacts / the server assign them.
import { FACT_KEYS } from "./lead.mjs";
import { EMAIL } from "../../domain/rules/contacts.mjs";
import { hasContact } from "../journey/journey.mjs";

const MARK = "[contact removed]";
export { EMAIL }; // the regex lives in domain/rules/contacts.mjs
// a run of digits with optional +, spaces, dots, dashes or brackets, 7+ digits in all (dates like 2026-11-06 have 8 but are kept below)
const PHONE = /(?:\+?\(?\d[\d\s().-]{5,}\d)/g;
const DATE = /^\d{4}-\d{2}-\d{2}$/;
const PRICEY = /[₱$€£¥]|\b(?:php|usd|sgd|vnd|peso|pesos)\b|\d[\d,.]*\s*(?:k|m)\b/i;

/**
 * Write-time value formats the portal enforces on POST /api/v1/leads/<slug>/facts (LEAD-V1-CONTRACT step 1), checked here first:
 *   users    a positive whole number, or a digits-only string ("6"); prose about users goes to client_words instead
 *   modules  an array of strings, each EXACTLY (case-sensitive) a module name of the current price matrix (column 0)
 *   package  exactly "OOTB" or "Enterprise Core" (Neil's decision, never derived)
 *   addons   "none" or a comma list of customization / training / migration
 * matrixModules (optional): the price matrix's module names; without it, modules are only checked as an array of strings.
 * Returns an error message, or null when the value is fine (other keys are free text).
 */
export function pricingValueError(key, value, { matrixModules } = {}) {
  if (key === "users") {
    const n = typeof value === "string" && /^\d+$/.test(value) ? Number(value) : value, ok = Number.isInteger(n) && n > 0 && n <= 100000;   // the quote save caps users at 100000 too
    return ok ? null : "users must be a whole number of 1 to one hundred thousand like \"6\" (put prose such as \"6 users, accounting only\" in client_words)";
  }
  if (key === "modules") {
    if (!Array.isArray(value) || !value.length || value.some((m) => typeof m !== "string" || !m)) return "modules must be an array of module names";
    const unknown = Array.isArray(matrixModules) ? value.filter((m) => !matrixModules.includes(m)) : [];
    // never echo the names: this message goes into POST /facts rejections (R61)
    return unknown.length ? "modules must each equal a module name of the price matrix (exact, case-sensitive)" : null;
  }
  const v = typeof value === "string" ? value.trim() : null;
  if (key === "package" && !["OOTB", "Enterprise Core"].includes(value)) return "package must be exactly OOTB or Enterprise Core";   // exact: no spaces around
  if (key === "addons" && (v === null || (v !== "none" && !v.split(",").map((x) => x.trim()).every((x) => ["customization", "training", "migration"].includes(x))))) {
    return "addons must be none or a comma list of customization, training, migration";
  }
  return null;
}

/** The head count of a stored users fact, read leniently (facts written before R59 may be prose such as "6 users, accounting only"):
 *  the leading whole number of a string, or the integer itself. NaN when there is none. */
export const usersCount = (value) => (typeof value === "string" ? Number(/^\s*(\d{1,6})\b/.exec(value)?.[1]) : value);

/** A fact value as stored: arrays (modules) and numbers (users) kept as they are, strings trimmed. */
export const factValue = (value) => (typeof value === "string" ? value.trim() : value);
const valueText = (value) => (Array.isArray(value) ? value.join(", ") : String(value ?? ""));
const emptyValue = (key, value) => (key === "modules" || key === "users" ? value == null || value === "" : typeof value !== "string" || !value.trim());

export function stripContacts(text) {
  let removed = 0;
  let out = String(text ?? "").replace(EMAIL, () => (removed++, MARK));
  out = out.replace(PHONE, (m) => {
    const digits = m.replace(/\D/g, "");
    if (digits.length < 7 || DATE.test(m.trim()) || /^\d{4}$/.test(m.trim())) return m;
    removed++;
    return MARK;
  });
  // whatever the shared contact rule still sees is removed line by line: nothing it flags may survive
  out = out.split("\n").map((line) => (hasContact(line) ? (removed++, MARK) : line)).join("\n");
  return { text: out, removed };
}

export function checkExtractedFacts(facts, { noteId, date, record, matrixModules } = {}) {
  const errors = [];
  if (typeof noteId !== "string" || !/^n[0-9]{1,6}$/.test(noteId)) errors.push("noteId is required (the portal note id, e.g. n1)");
  if (typeof date !== "string" || !DATE.test(date)) errors.push("date must be YYYY-MM-DD");
  if (!Array.isArray(facts)) return { facts: [], errors: [...errors, "facts must be an array"] };
  const known = new Map((record?.facts ?? []).map((f) => [f.id, f.key]));
  const out = [];
  facts.forEach((f, i) => {
    const w = `fact #${i} (${f?.key})`;
    if (!f || typeof f !== "object") return errors.push(`fact #${i}: must be an object`);
    if (!FACT_KEYS.includes(f.key)) return errors.push(`${w}: unknown key`);
    if (emptyValue(f.key, f.value)) return errors.push(`${w}: empty value`);
    if (f.grade !== undefined && f.grade !== "confirmed") return errors.push(`${w}: notes give confirmed facts only`);
    const kind = f.source?.kind ?? "meeting";
    if (!["call", "meeting"].includes(kind)) return errors.push(`${w}: source.kind must be call or meeting`);
    if (hasContact(valueText(f.value))) return errors.push(`${w}: contains a phone number or email`);
    if (["package", "modules", "addons"].includes(f.key) && PRICEY.test(valueText(f.value))) return errors.push(`${w}: no prices in facts`);
    const format = pricingValueError(f.key, f.value, { matrixModules });
    if (format) return errors.push(`${w}: ${format}`);
    if (f.supersedes != null) {
      if (record && !known.has(f.supersedes)) return errors.push(`${w}: supersedes unknown fact ${f.supersedes}`);
      if (record && known.get(f.supersedes) !== f.key) return errors.push(`${w}: supersedes a fact of another key`);
    }
    out.push({ key: f.key, value: factValue(f.value), grade: "confirmed", source: { kind, ref: noteId, at: date },
      ...(f.supersedes != null ? { supersedes: f.supersedes } : {}) });
  });
  return { facts: errors.length ? [] : out, errors };
}
