#!/usr/bin/env python3
# Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE.
"""Do one benchmark run: prepare the task, start the session, and score it when you exit.

  bin/run.py signin             setup only: sign in to the clean configuration
  bin/run.py check              setup only: check that Code Mode starts and the MCP server connects
  bin/run.py M1 off opus        task M1, Code Mode off, on Opus
  bin/run.py M1 on opus         the same task with Code Mode on
  bin/run.py T1 on sonnet --verbose     anything after the model is passed to claude

Tasks: C0, T1, E1, M1, M2. See tasks/ for the prompts.

What it does, in order:
  1. rebuilds the task's work folder from its starting files
  2. puts the task prompt on your clipboard
  3. starts Claude Code there, with the model you named, medium effort, fast mode off,
     Code Mode off or on, and the benchmark's MCP server connected
  4. after you type /exit, scores the run and records it for bin/measure.py

In the session you only paste the prompt, wait for the answer, and type /exit.

Settings, as environment variables:
  EFFORT=high            effort level (default medium)
  PERMISSION_MODE=default  ask before each action, if auto mode is not available to you
  BENCH_CONFIG=own       use your everyday Claude Code configuration, not the clean one
  DRY_RUN=1              show what would run, without starting Claude Code
  BENCH_AUTO=1           let the script type for you; bin/run-all.py sets this
"""

import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import benchlib as b  # noqa: E402
import check  # noqa: E402


def to_clipboard(text):
    for tool in (
        ["pbcopy"],
        ["wl-copy"],
        ["xclip", "-selection", "clipboard"],
        ["clip.exe"],
    ):
        if shutil.which(tool[0]):
            subprocess.run(tool, input=text, text=True, check=False)
            return True
    return False


def prompt_was_sent(transcript, prompt):
    head = prompt.strip()[:50]
    for d in b.read_jsonl(transcript):
        content = (d.get("message") or {}).get("content")
        if d.get("type") != "user":
            continue
        text = (
            content
            if isinstance(content, str)
            else "".join(
                x.get("text", "")
                for x in content or []
                if isinstance(x, dict) and x.get("type") == "text"
            )
        )
        if head in text:
            return True
    return False


ACCOUNT_SECTIONS = ("Custom Agents", "Skills")


def public_context_report(report):
    """Leave the lists of skills and custom agents out of a saved context report.

    Skills and agents from plugins synced to a Claude account still load in the clean
    configuration. Their names say nothing about the benchmark, so the per-item lists are
    dropped from the saved copy. The totals in the report's first table are kept.
    """
    kept, section = [], ""
    for line in report.splitlines():
        if line.startswith("### "):
            section = line[4:].strip()
        if section in ACCOUNT_SECTIONS:
            continue
        kept.append(line)
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).rstrip()
    return (
        text
        + "\n\n_Left out of this saved copy: the lists of custom agents and skills. Some of them"
        + " come from plugins on the tester's Claude account. Their totals are in the first table._"
    )


def save_context_report(transcript, task, model, mode, started):
    """Keep what /context printed at the end of the session, if it was run, as a text file."""
    report = ""
    for d in b.read_jsonl(transcript):
        content = (d.get("message") or {}).get("content")
        if d.get("type") == "user" and isinstance(content, str) and content.lstrip().startswith("## Context Usage"):
            report = content.strip()
    if not report:
        return None
    folder = os.path.join(b.RESULTS, "context")
    os.makedirs(folder, exist_ok=True)
    stamp = datetime.datetime.fromtimestamp(started).strftime("%Y%m%d-%H%M%S")
    name = "-".join([task, "".join(c if c.isalnum() else "-" for c in model), mode, stamp]) + ".md"
    path = os.path.join(folder, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f"<!-- {task}, Code Mode {mode}, {model}. Printed by /context after the final answer. -->\n\n")
        fh.write(public_context_report(report) + "\n")
    return path


def trust_work_folder(work):
    """Record, in the benchmark's own configuration, that its work folder is trusted.

    Claude Code asks "do you trust this folder?" the first time it opens one, and a script cannot
    answer. The folder is one the benchmark built itself, and this touches only the benchmark's
    configuration, never your own. A run typed by hand still shows you the question.
    """
    if b.OWN_CONFIG:
        return
    path = os.path.join(b.CONFIG, ".claude.json")
    if not os.path.exists(path):
        sys.exit("the benchmark's configuration is not set up: run bin/run.py signin first")
    with open(path, encoding="utf-8") as fh:
        config = json.load(fh)
    entry = config.setdefault("projects", {}).setdefault(os.path.realpath(work), {})
    if entry.get("hasTrustDialogAccepted"):
        return
    entry["hasTrustDialogAccepted"] = True
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)


