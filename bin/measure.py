#!/usr/bin/env python3
# Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE.
"""Print the numbers for every run recorded since the last bin/new-round.py.

  bin/measure.py          a table, then one block of detail per run
  bin/measure.py --json   the same as JSON
  bin/measure.py --compare   for anything run more than once, the first run beside the latest
  bin/measure.py --versions  the Claude Code versions recorded, and how many runs each has
  bin/measure.py --claude-code 2.1.325   only the runs made on that Claude Code version;
                                         combine it with any of the forms above

Everything is read from machine records: the transcript Claude Code saved for the session
(and for any subagents it started), the log of tools Claude Code ran, and the verdict
bin/run.py recorded. Nothing depends on screenshots.

Columns:
  result      PASS or FAIL from bin/check.py
  requests    calls to the model, subagents included
  tools_run   tools Claude Code actually ran, including those run from Code Mode scripts
  scripts     pieces of Code Mode JavaScript run (always 0 with Code Mode off)
  subagents   subagents the session started
  seconds     from your prompt to the last reply
  fixed_ctx   tokens sent in the first request: system prompt, tool definitions, your prompt
  task_ctx    tokens in the last request plus its reply, minus fixed_ctx (main conversation only)
  peak_ctx    the largest context of any request
  total_in    input tokens the model processed over the whole session: every request's
              context added up, cached or not, subagents included
  processed   total_in plus every output token: all the tokens the model read or wrote
  cost_usd    what Claude Code recorded as the session's cost
"""

import collections
import datetime
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import benchlib as b  # noqa: E402

CONTEXT = re.compile(r"\*\*Tokens:\*\*\s*([\d.]+)\s*([kKmM]?)\s*/")
UNIT = {"": 1, "k": 1_000, "m": 1_000_000}
PARTS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")


def text_of(message):
    content = message.get("content")
    if isinstance(content, str):
        return content
    return "".join(
        x.get("text", "")
        for x in content or []
        if isinstance(x, dict) and x.get("type") == "text"
    )


def when(value):
    return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))


def sent(usage):
    """Tokens the model was sent in one request: the size of the context at that point."""
    return sum(usage.get(k) or 0 for k in PARTS)


def is_virtual(record):
    """True for a transcript record that stands for a tool call made by a script, not a model reply."""
    return bool(record.get("isVirtual")) or (record.get("message") or {}).get("model") == "<synthetic>"


def measure(run):
    path = run["transcript"]
    with open(b.prompt_path(run["task"]), encoding="utf-8") as fh:
        head = fh.read().strip()[:50]
    usage, direct = collections.OrderedDict(), collections.Counter()
    inside = collections.Counter()
    start = end = model = version = effort = speed = cost = shown_start = shown_end = (
        None
    )
    api_requests = 0
    for d in b.read_jsonl(path):
        kind, msg = d.get("type"), d.get("message") or {}
        if kind == "api-request":
            api_requests += 1
        if kind == "cost-state" and d.get("totalCostUSD") is not None:
            cost = d["totalCostUSD"]
        if d.get("isSidechain"):
            continue
        if kind == "user":
            text = text_of(msg).strip()
            shown = (
                CONTEXT.search(text) if text.startswith("## Context Usage") else None
            )
            if shown:
                tokens = round(float(shown.group(1)) * UNIT[shown.group(2).lower()])
                if start is None:
                    shown_start = tokens
                elif shown_end is None:
                    shown_end = tokens
            elif start is None and head in text:
                start = when(d["timestamp"])
        elif kind == "assistant" and start is not None:
            end = when(d["timestamp"])
            # In a Code Mode session every tool call a script makes is written to the transcript as
            # its own assistant record, marked virtual. Those are not requests to the model.
            virtual = is_virtual(d)
            if not virtual:
                model, version = msg.get("model") or model, d.get("version") or version
                effort = d.get("effort") or effort
                if msg.get("id") and msg.get("usage"):
                    usage[msg["id"]] = msg["usage"]
                    speed = msg["usage"].get("speed") or speed
            for block in msg.get("content") or []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    (inside if virtual else direct)[block.get("name")] += 1
    if start is None or not usage:
        return None

    # Subagents keep their own transcripts beside the session's; their requests and tokens count.
    sub, agents = {}, 0
    for path_sub in glob.glob(
        os.path.join(path[: -len(".jsonl")], "subagents", "agent-*.jsonl")
    ):
        agents += 1
        for d in b.read_jsonl(path_sub):
            msg = d.get("message") or {}
            if d.get("type") == "assistant" and msg.get("id") and msg.get("usage") and not is_virtual(d):
                sub[msg["id"]] = msg["usage"]

    # The tool logger sees every tool Claude Code runs, including calls made from a script.
    session = os.path.basename(path)[: -len(".jsonl")]
    ran = collections.Counter(
        e.get("tool") for e in b.read_jsonl(b.TOOL_LOG) if e.get("session") == session
    )
    scripts = ran.pop("REPL", 0)
    main = list(usage.values())
    everything = main + list(sub.values())
    return {
        "task": run["task"],
        "mode": run["mode"],
        "typed": "hand" if run.get("typed", "by hand") == "by hand" else "script",
        "model": model,
        "result": "PASS" if run.get("passed") else "FAIL",
        "requests": len(everything),
        "tools_run": sum(ran.values()) if ran or scripts else sum(direct.values()) + sum(inside.values()),
        "scripts": scripts,
        "subagents": agents,
        "seconds": round((end - start).total_seconds()),
        "fixed_ctx": sent(main[0]),
        "task_ctx": sent(main[-1])
        + (main[-1].get("output_tokens") or 0)
        - sent(main[0]),
        "peak_ctx": max(sent(u) for u in main),
        "total_in": sum(sent(u) for u in everything),
        "processed": sum(sent(u) + (u.get("output_tokens") or 0) for u in everything),
        "cost_usd": round(cost, 2) if cost is not None else None,
        "detail": {
            "started": run["started"][:16].replace("T", " ") + " UTC",
            "effort": effort,
            "speed": speed,
            "permission": run.get("permission"),
            "config": run.get("config"),
            "version": version,
            "session": session[:8],
            "tools_logged": dict(ran.most_common()),
            "tool_calls_in_transcript": dict((direct + inside).most_common()),
            "api_requests_recorded": api_requests,
            "mcp_calls": run.get("mcp_calls"),
            "context_shown_start": shown_start,
            "context_shown_end": shown_end,
            "tokens": {
                "input": sum(u.get("input_tokens") or 0 for u in everything),
                "cache_write": sum(
                    u.get("cache_creation_input_tokens") or 0 for u in everything
                ),
                "cache_read": sum(
                    u.get("cache_read_input_tokens") or 0 for u in everything
                ),
                "output": sum(u.get("output_tokens") or 0 for u in everything),
            },
            "check": run.get("detail"),
        },
    }


