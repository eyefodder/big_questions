---
name: inquiry-synthesize
description: Produce twin outputs on a single inquiry-question page — a long-form Synthesis (magazine-style article-shape of the corpus) and a TL;DR (executive brief). Both write directly to the page, between Framing and Notes; the contributions in Notes stay as the receipts layer.
---

# inquiry-synthesize

## Purpose

Turn the stack of pull-quote-and-rationale contributions on a single question page into three layered artifacts:

- **TL;DR** — single Obsidian callout, ~200 words, info-rich, scannable on phone. The summary of what the corpus says. Derived FROM the synthesis (not independently generated).
- **Threads to pull** — single Obsidian callout placed between the TL;DR and the Synthesis. Forward-looking — horizon-opening "what if" prompts that fuel curiosity, plus a short **Patterns to look out for** sub-section with concrete things to notice in the wild.
- **Synthesis** — 500–800 word magazine-style essay; the article-shape of what the contributions, read together, say about the question.

All three write to the same page in this order: **Framing → TL;DR → Threads to pull → Synthesis → Notes**. The contributions in Notes stay where they are; they are the receipts layer the synthesis cites and the briefing artifacts compress and project from.

The exec read is **Framing → TL;DR → Threads to pull**: a sense of where we are, and where we might go. The deep read is the Synthesis below it.

Invoke when the user runs `/inquiry-synthesize <slug>`, `/inquiry-synthesize`, or otherwise asks for "the article on this page", "synthesize this question", "the brief on this question", or similar.

## The voice — load-bearing

The synthesis is a **meta-opinion**, not the user's opinion and not the LLM's commentary. The article is the article-shape of what the assembled contributions, read together, say about the question. The author of the synthesis is the corpus.

Concretely:

- **Right register:** "the contributions all point at…", "what these sources, taken together, say…", "the through-line is…", "Cutler and Caroli land in the same place; French-Owen breaks from both…".
- **Wrong register:** "I argue…", "<user> thinks…", "this article holds…", "we can see that…", "this synthesis shows…".
- **Authorial syntax, sourced position.** Definitive sentences, position-having — but the position belongs to the assembled contributions, surfaced. The model's job is to read the corpus together and produce the reading.
- **Hold disagreements visible.** If contributions point in different directions, name the disagreement. Do not smooth.
- **No personal stake added.** The framing's personal-stake language is context, not authorial position.

### Reading level — Grade 10, hard rule

Both outputs must be readable at roughly Grade 10 English. The synthesis is a magazine-feature read, not an academic paper. The TL;DR is a bulleted briefing, not a compressed essay. Specific bans and replacements:

- **No academic vocabulary.** Cut: "epistemic", "presumes", "implicitly maps onto", "unit of analysis", "downstream re-reading", "the empirical receipt", "convergence", "structural answer collapses", "alignment substrate". Replace each with everyday words. "Presumes" → "assumes". "Downstream re-reading" → "how it gets used after it's written". "Different epistemic altitudes" → "different levels — what *should* happen vs. what *does* happen".
- **No nominalised phrases when a verb works.** "The corpus implicitly maps onto" → "the corpus ends up sitting on". "Direction-change as value" (when used as prose, not a label) → "they treat changing direction as a value".
- **Short sentences when a long one would lose the reader.** Three short sentences usually beat one comma-spliced paragraph for a load-bearing claim.
- **Test by ear.** Read the line aloud. If a smart but non-academic reader on a phone would have to stop and parse, rewrite. Magazine voice can be lyrical; it cannot be opaque.

This rule applies to the killer line, the bolded generative claims, the inline labels, the body prose, and the entire TL;DR. The TL;DR is more strict: every bullet must read like a briefing item, not a compressed paragraph.

### Coining organizing labels IS the synthesis

Inventing labels that don't appear in the contributions is not contraband — it is the work. Phrases like "distributed authorship of strategy", "artifacts as yardsticks, not announcements", "when work is cheap, alignment becomes about limiting choice" are the synthesis happening: organizing language the corpus implies but doesn't state. Three labels is a typical shape; two is fine if the corpus only splits two ways; four-plus is a sign the synthesis hasn't found its through-line yet.

The labels render in two places, with two different shapes:

