---
name: inquiry-gap
description: Generate a gap report on an inquiry wiki — set-level (across all active questions) or within-question (on a single page with >=3 contributions) — surfacing non-obvious observations about what the question set or a single question is missing.
---

# inquiry-gap

## Purpose

Produce a **gap report** on an inquiry instrument: a dated markdown file under `meta/` plus a scannable in-session summary. This is the domain's signature operation — the thing that makes the wiki an *instrument* rather than a notebook. Invoke this skill when the user runs `/inquiry-gap`, `/inquiry-gap set`, or `/inquiry-gap within <slug>`, or otherwise asks for a "gap report," "gap analysis," or "what am I missing."

Two modes, both governed by the same quality bar:

- **`set`** (default) — operates on every active question page in `wiki/questions/`. Surfaces implicit frames, missing dimensions, overlapping pairs, too-narrow and too-broad questions.
- **`within <slug>`** — operates on a single question page whose `contributions` count is >=3. Surfaces thin evidence, one-sided arguments, missing counter-positions, repeated sources, missing concrete examples.

The non-negotiable quality bar (PRD 6.4, SCHEMA.md "Non-obvious-observation requirement"): **every run must produce at least one observation the user could not have made themselves by rereading their own questions.** Generic observations are a worse outcome than no report. Self-critique enforces this bar before the file is written.

## Preconditions

- The current working directory is a wiki root — it contains `SCHEMA.md`.
- `wiki/questions/` exists and contains at least one question page with `status: active`.
- For `set` mode: at least **3 active questions** (below that there is not enough structure to find set-level patterns — see **Failure modes**).
- For `within <slug>` mode: `wiki/questions/<slug>.md` exists with `status: active` and its `## Notes` section contains **>=3 contributions** (one bullet per contribution per the schema).
- `meta/` exists at the wiki root (sibling of `wiki/`). Create it if absent.
- The memex helper `log_append.py` is available. See **Helper invocation** for path resolution.

## Modes

### Mode selection

1. If the user supplies an explicit mode (`/inquiry-gap set` or `/inquiry-gap within <slug>`), use it.
2. If the user supplies a slug without the `within` keyword (`/inquiry-gap <slug>`), treat it as `within <slug>`.
3. If the user supplies no argument, default to `set`.
4. **Auto-suggest within-mode.** After a `set` run completes, scan `wiki/questions/` for any page whose `contributions` frontmatter is >=3 and for which no `meta/gap_report_*.md` in the last 7 days contains a `## Within-question observations — <slug>` section. If such a page exists, tell the user:
   > "Page `<slug>` has <N> contributions and no recent within-question report. Want me to run `/inquiry-gap within <slug>` now?"
   Do not auto-run without confirmation.

### Set-level analysis — what to surface

Read every active page in `wiki/questions/`: frontmatter (for slug and title) and the `## Framing` section. Then analyze the set as a whole. Look for:

- **Implicit frames** — assumptions the question set takes for granted across most/all questions. Example: "every question assumes a team of 10+ engineers — do any apply to solo or pair-sized teams?" or "every question assumes the reader is the builder — no questions about the buyer, the operator, or the user."
- **Missing dimensions** — axes no question covers. If all questions are "how to build," none may be "when to not build." If all questions are about product, none may be about distribution. Name the missing dimension concretely.
- **Overlapping pairs** — two questions that collapse into the same underlying inquiry once you look past surface wording. Recommend either merging or sharpening the differentiation (what would each keep that the other rules out?).
- **Too-narrow** — a question so specific that almost no new source could advance it. The question is really an answer in disguise, or is about one case rather than a class of cases.
- **Too-broad** — a question so abstract that no contribution would obviously count as advancing it. No imaginable paste-in would move the needle.

### Within-question analysis — what to surface

Read the single target page in full: frontmatter, `## Framing`, and every bullet in `## Notes`. Look for:

