# big_questions Manual Smoke Test

Verifies `/inquiry-elicit`, `/wiki-ingest`, and `/inquiry-gap` end-to-end against a throwaway instance before P-001. Sub-agents cannot invoke slash commands — this is the human-in-the-loop half.

Run in a **fresh Claude Code session** `cd`'d into the throwaway instance. Stop at the first unexpected result. Assumes memex is installed at `~/Development/memex/` with its `wiki-*` skills symlinked into `~/.claude/skills/`.

## Quick setup

```bash
# 1. Stage a throwaway instance.
rm -rf /tmp/paul_elicit_smoke
mkdir -p /tmp/paul_elicit_smoke/{wiki/questions,raw,meta,.claude/skills}

# 2. Compose SCHEMA.md from base + inquiry addendum.
cat ~/Development/memex/schema.example.md \
    ~/Development/big_questions/schema.inquiry.example.md \
    > /tmp/paul_elicit_smoke/SCHEMA.md

# 3. Seed empty wiki scaffolding.
touch /tmp/paul_elicit_smoke/wiki/index.md /tmp/paul_elicit_smoke/wiki/log.md

# 4. Project-scope the inquiry skills into the instance.
ln -s ~/Development/big_questions/skills/inquiry-elicit \
      /tmp/paul_elicit_smoke/.claude/skills/inquiry-elicit
ln -s ~/Development/big_questions/skills/inquiry-gap \
      /tmp/paul_elicit_smoke/.claude/skills/inquiry-gap

# 5. Enter the instance and launch Claude Code.
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
cat /tmp/paul_elicit_smoke/wiki/log.md       # one `elicit` entry
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
cat /tmp/paul_elicit_smoke/wiki/log.md               # `ingest` entry appended after `elicit`
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
grep "gap-report" /tmp/paul_elicit_smoke/wiki/log.md        # new log entry
```

## Test 4 — inquiry-gap (within <slug>)

Needs a page with **≥3 contributions** in `## Notes`. Hand-pad two extra contribution bullets on the ingested page and bump `contributions: 3` in frontmatter if Test 2 only produced one.

In Claude Code: `/inquiry-gap within <slug-with-3-contributions>`

Expected: same rigid render, header reads `Gap report for within-question (<slug>):`; observations cite specific contribution lines. File written as `_b` suffix on today's date.

Verify: `ls /tmp/paul_elicit_smoke/meta/` shows two dated reports (or `_b` suffix).

## Cleanup

```bash
rm -rf /tmp/paul_elicit_smoke
# inquiry-skill symlinks were project-scoped to the instance — cleaned up with rm -rf above.
# memex's user-scoped ~/.claude/skills/wiki-* symlinks stay (that's the intended install).
```

## Known quirks

- **Citations pointing to `../../raw/*.md` files that don't exist are flagged as `(outside wiki)` errors by `wiki-lint`** (exit 1). The lint helper counts anything resolving outside `<wiki>/` as an error, not a warning — this is stricter than MX-010's runbook implied. File as MX-015 if not yet tracked. For this runbook, don't worry: lint is not invoked by the inquiry skills, so Tests 1–4 are unaffected.
- **`inquiry-elicit` won't re-run over a non-empty `wiki/questions/`** (Skateboard constraint — re-elicitation is Bicycle scope). If you need to retest, `rm -rf` the instance and re-run Setup.
- **`inquiry-gap` set mode refuses <3 active questions**; within mode refuses <3 contributions. Both are intentional guards — see the SKILL's `## Failure modes`.
- **The "non-obvious" self-critique loop** in `inquiry-gap` can bounce twice and then write nothing. If that happens, the in-session summary tells you honestly — it's not a bug.
