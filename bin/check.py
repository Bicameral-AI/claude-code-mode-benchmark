#!/usr/bin/env python3
# Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE.
"""Score a finished run. bin/run.py does this for you when a session ends.

  bin/check.py T1            score the T1 work folder as it stands
  bin/check.py M1 opus off   the same, with a label in the result line
  bin/check.py truth         print the broken links T1 should find

Every task gets one verdict, PASS or FAIL, and the detail behind it.
"""

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import benchlib as b  # noqa: E402

sys.path.insert(0, os.path.join(b.ROOT, "mcp"))

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
MDLINK = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


# ---------------------------------------------------------------- T1: broken links


def strip_code(text):
    kept, fenced = [], False
    for line in text.split("\n"):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            kept.append(INLINE_CODE.sub("", line))
    return "\n".join(kept)


def resolve(source, target):
    target = urllib.parse.unquote(target.split("#")[0])
    return os.path.normpath(os.path.join(os.path.dirname(source), target))


def broken_links(base):
    files = b.all_files(base)
    paths, dirs = set(files), {os.path.dirname(f) for f in files}
    broken = set()
    for f in files:
        if not f.lower().endswith(".md"):
            continue
        with open(os.path.join(base, f), encoding="utf-8", errors="replace") as fh:
            text = strip_code(fh.read())
        for m in MDLINK.finditer(text):
            raw = m.group(1).strip("<>")
            if raw.startswith("#") or SCHEME.match(raw) or not raw.split("#")[0]:
                continue
            rel = resolve(f, raw)
            if rel not in paths and rel not in dirs:
                broken.add((f, rel))
    return broken


def check_t1():
    truth = broken_links(b.pristine_dir("T1"))
    path = os.path.join(b.work_dir("T1"), "answer.tsv")
    if not os.path.exists(path):
        return False, ["answer.tsv is missing"]
    got = set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2 and parts[0].strip():
                source, target = os.path.normpath(parts[0].strip()), parts[-1].strip()
                # Accept the target as written in the file, or as a path from the top folder.
                relative, from_root = (
                    (source, resolve(source, target)),
                    (source, resolve("", target)),
                )
                got.add(
                    from_root
                    if from_root in truth and relative not in truth
                    else relative
                )
    changed = b.changed_files("T1", allow={"answer.tsv"})
    lines = [
        f"expected {len(truth)} broken links, answered {len(got)}, correct {len(truth & got)}"
    ]
    for label, rows in (("missed", truth - got), ("wrong extra", got - truth)):
        lines += [f"{label}: {f} -> {t}" for f, t in sorted(rows)[:10]]
    lines.append(f"other files changed: {len(changed)} {changed[:5]}")
    return got == truth and not changed, lines


# ---------------------------------------------------------------- E1: API change, by tests

RUNNER = (
    "import json, os, unittest\n"
    "suite = unittest.defaultTestLoader.discover('.')\n"
    "result = unittest.TextTestRunner(stream=open(os.devnull, 'w')).run(suite)\n"
    "print(json.dumps({'ran': result.testsRun, 'bad': len(result.failures) + len(result.errors)}))\n"
)


