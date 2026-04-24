<!-- Inquiry domain addendum — appends to memex/schema.example.md -->
<!--
Bootstrap usage:

    cat memex/schema.example.md \
        big_questions/schema.inquiry.example.md \
      > <instance>/SCHEMA.md

Then edit the composed file freely for voice and instance-specific
customizations. The sections below are written to append cleanly onto the
memex base template — they fill the "Domain Vocabulary" extension point
and specialize the base page, log, and workflow conventions for the
inquiry-instrument domain.
-->

## Domain Vocabulary — Inquiry

This instance is an **inquiry instrument**: a wiki organized around a small,
explicit set of questions the user is actively trying to figure out. The
intellectual lineage is the "twelve favorite problems" practice attributed to
Richard Feynman and documented by Gian-Carlo Rota in *Ten Lessons I Wish I Had
Been Taught* (Notices of the AMS, 1997). Rota's rendering:

> *"You have to keep a dozen of your favorite problems constantly present in
> your mind... Every time you hear or read a new trick or a new result, test
> it against each of your twelve problems to see whether it helps."*

This domain externalizes that practice and hands the bookkeeping to an LLM.
The vocabulary below is how we talk about the pieces.

- **Question** — the core unit. One crisp one-sentence question plus 2–3
  sentences of framing. Stored as a page under `wiki/questions/`. Each
  question has its own page; the page accumulates over time as sources are
  ingested.

  Questions are simultaneously private and social artifacts. Privately, they
  organize the user's attention — what to read for, what to mark as
  relevant, what to ignore. Socially, they serve as conversation starters,
  evidence of intellectual range, or a way of introducing oneself. A
  well-crafted question works on both axes, and that constrains the form:
  readable by someone who doesn't know the user, specific enough to be
  genuinely theirs, short enough to land in one breath.
- **Contribution** — a one-sentence note appended to a question's `## Notes`
  section when an ingested source advances that question. Exactly one
  contribution line per `(source, question)` pair, added by `/wiki-ingest`.
  The page's `contributions` frontmatter counter is bumped in the same edit.
- **Question set** — the collection of ~8–12 active questions. The soft
  target comes from the Feynman/Rota lineage above: fewer than 6 and the set
  is too narrow to act as a filter; more than ~15 and it is too diffuse to
  be a real attention focus. The exact number matters less than keeping the
  set small and explicit.
- **Gap** — in this domain, a *gap* is not a missing citation. It is a
  missing dimension, an implicit frame, a thin-evidence spot, an unasked
  question, or a one-sided argument. Two gap-analysis scopes exist (see Gap
  Report Conventions below): **set-level** (across all questions) and
  **within-question** (on a single page).
- **Elicitation** — a structured LLM-led interview that produces the
  initial question set by probing the user's current context. See
  Elicitation Conventions below.
- **Retire** — a question leaving the active set. `status: retired` in
  frontmatter. Retired pages are archived in place, never deleted; query
  and ingest operations exclude them (per the base `status` convention).

---

## Inquiry Page Conventions

Inquiry pages live under `wiki/questions/` (this is the instance's
`<pages-dir>` from the base template). They specialize the base page
conventions as follows.

### Page filename

One page per question. Filename is `<slug>.md`, matching the `slug`
frontmatter field. Slugs are short, kebab-case, and stable — never renamed
once set, because contribution notes in other files cite them.

### Frontmatter

Inquiry pages use the baseline frontmatter fields from the memex template
with no domain-specific additions in v0.1:

```yaml
---
slug: self-improving-software
title: "How does software that knows what it's trying to become build itself?"
created: 2026-04-22
updated: 2026-04-22
status: active        # active | dormant | retired
contributions: 0
---
```

**On `title` holding the question.** In the inquiry domain, `title` contains
the one-sentence question verbatim. We do **not** introduce a separate
`question:` field. The base template uses `title` as the canonical display
string; in this domain that display string *is* the question, so the two
collapse. Framing (the 2–3 sentences of context) lives in the body's
`## Framing` section, not in frontmatter. Keep the question self-contained
in `title` — the elicit, ingest, and gap skills all read it there.

