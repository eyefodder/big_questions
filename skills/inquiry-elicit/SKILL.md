---
name: inquiry-elicit
description: Conduct a 15-20 minute structured interview to elicit and articulate a user's ~8-12 big questions, then write them as wiki pages under wiki/questions/.
---

# inquiry-elicit

## Purpose

This skill is the entry point for a new inquiry-instrument instance. It runs a structured conversation with the user, probes for the handful of questions they are genuinely trying to figure out right now, checks the draft set against signals of sustained attention, proposes an order for the committed set, and writes the result to disk as wiki pages conforming to the inquiry page schema. It produces 8-12 question files under `./wiki/questions/`, writes a shareable ordered-list file at `./wiki/my_open_questions.md`, rebuilds `./wiki/index.md`, and appends an entry to `./meta/log.md`.

Invoke when: the instance has a composed `SCHEMA.md` at its root but `./wiki/questions/` is empty (or the user explicitly wants to bootstrap a fresh question set). In v0.1, re-running against an existing set is not supported — that is planned for a future revision.

## Intellectual lineage

The practice this skill externalizes is the "twelve favorite problems" habit attributed to Richard Feynman and documented by Gian-Carlo Rota in *Ten Lessons I Wish I Had Been Taught* (Notices of the AMS, 1997): keep a dozen of your favorite problems present in mind, and test every new idea against them. This skill produces the externalized version of that set — questions the LLM can subsequently maintain and test new material against.

## Preconditions

Before starting the interview, verify:

1. `./SCHEMA.md` exists at the current working directory. Read it — it defines the inquiry page format (frontmatter, `## Framing`, `## Notes`), operation vocabulary, and instance-specific customizations that override anything below. If anything in SCHEMA.md conflicts with this SKILL.md, SCHEMA.md wins.
2. `./wiki/` exists, or can be created. If `./wiki/questions/` is missing, create it before writing pages.
3. The memex helpers `log_append.py` and `index_update.py` are reachable. Resolve `<harness-path>` by:
   1. Check `./memex/helpers/` (some instances vendor the harness).
   2. Follow this SKILL.md's symlink back to its source directory and look for a sibling `../Development/memex/helpers/` (the canonical install path per Decision 9).
   3. If neither resolves, ask the user for the path before proceeding. Do not silently skip the helper calls.
4. If `./wiki/questions/` already contains `*.md` files, stop and ask. Re-elicitation is not a v0.1 workflow; the user may have intended a second-pass append, which is out of scope here.

If SCHEMA.md is missing, error out with: "No SCHEMA.md at `<cwd>`. Bootstrap the instance first by composing `memex/schema.example.md + big_questions/schema.inquiry.example.md > SCHEMA.md`."

## Interview structure

Target wall-clock: **15-20 minutes**. Five probe areas, in order, taken from PRD Section 6.1.1. Do not rigidly timebox each area — let the conversation breathe where it is productive and cut it short where it is not. Aim for roughly 3-4 minutes per probe on average.

1. **Current role context.** What the user is actually doing day-to-day and what is shaping their thinking right now. Establishes the ground truth the rest of the questions have to sit against.
2. **What is keeping them up at night.** Genuinely open problems, not solved ones. Where is their current mental model breaking down?
3. **12-month expertise goals.** What they want to be expert on a year from now. Forward-looking; reveals questions they are not yet qualified to answer but want to be.
4. **Positions to defend.** What they would argue about in an interview-style conversation — positions they hold now but might have to defend. Reveals the shape of their opinions, which is where the sharpest questions usually live.
5. **Re-read material.** What they keep returning to. Where they go back because they are *not done thinking* about it. Strong signal for a live question.

### Probing for specificity

The quality bar for this skill is that every committed question is *the user's version* of the question, not a generic version of it. Generic questions produce generic pages produce generic gap reports produce an unshippable set. Push. Some prompts that work:

