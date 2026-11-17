#!/usr/bin/env python3
# Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE.
"""Keep a complete, browsable copy of the benchmark as it was published.

  bin/archive.py create --claude-code 2.1.325   copy the current benchmark into archive/
  bin/archive.py verify                         check every archive against what was published
  bin/archive.py verify claude-code-2.1.325     check one archive
  bin/archive.py list                           rewrite archive/README.md and print the archives
  bin/archive.py create --claude-code 2.1.325 --out "$PWD/archive-trial"
                                                a rehearsal: the same archive in a throwaway folder
  bin/archive.py promote --from new_run --claude-code 2.1.326
                                                put a validated new run in place of the current results

An archive mirrors the repository's layout: the top-level documents, LICENSE, assets/ and
results/, exactly as they were in the commit it was made from. The files listed in
bin/private-files.txt are never copied. Two things are added to each
document: a note at the top saying it is an archived copy, and nothing else. Links between the
archived files are left alone, so they keep working inside the archive. A link to something
that is not archived, such as a script, is pointed at the live file.

The archive is made from the last commit, not from the files on disk, so commit first. The
scripts, tasks and test data are not copied: the git tag this prints a command for keeps them.

ARCHIVING.md has the whole procedure.
"""

import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import benchlib as b  # noqa: E402
import privatelist  # noqa: E402

ARCHIVE = os.path.join(b.ROOT, "archive")
MANIFEST = "MANIFEST.json"
NAV = (
    "[README](../README.md) · [Benchmark Guide](../BENCHMARK_GUIDE.md) · [Archiving](../ARCHIVING.md) · "
    "[Results](../results/README.md) · [Changelog](../CHANGELOG.md)"
)
LINK = re.compile(r'(\]\()([^)\s]+)(\))|((?:href|src)=")([^"]+)(")')


def git(*args, binary=False):
    out = subprocess.run(
        ["git", "-C", b.ROOT, *args], check=True, capture_output=True
    ).stdout
    return out if binary else out.decode("utf-8")


def mirrored(path):
    """Is this tracked file part of an archive? Top-level documents, LICENSE, assets/ and results/."""
    if privatelist.is_private(path):
        return False  # on the list in bin/private-files.txt: never archived
    if path.startswith(("assets/", "results/")):
        return True
    return "/" not in path and (path.endswith(".md") or path == "LICENSE")


def option(name, default=None):
    if name in sys.argv:
        at = sys.argv.index(name) + 1
        if at < len(sys.argv):
            return sys.argv[at]
        sys.exit(f"{name} needs a value")
    return default


# Where archives are written and read. --out names another folder beside archive/, for a trial run.
BASE = option("--out", ARCHIVE)


def benchmark_version(commit):
    """The newest released version in the changelog: the first heading that starts with a digit."""
    for line in git("show", f"{commit}:CHANGELOG.md").splitlines():
        found = re.match(r"^## (\d+\.\d+\.\d+)", line)
        if found:
            return found.group(1)
    sys.exit("no released version found in CHANGELOG.md; pass --benchmark")


def banner(meta, path):
    up = "../" * (path.count("/") + 2)
    index = "../" * (path.count("/") + 1)
    return (
        "> [!NOTE]\n"
        f"> **Archived benchmark.** This is the benchmark as it was published for Claude Code {meta['claude_code']} "
        f"(benchmark version {meta['benchmark']}), archived on {meta['archived']} and kept unchanged. "
        f"See the [current benchmark]({up}README.md) or [all archived benchmarks]({index}README.md).\n\n"
    )