Instance customizations may add fields later (thematic tags, originating
interview turn, etc.); none are required in v0.1.

### Body structure

Baseline-compliant. Two sections, in order:

```markdown
# <The one-sentence question, duplicated from frontmatter `title`>

## Framing

Two or three sentences establishing why this is a live question for the
user right now, what it rules in, what it rules out. Written by
`/inquiry-elicit` at creation; revised sparingly.

## Notes

<!-- Contribution notes appended by /wiki-ingest, one per source. -->
<!-- Format: "- <one-sentence contribution> — <source citation>" -->
```

### Contribution note format

Under `## Notes`, each contribution is a single bullet:

```markdown
- The Karpathy wiki pattern does its expensive work at write-time, not query-time, which reframes this question's "build" vs. "maintain" axis. — [Karpathy LLM Wiki](../../raw/2026-04-22-karpathy-llm-wiki.md)
```

Rules:

- One bullet per ingested source, per page. If a source is re-ingested,
  dedupe rather than appending a second line.
- The sentence is specific to *this question* — it says how the source
  advances this question, not what the source is about in general.
- The citation is a markdown link to the source file under `raw/`, using
  the relative-link convention from the base template.

### Deferred structure

In v0.1, pages are **flat notes under `## Notes`**. A richer per-page
schema — claims, evidence, contradictions, open threads — is planned
for a future revision (PRD 6.2, 7/v0.2). When it lands, the baseline
frontmatter above is chosen to survive the migration unchanged;
additional body sections will layer on without renaming `title`, `slug`,
or `contributions`.

---

## Gap Report Conventions

Gap reports are this domain's `meta/` artifact. They are the operational
expression of the product thesis — the instrument's value is that it
points at negative space.

### Location and naming

- Per-run file: `meta/gap_report_<YYYY-MM-DD>.md`. Dated filename is how
  week-over-week comparison works (there is no `git diff` on the wiki —
  see base "Ownership" table and harness Decision 7).
- `meta/gap_report_latest.md` — a symlink (or a plain copy on systems
  without symlink support) pointing to the most recent dated report.
- Multiple reports on the same day use a `_b`, `_c` suffix rather than
  overwriting.

### Two modes

Gap analysis runs in one of two scopes. A single `/inquiry-gap` invocation
may produce one or both; the report file names the mode(s) in its opening
summary.

1. **Set-level** — operates on every page with `status: active`. Surfaces:
   - Implicit or assumed frames shared across the set
   - Missing dimensions (angles the set as a whole does not ask about)
   - Overlapping pairs (two questions that collapse to one)
   - Questions that are too narrow to be productive
   - Questions that are too broad to be answerable