- **In the synthesis,** as h4 headings nested under the second h3. The h4 form is **claim-shaped** — short enough to be a heading (4–8 words), self-contained in outline view (`Distributed authorship of strategy`, not `Distributed authorship`).
- **In the TL;DR,** as bolded inline labels at the start of bullets under "Where the corpus lands". The TL;DR form can be **shorter / label-shaped** (`**Distributed authorship.**`) because the explanation follows immediately in the bullet — outline-view self-containment doesn't apply inside a callout.

The two forms label the same answers but are optimised for different surfaces. Don't try to force one form to do both jobs.

## Preconditions

- Current working directory is a wiki root (contains `SCHEMA.md`).
- `wiki/<questions-dir>/<slug>.md` exists with `status: active`.
- The page's `## Notes` section contains **>=3 contributions** (one `### From "<title>"` block per source).
- The memex helper `log_append.py` is available (see **Helper invocation**).

## Steps

### 1. Read `SCHEMA.md`

Read `SCHEMA.md` from the wiki root. Pick up the questions-pages directory name and contribution conventions. If `SCHEMA.md` is missing, stop (see **Failure modes**).

### 2. Resolve the target page

If the user supplied a slug, validate that `wiki/<questions-dir>/<slug>.md` exists and is `status: active`.

If the user supplied no slug, scan for active pages with >=3 contributions. List them with contribution counts and ask. If zero qualify, stop.

### 3. Read the page

Parse:

- The frontmatter (`slug`, `title`, `contributions`).
- The `## Framing` section verbatim.
- Every `### From "<source title>"` block in `## Notes`. For each: source title, raw-file path, Readwise URL if present, every `> [!quote]` callout (takeaway title, quote body, italic rationale), and the block-id reference (e.g. `[[2026-04-25-cutler#^h1|↗]]`).
- If a `## TL;DR` and/or `## Synthesis` section already exists on the page, capture its body — both will be replaced by this run; the prior `## Synthesis` is archived (see step 10).

### 4. Killer-claim pass

Before drafting the synthesis, generate **3-5 candidate corpus-level claims** — single-sentence statements the corpus, taken together, says that no single contribution says. These are the load-bearing sentences the synthesis will be built around.

Examples of strong candidates (drawn from a real run, all at grade-10 reading level):

- "When engineering speed and planning speed run at different rates, both break."
- "An alignment document nobody refers to after it's written is the leader thinking out loud."
- "When the work is cheap, the alignment problem flips — from how to push effort to how to limit choice."

Examples of weak candidates (cut these):

- "There are several approaches to the problem." (Restating that the corpus is plural.)
- "Different sources agree that cascades fail." (Restating consensus without sharpening.)
- "Engineering velocity decoupled from planning velocity destroys both." (Right idea, wrong register — "decoupled" and "velocity" are textbook words; rewrite to "speed" and "run at different rates".)

Of the surviving candidates:

- Pick **2-4 that will be embedded as bolded sentences** in the synthesis body.
- Pick **the single strongest one as the killer line.** It will appear bolded in the synthesis, in the TL;DR's headline callout, and in the in-session "Killer line:" output.

If no candidate makes it past the test "could a reader have written this by stacking the contributions themselves?" — revise. Cap at 2 attempts. If still nothing lands, the corpus may not have enough structure for a real synthesis yet; surface the situation honestly.

### 5. Framing-axis identification

Re-read the page's `## Framing` section. Identify the **specific axis or edge** the framing names (e.g. "without either over-constraining them or leaving them to drift" — the axis is constraint vs drift). The synthesis must return to this axis at least once and test the corpus against it.

If the framing is too vague to name a specific axis, note this and skip the test; do not invent an axis the framing doesn't support.

### 6. Synthesis draft

Write a 500–800-word synthesis structured with **h3/h4 headings that earn their place in the Obsidian outline view**. Each heading is a claim or a question that's complete on its own — a reader scanning only the outline should know what each section says or asks, without needing the body. Apply the voice rules.

**Heading principle (load-bearing):** headings are claim-shaped or question-shaped, not label-shaped.

