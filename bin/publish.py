#!/usr/bin/env python3
# Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE.
"""Publish the benchmark as a clean copy, without the maintainer's private files.

  bin/publish.py check                       build the published copy in a temporary folder and check it
  bin/publish.py check --worktree            the same for the files on disk, before they are committed
  bin/publish.py export --to DIR             write the checked copy to a new or empty folder, to look at
  bin/publish.py commit --to CLONE --message "..." [--tag NAME]
                                             replace the contents of a clone of the public repository
                                             with the checked copy and make one commit there
  bin/publish.py guard REMOTE URL            what the pre-push hook in .githooks runs: it refuses every
                                             push to a remote other than the private one

The working repository holds more than is published: the files listed in bin/private-files.txt.
A push sends history, so once the working repository holds one of those files its branches can
never be pushed to a public repository. The public repository is built by export instead. It
gets one commit for each publication and shares no commit with the working repository.

The copy is made from the last commit, not from the files on disk, so commit first. It holds
every tracked file that is not on the private list. Before it is written anywhere it is checked:

  - no file in it is on the private list;
  - every local link, image and anchor in its documents leads somewhere inside it;
  - it holds no secret, no home-folder path, no stray email address, and none of the terms
    listed in private/scan-terms.txt, where that file exists;
  - its scripts parse.

This script never pushes. commit prints the push command for the owner to run.

ARCHIVING.md has the whole procedure.
"""

import os
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import privatelist  # noqa: E402

ROOT = privatelist.ROOT
TERMS = os.path.join(ROOT, "private", "scan-terms.txt")
LINK = re.compile(r'(\]\()([^)\s]+)(\))|((?:href|src)=")([^"]+)(")')
SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
HEADING = re.compile(r"^ {0,3}#{1,6}\s+(.*?)\s*#*\s*$")
ANCHOR = re.compile(r'(?:id|name)="([^"]+)"')

# Raw records, saved as Claude Code wrote them. They are scanned for private details but are
# not documents, so their links are not checked.
RECORDS = ("results/context/",)

SECRETS = [
    ("an API key", re.compile(r"sk-ant-[A-Za-z0-9_-]{8,}")),
    ("a GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("a GitHub token", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("an AWS key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("a private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY")),
    ("a Slack token", re.compile(r"xox[abps]-[A-Za-z0-9-]{10,}")),
]
MACHINE_PATH = re.compile(r"/(Users|home|Volumes)/([A-Za-z0-9._-]+)")
PLACEHOLDERS = {"you", "your-name", "yourname", "name", "user", "username", "shared"}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)")
EMAIL_DOMAINS_ALLOWED = (
    "example.invalid",
    "example.com",
    "example.org",
    "anthropic.com",
)


def git(*args, cwd=ROOT, binary=False, check=True, stdin=None, env=None):
    done = subprocess.run(
        ["git", "-C", cwd, *args],
        check=check,
        capture_output=True,
        input=stdin,
        env=env,
    )
    return done.stdout if binary else done.stdout.decode("utf-8")


def option(name, default=None):
    if name in sys.argv:
        at = sys.argv.index(name) + 1
        if at < len(sys.argv):
            return sys.argv[at]
        sys.exit(f"{name} needs a value")
    return default


def published():
    """Every file the last commit holds that is not private, with its mode: {path: mode}."""
    files, refused = {}, []
    for entry in git("ls-tree", "-r", "-z", "HEAD").split("\0"):
        if not entry:
            continue
        meta, path = entry.split("\t", 1)
        mode, kind, _ = meta.split(" ")
        if privatelist.is_private(path):
            continue
        if kind != "blob" or mode not in ("100644", "100755"):
            refused.append(
                f"{path} ({'a symbolic link' if mode == '120000' else kind})"
            )
            continue
        files[path] = mode
    if refused:
        sys.exit(
            "only ordinary files can be published; remove these or add them to bin/private-files.txt:\n  "
            + "\n  ".join(refused)
        )
    return files