- "That's a common concern — what's the version of it that's specifically yours?"
- "You said X. What would it take for you to change your mind about that?"
- "Give me an example of a time this mattered in practice."
- "Who is wrong about this, in your view? What do they believe that you don't?"
- "If I asked you this same question in six months, what would make your answer different?"
- "What's the part of this you're currently stuck on, not the part you've already worked out?"

When an answer is abstract, ask for a concrete instance. When an answer is a category, ask for the specific case. When an answer matches a cliche of the user's field, assume the cliche is camouflage and probe underneath.

## Time management

- Set a rough mental clock. At about 2/3 of the target window (~13 minutes in), mark the time internally and shift from probing to synthesizing — even if a probe area felt underexplored.
- Do not rush to 8 questions early. Do not drag past 20 minutes trying to reach 12.
- If the user is still surfacing rich material at minute 18, wrap the interview and note that a second pass would likely add value.

## Synthesis — producing the candidate set

After the interview, synthesize 8-12 candidate questions from the transcript. For each:

- **A crisp one-sentence question.** Single clean interrogative. Typically begins with *How*, *What*, *Why*, *When*, or *Under what conditions*. Ends with a question mark. 8-16 words. No hedging, no compound "and" joining two interrogatives, no setup clauses that bury the actual question.
- **2-3 sentences of framing.** Why this question is live for this user right now, what it rules in, what it rules out. Framing is the context a reader needs to understand why the question is worth asking *of this person*. **The framing belongs in the body, not inside the question.**

Aim for breadth: if three questions are about the same theme, collapse or retire the weakest one. A set of twelve questions should not feel like one question asked in twelve ways.

### Form — match the Feynman shape on the first draft

The target form is the one Feynman used for his own favorite problems: a single clean interrogative that lands in one breath. Match this shape on the first draft you present to the user, not on a correction pass after they push back.

**Positive examples (Feynman-style, verbatim):**

- "How can we measure the probability that a lump of uranium might explode too soon?"
- "What is the unifying principle underlying light, radio, magnetism, and electricity?"
- "How can I sustain a two-handed polyrhythm on the drums?"
- "What is the smallest working machine that can be constructed?"

Each is one interrogative. None stacks sub-questions. None has a setup clause. Framing (what makes the question live, what it rules in and out) is not inside the sentence — it lives alongside it.

**Negative example — the drift to catch.** A compound, over-conditional draft that runs as a paragraph instead of a question:

> "How should a self-evolving product balance its declared thesis against its observation of itself in the environment — and under what conditions does either end lead to degeneration?"

The crisp rewrite:

> "How does a self-evolving product balance what it says it is against what it sees about itself?"

Same question. One interrogative. No em-dash tail. No "and under what conditions" rider. The conditions and the degeneration concern belong in the framing paragraph, not the question.

### Self-critique before presenting

Before presenting the candidate set to the user, re-read each question and apply this pass:

- Does it run longer than ~16 words? If yes, something in it is probably framing that should move to the body.
- Does it contain "and" joining two interrogatives, or a mid-sentence em-dash that introduces a second question? If yes, split or drop one half.
- Is the actual question buried inside a setup clause ("Given that X, how does Y...")? If yes, foreground the question and move the setup to framing.
- Could a stranger who has never met this user parse the question in one read? If no, simplify.

Rewrite any candidate that fails this pass **before** showing it to the user. The user's push-back energy should go into whether these are the right questions, not into reformatting them.

Present the candidate set to the user in plain prose — questions numbered, framings as a short paragraph per question. Iterate based on their feedback. Offer to drop, merge, sharpen, or reorder. Keep pushing on anything that still reads generically.

## Quality bar — the non-generic requirement

For each candidate, ask:

1. Is this crisp enough that the user would defend it in an interview?
2. Is it *their* version of the question, or a generic version a colleague in their role would also write?
3. Could a stranger tell, from the framing alone, what this user specifically cares about?
4. Does the question point at a real tension or open decision, not a platitude?

Any question that fails this self-critique: surface the concern to the user and either refine or drop. Do not write it as-is.

