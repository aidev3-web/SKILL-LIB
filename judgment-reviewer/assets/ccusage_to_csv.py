"""
Per-task cost report — agent-agnostic, works on any machine, whichever coding agent
ran the task (Claude Code, Codex, Gemini CLI, Copilot CLI, ...).

Why not hand-parse each agent's own log files: every agent CLI stores its session
logs in its own private format and location (Claude Code under
~/.claude/projects/..., Codex under ~/.codex/sessions/..., etc.) — writing a parser
per agent has no end, and a company-wide skill can't assume everyone's machine only
ever runs Claude Code.

The fix: `ccusage` already solves exactly this — it auto-detects and reads 18+ coding
agents' local logs (Claude Code, Codex, Gemini CLI, Copilot CLI, Qwen, Kimi, ...), no
API key, no network call, and its unified `session` command tags every row with which
agent produced it (`"agent": "claude"` / `"codex"` / ...). So instead of parsing
anything ourselves, this script calls `ccusage session --json` and matches rows back
to tasks by session id.

The one thing `ccusage` can't do is split ONE session into several tasks. So the rule,
enforced by `checkpoint-manager`, is:

  * a dispatched task (a Phase 1 group, a subagent call) runs in its own isolated
    agent session/process — then "this task's cost" is exactly "this session's cost";
  * a task that genuinely runs inline in the orchestrator's own session still records
    that session's id, and the session is reported ONCE for all the tasks it hosted -
    never once per task, which would multiply the same cost by the number of tasks.

Either way there is no timestamp guessing and no per-agent file format to understand.

Usage:
    python ccusage_to_csv.py <out.csv> <checkpoint.json> [--since YYYYMMDD]
    python ccusage_to_csv.py --task "<task name>" <checkpoint.json> [--since YYYYMMDD]

This writes ONE file: the CSV. Any viewable table is handled by the shared
`cost-dashboard.html` in this skill's assets folder, which reads every run's CSV at
once — so this script never regenerates presentation, and re-running it can't leave a
stale second copy of the same numbers behind.

checkpoint.json's timeline entries must include, for every task:
    {"task": "...", "started": "...", "ended": "...", "session_id": "...", "agent": "claude"}
Several timeline entries may carry the SAME session_id when those tasks really did run
in one shared session (the orchestrator's own). That is fine and expected: those rows
are written once for the shared session, labelled `shared-session: <task> + <task>`.
`session_id` is whatever id that task's own agent session reports for itself (for
Claude Code: the session's transcript file id, visible for the current session from
its own project directory name; ask the dispatching tool for its own session id
rather than guessing). `agent` is optional (falls back to matching by session_id
alone) but recommended, since some agents could in theory reuse an id shape.

--since defaults to the earliest task's date in the timeline (ccusage needs some date
range; without one it may not scan far enough back to find an older session).
"""

import json
import sys
import csv
import subprocess
from datetime import datetime, timedelta


SHARED_LABEL_PREFIX = "shared-session: "