def main():
    args = sys.argv[1:]
    # Two setup sessions that send no prompt and record nothing.
    setup_session = args[0] if args and args[0] in ("signin", "check") else None
    if setup_session:
        model = args[1] if len(args) > 1 else "opus"
        args = ["C0", "off" if setup_session == "signin" else "on", model]
    if len(args) < 3 or args[1] not in ("off", "on"):
        sys.exit(__doc__)
    task, mode, model, extra = b.task_or_exit(args[0]), args[1], args[2], args[3:]
    # A session started from inside another Claude Code session inherits its settings, such as
    # the parent's effort level and telemetry switches, so its numbers would not be comparable.
    nested = [v for v in ("CLAUDECODE", "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_CODE_SESSION_ID") if os.environ.get(v)]
    if nested and not os.environ.get("BENCH_ALLOW_NESTED") and not os.environ.get("DRY_RUN"):
        sys.exit(
            "This terminal is inside a Claude Code session ("
            + ", ".join(nested)
            + " is set). Run the benchmark from an ordinary terminal window, so that every run\n"
            "starts from the same conditions."
        )
    effort = os.environ.get("EFFORT", "medium")
    auto = bool(os.environ.get("BENCH_AUTO"))  # typed by bin/autopilot.py, not by a person
    permission = os.environ.get("PERMISSION_MODE", "auto")
    with open(b.prompt_path(task), encoding="utf-8") as fh:
        prompt = fh.read()

    os.makedirs(b.LOGS, exist_ok=True)
    os.makedirs(b.HARNESS, exist_ok=True)
    server = {
        "command": "python3",
        "args": [os.path.join(b.ROOT, "mcp", "records_server.py")],
        "env": {
            "RECORDS_CALL_LOG": b.MCP_LOG,
            "RECORDS_VARIANT": "varied" if task in b.VARIED_TICKETS else "plain",
        },
    }
    with open(b.MCP_CONFIG, "w", encoding="utf-8") as fh:
        json.dump({"mcpServers": {"records": server}}, fh, indent=2)

    env = dict(os.environ)
    env["CLAUDE_CODE_EXPERIMENTAL_CODE_MODE"] = "1" if mode == "on" else "0"
    env["CLAUDE_CODE_DISABLE_FAST_MODE"] = "1"  # fast mode changes speed and cost
    env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = (
        "1"  # nothing learned in one run reaches the next
    )
    env.pop(
        "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE", None
    )  # use the standard compaction point
    if not b.OWN_CONFIG:
        os.makedirs(b.CONFIG, exist_ok=True)
        env["CLAUDE_CONFIG_DIR"] = b.CONFIG
    command = [
        "claude",
        "--mcp-config",
        b.MCP_CONFIG,
        # Only the benchmark's own MCP server: connectors tied to your Claude account stay out.
        "--strict-mcp-config",
        "--model",
        model,
        "--effort",
        effort,
    ]
    if permission != "default":
        command += ["--permission-mode", permission]
    command += extra

    if setup_session == "signin":
        print("Setup session: sign in to the benchmark's clean configuration. Not a benchmark run.")
    elif setup_session == "check":
        print("Setup session: check that Code Mode starts. Not a benchmark run.")
    else:
        print(f"{task}: {b.TASKS[task]['name']}")
    print(
        f"Code Mode {mode}, {model}, effort {effort}, fast mode off, "
        f"{'your own' if b.OWN_CONFIG else 'clean'} configuration"
    )
    print("  " + " ".join(command))
    if os.environ.get("DRY_RUN"):
        print("dry run: nothing was reset and Claude Code was not started")
        return

    work = b.reset(task)
    open(b.MCP_LOG, "w").close()
    if setup_session == "signin":
        print("Follow the first-run screens and sign in (type /login if it does not ask), then type /exit.")
    elif setup_session == "check":
        print("Confirm Code Mode when asked. Look for 'Code Mode (experimental) is on' near the top,")
        print("type /mcp and check that 'records' is connected ('easel' is built in and may show too),")
        print("then type /exit.")
    else:
        copied = to_clipboard(prompt) if not auto else True
        print(f"work folder rebuilt: {work}")
        if auto:
            print("automated run: the script pastes the prompt, waits for the answer and types /exit")
        elif copied:
            print("the task prompt is on your clipboard: paste it, wait for the answer, then type /exit")
        else:
            print(f"no clipboard tool found: copy the prompt from {b.prompt_path(task)}")
    print()

    started = time.time()
    outcome = "by hand"
    if auto and not setup_session:
        import autopilot

        trust_work_folder(work)

        def recent_transcripts():
            return [p for p in b.transcripts(task) if os.path.getmtime(p) >= started - 1]

        limit = 60 * float(os.environ.get("BENCH_TIMEOUT_MINUTES", "30"))
        outcome = autopilot.drive(command, work, env, prompt, recent_transcripts, timeout=limit)
    else:
        subprocess.call(command, cwd=work, env=env)
    ended = time.time()
    if setup_session:
        print("\nSetup session finished. Nothing was scored or recorded.")
        return

    recent = [p for p in b.transcripts(task) if os.path.getmtime(p) >= started - 1]
    if not recent or not prompt_was_sent(recent[-1], prompt):
        print(
            "\nNo task prompt was sent in that session, so nothing was scored or recorded."
        )
        if auto:
            sys.exit(f"automation: the session {outcome} without the prompt being answered")
        return
    label = f"{model} {mode}"
    passed, report = check.score(task, label)
    saved = save_context_report(recent[-1], task, model, mode, started)
    print("\n" + report)
    os.makedirs(b.RESULTS, exist_ok=True)
    with open(os.path.join(b.RESULTS, "checks.txt"), "a", encoding="utf-8") as fh:
        fh.write(report + "\n")
    record = {
        "task": task,
        "mode": mode,
        "model_asked": model,
        "effort": effort,
        "permission": permission,
        "config": "own" if b.OWN_CONFIG else "clean",
        "started": datetime.datetime.fromtimestamp(
            started, datetime.timezone.utc
        ).isoformat(),
        "minutes_in_session": round((ended - started) / 60, 1),
        "transcript": recent[-1],
        "passed": passed,
        "typed": outcome,
        "detail": report.split("\n")[1:],
        "mcp_calls": check.mcp_activity()[0] if task in ("M1", "M2", "M3") else None,
    }
    with open(b.RUNS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
    if saved:
        print(f"\ncontext report saved: {os.path.relpath(saved, b.ROOT)}")
    print("\nrecorded. See all runs so far with: bin/measure.py")
    if auto and outcome != "done":
        sys.exit(f"automation: the session ended with '{outcome}', so check this run before trusting it")


if __name__ == "__main__":
    main()