- **Thin evidence** — a claim in the framing or implied by the notes is supported by only one source, or only one *kind* of source (all blog posts, all from one community).
- **One-sided arguments** — all contributions lean the same direction; no counter-position is represented. Name the side the notes favor and what a reasonable dissent would look like.
- **Missing counter-positions** — specific named thinkers, books, traditions, or arguments the user should engage with. Be concrete: "no contribution references <specific position> — if you're serious about this question, that's the canonical counter."
- **Repeated sources** — multiple contributions citing the same author, venue, or community. Call out the diversity gap.
- **Missing concrete examples** — the notes are abstract. No lived case, no worked example, no "here is what this looked like in practice." Suggest the kind of example that would ground the question.

## Steps

### 1. Read `SCHEMA.md`

Before anything else, read `SCHEMA.md` from the current working directory. This tells you:

- The pages directory name (this skill assumes `questions` — the inquiry domain convention — but honor `SCHEMA.md` if it says otherwise).
- Frontmatter field names and body section names (`## Framing`, `## Notes`, `contributions`, `status`).
- The contribution bullet format (for parsing the `## Notes` section).
- The gap report structure and location conventions (baseline: `meta/gap_report_<YYYY-MM-DD>.md`).
- The log-verb convention for this operation (`gap-report`).

If `SCHEMA.md` is missing, stop and report the error (see **Failure modes**).

### 2. Determine the mode and validate preconditions

Resolve the mode per **Mode selection** above. Then:

- For `set`: list active question pages (`status: active`) in `wiki/questions/`. Count them. If fewer than 3, stop (see **Failure modes**).
- For `within <slug>`: open `wiki/questions/<slug>.md`. If it does not exist or is not `status: active`, stop. If its `## Notes` section has fewer than 3 bullet contributions, stop (see **Failure modes**).

### 3. First-pass analysis

Generate observations per the mode's rubric (set-level or within-question categories above). Aim for 5–8 first-pass observations across categories — more than the final report will hold, so self-critique has material to cut.

Do not write any file yet.

### 4. Self-critique — the non-obvious gate

This is the load-bearing step. For each first-pass observation, ask in your own reasoning:

> "Could the user have made this observation by rereading their own questions (or this single page) without me? If yes, it is not non-obvious — replace it or deepen it."

Generic observations that fail the bar look like:
- "Question 3 has only two contributions." (The user can see this by looking.)
- "Most of your questions are about AI." (Restating the topic.)
- "This page is thin on evidence." (Restating what `contributions: 2` already says.)

Non-obvious observations look like:
- "All 12 questions assume the subject is an engineering team; none ask about the team's relationship with its users, and one of your re-read sources explicitly treats that as the primary axis."
- "Q4 and Q9 collapse to the same underlying question — both ask how authority is delegated in fast-moving orgs — but Q4 frames it as an org-design problem and Q9 as a hiring problem. Either sharpen the difference or merge."
- "Every contribution on this page cites a Karpathy or Karpathy-adjacent source. If this question is as important as the framing suggests, the Yudkowsky / Chollet axis of disagreement deserves at least one contribution."

**At least ONE observation in the final report must clear this bar.** After the self-critique pass:

- If one or more observations clear the bar, keep those and round out the report with the next-strongest surviving observations (aim for 3–5 total — depth beats count).
- If zero observations clear the bar, **do not write the file yet.** Revise your prompt to yourself: re-read the framings more carefully, look for tensions between pages, look for what is *conspicuously absent* given the user's stated concerns. Re-run the first-pass analysis. Cap this revision loop at **2 attempts.** If still nothing lands after two attempts, proceed to the failure path under **Failure modes** — write nothing, and report honestly.

### 5. Rank and write the report

Order observations with the single strongest (most non-obvious) first. The `## Summary` section leads with that observation verbatim or paraphrased — **not** with a generic "here is what I found" sentence.

