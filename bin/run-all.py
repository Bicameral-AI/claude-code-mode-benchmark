#!/usr/bin/env python3
# Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE.
"""Run every task for a model, Code Mode off then on, back to back, with nobody typing.

  bin/run-all.py sonnet                          all twelve runs on Sonnet
  bin/run-all.py sonnet claude-haiku-5-5 fable   one model after another
  TASKS=M1,M2 bin/run-all.py opus                only some tasks
  REPEAT=3 bin/run-all.py sonnet                 the whole set three times

Each run is still an interactive Claude Code session, which Code Mode requires. The script opens
it in a terminal of its own, pastes the prompt, waits until the saved transcript shows Claude has
finished, and types /exit. Leave the terminal alone while it works; if a session asks you a
question, you can still answer it.

It stops at the first run that does not finish properly, so that a fault is looked at and not
repeated in every run after it. Do the setup in the guide first: bin/setup.py, bin/run.py signin and
bin/run.py check.
"""

import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import benchlib as b  # noqa: E402


def main():
    models = [m for m in sys.argv[1:] if not m.startswith("-")]
    if not models:
        sys.exit(__doc__)
    tasks = [t.strip() for t in os.environ.get("TASKS", ",".join(b.ORDER)).split(",") if t.strip()]
    for task in tasks:
        b.task_or_exit(task)
    repeat = int(os.environ.get("REPEAT", "1"))
    jobs = [(m, r, t, mode) for m in models for r in range(repeat) for t in tasks for mode in ("off", "on")]
    env = dict(os.environ, BENCH_AUTO="1")
    run = os.path.join(b.ROOT, "bin", "run.py")
    began = time.time()
    for n, (model, _, task, mode) in enumerate(jobs, 1):
        print(f"\n===== run {n} of {len(jobs)}: {task} Code Mode {mode} on {model} =====", flush=True)
        code = subprocess.call([sys.executable, run, task, mode, model], env=env)
        if code != 0:
            print(f"\nstopped at run {n} of {len(jobs)}. To repeat it by hand: bin/run.py {task} {mode} {model}")
            sys.exit(code)
        time.sleep(2)
    print(f"\nall {len(jobs)} runs finished in {round((time.time() - began) / 60)} minutes")
    subprocess.call([sys.executable, os.path.join(b.ROOT, "bin", "measure.py")])


if __name__ == "__main__":
    main()
