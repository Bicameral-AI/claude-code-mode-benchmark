#!/usr/bin/env python3
# Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE.
"""Start the benchmark over: set aside the runs recorded so far and rebuild the work folders.

  bin/new-round.py

After this, bin/measure.py reports only the runs you do from now on. Earlier records are kept,
renamed with the time, under the logs folder; screenshots are left alone.
"""

import datetime
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import benchlib as b  # noqa: E402

stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
kept = 0
for path in (
    b.RUNS,
    b.TOOL_LOG,
    os.path.join(b.RESULTS, "checks.txt"),
    os.path.join(b.RESULTS, "measure.txt"),
):
    if os.path.exists(path) and os.path.getsize(path):
        os.makedirs(os.path.join(b.LOGS, "earlier"), exist_ok=True)
        # shutil.move, not os.rename: the repository and the logs may be on different disks.
        shutil.move(path, os.path.join(b.LOGS, "earlier", f"{stamp}-{os.path.basename(path)}"))
        kept += 1
for task in b.ORDER:
    b.reset(task)
print(
    f"new round started; {kept} earlier record file(s) moved to {os.path.join(b.LOGS, 'earlier')}"
)
print("work folders rebuilt")