- **Label-shaped (bad):** "Distributed authorship", "Constraint, not direction", "Tensions live in the corpus". Each names the *topic* without saying anything about it. The reader has to open the body to learn anything.
- **Claim-shaped (good):** "Distributed authorship of strategy", "When work is cheap, alignment becomes about limiting choice", "The work is unavoidable. The artifacts are not." Each makes a complete point.
- **Question-shaped (good):** "Constraint vs drift: how much is too much?" — invites with a real question the section answers.
- **Length:** 4–11 words. Long enough to land a claim; short enough not to read as a paragraph.
- **Self-contained.** "Top-down plans lose contact" fails because the reader asks "lose contact with what?" "Top-down plans lose contact with the work — faster than admitted" stands alone.
- **TL;DR section names do NOT need to match.** Earlier guidance said headings should mirror TL;DR sections verbatim — that was based on a wrong model of Obsidian outline view. TL;DR section names live inside a callout and don't appear in the outline at all. The synthesis headings are the only navigation surface; optimise them for informativeness, not parity.

**Structural beats and their headings:**

1. **First h3 — the convergence finding.** Heading is the strongest single claim the corpus makes, complete in one sentence. One paragraph: anchor in 2-4 contributions across multiple sources, embed at least one killer-claim sentence (bolded inline). Worked example: `### Top-down plans lose contact with the work — faster than admitted`.

2. **Second h3 — the parent for the structural answers.** Heading names what the section delivers (e.g. `### Three ways out of the cascade`), not just labels it. One short orientation sentence, then nested h4 sub-sections:
   - **`#### <Claim-shaped label>`** — One paragraph per answer. The h4 heading IS the label, said as a small claim (`Distributed authorship of strategy`, not `Distributed authorship`). Do **not** also bold-label the paragraph lead — the h4 does that work.
   - Each h4 paragraph embeds a generative claim where the corpus's implication is sharp (bolded inline).

3. **Third h3 — the framing-axis test.** Heading captures the axis as a question or sharp claim (`Constraint vs drift: how much is too much?`), not just the axis name. One paragraph testing the corpus against the framing's specific edge.

