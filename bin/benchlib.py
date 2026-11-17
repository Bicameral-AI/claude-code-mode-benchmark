# Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE.
"""Shared paths and helpers for the benchmark scripts.

Everything a test session can see lives outside this repository, under BENCH_HOME, so that a
session cannot wander into the checker, the prompts or the answer data:

  BENCH_HOME/pristine/<corpus>   frozen copies of each task's starting files
  BENCH_WORK/<task>              the folder a session runs in; rebuilt before every run. It is
                                 outside your home folder, so that no CLAUDE.md above it is loaded
  BENCH_HOME/claude-config       a clean Claude Code configuration used only by the benchmark
  BENCH_HOME/harness, logs       the tool-call logger and what it and the MCP server record
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser(
    os.environ.get("BENCH_HOME") or "~/.cache/claude-code-mode-benchmark"
)
PRISTINE = os.path.join(HOME, "pristine")


def _default_work():
    """A folder with nothing personal above it.

    Claude Code loads every CLAUDE.md it finds in the folders above the one a session starts in,
    and your home folder usually has one. So the work folders live outside your home folder.
    """
    base = "/var/tmp" if os.path.isdir("/var/tmp") else tempfile.gettempdir()
    user = os.getuid() if hasattr(os, "getuid") else "user"
    return os.path.join(base, f"claude-code-mode-benchmark-{user}", "work")


WORK = os.path.expanduser(os.environ.get("BENCH_WORK") or _default_work())
HARNESS = os.path.join(HOME, "harness")
LOGS = os.path.join(HOME, "logs")
RESULTS = os.path.expanduser(os.environ.get("BENCH_RESULTS") or os.path.join(ROOT, "results"))

# BENCH_CONFIG=own runs sessions with your everyday Claude Code configuration instead of the
# clean one. Use it only if the clean configuration will not start; it makes your numbers
# depend on your own plugins, skills, hooks and memory files.
OWN_CONFIG = os.environ.get("BENCH_CONFIG") == "own"
CONFIG = (
    os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR") or "~/.claude")
    if OWN_CONFIG
    else os.path.join(HOME, "claude-config")
)

TOOL_LOG = os.path.join(LOGS, "tool-calls.jsonl")
MCP_LOG = os.path.join(LOGS, "mcp-calls.jsonl")
RUNS = os.path.join(LOGS, "runs.jsonl")
MCP_CONFIG = os.path.join(HARNESS, "mcp.json")
TOOL_LOGGER = os.path.join(HARNESS, "tool-log.py")

# Each task: the starting files it runs on, and a short name for tables.
TASKS = {
    "C0": {"corpus": "fastify", "name": "Control: one question, one file"},
    "T1": {"corpus": "fastify", "name": "Find broken links"},
    "E1": {"corpus": "invoice", "name": "Change an API across 36 call sites"},
    "M1": {"corpus": "empty", "name": "Aggregate 120 tickets through MCP"},
    "M2": {"corpus": "empty", "name": "Triage 120 tickets through MCP"},
    "M3": {"corpus": "empty", "name": "Triage 120 tickets with varied wording"},
}
ORDER = ["C0", "T1", "E1", "M1", "M2", "M3"]
# Tasks whose tickets use wording that does not repeat (see mcp/records.py).
VARIED_TICKETS = {"M3"}
MCP_TOOLS = ["mcp__records__list_tickets", "mcp__records__get_ticket"]


def task_or_exit(task):
    if task not in TASKS:
        sys.exit(f"unknown task {task!r}; choose one of {', '.join(ORDER)}")
    return task


def work_dir(task):
    return os.path.join(WORK, task)


def pristine_dir(task):
    return os.path.join(PRISTINE, TASKS[task]["corpus"])


def prompt_path(task):
    return os.path.join(ROOT, "tasks", task + ".txt")


def all_files(base):
    """Files under base, as sorted relative paths, leaving out tool and version-control folders."""
    out = []
    for d, dirs, names in os.walk(base):
        dirs[:] = [
            x
            for x in dirs
            if x not in (".git", ".claude", ".ruff_cache", "__pycache__")
        ]
        for n in names:
            out.append(os.path.relpath(os.path.join(d, n), base))
    return sorted(out)


def changed_files(task, allow=(), skip_prefixes=()):
    """Files that differ between the task's work folder and its starting files."""
    before, after = set(all_files(pristine_dir(task))), set(all_files(work_dir(task)))
    changed = sorted((before ^ after) - set(allow))
    for f in sorted(before & after):
        if f.startswith(tuple(skip_prefixes)) if skip_prefixes else False:
            continue
        with open(os.path.join(pristine_dir(task), f), "rb") as a:
            with open(os.path.join(work_dir(task), f), "rb") as b:
                if a.read() != b.read():
                    changed.append(f)
    return changed