def old_name_uses(base):
    """Places in the code that still mention format_amount as a name, attribute or import."""
    found = []
    for rel in b.all_files(base):
        if not rel.endswith(".py") or rel.startswith("tests/"):
            continue
        try:
            with open(os.path.join(base, rel), encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
        except SyntaxError:
            found.append(f"{rel}: does not parse")
            continue
        for node in ast.walk(tree):
            name = None
            if isinstance(node, ast.Name):
                name = node.id
            elif isinstance(node, ast.Attribute):
                name = node.attr
            elif isinstance(node, (ast.alias, ast.FunctionDef)):
                name = node.name
            if name == "format_amount":
                found.append(f"{rel}:{getattr(node, 'lineno', '?')}")
    return found


def check_e1():
    work, start = b.work_dir("E1"), b.pristine_dir("E1")
    tests_changed = [f for f in b.changed_files("E1") if f.startswith("tests/")]
    with tempfile.TemporaryDirectory() as tmp:
        copy = os.path.join(tmp, "project")
        shutil.copytree(
            work, copy, ignore=shutil.ignore_patterns(".git", ".claude", "__pycache__")
        )
        shutil.rmtree(os.path.join(copy, "tests"), ignore_errors=True)
        # Score against the original tests, whatever happened to the copy in the work folder.
        shutil.copytree(os.path.join(start, "tests"), os.path.join(copy, "tests"))
        try:
            out = subprocess.run(
                [sys.executable, "-c", RUNNER],
                cwd=copy,
                capture_output=True,
                text=True,
                timeout=120,
            ).stdout.strip()
            result = json.loads(out.splitlines()[-1])
        except (subprocess.TimeoutExpired, ValueError, IndexError):
            result = {"ran": 0, "bad": 0}
    passed = result["ran"] - result["bad"]
    left = old_name_uses(work)
    lines = [
        f"original tests passing: {passed} of 39",
        f"uses of the old name left in the code: {len(left)} {left[:6]}",
        f"test files edited: {len(tests_changed)} {tests_changed[:5]}",
    ]
    return passed == 39 and result[
        "ran"
    ] == 39 and not left and not tests_changed, lines


# ---------------------------------------------------------------- M1 and M2: through MCP


def mcp_activity():
    """What the benchmark's MCP server logged: calls by tool, tickets fetched, server processes."""
    from records import make_tickets

    wanted = {t["id"] for t in make_tickets()}
    calls, fetched, pids = {}, set(), set()
    for entry in b.read_jsonl(b.MCP_LOG):
        calls[entry.get("tool")] = calls.get(entry.get("tool"), 0) + 1
        pids.add(entry.get("pid"))
        if entry.get("tool") == "get_ticket":
            fetched.add(str((entry.get("args") or {}).get("id", "")).strip())
    valid = wanted <= fetched and len(pids) == 1
    return calls, len(wanted & fetched), len(wanted), len(pids), valid


def check_mcp(task):
    from records import expected_answer, expected_triage

    truth = expected_answer() if task == "M1" else expected_triage()
    path = os.path.join(b.work_dir(task), "answer.json")
    if not os.path.exists(path):
        return False, ["answer.json is missing"]
    try:
        with open(path, encoding="utf-8") as fh:
            got = json.load(fh)
        ids = sorted(str(i) for i in got.get("ids") or [])
    except (ValueError, AttributeError):
        return False, ["answer.json is not valid JSON in the form asked for"]
    right = ids == truth["ids"] and got.get("count") == truth["count"]
    if task == "M1":
        right = (
            right
            and got.get("total_refund_requested") == truth["total_refund_requested"]
        )
        lines = [
            f"expected {truth['count']} tickets totalling {truth['total_refund_requested']}, "
            f"answered {got.get('count')} totalling {got.get('total_refund_requested')}"
        ]
    else:
        hit = len(set(ids) & set(truth["ids"]))
        lines = [
            f"expected {truth['count']} tickets, answered {len(ids)}: {hit} right, {len(ids) - hit} wrong"
        ]
    missed, extra = (
        sorted(set(truth["ids"]) - set(ids)),
        sorted(set(ids) - set(truth["ids"])),
    )
    lines.append(f"missed {missed[:10]}  wrong extra {extra[:10]}")
    calls, fetched, wanted, servers, valid = mcp_activity()
    lines.append(f"MCP calls the server received: {calls or 'none recorded'}")
    lines.append(
        f"tickets fetched through the tools: {fetched} of {wanted}, from {servers} server process(es)"
        + (
            ""
            if valid
            else "  -> NOT A VALID RUN: the tickets were not all read through the tools"
        )
    )
    changed = b.changed_files(task, allow={"answer.json"})
    lines.append(f"other files changed: {len(changed)} {changed[:5]}")
    return right and valid and not changed, lines


# ---------------------------------------------------------------- C0: the control


def last_reply(task):
    """The final text Claude wrote in the most recent session run in the task's work folder."""
    paths = b.transcripts(task)
    text = ""
    for d in b.read_jsonl(paths[-1]) if paths else []:
        msg = d.get("message") or {}
        if (
            d.get("type") == "assistant"
            and not d.get("isSidechain")
            and isinstance(msg.get("content"), list)
        ):
            said = "".join(
                x.get("text", "") for x in msg["content"] if x.get("type") == "text"
            )
            text = said or text
    return text


def check_c0():
    reply = last_reply("C0")
    changed = b.changed_files("C0")
    ok = bool(re.search(r"\b(six|6)\s+months\b", reply, re.I))
    lines = [
        f"the answer {'mentions' if ok else 'does not mention'} the six-month support period",
        f"files changed: {len(changed)} {changed[:5]}",
    ]
    return ok and not changed, lines


CHECKS = {
    "C0": check_c0,
    "T1": check_t1,
    "E1": check_e1,
    "M1": lambda: check_mcp("M1"),
    "M2": lambda: check_mcp("M2"),
    "M3": lambda: check_mcp("M3"),
}


def score(task, label=""):
    passed, lines = CHECKS[task]()
    head = (
        f"{task}{' [' + label + ']' if label else ''}  {'PASS' if passed else 'FAIL'}"
    )
    return passed, "\n".join([head] + ["   " + line for line in lines])


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else ""
    if what == "truth":
        for f, t in sorted(broken_links(b.pristine_dir("T1"))):
            print(f"{f}\t{t}")
    elif what in CHECKS:
        print(score(what, " ".join(sys.argv[2:]))[1])
    else:
        sys.exit(__doc__)
