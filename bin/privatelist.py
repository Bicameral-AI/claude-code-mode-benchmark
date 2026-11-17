#!/usr/bin/env python3
# Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE.
"""The files that are never archived and never published.

  bin/privatelist.py              print the patterns
  bin/privatelist.py PATH ...     say which of these paths are private

bin/private-files.txt is the one list. bin/archive.py leaves the files it names out of every
archive, and bin/publish.py leaves them out of every published copy. The file explains the
patterns. If the list cannot be read, everything stops: a missing list must never be taken to
mean that nothing is private.
"""

import fnmatch
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIST = os.path.join(ROOT, "bin", "private-files.txt")

_patterns = None


def patterns():
    """The patterns in the list, lower-cased, without comments and blank lines."""
    global _patterns
    if _patterns is None:
        try:
            with open(LIST, encoding="utf-8") as fh:
                lines = [line.strip() for line in fh]
        except OSError as error:
            sys.exit(f"cannot read the list of private files, {LIST}: {error}")
        _patterns = [x.lower() for x in lines if x and not x.startswith("#")]
        if not _patterns:
            sys.exit(f"{LIST} names no files; refusing to treat nothing as private")
    return _patterns


def is_private(path):
    """Is this path, given from the top of the repository, on the private list?"""
    path = os.path.normpath(path).replace(os.sep, "/").lower()
    name = path.rsplit("/", 1)[-1]
    for pattern in patterns():
        if pattern.endswith("/"):
            if path.startswith(pattern) or path == pattern.rstrip("/"):
                return True
        elif "/" in pattern:
            if fnmatch.fnmatchcase(path, pattern):
                return True
        elif fnmatch.fnmatchcase(name, pattern):
            return True
    return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            print(f"{'private' if is_private(arg) else 'public '}  {arg}")
    else:
        print("\n".join(patterns()))
