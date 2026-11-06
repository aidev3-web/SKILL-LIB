// CLI over lib/journey.mjs and lib/lead.mjs, the only place that reads files.
//   node tools/journey-check.mjs --playbook <file> [--lead <file>] [--slug <s>] [--template <file>] [--record <file>] [--json]
// Without --lead only the playbook is checked. Exit 0 and "OK" when clean; exit 1 and one "LỖI: ..." line per error.
// --template: journey.html, to know which ids a video id must not collide with. --json prints {"ok", "errors"}.
// --record: the lead's record.json (needs --lead): checkRecord, and lead.profile must equal leadProfile(record.facts).
// Exit 2: bad usage or a file that cannot be read. A check that throws is reported as "lỗi khi kiểm: ...", exit 1.
import { readFileSync } from "node:fs";
import { isDeepStrictEqual } from "node:util";
import { checkLead, checkPlaybook, pageIdsOf } from "../lib/journey.mjs";
import { checkRecord, leadProfile } from "../lib/lead.mjs";

const args = process.argv.slice(2);
const opt = (name) => { const i = args.indexOf(name); return i < 0 ? undefined : args[i + 1]; };
const json = args.includes("--json");
const read = (f) => readFileSync(f, "utf8");

function fail(msg) {
  console.error(msg);
  process.exit(2);
}

const playbookFile = opt("--playbook"), leadFile = opt("--lead"), recordFile = opt("--record");
if (!playbookFile || (recordFile && !leadFile)) {
  fail("Dùng: node tools/journey-check.mjs --playbook <file> [--lead <file>] [--slug <s>] [--template <file>] [--record <file>] [--json] (--record cần --lead)");
}

let pb, ld, rec, pageIds = [];
try {
  pb = JSON.parse(read(playbookFile));
  if (leadFile) {
    ld = JSON.parse(read(leadFile));
    if (opt("--template")) pageIds = pageIdsOf(read(opt("--template")));
  }
  if (recordFile) rec = JSON.parse(read(recordFile));
} catch (e) {
  fail(`Không đọc được file: ${e.message}`);
}

const errors = [];
try {
  errors.push(...checkPlaybook(pb));
  if (leadFile) errors.push(...checkLead(ld, pb, { slug: opt("--slug"), pageIds }));
  if (recordFile) {
    const bad = checkRecord(rec).map((e) => `record.json: ${e}`);
    errors.push(...bad);
    if (!bad.length) {
      const want = JSON.parse(JSON.stringify(leadProfile(rec.facts))); // drops undefined src, as lead.json on disk does
      const got = ld.profile ?? {};
      const diff = [...new Set([...Object.keys(want), ...Object.keys(got)])].filter((k) => !isDeepStrictEqual(want[k], got[k])).sort();
      if (diff.length) errors.push(`lead.json.profile khác hồ sơ record.json ở: ${diff.join(", ")} (chạy add-facts để ghi lại profile)`);
    }
  }
} catch (e) {
  errors.push(`lỗi khi kiểm: ${e.message}`);
}

if (json) console.log(JSON.stringify({ ok: !errors.length, errors }));
else if (errors.length) for (const e of errors) console.log(`LỖI: ${e}`);
else console.log("OK");
process.exit(errors.length ? 1 : 0);