Write to `meta/gap_report_<YYYY-MM-DD>.md`. If a file with that name already exists for today, append a suffix: `_b`, `_c`, etc.

**Set-level file structure:**

```markdown
# Gap Report — <YYYY-MM-DD> — set-level

## Summary

<2–3 sentences. First sentence states the most non-obvious observation. Following sentences give context — how many questions analyzed, what else surfaced.>

## Observations

### <Category heading — e.g. Implicit frames>

- **<One-line observation>**
  <2–3 sentences of reasoning. Name the question(s) involved by slug. Suggest an action the user could take — sharpen, merge, add, retire.>

### <Next category>

- **<One-line observation>**
  <2–3 sentences of reasoning and action.>

(...)
```

**Within-question file structure** — identical, except replace `## Observations` with `## Within-question observations — <slug>` and drop any category heading that has no observations:

```markdown
# Gap Report — <YYYY-MM-DD> — within-question (<slug>)

## Summary

<Most non-obvious observation first, then context: page title, contribution count analyzed.>

## Within-question observations — <slug>

### <Category heading — e.g. One-sided arguments>

- **<One-line observation>**
  <2–3 sentences. Cite specific contribution bullets by their source if possible.>

(...)
```

If the `within` mode is auto-suggested and confirmed right after a `set` run, produce two separate files (one per mode), not a combined file. Dated filenames plus the mode-in-title make both scannable in `meta/`.

### 6. Update `meta/gap_report_latest.md`

After writing the dated file, update the symlink:

```bash
cd meta && ln -snf gap_report_<YYYY-MM-DD>.md gap_report_latest.md
```

On filesystems where symlinks are not available (rare on macOS/Linux, occasionally true of some Windows setups), fall back to writing a plain copy at the same path and note in the in-session summary that `gap_report_latest.md` is a copy rather than a symlink.

### 7. Render the in-session summary

**This is what gets captured on the Week 1 demo GIF.** Keep the format rigid and scannable. Print, to the conversation, exactly:

```
Gap report for <mode>:

Most non-obvious: <the single strongest observation, one sentence>

- <second observation, one line>
- <third observation, one line>
- <fourth observation, one line>
- <fifth observation, one line>  (optional — include only if it genuinely earns its place)

Full report written to meta/gap_report_<YYYY-MM-DD>.md
```

Design notes for the render:

- The "Most non-obvious" line is the one the GIF camera lingers on. Make it a complete sentence that stands alone without context — someone reading the GIF frame without the question set in front of them should still get the point.
- The bullet observations are shorter — one line each, no wrapping. They establish that the headline is not cherry-picked.
- No preamble, no apologies, no "let me know if you want to dig deeper." The rigid format is what makes it GIF-legible.
- For `within` mode, replace `<mode>` with `within-question (<slug>)` — naming the slug in the header keeps the screen grab unambiguous when the user is comparing reports across pages.

### 8. Append to `log.md`

Invoke the log helper via the bash tool. `log.md` lives inside `meta/` per the baseline layout — pass `--log-dir ./meta`:

```bash
python3 <path-to-memex>/helpers/log_append.py \
    --log-dir ./meta \
    --op gap-report \
    --subject "<mode>: <n> observations" \
    --body "<one-line paraphrase of the headline observation>. See meta/gap_report_<YYYY-MM-DD>.md."
```

Examples:

- `--subject "set-level: 4 observations"`
- `--subject "within-question (self-improving-software): 3 observations"`
- `--subject "set-level + within-question (self-improving-software): 6 observations"` (if a single run produced both)

See **Helper invocation** below for resolving `<path-to-memex>`.

## Helper invocation

This skill shells out to one helper script via the bash tool: `memex/helpers/log_append.py`. No inquiry-specific helpers exist in v0.1.

**Always invoke with `python3` explicitly** (per architecture Decision 6 — avoid ambiguous `python` on macOS).