def project_settings():
    """Settings written into every work folder. They apply to test sessions only."""
    return {
        # Code Mode does not work with Remote Control; a project setting turns it off here.
        "remoteControlAtStartup": False,
        # The benchmark's own MCP tools never ask, so 120 calls do not mean 120 prompts.
        "permissions": {"allow": MCP_TOOLS},
        # Log the name of every tool Claude Code runs, including the ones run from Code Mode
        # scripts, so tool executions can be counted the same way in both modes.
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "*",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f'python3 "{TOOL_LOGGER}" "{TOOL_LOG}"',
                            "timeout": 10,
                            "onFailure": "continue",
                        }
                    ],
                }
            ]
        },
    }


def instruction_files_above(path):
    """CLAUDE.md files in the folders above path, which Claude Code would load into a session."""
    found, folder = [], os.path.dirname(os.path.realpath(path))
    while True:
        for name in ("CLAUDE.md", "CLAUDE.local.md", os.path.join(".claude", "CLAUDE.md")):
            if os.path.isfile(os.path.join(folder, name)):
                found.append(os.path.join(folder, name))
        parent = os.path.dirname(folder)
        if parent == folder:
            return found
        folder = parent


def reset(task):
    """Rebuild the task's work folder from its starting files, as a one-commit git repository."""
    src, dst = pristine_dir(task), work_dir(task)
    if not os.path.isdir(src):
        sys.exit(f"{src} is missing; run bin/setup.py first")
    os.makedirs(os.path.dirname(WORK), mode=0o700, exist_ok=True)
    leaks = instruction_files_above(dst)
    if leaks:
        sys.exit(
            "Claude Code would load these instruction files into every test session:\n  "
            + "\n  ".join(leaks)
            + "\nSet BENCH_WORK to a folder that has no CLAUDE.md in any folder above it."
        )
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    os.makedirs(os.path.join(dst, ".claude"), exist_ok=True)
    with open(
        os.path.join(dst, ".claude", "settings.json"), "w", encoding="utf-8"
    ) as fh:
        json.dump(project_settings(), fh, indent=2)
        fh.write("\n")
    git = [
        "git",
        "-C",
        dst,
        "-c",
        "user.name=benchmark",
        "-c",
        "user.email=benchmark@example.invalid",
    ]
    quiet = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    subprocess.run(
        ["git", "-C", dst, "init", "--quiet", "-b", "main"], check=True, **quiet
    )
    subprocess.run(git + ["add", "-A"], check=True, **quiet)
    subprocess.run(
        git + ["commit", "--quiet", "--no-gpg-sign", "-m", "Starting files"],
        check=True,
        **quiet,
    )
    return dst


def project_dirs(task):
    """Folders where Claude Code saved transcripts of sessions run in the task's work folder."""
    base, want = os.path.join(CONFIG, "projects"), os.path.realpath(work_dir(task))
    if not os.path.isdir(base):
        return []
    key = re.sub(r"[^A-Za-z0-9]", "-", want)
    return [
        os.path.join(base, d)
        for d in os.listdir(base)
        if d == key or d.endswith("-work-" + task)
    ]


def transcripts(task):
    out = []
    for d in project_dirs(task):
        out += [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".jsonl")]
    return sorted(out, key=os.path.getmtime)


def read_jsonl(path):
    rows = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    continue
    return rows