4. **Fourth h3 — the tensions resolution.** Heading captures the meta-claim the tensions resolve into. Worked example: `### The work is unavoidable. The artifacts are not.` (Not `Tensions live in the corpus` — that's label-shaped.) One paragraph naming the disagreements and what the corpus implies if you hold them together.

5. **Fifth h3 — the negative-space close.** Heading captures what the section reveals (`What every contribution takes for granted`), not just announces the section's role (`What the corpus doesn't see` is borderline; the new version is sharper). Body is 2-4 short bullets — frames the corpus is sitting inside but does not notice. NOT a research-question list. Each bullet may start with a bolded inline label (the h3 doesn't replace that — the bullet labels are a separate level).

**Bolded inline content is reserved for the killer-claim sentences inside the prose** (and for the bullet labels in section 5). Do not bold the structural labels inside paragraphs — the h4 headings do that work, and double-labeling reads as noise.

Citation discipline:

- Every claim of substance is anchored to one or more contributions, using the existing block-id syntax: `[[<raw-filename>#^hN|<short label>]]`. The label is a 2–4-word handle for the contribution.
- Cite the contribution, not just the source.
- Two or three contributions can share a sentence: `…the through-line on this question [[a#^h1|label-a]] [[b#^h2|label-b]].`
- Aim for 6–14 citations across the piece.

**Worked rhythm for generative claims.** Bolded inline killer-claim sentences live inside the h3/h4 paragraphs (not at heading level — headings stay plain). A killer-claim can be one short sentence — *"When engineering speed and planning speed run at different rates, both break."* — or it can land as two or three short sentences in a row, where the rhythm carries the claim: *"When the work is cheap, the alignment problem flips. The question stops being how to push effort. It becomes how to limit choice."* The three-sentence variant works when the claim has a "from X to Y" shape; the one-sentence variant works for a single hard observation. Avoid the long comma-spliced sentence — it reads as academic and loses force on a phone.

**Worked rhythm for tensions and the negative-space close.** Short declarative sentences beat one-sentence-with-three-clauses. *"What the corpus suggests, without saying it directly: the work is unavoidable. The artifacts are not."* lands harder than the same idea folded into a single comma-spliced line. Apply the same rhythm to the negative-space bullets — bold label, period, plain elaboration, optional example after a dash.

### 7. Self-critique — the voice gate

Before writing anything to disk, re-read the draft against the rules below. If any rule fails, revise.

**Disqualifying tells:**

- First-person plural ("we can see…", "we find that…"). Cut all of them.
- Self-narration ("this synthesis argues", "the through-line is X"). Replace with the actual claim.
- Hedge stack ("interestingly", "notably", "importantly", "honestly", "actually"). Cut.
- Generic AI-essay register ("In an era of rapid change…", "It is becoming increasingly clear…"). Rewrite with specificity.
- Smoothed contradictions. If two contributions disagree, the synthesis must name the disagreement.
- A claim of substance with no citation. Either anchor or cut.
- Restating the page's framing in the opening paragraph. Start where the synthesis adds.
- Drift into the user's voice ("I'm asking…"). The author is the corpus.
- **Fewer than 2 embedded killer-claim sentences.** If the body has only one bolded generative claim, the synthesis is descriptive, not generative — revise.
- **Negative-space close that lists research questions.** "How does the transition happen?" is research; "every contribution treats X as a given" is negative space. Different output, different shape.
- **Framing axis not tested.** If step 5 named a specific axis and the synthesis does not return to it, revise.
- **Reading-level violation.** Any of the banned vocabulary from the Reading-level section (epistemic, presumes, implicitly maps, unit of analysis, etc.) appears anywhere in the synthesis, TL;DR, or Threads to pull. Cut and replace.
- **TL;DR bullets that read like compressed prose, not briefing items.** Each bullet should be one short complete thought, plain English, with the example/citation in parentheses if needed. Bullets that pack three clauses with semicolons fail this gate.
- **Threads to pull that read as homework, not provocation.** A thread that's a research question with no stake ("how does the transition happen?") fails. A thread should hook with "what if" + a real claim the reader could push back on. If a thread has no stake, either rewrite for stake or move it down to Patterns to look out for.
- **Patterns to look out for that are questions, not noun phrases.** "How does X happen?" and "What does Y look like?" fail this gate. Rewrite as concrete things the scout would notice in the wild — noun phrase + specific shape.
- **Forward-looking material in the TL;DR.** The TL;DR is a summary of what the corpus says. If forward-looking content (provocations, scouting prompts, research questions) appears inside the TL;DR callout, move it to the Threads to pull callout.
- **Synthesis missing h3/h4 headings.** The synthesis must be navigable from Obsidian outline view. A synthesis written as a single block of prose without headings fails this gate.
- **Label-shaped headings.** A heading like `Distributed authorship` or `Tensions live in the corpus` names the topic without saying anything about it. The reader scanning the outline learns nothing. Rewrite as a claim or a question — `Distributed authorship of strategy`, `The work is unavoidable. The artifacts are not.` Each heading must be self-contained (the reader doesn't have to open the body to know what the section says or asks).
- **Headings shorter than 4 words or longer than 11.** Below 4 risks label-shape; above 11 reads as a paragraph instead of a heading.
- **Doubled labels.** If a paragraph under an h4 heading also starts with a bolded inline label repeating the heading text, strip the inline label. Bolded inline content is for killer-claim sentences only.

Cap revision at 2 attempts. If the third pass still has disqualifying tells, surface the draft to the user with a note flagging which gates remained and ask whether to ship as-is, edit together, or abandon.

### 8. Generate the TL;DR brief

The brief is **derived from the synthesis**, not independently generated. Compress the synthesis into a single Obsidian callout, ~200 words, of this shape:

```markdown
> [!summary] TL;DR — YYYY-MM-DD
> *<N contributions · S sources>*
>
> **<The killer line — same sentence as in the synthesis body and the in-session output.>**
>
> **Where the corpus lands**
> - **<Label 1>.** <One short plain-English sentence.> (<one or two example sources/citations>)
> - **<Label 2>.** <One short plain-English sentence.> (<example sources/citations>)
> - (etc — one bullet per labeled answer in the synthesis)
>
> **Tensions live in the corpus**
> - <Source A's position. Source B's position. Two short sentences, often.>
> - <One sentence on what the disagreement implies, if anything.>
>
> **What the corpus doesn't see**
> - <Frame the corpus is inside. Plain-English elaboration. Specific examples after a dash if useful.>
> - (2-3 bullets total — frame-surfacing, mirroring the synthesis's negative-space close)
```

**Worked example** of the bullet shape (from a real run on a question about alignment under high velocity):

- `**Distributed authorship.** Teams write strategy too, not just receive it. (Cutler's fabric, Caroli's layered OKRs, OpenAI's "mini-executives".)`
- `**Artifacts as yardsticks, not announcements.** A document only aligns a team if every later decision gets measured against it. (Chen's Org-Bench: Jeff's PR/FAQ was cited twice in 165 messages — both by Jeff.)`

The bullet shape is **bold label, period. One short plain sentence. Parenthetical with the named sources or one concrete number.** Bullets that pack three clauses with semicolons fail the briefing-style rule.

The TL;DR reuses citations sparingly — only enough for a reader to drill in. The synthesis below it carries the full citation density. The TL;DR does **not** include forward-looking material — that lives in the **Threads to pull** callout (next step).

### 9. Generate the Threads to pull callout

Forward-looking. The job here is to fuel curiosity — the reader should finish this section with their imagination loaded, not a TODO list. Two parts inside one callout: **threads** (horizon-opening "what if" prompts at the top) and **Patterns to look out for** (concrete recognition triggers, sub-section).

Both parts derive from the synthesis's negative-space close, but at different registers:

- **Threads** turn each gap into a provocation that opens a horizon. Voice register: more colloquial than the synthesis. Use "what if", "imagine", "could it be that". Allow speculation. Italicise the surprise. Cocktail-party-worthy — something the reader could daydream on or ask someone about over a drink. Each thread has a **stake** — a thing you could disagree with, build on, or get excited about.
- **Patterns** are concrete reading prompts, the operational side of the same forward-look. Noun phrase + specific shape, not a question. They name what the scout would *notice* if they ran into it.

Callout shape:

```markdown
> [!tip] Threads to pull — YYYY-MM-DD
>
> **<Provocative "what if" hook in bold.>** <2-3 sentences that load the daydream. Reference the corpus where it earns its place. Italicise the surprise.>
>
> **<Second thread.>** <Same shape.>
>
> (3-4 threads is typical. Each thread has a stake.)
>
> **Patterns to look out for**
>
> - <Noun phrase + specific shape.>
> - (2-4 bullets total. Each is concrete enough that the scout would recognize a match in the wild.)
```

**Worked example of threads** (from a real run on a question about alignment under high velocity):

- `**What if the org chart isn't the right unit for alignment anymore?** Half the team is agents now. The whole vocabulary — cascades, fabrics, layered horizons — was built for a chart that's fragmenting.`
- `**When execution is cheap and taste is the moat — whose taste?** Miura-Ko names the inversion but doesn't say what it costs. How does taste stay sharp when the person changes? Can it be inherited, or does each generation have to re-find its own?`

**Worked example of Patterns to look out for** (same run):

- `A worked example of peer-team alignment held without a top-down forcing function.`
- `An org that transitioned out of an annual cascade — the change shape, not just the end-state.`
- `"The technology aligned the team" as a real feature, not speculation — shared context windows, agent observation, automatic claim-tracing.`

**Load-bearing rules:**

- **Threads must have a stake.** A thread that is just a research question ("how does the transition happen?") has no stake. A thread with a stake says "what if X" where X is a real claim the reader could push back on. If a thread reads as homework, it belongs in Patterns or it belongs cut.
- **Patterns must be noun-phrases, not questions.** "How does X happen?" is a question. "An org that transitioned out of X — the change shape, not just the end-state" is a recognition trigger.
- **Each thread maps loosely to a gap from the negative-space close**, but the language is provocative, not diagnostic. The TL;DR's negative-space says *"alignment is treated as a human-only problem"*; the matching thread says *"could the technology itself be doing the alignment work?"* Same gap, different register.
- **Threads come before Patterns.** Daydream first, then ground in concrete recognition. Mood goes from imaginative to operational, not the other way.

### 10. Render the in-session preview

Print, in this order, to the conversation:

1. The TL;DR (full callout).
2. The Threads to pull callout (full).
3. A horizontal rule.
4. The synthesis (full prose).
5. A summary line: `Synthesis: ~<N> words, <M> citations across <S> sources. TL;DR: ~<W> words. Threads to pull: <T> threads + <P> patterns. Will write all three above Notes; prior synthesis (if any) archived to meta/synthesis_history/<slug>/<date>.md.`
6. `Killer line: <the single sentence>`

Wait for the user's go-ahead before step 11.

### 11. Mutate the page and archive prior synthesis

Once approved:

1. **Archive any prior `## Synthesis` body** to `meta/synthesis_history/<slug>/YYYY-MM-DD.md` with frontmatter (`slug`, `archived: YYYY-MM-DD`). Create the directory if absent.
2. **Replace any prior `## TL;DR`, `## Threads to pull`, and `## Synthesis` sections** on the page. New structure: `## Framing` (untouched) → `## TL;DR` (new) → `## Threads to pull` (new) → `## Synthesis` (new) → `## Notes` (untouched).
3. **Bump the page's `updated` frontmatter** to today. Do not touch `contributions`.

### 12. Append to `meta/log.md`

```bash
python3 <path-to-memex>/helpers/log_append.py \
    --log-dir ./meta \
    --op synthesize \
    --subject "<slug>: synthesis (<N> words, <M> citations) + TL;DR + Threads to pull" \
    --body "Synthesized <slug> from <S> source(s) and <C> contribution(s). Killer line: <one-line paraphrase>. <T> threads + <P> patterns. <Optional note: prior synthesis archived to meta/synthesis_history/<slug>/<date>.md.>"
```

See **Helper invocation** for path resolution.

### 13. Final summary

One short message: where the synthesis, TL;DR, and Threads to pull live (page section names), word and citation counts, archive path if applicable. No promotional tail.

## Helper invocation

This skill shells out to `memex/helpers/log_append.py` once, in step 11.

**Always invoke with `python3` explicitly.**

**Resolving the helper path.** This skill is typically installed as a symlink into `~/.claude/skills/inquiry-synthesize/`. Resolve in order:

1. `./memex/helpers/log_append.py` relative to the wiki root (vendored case).
2. Resolve this SKILL.md's real path, walk to the big_questions repo root, then check `~/Development/memex/helpers/log_append.py` (sibling-repo case).
3. If neither resolves, ask the user where the memex harness is installed.

## Failure modes

- **`SCHEMA.md` missing.** Stop and report — same wording as `/inquiry-gap` and `/wiki-ingest`.
- **Target page does not exist or not active.** Stop. Name it; list active pages.
- **Fewer than 3 contributions.** Stop. Suggest pages with >=3 contributions if any exist.
- **No slug supplied, no eligible pages.** Stop. Suggest ingesting more sources first.
- **Killer-claim pass yields nothing past the test after 2 attempts.** The corpus may not have the structure for a generative synthesis yet. Surface this honestly; offer to ship a descriptive synthesis with a flag, or abandon and try later.
- **Self-critique gate fails after 2 revisions.** Surface the draft as in-conversation prose with a note on which gates remained. Offer ship-as-is / edit-together / abandon.
- **Helper script not found.** See helper resolution; ask the user if all options fail.
- **Page has unparseable contributions.** Synthesize against what is parseable; in the in-session summary, list skipped contributions and why.

## Behavioral notes

- **Two outputs, one run.** The TL;DR is derived from the synthesis, not independently generated. They share the killer line. They share the labels. The brief is the compression; the synthesis is the depth.

- **Coining labels is the synthesis happening.** See the voice section. Bold the labels inline; do not invent more than ~4.

- **Always synthesize the whole corpus.** Even when a prior synthesis exists, regenerate from the full set of contributions, not from the prior synthesis plus deltas. The whole-corpus pass catches shifts the new contributions force on earlier convergences.

- **Synthesis is a separate move from ingest.** Ingest stays cheap and fast (one quote, one rationale, append). Synthesis is the periodic let-the-model-think pass. v0.1 is invoked by the user; later revisions may schedule it.

- **Receipts are non-negotiable.** The `## Notes` section is what the synthesis is *of*. The synthesis cites it; the TL;DR points back to it; neither replaces it. A reader who doubts a synthesis claim must be able to land on the verbatim quote in one click.

- **Diff mechanic deferred.** v0.1 generates a fresh synthesis and TL;DR each run. The "what changed since last synthesis" preface — comparing the new synthesis to the archived prior — is the load-bearing feature for the "evolving feature article" frame; it is the next iteration's first job.

- **Epistemic weight is a light-touch awareness, not a taxonomy.** When naming a disagreement, the synthesis may note whether the disagreeing contributions sit at different altitudes (academic / insider / normative / industry war story). Do not bake in a fixed taxonomy; let the model handle case-by-case. Skip if the disagreement is at the same level — the note adds nothing.

- **The user is the editor.** The synthesis and TL;DR are LLM-drafted. Step 9's review gate is where the user accepts, edits, or rejects.
