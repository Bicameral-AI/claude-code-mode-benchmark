#!/usr/bin/env python3
# Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE.
"""Check that a set of runs is complete and consistent before its results are published.

  bin/validate.py --claude-code 2.1.326 --results new_run     a new run, before it is promoted
  bin/validate.py --claude-code 2.1.325                       the current results in results/
  bin/validate.py --claude-code 2.1.326 --results new_run --repeat 2
                                                              also require two runs of everything

It checks what a script can check: that every run used one Claude Code version and one effort
level, that every model has the same number of runs of every test in each mode, that every MCP
run fetched all the tickets, that sessions of one mode started at the same size, and that the
saved result files match what bin/measure.py prints now. It exits with 1 if a check fails.

It cannot judge a failed check or an odd number. Those are listed for a person to read in the
transcripts. ARCHIVING.md has the rest of the procedure.
"""

import collections
import getpass
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import benchlib as b  # noqa: E402
import measure  # noqa: E402

SPREAD = 600  # tokens: sessions of one model and mode started within about 300 of each other so far
failed = False


def report(status, text, lines=()):
    global failed
    failed = failed or status == "FAIL"
    print(f"{status:5s} {text}")
    for line in lines:
        print(f"        {line}")


def option(name, default=None):
    if name in sys.argv:
        at = sys.argv.index(name) + 1
        if at < len(sys.argv):
            return sys.argv[at]
        sys.exit(f"{name} needs a value")
    return default


def printed(*flags):
    done = subprocess.run(
        [sys.executable, os.path.join(b.ROOT, "bin", "measure.py"), *flags],
        capture_output=True,
    )
    return done.stdout if done.returncode == 0 else None


