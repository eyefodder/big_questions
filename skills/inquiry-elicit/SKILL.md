---
name: inquiry-elicit
description: Conduct a 15-20 minute structured interview to elicit and articulate a user's ~8-12 big questions, then write them as wiki pages under wiki/questions/.
---

# inquiry-elicit

## Purpose

This skill is the entry point for a new inquiry-instrument instance. It runs a structured conversation with the user, probes for the handful of questions they are genuinely trying to figure out right now, and writes those questions to disk as wiki pages conforming to the inquiry page schema. It produces 8-12 question files under `./wiki/questions/`, rebuilds `./wiki/index.md`, and appends an entry to `./wiki/log.md`.

Invoke when: the instance has a composed `SCHEMA.md` at its root but `./wiki/questions/` is empty (or the user explicitly wants to bootstrap a fresh question set). At Skateboard, re-running against an existing set is not supported — that is Bicycle scope.

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
4. If `./wiki/questions/` already contains `*.md` files, stop and ask. Re-elicitation is not a Skateboard workflow; the user may have intended a second-pass append, which is out of scope here.

If SCHEMA.md is missing, error out with: "No SCHEMA.md at `<cwd>`. Bootstrap the instance first by composing `memex/schema.example.md + big_questions/schema.inquiry.example.md > SCHEMA.md`."

## Interview structure

Target wall-clock: **15-20 minutes**. Five probe areas, in order, taken from PRD Section 6.1.1. Do not rigidly timebox each area — let the conversation breathe where it is productive and cut it short where it is not. Aim for roughly 3-4 minutes per probe on average.

1. **Current role context.** What the user is actually doing day-to-day and what is shaping their thinking right now. Establishes the ground truth the rest of the questions have to sit against.
2. **What is keeping them up at night.** Genuinely open problems, not solved ones. Where is their current mental model breaking down?
3. **12-month expertise goals.** What they want to be expert on a year from now. Forward-looking; reveals questions they are not yet qualified to answer but want to be.
4. **Positions to defend.** What they would argue about in an interview-style conversation — positions they hold now but might have to defend. Reveals the shape of their opinions, which is where the sharpest questions usually live.
5. **Re-read material.** What they keep returning to. Where they go back because they are *not done thinking* about it. Strong signal for a live question.

### Probing for specificity

The quality bar for this skill is that every committed question is *the user's version* of the question, not a generic version of it. Generic questions produce generic pages produce generic gap reports produce an unshippable Week 1 post. Push. Some prompts that work:

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

- **A crisp one-sentence question.** 10-20 words. Usually begins with *How*, *What*, *Why*, *When*, or *Under what conditions*. Ends with a question mark. No hedging, no compound conjunctions ("and"/"or" across two questions).
- **2-3 sentences of framing.** Why this question is live for this user right now, what it rules in, what it rules out. Framing is the context a reader needs to understand why the question is worth asking *of this person*.

Aim for breadth: if three questions are about the same theme, collapse or retire the weakest one. A set of twelve questions should not feel like one question asked in twelve ways.

Present the candidate set to the user in plain prose — questions numbered, framings as a short paragraph per question. Iterate based on their feedback before writing any files. Offer to drop, merge, sharpen, or reorder. Keep pushing on anything that still reads generically.

## Quality bar — the non-generic requirement

**Before writing files, self-critique the candidate set.** For each question, ask:

1. Is this crisp enough that the user would defend it in an interview?
2. Is it *their* version of the question, or a generic version a colleague in their role would also write?
3. Could a stranger tell, from the framing alone, what this user specifically cares about?
4. Does the question point at a real tension or open decision, not a platitude?

Any question that fails this self-critique: surface the concern to the user and either refine or drop. Do not write it as-is.

**If fewer than 8 genuinely specific questions survive after a full 20-minute interview, do not pad.** Write the set as it is (even if it's 6 or 7), note in the log entry that the set is incomplete, and recommend a second session after the user has had time to sit with the shape of what emerged. An 11-question set that is entirely the user's beats a 12-question set with one synthesized filler.

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
python3 <harness-path>/helpers/index_update.py --wiki ./wiki --pages-dir questions
```

Check the exit code. If it fails, read stderr and surface the error — the index is how the ingest and gap skills find the pages.

## Logging

Append a single entry to `./wiki/log.md`:

```bash
python3 <harness-path>/helpers/log_append.py \
  --wiki ./wiki \
  --op elicit \
  --subject "initial <n>-question set" \
  --body "Produced <n> questions across <brief theme summary>.<optional shortfall note>"
```

Where:

- `<n>` is the actual number of question files written.
- Theme summary is a short phrase naming 2-4 recurring themes (e.g. "self-improving software, org design, signal-vs-noise").
- If fewer than 8 questions were committed, append to the body: `" Set is incomplete; a second-pass elicitation is recommended."`

## Failure modes

| Failure | Handling |
|---|---|
| `SCHEMA.md` missing at CWD | Error with bootstrap instructions (see Preconditions). Do not start the interview. |
| User declines to continue mid-interview | Save the transcript and any synthesized candidates to `./wiki/.elicit_session_<YYYY-MM-DDTHHMMSS>.json` (structure: `{"started_at": ..., "probes_completed": [...], "transcript": "...", "candidates": [...]}`). Tell the user the session is saved and can be resumed. Do not write any `questions/*.md` files from a partial session. |
| Helpers unreachable | Ask the user for the path. If they still can't provide one, write the pages, skip the index and log calls, and print exact commands the user can run manually afterwards. |
| Duplicate slug | Append a numeric disambiguator (`-2`, `-3`, ...). Do not silently overwrite. |
| Fewer than 8 specific questions | Write what survived the quality bar. Log the shortfall. Recommend a second session. Do not pad. |
| User wants to re-elicit over an existing set | Stop. This is Bicycle scope. Offer instead: edit pages directly, or delete the directory and restart fresh. |

## What this skill is not

- Not domain-neutral. The vocabulary here is `question`, `framing`, `contribution`, `gap` — the inquiry-instrument domain. A book-companion or research-tracker instance would use a different elicit skill.
- Not a template filler. The content comes entirely from the user. Do not suggest questions from prior conversations or from generic "senior engineering leader" archetypes. The whole point is specificity.
- Not schema-defining. SCHEMA.md defines the page format; this skill *uses* that format. If the user wants to change the shape of a page, they edit SCHEMA.md, not this skill.