NUMBERS = ("requests", "tools_run", "scripts", "seconds", "fixed_ctx", "task_ctx", "peak_ctx", "total_in", "processed", "cost_usd")


def compare(rows):
    """For every task, mode and model run more than once: the first run beside the latest."""
    groups = collections.OrderedDict()
    for r in rows:
        groups.setdefault((r["task"], r["mode"], str(r["model"])), []).append(r)
    shown = 0
    for (task, mode, model), runs in groups.items():
        if len(runs) < 2:
            continue
        shown += 1
        first, last = runs[0], runs[-1]
        print(f"\n{task} Code Mode {mode}  {model}  ({len(runs)} runs)")
        print(f"   {'':12} {'first, by ' + first['typed']:>18} {'latest, by ' + last['typed']:>18}   change")
        print(f"   {'result':12} {first['result']:>18} {last['result']:>18}")
        for key in NUMBERS:
            a, z = first[key], last[key]
            if a is None or z is None:
                continue
            change = "same" if a == z else (f"{(z - a) / a * 100:+.0f}%" if a else "n/a")
            print(f"   {key:12} {a:>18,} {z:>18,}   {change}")
    if not shown:
        print("no task, mode and model has been run more than once yet")


def main():
    rows = [
        r
        for r in (
            measure(run)
            for run in b.read_jsonl(b.RUNS)
            if os.path.exists(run["transcript"])
        )
        if r
    ]
    rows.sort(
        key=lambda r: (
            b.ORDER.index(r["task"]),
            str(r["model"]),
            r["mode"] == "on",
            r["detail"]["started"],
        )
    )
    if "--versions" in sys.argv:
        counts = collections.Counter(str(r["detail"]["version"]) for r in rows)
        for version, count in sorted(counts.items()):
            print(f"Claude Code {version}: {count} run(s)")
        return
    if "--claude-code" in sys.argv:
        at = sys.argv.index("--claude-code") + 1
        if at >= len(sys.argv):
            sys.exit("--claude-code needs a version, such as 2.1.325")
        rows = [r for r in rows if str(r["detail"]["version"]) == sys.argv[at]]
    if "--json" in sys.argv:
        print(json.dumps(rows, indent=2))
        return
    if "--compare" in sys.argv:
        compare(rows)
        return
    if not rows:
        sys.exit("no runs recorded yet; do one with bin/run.py")
    cols = [c for c in rows[0] if c != "detail"]
    print("| " + " | ".join(cols) + " |")
    print("|" + "---|" * len(cols))
    for r in rows:
        print(
            "| "
            + " | ".join(
                f"{r[c]:,}" if isinstance(r[c], int) else str(r[c]) for c in cols
            )
            + " |"
        )
    totals = collections.defaultdict(float)
    for r in rows:
        totals[str(r["model"])] += r["cost_usd"] or 0
    print()
    for model, cost in sorted(totals.items()):
        runs = sum(1 for r in rows if str(r["model"]) == model)
        print(f"total recorded cost, {model}: ${cost:.2f} across {runs} run(s)")
    for r in rows:
        d = r["detail"]
        print(
            f"\n{r['task']} Code Mode {r['mode']}  {r['model']}  {d['started']}  session {d['session']}"
        )
        print(
            f"   effort {d['effort']}, speed {d['speed']}, permission mode {d['permission']}, "
            f"{d['config']} configuration, Claude Code {d['version']}"
        )
        print(f"   tools run: {d['tools_logged'] or d['tool_calls_in_transcript']}")
        if d["mcp_calls"]:
            print(f"   MCP calls the server received: {d['mcp_calls']}")
        print(f"   tokens: {d['tokens']}")
        if d["context_shown_start"] is not None:
            print(
                f"   /context showed {d['context_shown_start']:,} before and {d['context_shown_end']} after"
            )
        for line in d["check"] or []:
            print("  " + line)


if __name__ == "__main__":
    main()