def main():
    version = option("--claude-code") or sys.exit(__doc__)
    results = os.path.abspath(option("--results", b.RESULTS))
    repeat = option("--repeat")
    everything = [
        r
        for r in (
            measure.measure(run)
            for run in b.read_jsonl(b.RUNS)
            if os.path.exists(run["transcript"])
        )
        if r
    ]
    rows = [r for r in everything if str(r["detail"]["version"]) == version]
    print(
        f"Claude Code {version}: {len(rows)} run(s); results folder {os.path.relpath(results, b.ROOT)}\n"
    )
    if not rows:
        report("FAIL", "no run on this Claude Code version is recorded on this machine")
        sys.exit(1)

    efforts = sorted({str(r["detail"]["effort"]) for r in rows})
    report(
        "PASS" if len(efforts) == 1 else "FAIL",
        f"one effort level: {', '.join(efforts)}",
    )
    speeds = sorted({str(r["detail"]["speed"]) for r in rows})
    report(
        "PASS" if len(speeds) == 1 else "FAIL",
        f"one speed setting: {', '.join(speeds)}",
    )

    cells = collections.Counter((r["model"], r["task"], r["mode"]) for r in rows)
    models = sorted({r["model"] for r in rows})
    uneven = []
    for model in models:
        counts = {(t, m): cells[(model, t, m)] for t in b.ORDER for m in ("off", "on")}
        wanted = int(repeat) if repeat else max(counts.values())
        uneven += [
            f"{model} {t} Code Mode {m}: {n} run(s), expected {wanted}"
            for (t, m), n in counts.items()
            if n != wanted
        ]
    report(
        "FAIL" if uneven else "PASS",
        f"every model has the same number of runs of every test in each mode ({len(models)} model(s): {', '.join(models)})",
        uneven,
    )

    failures = [
        f"{r['model']} {r['task']} Code Mode {r['mode']}, started {r['detail']['started']}"
        for r in rows
        if r["result"] != "PASS"
    ]
    report(
        "WARN" if failures else "PASS",
        f"{len(rows) - len(failures)} of {len(rows)} runs passed their check"
        + (
            "; read each failed run's transcript and say in the results what happened"
            if failures
            else ""
        ),
        failures,
    )

    short = []
    for r in rows:
        if r["task"].startswith("M"):
            calls = r["detail"].get("mcp_calls") or {}
            one_server = any(
                "from 1 server process" in line
                for line in r["detail"].get("check") or []
            )
            if (calls.get("get_ticket") or 0) < 120 or not one_server:
                short.append(f"{r['model']} {r['task']} Code Mode {r['mode']}: {calls}")
    report(
        "FAIL" if short else "PASS",
        "every MCP run fetched all 120 tickets from one server process",
        short,
    )

    wide = []
    for model in models:
        for mode in ("off", "on"):
            sizes = [
                r["fixed_ctx"]
                for r in rows
                if r["model"] == model and r["mode"] == mode
            ]
            if sizes and max(sizes) - min(sizes) > SPREAD:
                wide.append(
                    f"{model} Code Mode {mode}: {min(sizes):,} to {max(sizes):,} tokens"
                )
    report(
        "FAIL" if wide else "PASS",
        f"sessions of one model and mode started within {SPREAD} tokens of each other (nothing leaked in)",
        wide,
    )

    agents = sum(r["subagents"] for r in rows)
    report(
        "PASS" if not agents else "WARN",
        f"subagents started: {agents}"
        + ("; task context does not count their work" if agents else ""),
    )

    for name, flags in (("measure.txt", ()), ("compare.txt", ("--compare",))):
        path = os.path.join(results, name)
        now = printed("--claude-code", version, *flags)
        if not os.path.isfile(path):
            report(
                "FAIL",
                f"{name} is missing from the results folder; make it with bin/measure.py --claude-code {version} {' '.join(flags)}".rstrip(),
            )
        elif now is None:
            report("FAIL", f"bin/measure.py failed, so {name} could not be checked")
        else:
            with open(path, "rb") as fh:
                same = fh.read() == now
            report(
                "PASS" if same else "FAIL",
                f"{name} matches what bin/measure.py prints from the transcripts now",
            )

    checks = os.path.join(results, "checks.txt")
    if os.path.isfile(checks):
        with open(checks, encoding="utf-8") as fh:
            verdicts = sum(
                1
                for line in fh
                if line.rstrip().endswith(("PASS", "FAIL")) and line[:1].strip()
            )
        report(
            "PASS" if verdicts == len(rows) else "FAIL",
            f"checks.txt holds {verdicts} verdict(s) for {len(rows)} run(s)",
        )
    else:
        report("FAIL", "checks.txt is missing from the results folder")

    scripted = sum(1 for r in rows if r["typed"] == "script")
    reports = os.path.join(results, "context")
    saved = (
        len([n for n in os.listdir(reports) if n.endswith(".md")])
        if os.path.isdir(reports)
        else 0
    )
    report(
        "PASS" if saved == scripted else "WARN",
        f"{saved} saved context report(s) for {scripted} scripted run(s)",
    )

    private = []
    needles = ("/Users/", "/home/", os.path.expanduser("~"), getpass.getuser() + "@")
    for top, _, names in os.walk(results):
        for name in names:
            if name.endswith((".md", ".txt", ".json")):
                with open(
                    os.path.join(top, name), encoding="utf-8", errors="replace"
                ) as fh:
                    text = fh.read()
                if any(n in text for n in needles):
                    private.append(os.path.relpath(os.path.join(top, name), results))
    report(
        "FAIL" if private else "PASS",
        "no home-folder path in the results folder",
        private[:10],
    )

    others = sorted({str(r["detail"]["version"]) for r in everything} - {version})
    if others:
        print(
            f"\nnote: this machine also holds runs on Claude Code {', '.join(others)}; they were left out."
        )
    print(
        "\n"
        + (
            "NOT VALID: fix what failed above."
            if failed
            else "Valid, as far as a script can tell. Read the WARN lines, then ARCHIVING.md for the next step."
        )
    )
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