def on_disk():
    """What the published copy would hold if the files on disk were committed: {path: mode}."""
    files, refused = {}, []
    listed = git("ls-files", "-z", "--cached", "--others", "--exclude-standard")
    for path in sorted(set(listed.split("\0"))):
        full = os.path.join(ROOT, path)
        if not path or privatelist.is_private(path) or not os.path.lexists(full):
            continue
        if os.path.islink(full) or not os.path.isfile(full):
            refused.append(f"{path} (not an ordinary file)")
            continue
        files[path] = "100755" if os.access(full, os.X_OK) else "100644"
    if refused:
        sys.exit(
            "only ordinary files can be published; remove these or add them to bin/private-files.txt:\n  "
            + "\n  ".join(refused)
        )
    return files


def uncommitted():
    """Tracked files that are published and differ from the last commit."""
    fields = git("status", "--porcelain", "-z").split("\0")
    dirty, at = [], 0
    while at < len(fields):
        field = fields[at]
        at += 1
        if not field:
            continue
        status, path = field[:2], field[3:]
        if "R" in status or "C" in status:
            at += 1  # the name it was renamed or copied from follows
        if status != "??" and not privatelist.is_private(path):
            dirty.append(f"{status} {path}")
    return dirty


def build(dest, files, worktree=False):
    for path, mode in files.items():
        target = os.path.join(dest, path)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        if worktree:
            shutil.copyfile(os.path.join(ROOT, path), target)
        else:
            with open(target, "wb") as fh:
                fh.write(git("show", f"HEAD:{path}", binary=True))
        os.chmod(target, 0o755 if mode == "100755" else 0o644)


def text_of(path):
    """The file as text, or None if it is not text."""
    with open(path, "rb") as fh:
        data = fh.read()
    if b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def unfenced(text):
    """Lines outside fenced code blocks, numbered from 1, with inline code removed."""
    fenced = False
    for number, line in enumerate(text.split("\n"), 1):
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if not fenced:
            yield number, re.sub(r"`[^`]*`", "", line), line


def slug(heading):
    """The anchor GitHub gives a heading."""
    heading = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    heading = re.sub(r"<[^>]+>", "", heading)
    heading = re.sub(r"[^\w\- ]", "", heading.strip().lower())
    return heading.replace(" ", "-")


def anchors(text):
    found, seen = set(), {}
    for _, _, line in unfenced(text):
        match = HEADING.match(line)
        if match:
            base = slug(match.group(1))
            count = seen.get(base, 0)
            seen[base] = count + 1
            found.add(base if not count else f"{base}-{count}")
        found.update(ANCHOR.findall(line))
    return found


def check_private(dest, files):
    return [
        f"{path} is on the private list"
        for path in files
        if privatelist.is_private(path)
    ]


def check_links(dest, files):
    folders = {""}
    for path in files:
        while "/" in path:
            path = path.rsplit("/", 1)[0]
            folders.add(path)
    cache, bad, count = {}, [], 0

    def anchors_in(path):
        if path not in cache:
            cache[path] = anchors(text_of(os.path.join(dest, path)) or "")
        return cache[path]

    for path in sorted(files):
        if not path.endswith(".md") or path.startswith(RECORDS):
            continue
        here = os.path.dirname(path)
        for number, line, _ in unfenced(text_of(os.path.join(dest, path)) or ""):
            for match in LINK.finditer(line):
                target = match.group(2) or match.group(5)
                if SCHEME.match(target) or target.startswith("//"):
                    continue
                count += 1
                file_part, _, fragment = target.partition("#")
                file_part = urllib.parse.unquote(file_part.partition("?")[0])
                resolved = (
                    os.path.normpath(os.path.join(here, file_part)).replace(os.sep, "/")
                    if file_part
                    else path
                )
                if resolved == ".":
                    resolved = ""
                where = f"{path}:{number}: {target}"
                if resolved.startswith(".."):
                    bad.append(f"{where} leads outside the repository")
                elif resolved not in files and resolved.rstrip("/") not in folders:
                    bad.append(f"{where} is not in the published copy")
                elif fragment and resolved.endswith(".md"):
                    if urllib.parse.unquote(fragment).lower() not in anchors_in(
                        resolved
                    ):
                        bad.append(f"{where} names a heading that is not there")
    return bad, count