**These questions are not only private thought-filing headers. They are also shareable artifacts** — a user may introduce themselves through them, use them as conversation starters, or signal intellectual range in an interview or a bio. A question that works as a file-header can still fail as a conversation opener. Optimize for both.

**If fewer than 8 genuinely specific questions survive after a full 20-minute interview, do not pad.** Write the set as it is (even if it's 6 or 7), note in the log entry that the set is incomplete, and recommend a second session after the user has had time to sit with the shape of what emerged. An 11-question set that is entirely the user's beats a 12-question set with one synthesized filler.

## Negative-space check

A 15-20 minute window will miss themes the user has been sitting with for months or years. **Before committing the set**, run an explicit check against signals of sustained attention. This is a defined phase, not an improvised move — propose it to the user and then run it. A session's strongest surprises often come from here.

### Signal sources, in rough priority order

1. **Reading-tracker CLIs with exportable data** — Readwise Reader, Readwise highlights, Instapaper, Pocket, Goodreads exports, Calibre library metadata. Richest signal when available.
2. **Social-media save streams** — LinkedIn saved posts (no clean export — expect paste or screenshot), Twitter/X bookmarks, Reddit saved.
3. **Purchase and wishlist signals** — Amazon wishlists (variable public-share behavior, rate-limited), Kindle library.
4. **Browser bookmarks / browsing history** — possible but noisy; use as a fallback.
5. **The user's own verbal recall** — "What have you kept coming back to over the past year?" A valid standalone signal when nothing else is available. Do not skip the phase just because no external source exists.

### CLI first — do not reach for scraping

Before scraping any web UI, check whether the user has an installed and authenticated CLI for the service. CLI output is cleaner, more complete, and more stable than scraping. Ask directly: "Do you have the `readwise` CLI installed? `goodreads`? Anything similar?" If yes, use it. Web scraping a logged-in UI is lossy and brittle — prefer a paste or an export over a scrape.

If no CLI exists for the source, ask the user to export (Readwise supports CSV/Markdown; most others have an export button), or paste titles and authors into a scratch file. Scrape only as a last resort.

### Analysis

Aggregate the signal by author, domain, and keyword cluster. Surface themes. Then, for each candidate question, ask:

- **(a)** Does this candidate have sustained-attention support? (If yes, you have validation.)
- **(b)** Are there sustained-attention themes with no candidate question? (These are candidate additions — the negative space the 20-minute interview missed.)
- **(c)** Are there candidates with no sustained-attention support? (Consider reframing, cutting, or keeping as a declared-forward-looking question with eyes open.)

Propose additions, reframes, and cuts to the user. They commit the final set.

### Time cap and graceful degradation

**Time cap: ~30 minutes total, including harvesting.** If the signal source is too large to scan in that window, sample rather than exhaust it.

**Graceful degradation.** A thin signal still produces useful findings. A user with hundreds of saved articles will get richer output than one with twenty — but twenty is not zero, and verbal recall alone is not zero. The skill should not assume Readwise-scale volume. Run the phase with whatever signal the user has.

## Ordering the committed set

After the user commits the final question set and before writing the per-question pages, **propose an order**. The set does double duty: privately it is an attention filter (file headers); publicly it is a shareable artifact. For the shareable role, sequence matters — alphabetical is a bug, not a feature.

Propose a first-draft order with a one-line rationale per position. Heuristics:

- **Position 1-2** — provocative or surprising questions. Something that makes a reader stop scrolling. Hooks.
- **Middle** — cluster related questions so the reader can follow a thread. Interleave pure-curiosity "favorite problems" as palette cleansers between heavier role/identity questions, so the reader isn't fatigued.
- **Final position** — a commitment question. The stake the user is putting in the ground. Often names the user's own role in the thing being discussed.

Present the proposed order as a numbered list with the rationale alongside each position. Iterate with the user until they commit. This is not a place to rush — the order is load-bearing for how the set reads.

### Persist the ordered set

Write the committed order to `./wiki/my_open_questions.md` (or a user-specified filename). **Default: plain numbered list.** Title, at most one line of intro, questions numbered in the committed order, nothing else. No framings, no links, no metadata. The shareable artifact's job is to be scannable and pasteable — into a bio, a LinkedIn intro, a conversation.

Template:

```markdown
# My open questions

The questions I'm actively trying to figure out right now.

1. <First question, verbatim>
2. <Second question, verbatim>
...
12. <Last question, verbatim>
```

Framings live in the per-question pages under `wiki/questions/` for anyone who wants to follow up. If the user later wants a richer variant with framings inline, they can edit the file or ask for a second version — but the default ships plain.

**This file is distinct from `wiki/index.md`.** The index is alphabetical, auto-generated by `index_update.py`, and intended for LLM navigation. `my_open_questions.md` is ordered, curated, and intended for human readers. Two audiences, two files — do not conflate them.

## Writing the question pages

For each confirmed question, write one markdown file to `./wiki/questions/<slug>.md`.

### Slugging

Deterministic transform from the one-sentence question:

1. Lowercase.
2. Replace every run of non-alphanumeric characters with a single `-`.
3. Trim leading and trailing `-`.
4. Truncate to ~60 characters at a word boundary if longer.

If the resulting slug collides with an already-written file in this run (or a file already on disk from a prior session), append `-2`, `-3`, ... until unique.

### Page format

Follow the format defined in SCHEMA.md (the inquiry addendum). At minimum:

```markdown
---
slug: <slug>
title: "<the one-sentence question, verbatim, with the question mark>"
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
status: active
contributions: 0
---

# <the one-sentence question, verbatim>

## Framing

<2-3 sentences of framing, written from the interview transcript>

## Notes

<!-- Contribution notes appended by /wiki-ingest, one per source. -->
```

The `title` frontmatter field holds the question verbatim (per the schema's decision to collapse `title` and `question` — do not introduce a separate `question:` field). `created` and `updated` are both today. `status: active`. `contributions: 0`. Body `# <title>` matches frontmatter `title` exactly.

## Updating the index

After all pages are written, rebuild the index:

```bash
python3 <harness-path>/helpers/index_update.py --content-dir ./wiki --pages-dir questions
```

Check the exit code. If it fails, read stderr and surface the error — the index is how the ingest and gap skills find the pages.

## Logging

Append a single entry to `./meta/log.md`:

```bash
python3 <harness-path>/helpers/log_append.py \
  --log-dir ./meta \
  --op elicit \
  --subject "initial <n>-question set" \
  --body "Produced <n> questions across <brief theme summary>. Ordered for sharing: <one-line rationale>.<optional shortfall note>"
```

Where:

- `<n>` is the actual number of question files written.
- Theme summary is a short phrase naming 2-4 recurring themes (e.g. "self-improving software, org design, signal-vs-noise").
- The ordering rationale is a single line naming the hook and the closing commitment (e.g. "opens with the radical-creativity hook, closes with the AI-moment commitment").
- If fewer than 8 questions were committed, append to the body: `" Set is incomplete; a second-pass elicitation is recommended."`

## End-of-session retro

After the log append succeeds, run a short wrap-up retro with the user before signing off. The tone is conversational — "before we finish, one more thing" — not a form or a survey. Ask the questions one at a time and wait for each answer before moving to the next. Do not batch them, do not dump them as a numbered list.

Ask, in order, phrased naturally in your own words. Approximate phrasings:

1. "Before we finish — how did this go for you? (one sentence is fine)"
2. "Did you leave with questions you'd defend publicly? If yes, which one(s)? If no, what got in the way?"
3. "Where did I push you effectively? (One concrete moment, if you can.)"
4. "Where did I let you off easy when I should have pushed harder?"
5. "One specific change that would have made this better?"

Run the retro even if the user was terse throughout the interview — the retro is where thin feedback gets a last chance to surface. If the user tries to wave it off with "no feedback," push once gently: "Even one observation is useful." If they're still rushed, accept whatever they give and mark unanswered prompts as `(skipped)` in the file — do not accept a fully empty retro silently.

### Writing the feedback file

After the final answer, write to `./meta/feedback_elicit_<YYYY-MM-DD>.md`. If a file already exists at that path (same-day retry), append a numeric suffix: `_2`, `_3`, ... — never clobber a prior session's feedback.

**Resolving the `version:` field.** Try to capture the big_questions commit SHA so the feedback is tied to the skill revision that produced it:

1. Resolve this SKILL.md's real path (follow the symlink from `~/.claude/skills/inquiry-elicit/` back to the repo).
2. From that path, find the repo root (the enclosing `big_questions/` directory).
3. Run `git -C <repo> rev-parse --short HEAD` via the bash tool.
4. If git is unavailable, the path doesn't resolve, or the command fails for any reason, set `version: unknown`. Never fail the retro over this — the user's answers matter more than the SHA.

File content (fill answers verbatim as the user gave them; preserve their words, don't paraphrase):

```markdown
---
skill: inquiry-elicit
date: YYYY-MM-DD
version: <sha-or-unknown>
---

# Session feedback — inquiry-elicit — YYYY-MM-DD

## How did this go? (one sentence)

<answer>

## Did you leave with questions you'd defend publicly?

<answer>

## Where did the skill push you effectively?

<answer>

## Where did the skill let you off easy?

<answer>

## One specific change that would have made this better

<answer>
```

### Final message to the user

After the file is written, tell the user where it is and offer the issue-template URL. Something like:

> Saved your feedback to `./meta/feedback_elicit_<YYYY-MM-DD>.md`. If you'd like to share it back to help improve the skill, file an issue using this template: https://github.com/eyefodder/big_questions/issues/new?template=skill_feedback.yml — no pressure, it's your file.

Keep the tone warm and low-friction. The file is the user's by default; sharing is opt-in.

## Failure modes

| Failure | Handling |
|---|---|
| `SCHEMA.md` missing at CWD | Error with bootstrap instructions (see Preconditions). Do not start the interview. |
| User declines to continue mid-interview | Save the transcript and any synthesized candidates to `./wiki/.elicit_session_<YYYY-MM-DDTHHMMSS>.json` (structure: `{"started_at": ..., "probes_completed": [...], "transcript": "...", "candidates": [...]}`). Tell the user the session is saved and can be resumed. Do not write any `questions/*.md` files from a partial session. |
| Helpers unreachable | Ask the user for the path. If they still can't provide one, write the pages and `my_open_questions.md`, skip the index and log calls, and print exact commands the user can run manually afterwards. |
| Duplicate slug | Append a numeric disambiguator (`-2`, `-3`, ...). Do not silently overwrite. |
| Fewer than 8 specific questions | Write what survived the quality bar. Log the shortfall. Recommend a second session. Do not pad. |
| No sustained-attention signal available at all | Run the negative-space phase against verbal recall alone ("What have you kept coming back to over the past year?"). Do not skip the phase. |
| User wants to re-elicit over an existing set | Stop. That workflow is planned for a future revision. Offer instead: edit pages directly, or delete the directory and restart fresh. |
| Git unavailable when resolving retro `version:` | Write `version: unknown` and continue. Never fail the retro over SHA resolution. |
| User waves off retro entirely | Push once ("even one observation is useful"), then accept whatever they give and mark the rest `(skipped)`. Do not silently skip the file write. |

## What this skill is not

- Not domain-neutral. The vocabulary here is `question`, `framing`, `contribution`, `gap` — the inquiry-instrument domain. A book-companion or research-tracker instance would use a different elicit skill.
- Not a template filler. The content comes entirely from the user. Do not suggest questions from prior conversations or from generic "senior engineering leader" archetypes. The whole point is specificity.
- Not schema-defining. SCHEMA.md defines the page format; this skill *uses* that format. If the user wants to change the shape of a page, they edit SCHEMA.md, not this skill.
