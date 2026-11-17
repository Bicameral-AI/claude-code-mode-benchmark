#!/usr/bin/env python3
# Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE.
"""Do by script what a person does in a benchmark session: paste the prompt, wait, type /exit.

Code Mode only works in an interactive terminal session, so a run cannot be a background job.
This opens Claude Code in a pseudo-terminal, which is a real terminal as far as Claude Code can
tell, and types into it. It knows Claude has finished from the transcript Claude Code saves, not
from what is on the screen.

Used by bin/run.py when BENCH_AUTO is set, and so by bin/run-all.py.
"""

import fcntl
import os
import pty
import select
import signal
import struct
import sys
import termios
import time
import tty

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import benchlib as b  # noqa: E402

PASTE_START, PASTE_END = b"\x1b[200~", b"\x1b[201~"
QUIET = 10  # seconds the transcript must stay unchanged after Claude's last reply
START_WAIT = (4, 1.5, 60)  # at least, then quiet for, at most: seconds before pasting


def text_of(message):
    content = message.get("content")
    if isinstance(content, str):
        return content
    return "".join(
        x.get("text", "")
        for x in content or []
        if isinstance(x, dict) and x.get("type") == "text"
    )


def progress(path, head):
    """Where a session has got to: 'no prompt', 'working' or 'finished'."""
    sent = answered = False
    for d in b.read_jsonl(path):
        kind, msg = d.get("type"), d.get("message") or {}
        if not sent:
            sent = kind == "user" and head in text_of(msg)
            continue
        if kind == "assistant" and not (d.get("isVirtual") or msg.get("model") == "<synthetic>"):
            # A reply that ends the turn, as opposed to one that asks for a tool.
            answered = msg.get("stop_reason") == "end_turn"
        elif kind == "user" and not d.get("isVirtual") and not d.get("isMeta"):
            answered = False  # a tool result or a script's output: Claude carries on
    if not sent:
        return "no prompt"
    return "finished" if answered else "working"


def context_reports(path):
    """How many times /context has printed its report in this session."""
    return sum(
        1
        for d in b.read_jsonl(path)
        if d.get("type") == "user" and text_of(d.get("message") or {}).lstrip().startswith("## Context Usage")
    )


def drive(command, cwd, env, prompt, transcripts, timeout=1800):
    """Run one session to the end. Returns 'done', 'timeout' or 'ended early'."""
    head = prompt.strip()[:50]
    pid, fd = pty.fork()
    if pid == 0:
        os.chdir(cwd)
        os.execvpe(command[0], command, env)

    watching = sys.stdin.isatty() and sys.stdout.isatty()
    rows, cols = 45, 150
    if watching:
        rows, cols = struct.unpack(
            "HHHH", fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, b"\0" * 8)
        )[:2]
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
    saved = termios.tcgetattr(sys.stdin) if watching else None
    if watching:
        tty.setraw(
            sys.stdin.fileno()
        )  # so you can still type, for example to answer a question

    def send(data):
        try:
            os.write(fd, data)
        except OSError:
            pass

    state, began, heard, mark, checked, outcome = (
        "starting",
        time.time(),
        time.time(),
        0.0,
        0.0,
        None,
    )
    seen = 0
    try:
        while outcome is None:
            readable = select.select(
                [fd] + ([sys.stdin] if watching else []), [], [], 0.25
            )[0]
            now = time.time()
            if fd in readable:
                try:
                    data = os.read(fd, 65536)
                except OSError:
                    data = b""
                if not data:
                    outcome = "done" if state in ("leaving", "leaving again", "stopped") else "ended early"
                    break
                heard = now
                if watching:
                    sys.stdout.buffer.write(data)
                    sys.stdout.buffer.flush()
            if watching and sys.stdin in readable:
                send(os.read(sys.stdin.fileno(), 1024))

            least, quiet, most = START_WAIT
            if (
                state == "starting"
                and now - began > least
                and (now - heard > quiet or now - began > most)
            ):
                send(PASTE_START + prompt.strip().encode() + PASTE_END)
                state, mark = "pasted", now
            elif state == "pasted" and now - mark > 1.0:
                send(b"\r")
                state, mark = "working", now
            elif state == "working" and now - checked > 1.0:
                checked = now
                recent = transcripts()
                where = progress(recent[-1], head) if recent else "no prompt"
                if where == "no prompt" and now - mark > 20:
                    send(b"\r")  # the Enter did not take; try once more
                    mark = now
                elif (
                    where == "finished" and now - os.path.getmtime(recent[-1]) >= QUIET
                ):
                    # Ask for the context report now, after the last request to the model, so
                    # that it is saved with the session without changing any measured number.
                    seen = context_reports(recent[-1])
                    send(b"/context")
                    state, mark = "typing context", now
            elif state == "typing context" and now - mark > 0.8:
                send(b"\r")
                state, mark = "context asked", now
            elif state == "context asked" and now - checked > 0.5:
                checked = now
                recent = transcripts()
                if (recent and context_reports(recent[-1]) > seen) or now - mark > 10:
                    send(b"/exit")
                    state, mark = "typing exit", now
            elif state == "typing exit" and now - mark > 0.8:
                send(b"\r")
                state, mark = "leaving", now
            elif state == "leaving" and now - mark > 12:
                send(b"/exit\r")  # ask once more
                state, mark = "leaving again", now
            elif state == "leaving again" and now - mark > 30:
                os.kill(pid, signal.SIGTERM)  # the session will not close; stop waiting for it
                state = "stopped"
            if now - began > timeout:
                os.kill(pid, signal.SIGTERM)
                outcome = "timeout"
    finally:
        if saved:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, saved)
        try:
            os.waitpid(pid, 0)
        except OSError:
            pass
        os.close(fd)
    return outcome