def extra_terms():
    if not os.path.isfile(TERMS):
        return None
    terms = []
    with open(TERMS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                try:
                    terms.append(re.compile(line, re.IGNORECASE))
                except re.error as error:
                    sys.exit(f"{TERMS}: {line!r} is not a regular expression: {error}")
    return terms


def allowed_domain(domain):
    domain = domain.lower()
    return any(domain == a or domain.endswith("." + a) for a in EMAIL_DOMAINS_ALLOWED)


def line_problems(line, terms):
    """What in one line of text must not be published."""
    bad = []
    for what, pattern in SECRETS:
        if pattern.search(line):
            bad.append(f"looks like {what}")
    for match in MACHINE_PATH.finditer(line):
        if match.group(2).lower() not in PLACEHOLDERS:
            bad.append(f"a path on one machine, {match.group(0)}")
    for match in EMAIL.finditer(line):
        if not allowed_domain(match.group(1)):
            bad.append(f"an email address, {match.group(0)}")
    for pattern in terms or []:
        match = pattern.search(line)
        if match:
            bad.append(f"a term from private/scan-terms.txt, {match.group(0)}")
    return bad


def check_details(dest, files, terms):
    bad = []
    for path in sorted(files):
        text = text_of(os.path.join(dest, path))
        if text is None:
            continue
        for number, line in enumerate(text.split("\n"), 1):
            bad += [f"{path}:{number}: {p}" for p in line_problems(line, terms)]
    return bad


def check_scripts(dest, files):
    bad = []
    with tempfile.TemporaryDirectory() as scratch:
        for path in sorted(files):
            if path.endswith(".py"):
                try:
                    py_compile.compile(
                        os.path.join(dest, path),
                        cfile=os.path.join(scratch, "out.pyc"),
                        doraise=True,
                    )
                except py_compile.PyCompileError as error:
                    bad.append(f"{path} does not parse: {error.msg.strip()}")
    return bad


def checked_copy(dest, worktree=False):
    """Build the published copy in dest and check it. Returns the files, or exits."""
    dirty = [] if worktree else uncommitted()
    if dirty:
        sys.exit(
            "commit these first; the published copy is made from the last commit, not from the files on disk:\n  "
            + "\n  ".join(dirty)
            + "\nor try the files on disk with: bin/publish.py check --worktree"
        )
    files = on_disk() if worktree else published()
    build(dest, files, worktree)
    terms = extra_terms()
    links, link_count = check_links(dest, files)
    results = [
        ("no private file", check_private(dest, files)),
        (f"{link_count} local links, images and anchors resolve", links),
        (
            "no secrets, machine paths, stray addresses or listed terms",
            check_details(dest, files, terms),
        ),
        ("scripts parse", check_scripts(dest, files)),
    ]
    commit = git("rev-parse", "--short", "HEAD").strip()
    source = "the files on disk, not yet committed" if worktree else f"commit {commit}"
    print(f"published copy of {source}: {len(files)} files")
    for name, problems in results:
        print(f"{'PASS' if not problems else 'FAIL'}  {name}")
        for line in problems:
            print("      " + line)
    if not worktree:
        loose = [
            f
            for f in git("ls-files", "-z", "--others", "--exclude-standard").split("\0")
            if f and not privatelist.is_private(f)
        ]
        if loose:
            print(
                f"      note: {len(loose)} untracked file(s) are not in the copy until committed, such as {loose[0]}"
            )
    if terms is None:
        print(
            "      note: private/scan-terms.txt is not here, so only the general scan for private details ran"
        )
    if any(problems for _, problems in results):
        sys.exit("the published copy failed its checks; nothing was written")
    return files


def check():
    with tempfile.TemporaryDirectory() as dest:
        checked_copy(dest, worktree="--worktree" in sys.argv)


def export():
    target = os.path.abspath(
        option("--to") or sys.exit("export needs --to, a new or empty folder")
    )
    if os.path.exists(target) and (not os.path.isdir(target) or os.listdir(target)):
        sys.exit(
            f"{target} exists and is not empty; export writes only to a new or empty folder"
        )
    with tempfile.TemporaryDirectory() as dest:
        files = checked_copy(dest)
        shutil.copytree(dest, target, dirs_exist_ok=True)
    print(f"wrote {len(files)} files to {target}")


def real(path):
    return os.path.realpath(path)


def commit():
    target = os.path.abspath(
        option("--to")
        or sys.exit("commit needs --to, a clone of the public repository")
    )
    message = option("--message") or sys.exit("commit needs --message")
    tag = option("--tag")
    # The published commit carries the identity set in this repository with git config --local,
    # and nothing else. It is passed in the environment, which outranks every git setting
    # (user.*, author.*, committer.*), and any identity already in the environment is replaced.
    name = git("config", "--local", "--get", "user.name", check=False).strip()
    email = git("config", "--local", "--get", "user.email", check=False).strip()
    if not name or not email:
        sys.exit(
            "set the identity for published commits in this repository first:\n"
            '  git config --local user.name "<name>"\n'
            '  git config --local user.email "<address>"\n'
            "They are used for every published commit, whatever any other setting says."
        )
    identity = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("GIT_AUTHOR_", "GIT_COMMITTER_")) and k != "EMAIL"
    }
    identity.update(
        GIT_AUTHOR_NAME=name,
        GIT_AUTHOR_EMAIL=email,
        GIT_COMMITTER_NAME=name,
        GIT_COMMITTER_EMAIL=email,
    )
    said = [f"the message: {p}" for p in line_problems(message, extra_terms())]
    said += [f"the tag: {p}" for p in line_problems(tag or "", extra_terms())]
    if said:
        sys.exit("the message or tag would publish something private:\n  " + "\n  ".join(said))
    if not os.path.isdir(target):
        sys.exit(f"{target} is not a folder")
    if tag and git("tag", "-l", tag, cwd=target, check=False).strip():
        sys.exit(f"{target} already has a tag named {tag}; a tag is never moved")
    try:
        top = git("rev-parse", "--show-toplevel", cwd=target).strip()
        common = git("rev-parse", "--git-common-dir", cwd=target).strip()
    except subprocess.CalledProcessError:
        sys.exit(
            f"{target} is not a git repository; clone the public repository, or run git init in an empty folder"
        )
    if real(top) != real(target):
        sys.exit(
            f"{target} is inside the repository at {top}; give the top of a clone of the public repository"
        )
    ours = git("rev-parse", "--git-common-dir").strip()
    if real(os.path.join(target, common)) == real(os.path.join(ROOT, ours)):
        sys.exit(
            "that is the working repository itself; the published copy goes to a separate clone of the public repository"
        )
    if git("status", "--porcelain", cwd=target).strip():
        sys.exit(
            f"{target} has uncommitted changes or untracked files; start from a clean clone"
        )
    theirs = git("rev-list", "--all", cwd=target).split()
    if theirs:
        known = git(
            "cat-file", "--batch-check", stdin=("\n".join(theirs) + "\n").encode()
        ).splitlines()
        shared = [line.split()[0] for line in known if not line.endswith("missing")]
        if shared:
            sys.exit(
                f"{target} shares {len(shared)} commit(s) with the working repository, such as {shared[0][:7]}. "
                "The public repository must have its own history; this looks like a clone of the working repository."
            )
    with tempfile.TemporaryDirectory() as dest:
        files = checked_copy(dest)
        # From here on the clone is changed. Whatever stops the work, put it back as it was.
        try:
            for old in git("ls-files", "-z", cwd=target).split("\0"):
                if old and os.path.lexists(os.path.join(target, old)):
                    os.remove(os.path.join(target, old))
            for top_dir, _, _ in os.walk(target, topdown=False):
                if (
                    ".git" not in os.path.relpath(top_dir, target).split(os.sep)
                    and top_dir != target
                ):
                    if not os.listdir(top_dir):
                        os.rmdir(top_dir)
            shutil.copytree(dest, target, dirs_exist_ok=True)
            # Stage what was removed, then every file of the copy by name. The names are forced,
            # so an ignore rule in the clone or on this machine cannot leave a published file out.
            git("add", "-u", cwd=target)
            git(
                "add",
                "--force",
                "--pathspec-from-file=-",
                "--pathspec-file-nul",
                cwd=target,
                stdin="\0".join(sorted(files)).encode(),
            )
            staged = {f for f in git("ls-files", "-z", cwd=target).split("\0") if f}
            leaked = sorted(f for f in staged if privatelist.is_private(f))
            extra = sorted(staged - set(files))
            missing = sorted(set(files) - staged)
            if leaked or extra or missing:
                sys.exit(
                    "stopped before committing; the clone does not match the published copy:"
                    + "".join(f"\n  private: {f}" for f in leaked)
                    + "".join(f"\n  not in the copy: {f}" for f in extra)
                    + "".join(f"\n  left out: {f}" for f in missing)
                    + "\nThe clone was put back as it was."
                )
            if not git("status", "--porcelain", "--untracked-files=no", cwd=target).strip():
                print(f"{target} already holds this published copy; no commit was made")
            else:
                git("commit", "-q", "-m", message, cwd=target, env=identity)
                made = git("rev-parse", "--short", "HEAD", cwd=target).strip()
                who = git(
                    "log", "-1", "--format=%an <%ae>%n%cn <%ce>", cwd=target
                ).split("\n")[:2]
                if who != [f"{name} <{email}>"] * 2:
                    git("reset", "-q", "--soft", "HEAD~1", cwd=target, check=False)
                    sys.exit(
                        f"the commit came out as author {who[0]}, committer {who[1]}, "
                        f"not {name} <{email}>; it was undone"
                    )
                print(f"committed {made} in {target}: {len(files)} files, as {who[0]}")
        except BaseException:
            restore(target, files)
            raise
    if tag:
        git("tag", tag, cwd=target, env=identity)
        print(f"tagged {tag}")
    print("nothing was pushed. When you have looked at it:")
    if git("remote", cwd=target).strip():
        print(
            f'  git -C "{target}" push'
            + (f' && git -C "{target}" push --tags' if tag else "")
        )
    else:
        print("  this clone has no remote yet; add the public repository, then push:")
        print(f'  git -C "{target}" remote add origin <address of the public repository>')
        print(
            f'  git -C "{target}" push -u origin HEAD'
            + (f' && git -C "{target}" push --tags' if tag else "")
        )


