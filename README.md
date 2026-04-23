# big_questions

**big_questions** is an inquiry-instrument layer on top of the [memex](https://github.com/eyefodder/memex) LLM-wiki harness. It adds two Claude Code skills — `/inquiry-elicit` to conduct a structured interview and produce your ~12 big questions, and `/inquiry-gap` to run gap analysis against them. You keep a small, explicit set of questions; the system watches what you're missing.

The intellectual lineage is Feynman's "twelve favorite problems," documented by Gian-Carlo Rota (see [Intellectual lineage](#intellectual-lineage) below). memex supplies the generic wiki harness; big_questions specializes it for the inquiry domain.

## What's in the box

| Artifact | Purpose |
|---|---|
| `skills/inquiry-elicit/` | Claude Code skill — runs a 15–20 minute structured interview and writes 8–12 question pages under `wiki/questions/`. |
| `skills/inquiry-gap/` | Claude Code skill — produces gap reports at two scopes: **set-level** (across all active questions) and **within-question** (on any page with ≥3 contributions). |
| `skills/inquiry-init/` | Claude Code skill — one-command bootstrap for a new inquiry instance: creates the directory tree and composes `SCHEMA.md` from the memex base plus the inquiry addendum. |
| `helpers/init_inquiry.py` | Python CLI invoked by `/inquiry-init`; shells out to memex's `init_wiki.py` and layers the inquiry addendum onto `SCHEMA.md`. |
| `schema.inquiry.example.md` | Inquiry-specific schema addendum. Appends onto `memex/schema.example.md` to define question pages, contribution notes, gap reports, and elicitation conventions. |

## Requires

[memex](https://github.com/eyefodder/memex) — the generic LLM-wiki harness. big_questions will not function without it: ingestion, querying, linting, `log.md` formatting, and `index.md` maintenance all come from memex. The inquiry skills here call memex's helper scripts (`helpers/log_append.py`, `helpers/index_update.py`) directly.

## Install

Two-part install: memex first, then big_questions. Both install user-scoped — the skills live in `~/.claude/skills/` and are available in any Claude Code session.

### 1. Install memex

Follow the install section of the [memex README](https://github.com/eyefodder/memex#install). That sets up `~/Development/memex/` and symlinks the `wiki-*` harness skills into `~/.claude/skills/`.

### 2. Clone big_questions and symlink the inquiry skills user-scoped

```bash
git clone https://github.com/eyefodder/big_questions ~/Development/big_questions
mkdir -p ~/.claude/skills
ln -s ~/Development/big_questions/skills/inquiry-elicit ~/.claude/skills/
ln -s ~/Development/big_questions/skills/inquiry-gap    ~/.claude/skills/
ln -s ~/Development/big_questions/skills/inquiry-init   ~/.claude/skills/
```

Then **restart Claude Code** so it picks up the new skills. `/inquiry-init`, `/inquiry-elicit`, and `/inquiry-gap` are now available in any Claude Code session.

**Why user-scoped.** Keeping install locations consistent with memex removes a chicken-and-egg problem: `/inquiry-init` needs to be invocable *before* an inquiry instance exists, which rules out project-scoped installation. The minor cost — `/inquiry-elicit` and `/inquiry-gap` appear in autocomplete in non-inquiry sessions — matches how Claude Code's built-in skills work and is acceptable at v0.1.

## Bootstrap a new inquiry instance

An **instance** is the folder holding your actual question wiki — the questions, the paste-ins, the gap reports. It is independent of this repo so skill development stays decoupled from question content.

One command, from any Claude Code session:

```
/inquiry-init <instance-path>
```

For example: `/inquiry-init ~/vaults/MyVault/01_Projects/my_big_questions`.

The skill shells out to `helpers/init_inquiry.py`, which:

1. Checks that memex is installed (precondition — fails fast with a clear message if not).
2. Invokes memex's `init_wiki.py --path <instance-path> --pages-dir questions` to build the generic directory tree (`wiki/questions/`, `raw/`, `meta/`, `SCHEMA.md` seeded from the memex base).
3. Appends `schema.inquiry.example.md` onto the new `SCHEMA.md`, producing the composed inquiry schema.

The instance is now ready for `/inquiry-elicit`. Re-running `/inquiry-init` on the same path is idempotent (safe); pass `--force` to reseed `SCHEMA.md` from the templates after a schema update (question content is preserved).

### Manual bootstrap (if you prefer)

If you'd rather not use the helper, the equivalent is four shell commands:

```bash
mkdir -p <instance-path>/{wiki/questions,raw,meta,.claude/skills}
touch <instance-path>/wiki/index.md <instance-path>/meta/log.md
cat ~/Development/memex/schema.example.md \
    ~/Development/big_questions/schema.inquiry.example.md \
    > <instance-path>/SCHEMA.md
```

No skill symlinking into the instance — the inquiry skills are user-scoped.

## Quickstart

The core loop in four steps:

1. **Elicit your question set.** In Claude Code, from your instance directory:

    ```
    /inquiry-elicit
    ```

    A 15–20 minute interview that probes your current role, concerns, 12-month expertise goals, positions you'd want to argue, and re-read material. Produces 8–12 question pages under `wiki/questions/`, each with frontmatter and a framing section. No padding — if fewer than 8 honest questions surface, the skill says so and recommends a second pass.

2. **Ingest sources.** Paste a URL or a chunk of text into Claude Code and run:

    ```
    /wiki-ingest
    ```

    (from memex). The harness classifies the source against your question pages and appends a one-sentence contribution note to each one it advances.

3. **Run a within-question gap report** on any page that has accumulated ≥3 contributions:

    ```
    /inquiry-gap within <slug>
    ```

    Surfaces thin evidence, one-sided arguments, missing counter-positions, repeated sources.

4. **Run a set-level gap report** any time:

    ```
    /inquiry-gap
    ```

    Surfaces implicit frames, missing dimensions, overlapping pairs, questions too narrow or too broad to be productive. Writes `meta/gap_report_<YYYY-MM-DD>.md` and renders a scannable summary in the conversation.

Gap reports are required to produce at least one non-obvious observation per run. A generic report is worse than no report — it teaches you the instrument doesn't see anything you don't.

## Intellectual lineage

This project externalizes a practice attributed to Richard Feynman and documented by Gian-Carlo Rota in *["Ten Lessons I Wish I Had Been Taught"](https://www.ams.org/notices/199701/comm-rota.pdf)* (Notices of the AMS, 1997):

> *"You have to keep a dozen of your favorite problems constantly present in your mind, although by and large they will lay in a dormant state. Every time you hear or read a new trick or a new result, test it against each of your twelve problems to see whether it helps."*

Feynman's twelve problems lived in his head. big_questions is what that practice looks like when the bookkeeping is handed to an LLM — the questions, the framing, the contributions, the cross-references, and the gap analysis all live on disk and are maintained by the model. The user keeps their attention small and explicit; the model keeps the records.

See PRD Section 2.1 of the parent project for more on the framing.

## Feedback

Every `/inquiry-elicit` and `/inquiry-gap` session ends with a short conversational retro — five questions on how it went, where the skill pushed well, where it let you off easy, and one specific change that would make it better. Your answers are written to `meta/feedback_<skill>_<date>.md` inside your instance.

The file is yours by default — it stays local in your instance and is never uploaded anywhere automatically. If you want to share what you found back to help sharpen the skill, file an issue using the [Skill feedback template](https://github.com/eyefodder/big_questions/issues/new?template=skill_feedback.yml) and paste the contents of your retro file in. The template fields line up with the file sections, so it's copy-paste. Sharing is opt-in, per session, per file.

## Schema composition model

The schema behind an inquiry instance is composed of three layers (memex Decision 8):

1. **Generic wiki conventions** — baked into the memex harness skills and shipped as `memex/schema.example.md`. Directory structure, `log.md` and `index.md` formats, ingest/query/lint workflow.
2. **Inquiry-specific additions** — shipped here as `schema.inquiry.example.md`. Question page format, contribution notes, gap report conventions, elicitation workflow, inquiry-domain vocabulary.
3. **Instance customizations** — live in your instance's `SCHEMA.md` after the two templates are composed at bootstrap. Voice, status vocabulary, thematic tags, anything project-specific.

The two template files are a starting point, not a live dependency. Once `SCHEMA.md` is composed, you edit it directly. No ongoing merge burden.

## Status / versioning

**v0.1.** Question elicitation, set-level gap, within-question gap. Revision and retirement workflow, automated ingestion, and semi-automated write-ups are planned for future revisions.

## License

MIT.