**Resolving the helper path.** This skill is typically installed as a symlink into an instance's `.claude/skills/inquiry-gap/`, so `helpers/` is not adjacent to the running SKILL.md. Resolve in order:

1. If `./memex/helpers/log_append.py` exists relative to the wiki root (the user vendored the harness into their wiki), use that.
2. Otherwise, resolve the SKILL.md's *real* path (follow the symlinks: instance -> `big_questions/skills/inquiry-gap`). The memex harness lives separately at `~/Development/memex/` on a typical install — use `~/Development/memex/helpers/log_append.py`.
3. If neither resolves, ask the user where the memex harness is installed. Do not silently skip the log append — the log is how week-over-week comparison works (Decision 7).

## Quality enforcement — operational summary

The non-obvious requirement is enforced mechanically in Step 4 by:

1. **Generating more observations than will ship** (5–8 first-pass) so the self-critique has headroom to cut generics.
2. **Applying the rereading test to each candidate** — could the user have made this observation alone? If yes, the observation is disqualified from being the headline, and must be either deepened or replaced.
3. **Requiring at least one observation to pass the test before the file is written.** The check happens in-memory before any disk write; a generic-only draft is never persisted.
4. **Allowing up to two revision attempts** before accepting that this run did not produce a non-obvious finding. The loop is bounded; it does not stall the user.
5. **Failing honestly when no non-obvious finding emerges** (see **Failure modes**). The skill reports the shortfall rather than shipping a generic report — because in this domain, a generic report is worse than no report.
6. **Ordering the final output most-non-obvious-first** so the `## Summary` lede and the in-session "Most non-obvious:" line are the same sentence, and both are the strongest sentence in the run.

## Failure modes

- **`SCHEMA.md` is missing.** Stop. Report: "No `SCHEMA.md` found in the current directory. `/inquiry-gap` expects to run from the root of an inquiry instance. Bootstrap one from `memex/schema.example.md` + `big_questions/schema.inquiry.example.md`, or `cd` into an existing instance."

- **Fewer than 3 active questions** (set mode). Stop and report: "Set-level gap analysis needs at least 3 active questions to find structure. This instance has <N>. Run `/inquiry-elicit` to build out the set, or use `/inquiry-gap within <slug>` if you want analysis on a single page." Do not attempt a degraded set-level pass — a gap report on two questions cannot surface implicit frames honestly.

- **Within-mode on a page with fewer than 3 contributions.** Stop and report: "Page `<slug>` has <N> contributions. Within-question analysis needs at least 3 to be worth the run. Run `/inquiry-gap` (set mode) instead, or ingest more sources against this page first." Name other pages with >=3 contributions if any exist.

- **Within-mode target page does not exist or is `status: retired` / `status: dormant`.** Stop. Report which it is and list existing active pages the user may have meant.

- **Self-critique produces no non-obvious observation after 2 attempts.** Do not write a file. Tell the user, honestly: "I ran two analysis passes and could not surface an observation you would not have made yourself. This can happen when (a) the question set is already sharp and my pattern-matching has nothing to add, (b) the framings are thin and there is not enough text to pattern-match against, or (c) the set is not varied enough for set-level structure to show. Options: show me the draft anyway for your own reading, rerun after ingesting more sources, or revisit the framings themselves." Offer to surface the draft as in-conversation prose (no file write) if the user wants to see what came up.

- **Helper script not found.** See the resolution order under **Helper invocation**. If all three options fail, ask the user where memex is installed rather than silently skipping the log append.

- **`meta/` directory missing.** Create it (`mkdir -p meta`) and continue. Note the creation in the in-session summary so the user knows where reports are now living.

- **A `gap_report_<YYYY-MM-DD>.md` for today already exists.** Write to `gap_report_<YYYY-MM-DD>_b.md` (then `_c`, etc.). Update the `gap_report_latest.md` symlink to point to the newest. Tell the user a prior run existed and give the filename so they can compare.
