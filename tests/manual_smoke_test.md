# big_questions Manual Smoke Test

Verifies `/inquiry-elicit`, `/wiki-ingest`, and `/inquiry-gap` end-to-end against a throwaway instance before P-001. Sub-agents cannot invoke slash commands — this is the human-in-the-loop half.

Run in a **fresh Claude Code session** `cd`'d into the throwaway instance. Stop at the first unexpected result. Assumes memex AND big_questions are both installed user-scoped — all `wiki-*` and `inquiry-*` skills symlinked into `~/.claude/skills/` per the two repos' READMEs.

## Quick setup

From any Claude Code session (the `inquiry-init` skill is user-scoped, so it's always available):

```
/inquiry-init /tmp/paul_elicit_smoke
```

Then in a terminal:

```bash
cd /tmp/paul_elicit_smoke && claude
```

Running `/inquiry-init` twice is safe (idempotent) — the helper detects an already-initialized instance and short-circuits cleanly without touching existing content. To reseed `SCHEMA.md` after a template update, re-run with `--force`.

### Manual setup (if `/inquiry-init` isn't available yet)

Use this for debugging or if you're on a machine that doesn't have the `inquiry-init` skill wired up:

```bash
# 1. Stage a throwaway instance.
rm -rf /tmp/paul_elicit_smoke
mkdir -p /tmp/paul_elicit_smoke/{wiki/questions,raw,meta}

# 2. Compose SCHEMA.md from base + inquiry addendum.
cat ~/Development/memex/schema.example.md \
    ~/Development/big_questions/schema.inquiry.example.md \
    > /tmp/paul_elicit_smoke/SCHEMA.md

# 3. Seed empty wiki scaffolding.
touch /tmp/paul_elicit_smoke/wiki/index.md /tmp/paul_elicit_smoke/meta/log.md

# 4. Enter the instance and launch Claude Code.
#    No project-scoped symlinks needed — inquiry skills are user-scoped.
cd /tmp/paul_elicit_smoke && claude
```

## Test 1 — inquiry-elicit (cold start)

In Claude Code: `/inquiry-elicit`

Expected:
- Claude reads `./SCHEMA.md` and empty `./wiki/questions/`, then opens with probe 1 of 5 (role context). The five probes are role / concerns / 12-month goals / positions to defend / re-read material.
- Walk through **2–3 probes only** — this is a mechanics check, not a real elicitation. Answer briefly with throwaway responses.
- After ~3 probes, say: *"Stop — this is a smoke test. Synthesize what you have and write 2–3 pages so I can verify the write path."*
- Expect Claude to push back on padding (per SKILL `## Quality bar`). Accept the short set.

Verify after exit:
```bash
ls /tmp/paul_elicit_smoke/wiki/questions/    # 2–3 *.md files
cat /tmp/paul_elicit_smoke/wiki/index.md     # lists the pages, sorted by slug
cat /tmp/paul_elicit_smoke/meta/log.md       # one `elicit` entry
head -6 /tmp/paul_elicit_smoke/wiki/questions/*.md    # frontmatter has slug/title/created/updated/status/contributions
```

## Test 2 — wiki-ingest

Paste the following into Claude Code, then run `/wiki-ingest`:

> *"Shopify's 'AI-native by default' memo (2026) argues performance review should distinguish what an engineer delegates to AI from what they still own by hand. Delegation fluency is a promotion criterion, not just a productivity metric."*

Expected:
- Claude reads `SCHEMA.md`, writes `raw/2026-04-22-*.md` with provenance frontmatter and verbatim text.
- Classifies against Test 1 pages; reports relevance per page.
- On confirm, appends one-line contribution to relevant page's `## Notes`; bumps `contributions` and `updated`.
- Shells out to `index_update.py` and `log_append.py` at `~/Development/memex/helpers/`.

Verify:
```bash
ls /tmp/paul_elicit_smoke/raw/                       # new raw file exists
grep -A1 "^## Notes" /tmp/paul_elicit_smoke/wiki/questions/*.md  # contribution appended
cat /tmp/paul_elicit_smoke/meta/log.md               # `ingest` entry appended after `elicit`
```

## Test 3 — inquiry-gap (set-level)

Needs **≥3 active questions** (SKILL `## Failure modes`). If Test 1 gave you only 2, hand-write a stub third page before running.

In Claude Code: `/inquiry-gap`

Expected in-session render (rigid format from SKILL Step 7):

```
Gap report for set-level:

Most non-obvious: <one complete sentence>

- <observation 2, one line>
- <observation 3, one line>

Full report written to meta/gap_report_2026-04-22.md
```

The *Most non-obvious* sentence must stand alone — that's the GIF frame.

Verify:
```bash
ls /tmp/paul_elicit_smoke/meta/                             # gap_report_<YYYY-MM-DD>.md
readlink /tmp/paul_elicit_smoke/meta/gap_report_latest.md   # points to today's file
grep "gap-report" /tmp/paul_elicit_smoke/meta/log.md        # new log entry
```

## Test 4 — inquiry-gap (within <slug>)

Needs a page with **≥3 contributions** in `## Notes`. Hand-pad two extra contribution bullets on the ingested page and bump `contributions: 3` in frontmatter if Test 2 only produced one.

In Claude Code: `/inquiry-gap within <slug-with-3-contributions>`

Expected: same rigid render, header reads `Gap report for within-question (<slug>):`; observations cite specific contribution lines. File written as `_b` suffix on today's date.

Verify: `ls /tmp/paul_elicit_smoke/meta/` shows two dated reports (or `_b` suffix).

## Cleanup

```bash
rm -rf /tmp/paul_elicit_smoke
# User-scoped ~/.claude/skills/ symlinks (wiki-*, inquiry-*) stay — that's the intended install.
```

## Known quirks

- **Citations pointing outside the wiki root (e.g. `../../raw/*.md` provenance links) are `wiki-lint` warnings, not errors** — they appear under the "Outside-wiki citations (warnings)" section and do not affect exit code. Lint is not invoked by the inquiry skills, so Tests 1–4 are unaffected either way.
- **`inquiry-elicit` won't re-run over a non-empty `wiki/questions/`** (v0.1 constraint — re-elicitation is planned for a future revision). If you need to retest, `rm -rf` the instance and re-run Setup.
- **`inquiry-gap` set mode refuses <3 active questions**; within mode refuses <3 contributions. Both are intentional guards — see the SKILL's `## Failure modes`.
- **The "non-obvious" self-critique loop** in `inquiry-gap` can bounce twice and then write nothing. If that happens, the in-session summary tells you honestly — it's not a bug.