2. **Within-question** — operates on a single page whose
   `contributions` count is ≥3. Surfaces:
   - Thin evidence (the accumulated notes don't yet say much)
   - One-sided arguments (no counter-position represented)
   - Missing counter-positions worth seeking out
   - Repeated sources (the same voice is carrying too much weight)
   - Missing concrete examples

### Report structure

```markdown
# Gap Report — <YYYY-MM-DD>

<Opening summary: which mode(s) ran, how many questions or which page,
and the one most important observation in a single sentence.>

## Set-level observations
<!-- Present if set-level mode ran. Otherwise omit the section. -->

### <one-line summary of observation 1>
2–3 sentences of reasoning. Name the question(s) involved by slug.

### <one-line summary of observation 2>
...

## Within-question — <slug>
<!-- Present if within-question mode ran. Repeat for each page analyzed. -->

### <one-line summary of observation 1>
2–3 sentences of reasoning. Cite specific contribution lines or sources.

...
```

### Non-obvious-observation requirement

Gap-analysis operations **must produce at least one observation the user
would not have made themselves.** A report that only restates what the
user already sees (e.g. "question 3 has only two contributions") fails this
bar.

If the first analysis pass is generic, the skill self-critiques and reruns
before writing the file. A generic gap report is worse than no gap report —
it teaches the user that the instrument doesn't see anything they don't.

---

## Elicitation Conventions

Elicitation is an inquiry-specific workflow that produces the initial
question set. It does not exist in the memex base; it is defined here
because "how do the pages get created in the first place" is a
domain-shaped question.

### Output

- 8–12 question markdown files under `wiki/questions/`, each with full
  frontmatter per **Inquiry Page Conventions** above.
- Each file has a complete `## Framing` section written by the LLM from
  the interview transcript.
- `## Notes` is present but empty at creation.
- `wiki/index.md` is rebuilt to include the new pages.
- One entry appended to `meta/log.md` using the `elicit` verb (see Log
  Format Extensions below).

### Interview structure

The interview probes five areas (PRD 6.1.1):

1. **Current role context** — what the user is actually doing day to day
2. **Current concerns** — what is keeping them up at night
3. **12-month expertise goals** — what they want to be expert on a year
   from now
4. **Positions to argue** — what they would want to defend in an
   interview-style conversation
5. **Re-read material** — what they keep coming back to

Weak articulations are probed with follow-ups before they are written
into a question file.

### Cap and pad-avoidance

- **20-minute wall-clock cap** on the interview itself. If the
  elicitation is producing less than a question per ~2 minutes after the
  warm-up, wrap up rather than extending.
- **No padding.** If fewer than 8 questions surface honestly, the skill
  writes the files it has, notes the shortfall in `log.md`, and
  recommends a second pass on a later day. An 11-question set with real
  questions beats a 12-question set with one synthesized filler.

### Deferred — revision workflow

Revising, splitting, merging, or retiring questions after elicitation
is planned for a future revision. In v0.1, re-running `/inquiry-elicit`
against an existing set is not supported; the user edits pages directly
or deletes and restarts.

---

## Operation Vocabulary Extensions

The inquiry domain uses the base harness operations as-is where it can
and adds two domain-specific operations.

| Operation | Source | Behavior in this domain |
|---|---|---|
| `/wiki-ingest` | memex (base) | Used as-is. Classifies the paste-in against `wiki/questions/` pages, appends a contribution to each relevant page's `## Notes`, bumps `contributions` and `updated`. |
| `/wiki-query` | memex (base) | Used as-is. Reads across question pages; may propose a synthesis page. |
| `/wiki-lint` | memex (base) | Used as-is, with the inquiry page conventions applied (e.g. stale `updated` means a page hasn't accumulated recently, not necessarily that it is wrong). |
| `/inquiry-elicit` | big_questions (domain) | Produces the initial question set per **Elicitation Conventions** above. |
| `/inquiry-gap` | big_questions (domain) | Produces a gap report per **Gap Report Conventions** above. Modes: `set` (default), `within <slug>`. |

### Log Format Extensions

The base `log.md` header format is `## [YYYY-MM-DD] <op> | <subject>`.
This domain uses the following verbs for `<op>`:

- `ingest` / `query` / `lint` — from the base harness, unchanged
- `elicit` — for `/inquiry-elicit` runs. Subject: `initial <n>-question set`
  or `second-pass elicitation` etc.
- `gap-report` — for `/inquiry-gap` runs. Subject names the mode(s),
  e.g. `set-level`, `within-question (<slug>)`, or
  `set-level + within-question`.

Example entries:

```markdown
## [2026-04-22] elicit | initial 11-question set
Produced 11 questions across four themes. Second-pass recommended to reach 12.

## [2026-04-23] ingest | "Karpathy LLM Wiki" (gist.github.com)
Classified against 2 questions; appended one contribution each.

## [2026-04-24] gap-report | set-level
See meta/gap_report_2026-04-24.md. Key observation: the set over-indexes
on org-shape questions at the expense of user-shape questions.
```

<!-- END OF INQUIRY DOMAIN ADDENDUM — instance customizations append below -->
