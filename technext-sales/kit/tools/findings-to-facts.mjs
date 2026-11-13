#!/usr/bin/env node
// node tools/findings-to-facts.mjs <audited-findings.json> <picks.json> --by <name> [--at YYYY-MM-DD] [--matrix <price-matrix.json>]
//   --note n<k>: the portal note holding the call transcript; Confirmed findings become confirmed facts citing it (else assumed)
//   --matrix: the get_price_matrix answer ({rows} or {matrix: {rows}}); module names are column 0, matched exactly
// node tools/findings-to-facts.mjs <audited-findings.json> --usable      (prints the numbered usable findings for the AI)
// Prints {facts, errors} as JSON; exit 1 when there are errors. See docs/findings-picks-prompt.md.
import { readFileSync } from "node:fs";
import { usableFindings, factsFromPicks, SECTION_HINTS } from "../lib/adapters/findings.mjs";

const args = process.argv.slice(2);
const flag = (name) => { const i = args.indexOf(name); return i < 0 ? undefined : args.splice(i, 2)[1]; };
const usableOnly = args.includes("--usable") && args.splice(args.indexOf("--usable"), 1);
const by = flag("--by"), at = flag("--at"), matrixPath = flag("--matrix"), noteId = flag("--note");
const [auditedPath, picksPath] = args;
const read = (p) => JSON.parse(readFileSync(p, "utf8"));

if (!auditedPath || (!usableOnly && !picksPath)) {
  console.error("dùng: findings-to-facts.mjs <audited-findings.json> <picks.json> --by <tên> [--at YYYY-MM-DD]\n     findings-to-facts.mjs <audited-findings.json> --usable");
  process.exit(2);
}
const audited = read(auditedPath);
if (usableOnly) {
  const { usable, dropped } = usableFindings(audited);
  console.log(JSON.stringify({ hints: SECTION_HINTS, usable, dropped }, null, 1));
} else {
  let matrixModules;
  if (matrixPath) {
    const m = read(matrixPath), rows = m.rows ?? m.matrix?.rows ?? [];
    matrixModules = rows.map((r) => (Array.isArray(r) ? r[0] : r?.name)).filter((n) => typeof n === "string");
  }
  const out = factsFromPicks(audited, read(picksPath), { by, at, matrixModules, noteId });
  console.log(JSON.stringify(out, null, 1));
  if (out.errors.length) process.exit(1);
}
