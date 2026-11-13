// Contact detection shared by journey lint, notes and lead checks. Regexes moved verbatim from lib/journey/journey.mjs,
// lib/journey/journey-rules.mjs and lib/lead/notes.mjs. Never returns or logs a matched value.
const W = "[\\p{L}\\p{N}_]";
const D = "\\p{Nd}";
const P = "\\p{L}\\p{N}_";

export const EMAIL = /(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g;
export const LINK = new RegExp(`(?<!${W})(wa\\.me|zalo\\.me)/\\+?\\p{Nd}|(?<!${W})tel:|(?<!${W})mailto:`, "iu");
const MAIL_SRC = `(?<![${P}.+-])[${P}.+-]+@[${P}-]+\\.[${P}.]+`;
const TEL_SRC = `(?:\\+?\\(?${D}\\)?[\\s.-]?){9,}`;
export const CONTACT = new RegExp(`${MAIL_SRC}|${TEL_SRC}`, "u");
const URLS = /https?:\/\/\S+/giu;

const MAIL_G = new RegExp(MAIL_SRC, "gu");
const TEL_G = new RegExp(TEL_SRC, "gu");
const LINK_RUN = new RegExp(`(?:${LINK.source})\\S*`, "giu"); // the group keeps \S* on every alternative

export const hasContact = (t) => LINK.test(t) || CONTACT.test(t.replace(URLS, " "));

const kindOf = (s) => {
  if (LINK.test(s)) return "link";
  const bare = s.replace(URLS, " ");
  if (new RegExp(MAIL_SRC, "u").test(bare)) return "email";
  return new RegExp(TEL_SRC, "u").test(bare) ? "phone" : null;
};

const isNum = (v) => (typeof v === "number" && Number.isFinite(v)) || typeof v === "bigint";

/** First string, number or key in value (dotted path, array index as number) that hasContact flags: { field, kind } or null. A key is reported as its parent path. */
export function findContact(value, path = "") {
  if (typeof value === "string" || isNum(value)) {
    const kind = kindOf(String(value));
    return kind ? { field: path, kind } : null;
  }
  if (value && typeof value === "object") {
    for (const [k, v] of Object.entries(value)) {
      const kind = kindOf(k);
      if (kind) return { field: path, kind };
      const hit = findContact(v, path ? `${path}.${k}` : k);
      if (hit) return hit;
    }
  }
  return null;
}

// URL spans are kept apart so a URL's own digits are not read as a phone
const markString = (raw) => {
  const s = raw.replace(LINK_RUN, "⟦link⟧"); // links first, also inside URLs
  const outside = (t) => t.replace(MAIL_G, "⟦email⟧").replace(TEL_G, "⟦phone⟧");
  let out = "", last = 0;
  for (const m of s.matchAll(URLS)) { out += outside(s.slice(last, m.index)) + m[0]; last = m.index + m[0].length; }
  return out + outside(s.slice(last));
};

/** Same shape as value, every contact in every string replaced by ⟦link⟧, ⟦email⟧ or ⟦phone⟧. */
export function markContacts(value) {
  if (typeof value === "string") return markString(value);
  if (isNum(value)) { const s = String(value), m = markString(s); return m === s ? value : m; }
  if (Array.isArray(value)) return value.map(markContacts);
  if (value && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([k, v]) => [markString(k), markContacts(v)]));
  return value;
}
