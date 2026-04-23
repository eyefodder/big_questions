---
name: inquiry-init
description: Bootstrap a new inquiry-instance in one command — creates the directory tree, composes SCHEMA.md from the memex base plus the inquiry addendum, and symlinks the inquiry-elicit and inquiry-gap skills into the instance's project-scoped .claude/skills/.
---

# inquiry-init

## Purpose

One-command bootstrap for an inquiry-instrument instance. Invoke this skill when the user runs `/inquiry-init <path>` or otherwise asks to "bootstrap," "initialize," or "set up" a new inquiry (a collection of ~12 big questions). This replaces the multi-step manual recipe (`mkdir` + `cat` + `ln -s`) that used to live in the big_questions README's "Bootstrap" section: the helper shells out to memex's `init_wiki.py` for the generic wiki tree, appends the inquiry schema addendum to `SCHEMA.md`, and symlinks the two inquiry skills into `<target>/.claude/skills/`.

This skill is domain-specific to the inquiry-instrument pattern — questions, contributions, and gap reports. The parallel generic bootstrap is `/wiki-init`; the helper this skill wraps calls it internally with `--pages-dir questions`.

## Preconditions

- The **memex harness is installed** — specifically, `<memex-path>/helpers/init_wiki.py` must exist and be executable. The default install location is `~/Development/memex/`; the user may pass a different path via `--memex-path`. The helper checks this first and exits with a clear error if memex isn't found (so no file operations happen on the target directory). If the user sees that error, the fix is to install memex (clone the repo and symlink harness skills per the big_questions README).
- The user has write access to the target path. The target may or may not already exist; if it exists, it must be a directory (not a file).
- Python 3 is available on `PATH` as `python3`.

## Steps

### 1. Parse the target path

Extract the target path from the user's invocation. Typical shapes:

- `/inquiry-init ~/vaults/MyVault/01_Projects/my_big_questions`
- `/inquiry-init /tmp/scratch_inquiry`
- `/inquiry-init` (path omitted — ask the user)

If the path is missing or ambiguous, ask: "What path? e.g. `~/vaults/MyVault/01_Projects/my_big_questions`." Do not guess or default silently to anything potentially destructive.

Expand `~` to the user's home directory before passing to the helper (the helper does not expand shell metacharacters itself).

### 2. (Optional) `--memex-path` override

If the user has memex installed somewhere non-standard (not `~/Development/memex/`), accept `--memex-path <path>` and pass it through. Most users will not need this — the default is correct for the standard install pattern documented in the big_questions README.

### 3. (Optional) `--force` reseed

If the user passes `--force` — or explicitly asks to "reseed," "reset," or "refresh" the schema after a schema template update — pass `--force` through.

**What `--force` does:** re-copies `SCHEMA.md` from the templates (memex base + inquiry addendum). It **preserves** your questions under `wiki/questions/`, `log.md`, `index.md`, and anything in `raw/` or `meta/`. Use it when you've pulled a schema update and want the instance to pick it up. The final `SCHEMA.md` will contain exactly one copy of the addendum — not double-appended — so `--force` is safe on an already-initialized instance.

### 4. Invoke the helper

Shell out via the bash tool. **Always invoke with `python3` explicitly** (per Decision 5 in the architecture decisions — avoid ambiguous `python` on macOS where it may resolve to Python 2 or be missing):

```bash
python3 <path-to-big_questions>/helpers/init_inquiry.py --path <target> [--memex-path <path>] [--force]
```

**Resolving the helper path.** Because this skill is typically installed as a symlink into `<target>/.claude/skills/inquiry-init/` (or invoked from a staging instance before install), `helpers/` is not adjacent to the running SKILL.md in the skills directory. Resolve the helper path in this order (same pattern as `wiki-init` and `wiki-ingest`):

1. If `./big_questions/helpers/init_inquiry.py` exists relative to the current working directory (the user has vendored or symlinked the repo into their instance), use that.
2. Otherwise, resolve the SKILL.md's *real* path (follow the symlink) and use `<big_questions-repo>/helpers/init_inquiry.py` — the helpers live as siblings of `skills/` in the big_questions repo. On a typical install this is `~/Development/big_questions/helpers/init_inquiry.py`.
3. If neither resolves, ask the user where the big_questions repo is installed rather than guessing.

Example — on a typical install bootstrapping a vault-local instance:

```bash
python3 ~/Development/big_questions/helpers/init_inquiry.py --path ~/vaults/MyVault/01_Projects/my_big_questions
```

### 5. On success — surface the helper's output and suggest next steps

The helper prints a clean structured summary to stdout: a banner line (`Inquiry instance initialized at <path>`), an `[init_wiki output]` block relaying the generic wiki helper's own summary, and an `[inquiry layer]` block listing the addendum status and each symlinked skill. Relay it to the user verbatim — it already communicates exactly what changed on disk.

Then suggest the natural next step: **`cd <target> && /inquiry-elicit`** to start the question-elicitation interview. That's the first thing the user should run in a fresh inquiry instance.

### 6. On failure — surface the helper's stderr

On non-zero exit, the helper writes one or more clear lines to stderr, each prefixed with `init_inquiry:`. Relay them to the user verbatim — the prefix makes it easy to recognize as coming from this helper rather than the shell, Python, or a nested subprocess.

- If the error says `memex harness not found at <path>`: gently suggest installing memex. The big_questions README has the install recipe (clone `~/Development/memex/`, symlink the harness skills into `~/.claude/skills/`). If the user's memex install is elsewhere, suggest re-running with `--memex-path <their-path>`.
- If the helper reports that `init_wiki` itself failed, the nested error will appear in stderr after the `init_inquiry:` line. Surface both and let the user decide how to proceed; don't retry automatically.
- Any other stderr line — surface it and ask the user how they'd like to proceed.

## Idempotency

**Safe to re-run this command.** If the instance is already initialized, the helper detects it and does nothing destructive — you do **not** need `--force` for a plain re-run. Specifically:

- The helper sees that `<target>/SCHEMA.md` already exists and skips calling `init_wiki` (which would otherwise hard-fail). It emits a note saying the sub-call was skipped.
- The addendum append checks for the addendum's opening marker in `SCHEMA.md`. If it's already present, append is skipped.
- Existing symlinks that already resolve to the correct big_questions skill directories are left in place.

Use `--force` only when you explicitly want to reseed `SCHEMA.md` from the templates (e.g., after a schema-template update). With `--force`, the final `SCHEMA.md` still contains exactly one copy of the addendum.

## Failure modes

- **Target path not provided.** Ask the user for an absolute path. Do not assume a default.
- **Helper not findable.** Follow the three-step resolution order under **Step 4**. If all three fail, ask: "Where is the big_questions repo installed? I need the path to `helpers/init_inquiry.py`."
- **memex not installed.** The helper's precondition check writes `init_inquiry: memex harness not found at <path>` and exits before touching the target. Surface the error and suggest installing memex (clone + symlink per the big_questions README) or re-running with `--memex-path <path>` pointing at an existing install.
- **Target exists but isn't a directory.** The helper (via `init_wiki`) surfaces the error. Echo it. The user must rename, move, or pick a different path; do not delete anything on their behalf.
- **Symlink conflict.** If `<target>/.claude/skills/inquiry-elicit` or `inquiry-gap` already exists but resolves to a different path than the big_questions source skill, the helper aborts with a `conflicting path at <link>` error and a partial-state summary to stderr. Surface the error and suggest the user remove the conflicting link manually (`rm <link>`), then re-run `/inquiry-init`.
- **Write permission denied.** Surface the helper's `OSError` message and suggest the user pick a writable target or adjust permissions.
