# big_questions

**big_questions** is an inquiry-instrument layer on top of the [memex](https://github.com/eyefodder/memex) LLM-wiki harness. It adds three Claude Code skills — `/inquiry-init` to bootstrap an instance, `/inquiry-elicit` to conduct a structured interview and produce your ~12 big questions, and `/inquiry-gap` to run gap analysis against them. You keep a small, explicit set of questions; the model watches what you're missing.

The intellectual lineage is the "twelve favorite problems" practice attributed to Richard Feynman and documented by Gian-Carlo Rota in [*Ten Lessons I Wish I Had Been Taught*](https://www.ams.org/notices/199701/comm-rota.pdf) (Notices of the AMS, 1997) — keep a dozen of your favorite problems constantly in mind, and test every new idea against them. memex supplies the generic wiki harness; big_questions specializes it for this inquiry domain.

## What's in the box

| Artifact | Purpose |
|---|---|
| [`skills/inquiry-init/`](./skills/inquiry-init/SKILL.md) | Claude Code skill — one-command bootstrap for a new inquiry instance: creates the directory tree and composes `SCHEMA.md` from the memex base plus the inquiry addendum. |
| [`skills/inquiry-elicit/`](./skills/inquiry-elicit/SKILL.md) | Claude Code skill — runs a 15–20 minute structured interview, a negative-space check against your sustained-attention signals, and an ordering step. Writes 8–12 question pages under `wiki/questions/` and a shareable ordered list at `wiki/my_open_questions.md`. |
| [`skills/inquiry-gap/`](./skills/inquiry-gap/SKILL.md) | Claude Code skill — produces gap reports at two scopes: **set-level** (across all active questions) and **within-question** (on any page with at least three contributions). |
| [`helpers/init_inquiry.py`](./helpers/init_inquiry.py) | Python CLI invoked by `/inquiry-init`; shells out to memex's `init_wiki.py` and layers the inquiry addendum onto `SCHEMA.md`. |
| [`schema.inquiry.example.md`](./schema.inquiry.example.md) | Inquiry-specific schema addendum. Appends onto `memex/schema.example.md` to define question pages, contribution notes, gap reports, and elicitation conventions. |

## Requires

[memex](https://github.com/eyefodder/memex) — the generic LLM-wiki harness. big_questions will not function without it: ingestion, querying, linting, `log.md` formatting, and `index.md` maintenance all come from memex. The inquiry skills here call memex's helper scripts (`log_append.py`, `index_update.py`, `init_wiki.py`) directly.

## Install

Two-part install: memex first, then big_questions. Both install user-scoped — the skills live in `~/.claude/skills/` and are available in any Claude Code session.

### 1. Install memex

Follow the install section of the [memex README](https://github.com/eyefodder/memex#install). That clones memex to `~/Development/memex/` and symlinks the `wiki-*` harness skills into `~/.claude/skills/`. Come back here once that's done.

### 2. Clone big_questions and symlink the inquiry skills

```bash
git clone https://github.com/eyefodder/big_questions ~/Development/big_questions
mkdir -p ~/.claude/skills
ln -s ~/Development/big_questions/skills/inquiry-init    ~/.claude/skills/
ln -s ~/Development/big_questions/skills/inquiry-elicit  ~/.claude/skills/
ln -s ~/Development/big_questions/skills/inquiry-gap     ~/.claude/skills/
```

Then **restart Claude Code** so it picks up the new skills. `/inquiry-init`, `/inquiry-elicit`, and `/inquiry-gap` are now available in any Claude Code session.

**Why user-scoped.** Keeping install locations consistent with memex removes a chicken-and-egg problem: `/inquiry-init` needs to be invocable *before* an inquiry instance exists, which rules out project-scoped installation. The minor cost — `/inquiry-elicit` and `/inquiry-gap` appear in autocomplete in non-inquiry sessions — matches how Claude Code's built-in skills work and is acceptable at v0.1.

## Bootstrap a new inquiry instance

An **instance** is the folder holding your actual question wiki — the questions, the ingested sources, the gap reports. It lives wherever markdown lives comfortably for you (a plain folder, a git repo, an Obsidian vault, a directory under Dropbox). It is independent of this repo so skill development stays decoupled from question content.

One command, from any Claude Code session:

```
/inquiry-init <instance-path>
```

For example: `/inquiry-init ~/vaults/MyVault/01_Projects/my_big_questions`.

The skill shells out to `helpers/init_inquiry.py`, which:

1. Checks that memex is installed (fails fast with a clear message if not).
2. Invokes memex's `init_wiki.py --path <instance-path> --pages-dir questions` to build the generic tree (`wiki/questions/`, `raw/`, `meta/`, `SCHEMA.md` seeded from the memex base).
3. Appends `schema.inquiry.example.md` onto the new `SCHEMA.md`, producing the composed inquiry schema.

Re-running `/inquiry-init` on the same path is safe (idempotent); pass `--force` to reseed `SCHEMA.md` from the templates after a schema update (question content is preserved).

### Manual bootstrap (if you prefer)

If you'd rather not use the helper, the equivalent is a few shell commands:

```bash
mkdir -p <instance-path>/{wiki/questions,raw,meta}
touch <instance-path>/wiki/index.md <instance-path>/meta/log.md
cat ~/Development/memex/schema.example.md \
    ~/Development/big_questions/schema.inquiry.example.md \
    > <instance-path>/SCHEMA.md
```

No skill symlinking into the instance — the inquiry skills are user-scoped.

## First-session walkthrough

Once the instance is bootstrapped, a first session has three moves.

### 1. (Optional, recommended) Gather signals beforehand

The `/inquiry-elicit` skill includes a **negative-space check** phase that compares your draft question set against signals of what you've sustained attention on over months or years. A 15–20 minute interview will miss themes you've been sitting with for a long time; the signal check catches them.

Signal sources in rough priority order:

1. **Reading-tracker exports** — Readwise Reader, Readwise highlights, Instapaper, Pocket, Goodreads, Calibre library metadata. Richest signal when available. If you have an installed and authenticated CLI (for example the `readwise` CLI), the skill will prefer that over a scrape or paste.
2. **Social-media save streams** — LinkedIn saved posts (no clean export; paste or screenshot works), Twitter/X bookmarks, Reddit saved.
3. **Purchase and wishlist signals** — Amazon wishlists, Kindle library.
4. **Browser bookmarks / history** — possible but noisy; use as a fallback.
5. **Verbal recall** — "What have you kept coming back to over the past year?" A valid standalone signal if nothing else is available.

**Graceful degradation.** The phase works with whatever signal you have. A user with hundreds of saved articles will get richer output than one with twenty — but twenty is not zero, and verbal recall alone is not zero. Don't skip the session because your Readwise is empty.

### 2. Run `/inquiry-elicit`

From the instance directory, in Claude Code:

```
/inquiry-elicit
```

What to expect:

- **A 15–20 minute structured interview** across five probe areas: current role context, what is keeping you up at night, 12-month expertise goals, positions you'd defend in an interview, and re-read material.
- **A synthesis pass** producing 8–12 candidate questions. Each is a single crisp one-sentence question plus 2–3 sentences of framing. The skill pushes for *your* version of the question — generic questions get rewritten before you see them.
- **The negative-space check** against the signals gathered above (or verbal recall if none). Surfaces themes the interview missed, validates themes it caught, and flags candidates with no sustained-attention support.
- **An ordering step.** Before writing pages, the skill proposes an order for your committed set with a one-line rationale per position (provocative hook up front, related questions clustered in the middle, commitment question at the end). You iterate with it until you're happy.
- **A short retro** at the end — five conversational questions on how it went. Your answers go to `meta/feedback_elicit_<YYYY-MM-DD>.md` locally; sharing back is opt-in via a linked issue template.

### 3. Inspect the outputs

After the session, the instance contains:

- **`wiki/questions/<slug>.md`** — one markdown file per committed question, with frontmatter, a `## Framing` section, and an empty `## Notes` section ready for contribution notes.
- **`wiki/my_open_questions.md`** — the shareable ordered list. Plain numbered list, no framings or links, scannable and pasteable into a bio, a LinkedIn intro, or a conversation. This file is distinct from `wiki/index.md` (which is alphabetical, auto-generated, and intended for LLM navigation).
- **`wiki/index.md`** — regenerated to include the new pages.
- **`meta/log.md`** — a new `elicit` entry recording the session.
- **`meta/feedback_elicit_<YYYY-MM-DD>.md`** — your retro answers.

Once the set is written, the natural next move is `/wiki-ingest` — paste a URL or a chunk of text and the harness will classify it against your question pages and append contribution notes to each one it advances.

## Adjacent skills

Once an instance is bootstrapped and the question set is written, the full skill surface available to you:

- **[`/wiki-ingest`](https://github.com/eyefodder/memex#whats-in-the-box)** (memex) — capture a new source, classify against your questions, append contribution notes to the ones it advances, rebuild the index, log the operation.
- **[`/wiki-query`](https://github.com/eyefodder/memex#whats-in-the-box)** (memex) — ask a question against the wiki; get an answer synthesized from contributions with citations, optionally filed back as a new page.
- **[`/wiki-lint`](https://github.com/eyefodder/memex#whats-in-the-box)** (memex) — health check: mechanical integrity pass (frontmatter, broken links, orphans, stale dates) plus an LLM pass for contradictions and missing cross-references.
- **[`/inquiry-gap`](./skills/inquiry-gap/SKILL.md)** (this repo) — gap report at set-level (default) or within a single page (`/inquiry-gap within <slug>`). Required to surface at least one non-obvious observation per run; a generic report is worse than no report.

## Schema composition model

The schema behind an inquiry instance is composed of three layers:

1. **Generic wiki conventions** — baked into the memex harness skills and shipped as `memex/schema.example.md`. Directory structure, `log.md` and `index.md` formats, ingest/query/lint workflow.
2. **Inquiry-specific additions** — shipped here as [`schema.inquiry.example.md`](./schema.inquiry.example.md). Question page format, contribution notes, gap report conventions, elicitation workflow, inquiry-domain vocabulary.
3. **Instance customizations** — live in your instance's `SCHEMA.md` after the two templates are composed at bootstrap. Voice, status vocabulary, thematic tags, anything project-specific.

The two template files are a starting point, not a live dependency. Once `SCHEMA.md` is composed, you edit it directly. No ongoing merge burden.

## Known rough edges

- **Amazon wishlist scraping is rate-limited.** If you point the negative-space check at a public Amazon wishlist, you may get a 503. The workarounds: export the wishlist manually (browser print-to-PDF or copy-paste), or skip it and rely on other signal sources. A dedicated CLI or browser-extension path is a candidate for a future revision.
- **LinkedIn saved posts have no clean export.** The practical path is copy-paste a screen's worth of titles into a scratch file, or take screenshots and paste them into the session. Noisy but workable.
- **No re-elicitation against an existing set (v0.1).** Re-running `/inquiry-elicit` on an instance that already has question pages stops and asks. For now, edit pages directly, or delete `wiki/questions/` and run the skill fresh. A partial-refresh workflow is planned for a future revision.

## Feedback

Every `/inquiry-elicit` and `/inquiry-gap` session ends with a short conversational retro — a few questions on how it went, where the skill pushed well, where it let you off easy, and one specific change that would make it better. Your answers are written to `meta/feedback_<skill>_<date>.md` inside your instance.

The file is yours by default — it stays local and is never uploaded anywhere automatically. If you want to share what you found back to help sharpen the skill, file an issue using the [Skill feedback template](https://github.com/eyefodder/big_questions/issues/new?template=skill_feedback.yml) and paste the contents of your retro file in. The template fields line up with the file sections, so it's copy-paste. Sharing is opt-in, per session, per file.

## Status

**v0.1.** Question elicitation (with negative-space check and ordered-set output), set-level gap, within-question gap, one-command bootstrap. Revision and retirement workflows, automated ingestion, and semi-automated write-ups are planned for future revisions.

## License

MIT. See [LICENSE](./LICENSE).
