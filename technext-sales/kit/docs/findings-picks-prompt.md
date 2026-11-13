# Picks prompt: audited findings → lead facts

Used by the `technext-sales` skill after source-auditor. The code decides grade and source; you only choose.

1. Run `node tools/findings-to-facts.mjs <audited-findings.json> --usable`. You get `usable` (numbered findings, field `n`), `dropped` (ignore them, never cite them) and `hints` (sections where each key usually sits).
2. For each of the 14 keys — `industry, size, location, regulatory, risks, current_system, users, departments, client_words, next_step, decision_maker, modules, package, addons` — write at most ONE pick:
   ```json
   {"key": "current_system", "value": "Asia GP (Thailand-based accounting system)", "from": [1, 7]}
   ```
3. Rules:
   - Skip a key when no usable finding supports it. An empty key becomes a question for the client; a guess does not.
   - `value`: short (≤ 120 characters), English, a summary of what the cited findings say — nothing they do not say.
   - `from`: every finding index you relied on. Prefer `Confirmed` findings (what the client said); citing any web finding makes the fact `assumed`, which is correct when it is not confirmed.
   - Never a price or amount for `package`, `modules`, `addons`; never a phone number or email; never a person's contact details for `decision_maker` (role and name only).
   - `client_words`: the client's own words, quoted, from a `Confirmed` finding only.
   - `package`: NEVER from research — skip it. Neil decides OOTB or Enterprise Core; it is added later as a confirmed fact.
   - `users`: digits only, e.g. `"6"`. Put any prose about users ("6 users, accounting module only") in `client_words` instead. No number in the findings → skip.
   - `addons`: only `"none"` or a comma list of `customization`, `training`, `migration`, and only when a finding states it.
   - `modules`: an ARRAY of module names, each written EXACTLY (case-sensitive) as column 0 of a price-matrix row (`get_price_matrix`), e.g. `["Accounting CAS"]`; only when a finding states the client wants them. Otherwise skip — Neil chooses.
4. Save the array as `picks.json`, then run `node tools/findings-to-facts.mjs <audited-findings.json> picks.json --by <your name> --matrix price-matrix.json` (the saved `get_price_matrix` answer) (add `--at YYYY-MM-DD` if the file has no `audited_at`/`as_of`). On errors, fix the picks, rerun. Then send `facts` with `add_facts`.