def parse_iso(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def load_timeline(checkpoint_path):
    # utf-8-sig strips a leading BOM if present (e.g. a checkpoint written by
    # PowerShell's `Set-Content -Encoding UTF8`, which adds one) — plain "utf-8"
    # leaves the BOM in place, which then breaks json.load with a decode error that
    # used to be silently swallowed into "no timeline found", the exact kind of
    # silent-$0 failure this script's docstring says it avoids.
    try:
        with open(checkpoint_path, encoding="utf-8-sig") as f:
            cp = json.load(f)
    except FileNotFoundError:
        print(f"Checkpoint file not found: {checkpoint_path}", file=sys.stderr)
        return []
    except json.JSONDecodeError as exc:
        print(f"Checkpoint file {checkpoint_path} is not valid JSON ({exc}) — "
              f"cannot read its timeline. Check the file wasn't corrupted or saved "
              f"with unexpected encoding.", file=sys.stderr)
        return []
    timeline = []
    for entry in cp.get("timeline", []):
        try:
            timeline.append({
                "task": entry["task"],
                "started": parse_iso(entry["started"]),
                "ended": parse_iso(entry["ended"]),
                "session_id": entry.get("session_id"),
                "agent": entry.get("agent"),
            })
        except (KeyError, ValueError):
            continue
    return timeline


def fmt_duration(seconds):
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h{minutes:02d}m"
    if minutes:
        return f"{minutes}m{secs:02d}s"
    return f"{secs}s"


def fetch_all_sessions(since=None):
    """One call to ccusage's unified, multi-agent session report. `since` should cover
    the earliest task in the timeline — ccusage needs a date floor to know how far
    back to scan."""
    cmd = "npx ccusage@latest session --json"
    if since:
        cmd += f" -s {since}"
    raw = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if raw.returncode != 0:
        print(f"ccusage failed (exit {raw.returncode}): {raw.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(raw.stdout).get("session", [])
    except json.JSONDecodeError:
        print("ccusage returned non-JSON output — is it installed/reachable (npx)?", file=sys.stderr)
        sys.exit(1)


def match_session(entry, all_sessions):
    """Find the one ccusage session row for this task. Requires session_id (the rule
    this whole mechanism depends on: one task, one isolated session)."""
    if not entry.get("session_id"):
        return None, "no-session_id-recorded"
    # For most agents ccusage's `period` IS the bare session id (Claude Code
    # "00872dc3-...", OpenCode "ses_..."), but for Codex it is the log path prefixed
    # with the start time — "2026/09/24/rollout-2026-09-24T12-21-56-01a0d1dc-..." —
    # while `checkpoint-manager` records only the id itself. So accept the id as a
    # suffix as well as an exact match. This is still identity matching against the
    # recorded id, never the timestamp guessing this script exists to avoid.
    wanted = entry["session_id"]
    matches = [
        s for s in all_sessions
        if (s.get("period") == wanted or (s.get("period") or "").endswith(wanted))
        and (not entry.get("agent") or s.get("agent") == entry["agent"])
    ]
    if not matches:
        return None, "session-not-found-in-ccusage"
    if len(matches) > 1:
        return None, "ambiguous-multiple-sessions-matched"
    return matches[0], "matched"


def rows_for_task(entry, all_sessions):
    session, status = match_session(entry, all_sessions)
    duration = fmt_duration((entry["ended"] - entry["started"]).total_seconds())
    if not session:
        return [], status, duration
    rows = []
    for mb in session.get("modelBreakdowns", []):
        rows.append({
            "task_label": entry["task"],
            "task_duration": duration,
            "agent": session.get("agent", entry.get("agent", "")),
            "session_id": session.get("period", ""),
            "model_name": mb.get("modelName", ""),
            "input_tokens": mb.get("inputTokens", 0),
            "output_tokens": mb.get("outputTokens", 0),
            "cache_creation_tokens": mb.get("cacheCreationTokens", 0),
            "cache_read_tokens": mb.get("cacheReadTokens", 0),
            "cost_usd": round(mb.get("cost", 0), 4),
        })
    return rows, status, duration


def report_task_mode(task_name, checkpoint_path, since):
    timeline = load_timeline(checkpoint_path)
    entry = next((e for e in timeline if e["task"] == task_name), None)
    if not entry:
        print(f"No timeline entry named '{task_name}' found in {checkpoint_path}", file=sys.stderr)
        sys.exit(1)

    all_sessions = fetch_all_sessions(since or entry["started"].strftime("%Y%m%d"))
    rows, status, duration = rows_for_task(entry, all_sessions)

    if status == "no-session_id-recorded":
        print(f"Task '{task_name}' has no `session_id` in its timeline entry — this "
              f"mechanism requires the dispatching tool to record its own session id "
              f"at task start (see this script's module docstring). Cannot report cost "
              f"for this task without it.", file=sys.stderr)
        sys.exit(1)
    if status == "session-not-found-in-ccusage":
        print(f"Task '{task_name}' recorded session_id={entry['session_id']!r} "
              f"(agent={entry.get('agent')!r}) but ccusage found no matching session — "
              f"check the id was recorded correctly, or widen --since.", file=sys.stderr)
        sys.exit(1)
    if status == "ambiguous-multiple-sessions-matched":
        print(f"Task '{task_name}': more than one ccusage session matched "
              f"session_id={entry['session_id']!r} — recording `agent` alongside "
              f"`session_id` should disambiguate this.", file=sys.stderr)
        sys.exit(1)

    total_cost = sum(r["cost_usd"] for r in rows)
    print(f"=== Chi phí task: {task_name} (thời gian chạy: {duration}, agent: {rows[0]['agent'] if rows else '?'}) ===")
    non_claude = []
    for r in rows:
        print(f"  {r['model_name']}: input={r['input_tokens']} output={r['output_tokens']} "
              f"cache_write={r['cache_creation_tokens']} cache_read={r['cache_read_tokens']} "
              f"-> ${r['cost_usd']:.4f}")
        if not r["model_name"].startswith("claude-") and r["agent"] == "claude":
            non_claude.append(r["model_name"])
    print(f"  TỔNG: ${total_cost:.4f}")
    shared_with = [e["task"] for e in timeline
                   if e.get("session_id") and e["session_id"] == entry.get("session_id")
                   and e["task"] != task_name]
    if shared_with:
        print(f"  ℹ Task này chạy chung session với {len(shared_with)} task khác "
              f"({', '.join(shared_with)}) — số trên là chi phí của CẢ session đó, không "
              f"riêng task này. Trong file CSV đầy đủ, session này chỉ được tính MỘT lần.",
              file=sys.stderr)
    if non_claude:
        print(f"  ⚠ CẢNH BÁO: agent 'claude' nhưng model không phải Claude "
              f"({', '.join(non_claude)}) xuất hiện trong session này — dấu hiệu 1 tool "
              f"nội bộ (vd MCP) gọi qua provider khác mà bị ghi lẫn vào session Claude. "
              f"Kiểm tra thủ công trước khi báo giá.", file=sys.stderr)


def build_rows(timeline, since):
    if not timeline:
        return [], []
    all_sessions = fetch_all_sessions(since or min(e["started"] for e in timeline).strftime("%Y%m%d"))
    rows = []
    problems = []

    # Group by session first. Tasks that ran in one shared session (typically the
    # orchestrator's own session, which hosts several phases inline) must produce ONE
    # set of rows for that session, never one set per task - otherwise the same
    # session's cost is added to the run total once per task it hosted, which is
    # exactly the silent multiplication this script exists to prevent.
    groups = {}
    order = []
    for entry in timeline:
        key = (entry.get("session_id"), entry.get("agent"))
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(entry)

    for key in order:
        entries = groups[key]
        if not key[0]:
            for entry in entries:
                problems.append((entry["task"], "no-session_id-recorded"))
            continue
        if len(entries) == 1:
            subject = entries[0]
        else:
            subject = {
                "task": SHARED_LABEL_PREFIX + " + ".join(e["task"] for e in entries),
                "started": min(e["started"] for e in entries),
                "ended": max(e["ended"] for e in entries),
                "session_id": entries[0]["session_id"],
                "agent": entries[0].get("agent"),
            }
        task_rows, status, _ = rows_for_task(subject, all_sessions)
        if not task_rows:
            for entry in entries:
                problems.append((entry["task"], status))
            continue
        rows.extend(task_rows)
    return rows, problems


def write_csv(rows, out_path):
    fieldnames = ["task_label", "task_duration", "agent", "session_id", "model_name",
                  "input_tokens", "output_tokens", "cache_creation_tokens",
                  "cache_read_tokens", "cost_usd"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def parse_since_flag(argv):
    since = None
    if "--since" in argv:
        i = argv.index("--since")
        since = argv[i + 1]
        del argv[i:i + 2]
    return since, argv


def main():
    argv = sys.argv[1:]
    since, argv = parse_since_flag(argv)

    if argv and argv[0] == "--task":
        if len(argv) < 3:
            print('Usage: ccusage_to_csv.py --task "<task name>" <checkpoint.json> [--since YYYYMMDD]', file=sys.stderr)
            sys.exit(2)
        report_task_mode(argv[1], argv[2], since)
        return

    if len(argv) < 2:
        print("Usage: ccusage_to_csv.py <out.csv> <checkpoint.json> [--since YYYYMMDD]", file=sys.stderr)
        sys.exit(2)
    out_path, checkpoint_path = argv[0], argv[1]
    timeline = load_timeline(checkpoint_path)
    if not timeline:
        print(f"No timeline found in {checkpoint_path} — nothing to report.", file=sys.stderr)
        sys.exit(1)
    rows, problems = build_rows(timeline, since)
    write_csv(rows, out_path)
    print(f"Wrote {len(rows)} rows to {out_path}")
    shared = sorted({r["task_label"] for r in rows if r["task_label"].startswith(SHARED_LABEL_PREFIX)})
    if shared:
        print(f"ℹ {len(shared)} session(s) hosted several tasks each — reported as ONE "
              f"row-set per session, not one per task (which would multiply the cost):")
        for label in shared:
            print(f"    - {label}")
    if problems:
        print(f"⚠ {len(problems)} task(s) have NO row in this CSV — state this gap "
              f"explicitly when reporting totals, don't imply full coverage:", file=sys.stderr)
        for task, status in problems:
            print(f"    - {task}: {status}", file=sys.stderr)


if __name__ == "__main__":
    main()