def repoint(text, path, files, label):
    """Leave links between archived files alone; point any other local link at the live file."""
    here = os.path.dirname(path)
    folders = {os.path.dirname(f) for f in files} | {""}

    def fix(match):
        before, target, after = (
            (match.group(1), match.group(2), match.group(3))
            if match.group(1)
            else (match.group(4), match.group(5), match.group(6))
        )
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
            return match.group(0)
        file_part, hash_mark, fragment = target.partition("#")
        resolved = os.path.normpath(os.path.join(here, file_part))
        if (
            resolved in files
            or resolved.rstrip("/") in folders
            or resolved.startswith("..")
        ):
            return match.group(0)
        if not os.path.exists(os.path.join(b.ROOT, resolved)):
            return match.group(0)  # already broken at the source; leave it to be seen
        live = os.path.relpath(
            os.path.join(b.ROOT, resolved), os.path.join(BASE, label, here)
        )
        return before + live + hash_mark + fragment + after

    out, fenced = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        out.append(line if fenced else LINK.sub(fix, line))
    return "\n".join(out)


def is_document(path):
    """Documents get the archive note and link fixes. Saved context reports are raw records and do not."""
    return path.endswith(".md") and not path.startswith("results/context/")


def archived_bytes(meta, path, files):
    """What an archived file must contain: the published bytes, plus the note and link fixes for documents."""
    data = git("show", f"{meta['source_commit']}:{path}", binary=True)
    if not is_document(path):
        return data
    text = repoint(data.decode("utf-8"), path, files, meta["label"])
    return (banner(meta, path) + text).encode("utf-8")


def summary_of(commit):
    """Models and run counts, read from the published measure.txt."""
    try:
        table = git("show", f"{commit}:results/measure.txt")
    except subprocess.CalledProcessError:
        return {}
    models, runs, passed = [], 0, 0
    for line in table.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) > 5 and cells[4] in ("PASS", "FAIL"):
            runs += 1
            passed += cells[4] == "PASS"
            if cells[3] not in models:
                models.append(cells[3])
        elif runs:
            break
    return {"models": models, "runs": runs, "passed": passed}


def manifests():
    found = []
    if os.path.isdir(BASE):
        for name in sorted(os.listdir(BASE)):
            path = os.path.join(BASE, name, MANIFEST)
            if os.path.isfile(path):
                with open(path, encoding="utf-8") as fh:
                    found.append(json.load(fh))
    return sorted(found, key=lambda m: m["archived"], reverse=True)


