// Add facts to <leads>/<slug>/record.json, refresh lead.json.profile, print {"version", "stale"}.
// Usage: node <skill>/tools/add-facts.mjs <slug> <facts.json>
//        node <skill>/tools/add-facts.mjs <slug> --profile     (print profileOf(record.facts), write nothing)
//   facts.json: [{key, value, grade, source: {kind, ref, at}, by, supersedes?}]   (JOURNEY_ROOT, JOURNEY_LEADS, PORTAL_DIR override paths)
// Exit 1, nothing written: the new record fails checkRecord, or the lead.json about to be written fails checkLead.
// Exit 2, nothing written: bad usage, or PORTAL_DIR is not a portal clone on the right branch (fix the setup, not the facts).
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = process.env.JOURNEY_ROOT || path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
// Same lookup as build.py: the packaged skill has no leads/ (lead data lives in ~/sales-journey) and ships tools/portal.
const LEADS = process.env.JOURNEY_LEADS
  || (fs.existsSync(path.join(ROOT, "leads")) ? path.join(ROOT, "leads") : path.join(os.homedir(), "sales-journey"));
const BUNDLED = path.join(ROOT, "tools", "portal");
// shortcut: falls back to Anthony's portal clone (the repo's tests rely on it); drop once the repo also uses tools/portal.
const PORTAL_DIR = process.env.PORTAL_DIR || (fs.existsSync(BUNDLED) ? BUNDLED : "C:\\Anthony\\proposal-portal");
const NO_PORTAL = `Không thấy lib/lead.mjs và tools/journey-check.mjs (bản có appendFacts) trong PORTAL_DIR=${PORTAL_DIR}. `
  + "Clone proposal-portal vào đó (hoặc đặt PORTAL_DIR) và checkout nhánh feat/lead-contracts (sau khi merge: preview). Lỗi cài đặt, không phải lỗi facts.";
if (!["lib/lead.mjs", "tools/journey-check.mjs"].every((f) => fs.existsSync(path.join(PORTAL_DIR, f)))) { console.error(NO_PORTAL); process.exit(2); }
const lib = (f) => import(pathToFileURL(path.join(PORTAL_DIR, "lib", f)).href);
const { appendFacts, leadProfile, profileOf, staleOutputs } = await lib("lead.mjs");
const { checkLead, pageIdsOf } = await lib("journey.mjs");
if (typeof appendFacts !== "function" || typeof checkLead !== "function") { console.error(NO_PORTAL); process.exit(2); } // an older checkout of the branch

const [slug, factsPath] = process.argv.slice(2);
if (!slug || !factsPath) { console.error("Usage: add-facts.mjs <slug> <facts.json | --profile>"); process.exit(2); }
const read = (p) => JSON.parse(fs.readFileSync(p, "utf8").replace(/^\uFEFF/, ""));
const dir = path.join(LEADS, slug);
if (factsPath === "--profile") {
  console.log(JSON.stringify(profileOf(read(path.join(dir, "record.json")).facts), null, 1));
  process.exit(0);
}
const lead = read(path.join(dir, "lead.json"));
const pb = read(path.join(ROOT, "playbook", "playbook.json"));

const { record, errors } = appendFacts(read(path.join(dir, "record.json")), read(factsPath));
if (errors.length) { console.error(`${slug}: không thêm được facts\n` + errors.join("\n")); process.exit(1); }
lead.profile = leadProfile(record.facts);

// A lead still being created (no outputs.journey yet) has no kit yet: kit.md and build.py check it at the end.
if (record.outputs?.journey) {
  const pageIds = pageIdsOf(fs.readFileSync(path.join(ROOT, "template", "journey.html"), "utf8"));
  const bad = checkLead(lead, pb, { slug, pageIds });
  if (bad.length) { console.error(`${slug}: lead.json sau khi thêm facts không qua bộ kiểm, chưa ghi gì\n` + bad.join("\n")); process.exit(1); }
}

fs.writeFileSync(path.join(dir, "record.json"), JSON.stringify(record, null, 2) + "\n", "utf8");
fs.writeFileSync(path.join(dir, "lead.json"), JSON.stringify(lead, null, 2) + "\n", "utf8");
console.log(JSON.stringify({ version: record.version, stale: staleOutputs(record, { playbook: pb.version, matrix: 0 }) }));
