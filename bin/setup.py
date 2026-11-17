#!/usr/bin/env python3
# Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE.
"""Build everything the benchmark needs. Safe to run again; it rebuilds from scratch.

  bin/setup.py

It creates a folder outside this repository (see BENCH_HOME in bin/benchlib.py) holding:
  - Fastify at a fixed commit, with five files removed to plant eleven broken links
  - a small generated Python project for the API-change task
  - an empty folder for the MCP tasks
  - a tiny logger that records the name of every tool a session runs
"""

import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import benchlib as b  # noqa: E402
import check  # noqa: E402

sys.path.insert(0, os.path.join(b.ROOT, "fixtures"))
import invoice_gen  # noqa: E402

FASTIFY_COMMIT = "467972380963813755ac99f68fae228e30ac748f"
REMOVED = [
    "docs/Reference/Middleware.md",
    "docs/Reference/HTTP2.md",
    "docs/Reference/Warnings.md",
    "docs/resources/encapsulation_context.svg",
    "SPONSORS.md",
]
IGNORE_ALL = "# Test harness: keep code formatters off these files during a run.\n*\n"
LOGGER = '''"""Append the name of the tool Claude Code is about to run to a log. Never blocks a call."""
import json
import sys
import time

try:
    call = json.load(sys.stdin)
    entry = {
        "ts": round(time.time(), 3),
        "session": call.get("session_id"),
        "tool": call.get("tool_name"),
        "agent": call.get("agent_id"),
    }
    with open(sys.argv[1], "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\\n")
except Exception:
    pass
'''


def fresh(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)
    return path


def build_fastify():
    target = fresh(os.path.join(b.PRISTINE, "fastify"))
    with tempfile.TemporaryDirectory() as tmp:
        git = ["git", "-C", tmp]
        print(f"fetching fastify/fastify at {FASTIFY_COMMIT[:12]}")
        subprocess.run(git + ["init", "--quiet"], check=True)
        subprocess.run(
            git + ["remote", "add", "origin", "https://github.com/fastify/fastify.git"],
            check=True,
        )
        subprocess.run(
            git + ["fetch", "--quiet", "--depth", "1", "origin", FASTIFY_COMMIT],
            check=True,
        )
        subprocess.run(
            git
            + ["-c", "advice.detachedHead=false", "checkout", "--quiet", "FETCH_HEAD"],
            check=True,
        )
        shutil.rmtree(os.path.join(tmp, ".git"))
        for rel in REMOVED:
            os.remove(os.path.join(tmp, rel))
        with open(os.path.join(tmp, ".prettierignore"), "w", encoding="utf-8") as fh:
            fh.write(IGNORE_ALL)
        shutil.copytree(tmp, target, dirs_exist_ok=True)
    files, broken = len(b.all_files(target)), len(check.broken_links(target))
    print(f"fastify: {files} files, {broken} broken links")
    if (files, broken) != (392, 11):
        sys.exit(
            "expected 392 files and 11 broken links; the copy does not match the published test"
        )


def build_invoice():
    target = fresh(os.path.join(b.PRISTINE, "invoice"))
    sites = invoice_gen.build(target)
    with open(os.path.join(target, ".prettierignore"), "w", encoding="utf-8") as fh:
        fh.write(IGNORE_ALL)
    # Prove the task is sound: the starting files fail three tests, and a correct change passes.
    with tempfile.TemporaryDirectory() as tmp:
        invoice_gen.build(tmp, solved=True)
        solved = subprocess.run(
            [sys.executable, "-m", "unittest"], cwd=tmp, capture_output=True, text=True
        )
    start = subprocess.run(
        [sys.executable, "-m", "unittest"], cwd=target, capture_output=True, text=True
    )
    for cache in ("invoice/__pycache__", "scripts/__pycache__", "tests/__pycache__"):
        shutil.rmtree(os.path.join(target, cache), ignore_errors=True)
    ok = (
        "Ran 39 tests" in solved.stderr
        and "OK" in solved.stderr
        and "failures=1, errors=2" in start.stderr
    )
    print(
        f"invoice: {sites} call sites, 39 tests; starting files fail 3, a correct change passes all: {'yes' if ok else 'NO'}"
    )
    if not ok:
        sys.exit("the generated project does not behave as the task expects")


def build_empty():
    target = fresh(os.path.join(b.PRISTINE, "empty"))
    with open(os.path.join(target, "README.md"), "w", encoding="utf-8") as fh:
        fh.write("# Work folder\n\nThis folder starts empty on purpose.\n")
    print("empty: a folder with one README, for the MCP tasks")


def main():
    for tool in ("git", "claude"):
        if not shutil.which(tool):
            sys.exit(f"{tool} was not found on your PATH")
    os.makedirs(b.HARNESS, exist_ok=True)
    os.makedirs(b.LOGS, exist_ok=True)
    os.makedirs(os.path.join(b.RESULTS, "screenshots"), exist_ok=True)
    with open(b.TOOL_LOGGER, "w", encoding="utf-8") as fh:
        fh.write(LOGGER)
    build_fastify()
    build_invoice()
    build_empty()
    for task in b.ORDER:
        b.reset(task)
    print(f"work folders ready under {b.WORK}")
    if not b.OWN_CONFIG and not os.path.isdir(b.CONFIG):
        print(
            "\nNext: the benchmark uses its own clean Claude Code configuration, so you sign in once.\n"
            "Run  bin/run.py signin  and follow the first-run screens, then  bin/run.py check  to see that Code Mode starts."
        )


if __name__ == "__main__":
    main()
