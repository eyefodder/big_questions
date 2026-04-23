#!/usr/bin/env python3
"""Bootstrap a new inquiry-instrument instance at a given path.

Usage:
    python3 init_inquiry.py --path <target> [--memex-path <path>] [--force]

Shells out to memex's `helpers/init_wiki.py` to create the generic
Karpathy-style wiki tree (with `wiki/questions/` as the pages subdir),
then appends the inquiry-specific addendum onto `<target>/SCHEMA.md`.

Inquiry skills (inquiry-elicit, inquiry-gap, inquiry-init) are installed
user-scoped at `~/.claude/skills/` per the big_questions README — same
pattern as memex. This helper does not manage that install; it only
bootstraps the instance content (SCHEMA.md + directory tree).

Idempotent: re-running against a target that is already initialized
will detect the addendum marker in SCHEMA.md and skip re-appending
(unless --force is set).

Stdlib only. Python 3.11+.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# The addendum file's first line is this exact comment. We use it as the
# idempotency marker — if it's already in SCHEMA.md, the addendum was
# applied.
ADDENDUM_MARKER = "<!-- Inquiry domain addendum — appends to memex/schema.example.md -->"

# Resolve paths relative to this helper's install location
# (big_questions/helpers/init_inquiry.py -> big_questions/).
BIG_QUESTIONS_ROOT = Path(__file__).resolve().parent.parent
ADDENDUM_PATH = BIG_QUESTIONS_ROOT / "schema.inquiry.example.md"


def eprint(msg: str) -> None:
    print(f"init_inquiry: {msg}", file=sys.stderr)


def precondition_check(memex_path: Path) -> Path | None:
    """Return the init_wiki.py Path if present and executable, else None."""
    init_wiki = memex_path / "helpers" / "init_wiki.py"
    if not init_wiki.is_file() or not os.access(init_wiki, os.X_OK):
        eprint(f"memex harness not found at {memex_path}")
        print("Install memex first: https://github.com/<user>/memex",
              file=sys.stderr)
        print("Or pass --memex-path pointing at your install location.",
              file=sys.stderr)
        return None
    return init_wiki


def run_init_wiki(init_wiki: Path, target: Path, force: bool) -> tuple[bool, str]:
    """Invoke memex's init_wiki.py. Return (ok, stdout).

    If SCHEMA.md already exists and --force is not set, memex's init_wiki
    would hard-fail. To preserve our own top-level idempotency contract
    (re-run without --force should be green when the instance is already
    initialized), we detect that state and skip the sub-call — returning
    a synthetic stdout note. The addendum step still runs and will
    short-circuit on its own idempotency check.
    """
    schema_dst = target / "SCHEMA.md"
    if schema_dst.exists() and not force:
        return True, (f"init_wiki: target already initialized at {target}; "
                      "sub-call skipped (re-run with --force to reseed SCHEMA.md).")

    cmd = [sys.executable, str(init_wiki),
           "--path", str(target), "--pages-dir", "questions"]
    if force:
        cmd.append("--force")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        eprint("init_wiki failed (see below); aborting before layering.")
        if result.stderr:
            sys.stderr.write(result.stderr)
            if not result.stderr.endswith("\n"):
                sys.stderr.write("\n")
        return False, result.stdout
    return True, result.stdout


def append_addendum(target: Path, force: bool) -> str:
    """Append the inquiry addendum to <target>/SCHEMA.md.

    Returns a short status string for the final report:
      "appended", "already present (skipped)", or "re-appended (--force)".
    """
    schema_dst = target / "SCHEMA.md"
    addendum_text = ADDENDUM_PATH.read_text(encoding="utf-8")
    existing = schema_dst.read_text(encoding="utf-8") if schema_dst.exists() else ""
    already_present = ADDENDUM_MARKER in existing

    if already_present and not force:
        return "already present (skipped)"

    # Ensure a newline separator between existing content and addendum.
    separator = ""
    if existing and not existing.endswith("\n"):
        separator = "\n"
    with schema_dst.open("a", encoding="utf-8") as fh:
        fh.write(separator)
        fh.write(addendum_text)

    return "re-appended (--force)" if already_present else "appended"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bootstrap a new inquiry-instrument instance.")
    parser.add_argument("--path", required=True, type=Path,
                        help="Target instance directory")
    parser.add_argument("--memex-path", type=str,
                        default="~/Development/memex",
                        help="Path to memex install "
                             "(default: ~/Development/memex)")
    parser.add_argument("--force", action="store_true",
                        help="Pass --force to init_wiki; also re-append "
                             "the inquiry addendum even if already present")
    args = parser.parse_args()

    target: Path = args.path
    memex_path = Path(os.path.expanduser(args.memex_path)).resolve()
    force: bool = args.force

    # Step 1 — Precondition check
    init_wiki = precondition_check(memex_path)
    if init_wiki is None:
        return 1

    # Sanity-check our own install: the addendum file must exist.
    if not ADDENDUM_PATH.is_file():
        eprint(f"inquiry schema addendum missing at {ADDENDUM_PATH}")
        return 1

    # Step 2 — Shell out to init_wiki
    ok, init_wiki_stdout = run_init_wiki(init_wiki, target, force)
    if not ok:
        return 1

    # Step 3 — Append (or skip) the inquiry addendum
    try:
        addendum_status = append_addendum(target, force)
    except OSError as err:
        eprint(f"failed to append addendum to SCHEMA.md: {err}")
        eprint("init_wiki completed but addendum was not applied. "
               "Re-run once the issue is fixed.")
        return 1

    # Step 4 — Final report
    print("=" * 60)
    print(f"Inquiry instance initialized at {target}")
    print("=" * 60)
    if init_wiki_stdout.strip():
        print("\n[init_wiki output]")
        for line in init_wiki_stdout.rstrip("\n").splitlines():
            print(f"  {line}")
    print("\n[inquiry layer]")
    print(f"  SCHEMA.md addendum: {addendum_status}")
    print("\nNext step: run `/inquiry-elicit` in this directory to begin "
          "eliciting your questions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
