#!/usr/bin/env python3
# Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE.
"""Remove everything the benchmark has built or recorded, back to a fresh download.

  bin/clean.py          show what would be removed
  bin/clean.py --yes    remove it

It removes:
  - the starting files, the tool logger and the logs
  - the benchmark's own Claude Code configuration, which means signing in again next time
  - the work folders that sessions run in
  - the recorded results (results/checks.txt and results/measure.txt) and Python caches

It keeps your screenshots, the scripts and the documentation. Afterwards, start again with
bin/setup.py.
"""

import glob
import os
import shutil
import sys

sys.dont_write_bytecode = True  # do not leave a cache behind while cleaning up
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import benchlib as b  # noqa: E402

NAME = "claude-code-mode-benchmark"


def safe(path):
    """Only ever delete a folder that is plainly the benchmark's own."""
    real = os.path.realpath(path)
    return NAME in os.path.basename(real) and real not in ("/", os.path.expanduser("~"))


def main():
    work_root = (
        os.path.dirname(b.WORK)
        if NAME in os.path.basename(os.path.dirname(b.WORK))
        else b.WORK
    )
    folders = [p for p in (b.HOME, work_root) if os.path.isdir(p)]
    files = [
        p
        for p in (
            os.path.join(b.RESULTS, "checks.txt"),
            os.path.join(b.RESULTS, "measure.txt"),
        )
        if os.path.exists(p)
    ]
    caches = glob.glob(os.path.join(b.ROOT, "**", "__pycache__"), recursive=True)
    caches += [p for p in (os.path.join(b.ROOT, ".ruff_cache"),) if os.path.isdir(p)]
    refused = [p for p in folders if not safe(p)]
    if refused:
        sys.exit(
            "refusing to remove a folder that is not named for the benchmark:\n  "
            + "\n  ".join(refused)
        )
    everything = folders + files + caches
    if not everything:
        print("nothing to remove: already clean")
        return
    go = "--yes" in sys.argv
    print("removing:" if go else "would remove (run with --yes to do it):")
    for p in everything:
        print("  " + p)
        if go:
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    if go:
        print("clean. Start again with: bin/setup.py")


if __name__ == "__main__":
    main()