def restore(target, files):
    """Put a clone back as it was before the published copy was written into it."""
    has_head = git("rev-parse", "--verify", "-q", "HEAD", cwd=target, check=False).strip()
    before = set()
    if has_head:
        before = {
            f
            for f in git("ls-tree", "-r", "-z", "--name-only", "HEAD", cwd=target).split("\0")
            if f
        }
        git("reset", "-q", "--hard", cwd=target, check=False)
    else:
        git("read-tree", "--empty", cwd=target, check=False)
    for path in files:
        full = os.path.join(target, path)
        if path not in before and os.path.lexists(full):
            os.remove(full)
    git("clean", "-fdq", cwd=target, check=False)
    for top_dir, _, _ in os.walk(target, topdown=False):
        if ".git" not in os.path.relpath(top_dir, target).split(os.sep) and top_dir != target:
            if not os.listdir(top_dir):
                os.rmdir(top_dir)


def same_remote(one, two):
    def plain(url):
        url = url.strip().rstrip("/")
        return url[:-4] if url.endswith(".git") else url

    return bool(one) and plain(one) == plain(two)


def guard():
    """The pre-push hook: this repository is pushed to its private remote and nowhere else.

    Every push to another remote is refused, whatever it carries. Even the commits made before
    the private files were added carry details of the working repository, such as its authors.
    """
    name = sys.argv[2] if len(sys.argv) > 2 else ""
    url = sys.argv[3] if len(sys.argv) > 3 else ""
    sys.stdin.read()  # git sends the refs; read them so it is not cut off mid-write
    allowed = git("config", "--get", "benchmark.privateRemote", check=False).strip()
    if same_remote(allowed, url):
        return
    sys.exit(
        f"push refused: {name or url} ({url}) is not the private remote of this repository.\n"
        "The working repository is never pushed to any other remote. To publish, use:\n"
        '  bin/publish.py commit --to <a clone of the public repository> --message "..."\n'
        + (
            f"The private remote is recorded as {allowed}."
            if allowed
            else 'No private remote is recorded. Record it with:\n  git config benchmark.privateRemote "$(git remote get-url origin)"'
        )
    )


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action == "check":
        check()
    elif action == "export":
        export()
    elif action == "commit":
        commit()
    elif action == "guard":
        guard()
    else:
        sys.exit(__doc__)
