// Sales Journey rules: the content of journey/rules/lint.json (ai-sales-proposal repo), with the regexes as JS RegExp.
// Pure data, no I/O. Python's re is Unicode-aware but JS \b, \w and \d are ASCII, so word boundaries are written as
// lookarounds on W (letters, digits, underscore in any script) and the "u" flag is always on. Python's inline (?i) becomes
// the "i" flag; (?-i:\bP\d) cannot live inside an "i" regex, so no_money is a small object with the same .test().

const W = "[\\p{L}\\p{N}_]";
const B = `(?<!${W})`; // \b before a word character
const E = `(?!${W})`; // \b after a word character
const D = "\\p{Nd}";

const moneyI = new RegExp(
  `₱|\\$|${B}php\\s?${D}|${B}usd\\s?${D}|${B}pesos?${E}|${B}${D}{1,3}(?:,${D}{3})+${E}|${B}${D}[${D},.]*\\s?(?:k|m)${E}`,
  "iu"
);
const moneyP = new RegExp(`${B}P${D}`, "u"); // case-sensitive: "P250,000" yes, "p5" no

export const RULES = {
  version: 1,
  roles: ["it", "finance", "owner", "ops"],
  status: ["assumed", "confirmed"],
  builtin_vars: ["name", "slot", "meet", "video", "plink", "words", "next", "owner", "system", "company", "rep", "company_full"],
  no_daypart: new RegExp(`${B}good\\s+(morning|afternoon|evening)${E}|chào buổi (sáng|chiều|tối)`, "iu"),
  no_money: { test: (t) => moneyI.test(t) || moneyP.test(t) },
  no_placeholder: /\[[^\]]*\]|\{[^}]*\}/u,
  contact: new RegExp(`[${"\\p{L}\\p{N}_"}.+-]+@[${"\\p{L}\\p{N}_"}-]+\\.[${"\\p{L}\\p{N}_"}.]+|(?:\\+?\\(?${D}\\)?[\\s.-]?){9,}`, "u"),
  limits: { qa_per_role: [1, 8], qa_groups: [1, 4], objections: [3, 6], close_checks: [0, 3], videos: [1, 2] },
};

export const W_CLASS = W;