def write_index():
    lines = [
        "# Archived Benchmarks",
        "",
        NAV,
        "",
        "Each folder here is a complete copy of this benchmark as it was published for one version of Claude Code: "
        "its README, guide, predictions, results page, raw results and charts, kept unchanged. Open a folder's README "
        "to read that benchmark as it stood. The [current benchmark](../README.md) is always at the top of the repository.",
        "",
        "How a benchmark is archived, checked and replaced is described in [ARCHIVING.md](../ARCHIVING.md).",
        "",
    ]
    found = manifests()
    if not found:
        lines += [
            "No benchmark has been archived yet. The first archive is made when a newer benchmark replaces the current one.",
            "",
        ]
    else:
        lines += [
            "| Benchmark | Claude Code | Benchmark version | Archived | Models | Runs |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for m in found:
            s = m.get("summary") or {}
            models = ", ".join(f"`{x}`" for x in s.get("models", [])) or "not recorded"
            runs = (
                f"{s['runs']}, {s['passed']} passed"
                if s.get("runs")
                else "not recorded"
            )
            lines.append(
                f"| [{m['label']}]({m['label']}/README.md) | {m['claude_code']} | {m['benchmark']} | {m['archived']} | {models} | {runs} |"
            )
        lines.append("")
    lines += [
        "---",
        "",
        "© 2026 Bicameral, LLC. All rights reserved. See [LICENSE](../LICENSE).",
        "",
    ]
    os.makedirs(BASE, exist_ok=True)
    with open(os.path.join(BASE, "README.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return found


def create():
    claude_code = option("--claude-code") or sys.exit(
        "create needs --claude-code, the version the current results were made on"
    )
    commit = git("rev-parse", "HEAD").strip()
    files = [f for f in git("ls-files").splitlines() if mirrored(f)]
    dirty = [
        line
        for line in git("status", "--porcelain").splitlines()
        if mirrored(line[3:].strip('"'))
    ]
    if dirty:
        sys.exit(
            "commit these first; an archive is made from the last commit, not from the files on disk:\n  "
            + "\n  ".join(dirty)
        )
    label = option("--label", f"claude-code-{claude_code}")
    base = option("--out", ARCHIVE)
    target = os.path.join(base, label)
    if os.path.exists(target):
        sys.exit(f"{target} already exists; an archive is never overwritten")
    meta = {
        "label": label,
        "claude_code": claude_code,
        "benchmark": option("--benchmark") or benchmark_version(commit),
        "archived": option("--date") or datetime.date.today().isoformat(),
        "source_commit": commit,
        "summary": summary_of(commit),
        "files": {},
    }
    recorded = (
        git("show", f"{commit}:results/measure.txt")
        if "results/measure.txt" in files
        else ""
    )
    if recorded and f"Claude Code {claude_code}" not in recorded:
        sys.exit(
            f"results/measure.txt has no run on Claude Code {claude_code}; check --claude-code"
        )
    for path in files:
        data = archived_bytes(meta, path, set(files))
        dest = os.path.join(target, path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(data)
        meta["files"][path] = hashlib.sha256(data).hexdigest()
    with open(os.path.join(target, MANIFEST), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
        fh.write("\n")
    print(
        f"archived {len(files)} files from commit {commit[:7]} to {os.path.relpath(target, b.ROOT)}"
    )
    write_index()
    print(f"{os.path.relpath(os.path.join(base, 'README.md'), b.ROOT)} rewritten")
    print("next:")
    print(f"  bin/archive.py verify {label}")
    print(
        f"  git tag benchmark-{meta['benchmark']}_claude-code-{claude_code} {commit[:12]}"
    )
    print(
        "  then commit the archive folder by itself, before anything at the top level is changed"
    )


def broken_links(folder):
    """Local links and images inside an archive that lead nowhere."""
    bad = []
    for top, _, names in os.walk(folder):
        for name in names:
            if not name.endswith(".md"):
                continue
            path, fenced = os.path.join(top, name), False
            for line in open(path, encoding="utf-8"):
                if line.lstrip().startswith("```"):
                    fenced = not fenced
                if fenced:
                    continue
                for match in LINK.finditer(line):
                    target = match.group(2) or match.group(5)
                    if re.match(
                        r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target
                    ) or target.startswith("#"):
                        continue
                    if not os.path.exists(
                        os.path.normpath(os.path.join(top, target.partition("#")[0]))
                    ):
                        bad.append(f"{os.path.relpath(path, folder)}: {target}")
    return bad


def verify_one(meta, base=ARCHIVE):
    label, folder = meta["label"], os.path.join(base, meta["label"])
    problems, notes = [], []
    on_disk = set()
    for top, _, names in os.walk(folder):
        for name in names:
            on_disk.add(os.path.relpath(os.path.join(top, name), folder))
    on_disk.discard(MANIFEST)
    listed = set(meta["files"])
    problems += [f"missing: {p}" for p in sorted(listed - on_disk)]
    problems += [f"not in the manifest: {p}" for p in sorted(on_disk - listed)]
    for path in sorted(listed & on_disk):
        with open(os.path.join(folder, path), "rb") as fh:
            if hashlib.sha256(fh.read()).hexdigest() != meta["files"][path]:
                problems.append(f"changed since it was archived: {path}")
    try:
        git("cat-file", "-e", meta["source_commit"] + "^{commit}")
        files = set(listed)
        for path in sorted(listed & on_disk):
            with open(os.path.join(folder, path), "rb") as fh:
                if fh.read() != archived_bytes(meta, path, files):
                    problems.append(
                        f"differs from what commit {meta['source_commit'][:7]} published: {path}"
                    )
    except subprocess.CalledProcessError:
        notes.append(
            f"commit {meta['source_commit'][:7]} is not in this clone, so files were checked against the manifest only"
        )
    problems += [f"broken link in {entry}" for entry in broken_links(folder)]
    measure = os.path.join(folder, "results", "measure.txt")
    if os.path.isfile(measure) and os.path.isfile(b.RUNS):
        again = subprocess.run(
            [
                sys.executable,
                os.path.join(b.ROOT, "bin", "measure.py"),
                "--claude-code",
                meta["claude_code"],
            ],
            capture_output=True,
        )
        with open(measure, "rb") as fh:
            if again.returncode != 0 or not again.stdout.strip():
                notes.append(
                    "the raw transcripts for this version are not on this machine, so measure.txt was not regenerated"
                )
            elif again.stdout != fh.read():
                problems.append(
                    "results/measure.txt does not match what bin/measure.py prints from the raw transcripts now "
                    "(expected if bin/measure.py has changed since; otherwise look into it)"
                )
            else:
                notes.append(
                    "results/measure.txt regenerates from the raw transcripts, byte for byte"
                )
    else:
        notes.append("no run log on this machine, so measure.txt was not regenerated")
    print(
        f"{'PASS' if not problems else 'FAIL'}  {label}: {len(listed)} files, Claude Code {meta['claude_code']}, benchmark {meta['benchmark']}"
    )
    for line in problems:
        print("      " + line)
    for line in notes:
        print("      note: " + line)
    return not problems


def verify():
    wanted = [a for a in sys.argv[2:] if not a.startswith("-") and a != option("--out")]
    base = option("--out", ARCHIVE)
    found = []
    if os.path.isdir(base):
        for name in sorted(os.listdir(base)):
            path = os.path.join(base, name, MANIFEST)
            if os.path.isfile(path) and (not wanted or name in wanted):
                with open(path, encoding="utf-8") as fh:
                    found.append(json.load(fh))
    if not found:
        sys.exit("no archive found" + (f" named {', '.join(wanted)}" if wanted else ""))
    results = [verify_one(m, base) for m in found]
    sys.exit(0 if all(results) else 1)


def promote():
    """Put a validated new run where the current results are. The current benchmark must be archived first."""
    source = os.path.abspath(
        option("--from")
        or sys.exit("promote needs --from, the folder the new run was saved in")
    )
    new_version = option("--claude-code") or sys.exit(
        "promote needs --claude-code, the version of the new run"
    )
    current = git("show", "HEAD:results/measure.txt")
    held = sorted(set(re.findall(r"Claude Code (\d+\.\d+\.\d+)", current)))
    archived = {m["claude_code"]: m for m in manifests()}
    for version in held:
        if version not in archived:
            sys.exit(
                f"the current results are for Claude Code {version}, which is not archived; run bin/archive.py create --claude-code {version}"
            )
        if not verify_one(archived[version]):
            sys.exit(
                "the archive of the current benchmark does not verify; nothing was changed"
            )
    if not os.path.isfile(os.path.join(source, "checks.txt")):
        sys.exit(
            f"{source} has no checks.txt; it does not look like a run's results folder"
        )
    checked = subprocess.run(
        [
            sys.executable,
            os.path.join(b.ROOT, "bin", "validate.py"),
            "--claude-code",
            new_version,
            "--results",
            source,
        ]
    )
    if checked.returncode != 0:
        sys.exit("the new run does not validate; nothing was changed")
    for name in ("checks.txt", "measure.txt", "compare.txt"):
        if os.path.isfile(os.path.join(source, name)):
            shutil.copyfile(os.path.join(source, name), os.path.join(b.RESULTS, name))
    old_reports = os.path.join(b.RESULTS, "context")
    if os.path.isdir(os.path.join(source, "context")):
        if os.path.isdir(old_reports):
            shutil.rmtree(old_reports)
        shutil.copytree(os.path.join(source, "context"), old_reports)
    print(f"results/ now holds the run on Claude Code {new_version}.")
    print(
        "Still to do by hand: rewrite results/README.md, the README's summary, table and chart, the guide's costs,"
    )
    print(
        "and the changelog; add a folded block for the archived version to the README; then commit and tag."
    )


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action == "create":
        create()
    elif action == "verify":
        verify()
    elif action == "list":
        for m in write_index():
            print(
                f"{m['label']}  Claude Code {m['claude_code']}  benchmark {m['benchmark']}  archived {m['archived']}"
            )
        print("archive/README.md rewritten")
    elif action == "promote":
        promote()
    else:
        sys.exit(__doc__)
