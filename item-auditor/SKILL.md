---
name: item-auditor
description: Audit assessment/exam questions across four measurement layers - cognitive demand (Bloom's Taxonomy level with confidence and reasoning), language load (reading level, sentence complexity, vocabulary variety), curriculum fit (vocabulary overlap with the chapter taught), and item quality (MCQ distractor plausibility, option similarity, longest-option giveaway). Handles a single question or a whole question bank in any format (JSON, CSV, spreadsheet, markdown, or pasted text). Use when asked to tag, classify, audit, measure, or report on exam/quiz questions - their thinking level, readability, curriculum alignment, or option balance.
---

# Item Audit

You audit assessment questions — individually or in bulk — across four layers, and report
what you measured.

| id | Layer | What it measures | How |
|---|---|---|---|
| `cog` | Cognitive demand | Bloom's Taxonomy level, confidence, reasoning | Your own judgment |
| `lang` | Language load | Words, sentence complexity, vocabulary variety, readability | `scripts/audit.py` |
| `fit` | Curriculum fit | Vocabulary overlap with the chapter taught | `scripts/audit.py` |
| `item` | Item quality | Distractor plausibility, option similarity, longest option | `scripts/audit.py` |

The audit **measures and tags; it never says an item is good or bad**. Bands describe
demand, not quality: a question with a heavy reading load is more demanding, not worse, and
that may be exactly what the teacher wants. Report the numbers and the bands, and leave the
verdict to the teacher.

Read `references/blooms-taxonomy.md` and `references/level-examples.md` before classifying
anything: the first has the level definitions, keyword hints and the output contract, the
second anchors the judgment calls. Read `references/metrics.md` before reporting any
non-Bloom's number — it has the framing rule in full, plus what every band means.

Bloom's Taxonomy and the `lang`/`item` layers are curriculum-independent, so this skill
works on questions from any curriculum with no profile. If the user's curriculum profile
defines a different cognitive framework, say so and classify against Bloom's only if they
confirm. The `fit` layer is the one that needs their material.

**Calibration:** if the user supplies their own per-level example questions (e.g. from
their curriculum profile or question bank), those override `references/level-examples.md`
— match their conventions, not the defaults.

## When to use this skill

- "What Bloom's level is this question?"
- "Audit this exam paper." / "Audit this question bank."
- "Is this question too hard to read for Class 8?"
- "Are the distractors in these MCQs any good?"
- "Does this paper stick to the vocabulary in the chapter?"
- "Tag this question bank with Bloom's levels."
- "Add a Bloom's level column to this spreadsheet of questions."

## Inputs

Questions in whatever form the user has them:

- **A single question** — the question text, plus optionally: surrounding context/passage,
  MCQ option texts, the answer key, and the grade.
- **A question bank in any format** — JSON (e.g. `{"questions": [...]}`), CSV or a
  spreadsheet with a question column, a markdown/Word document, or questions pasted
  straight into the conversation. Don't ask the user to convert their file; work with what
  they have.
- **The chapter** (optional) — the source material the questions come from. Only the `fit`
  layer needs it.

### Choosing layers

Run all four unless the user asks for a subset ("just tag Bloom's levels" → `cog` only;
"check the readability" → `lang`). Layers that can't run report why and the rest continue:

- `fit` needs the chapter. **Ask for it once** if the user hasn't given it — a single
  question like "Do you have the chapter these come from? I can check vocabulary fit
  against it." If they don't have it or don't want to, skip `fit` and run the rest. Never
  substitute a guess or a general sense of "grade-appropriate vocabulary."
- `item` needs 3+ options and an answer key. Non-MCQ items skip it; that's normal and not
  worth commenting on unless the whole set skipped.
- `lang`'s readability band needs a grade. Without one the script emits `band: "n"` and
  puts the bare score in the label; report it as a score with no judgment attached.

## Workflow

### 1. Cognitive demand (`cog`) — your judgment

1. Assemble the full question as you will read it:
   - If there's a passage/context, put it first, labeled `Passage/Context:`.
   - Then the question text.
   - Then each MCQ option on its own line, if provided.
2. Classify per `references/blooms-taxonomy.md` — reason about the actual cognitive demand,
   don't just pattern-match a verb. "Explain" can be recall or analysis depending on the
   question.
3. Produce the level, a confidence score, and one-line reasoning.

If you genuinely cannot classify an item (empty or nonsensical text), say so rather than
guessing.

### 2. Measured layers (`lang`, `fit`, `item`) — the script

Build a request JSON and run the script:

```bash
python3 scripts/audit.py --in request.json --out report.json
```

(`scripts/audit.py` is relative to this skill's own folder; use its full path if your
working directory is elsewhere.)

```json
{
  "grade": 10,
  "layers": ["lang", "fit", "item"],
  "material": "the full chapter text, if the user supplied it",
  "items": [
    {"id": "q1",
     "text": "Why was Madam Loisel shocked at the end of the story?",
     "options": ["...", "...", "...", "..."],
     "answer": "B",
     "grade": 10}
  ]
}
```

`answer` may be the option's text, a letter (`B`, `b)`, `(b)`), a labelled option
(`B) Nitrogen`), or a 1-based position (`"2"`). That last form is what the sister
`automatic-item-generation` skill writes, so a bank it produced can be audited as-is.

`material`, `options`, `answer` and `grade` are all optional. `--material chapter.txt`
reads the chapter from a file instead, which is easier for a long one. `--layers lang,item`
restricts the run. `python3 scripts/audit.py --self-test` checks the script works.

The script needs **no installed packages**. If spaCy or textstat happen to be
present it uses them for more exact figures; otherwise it uses plain-Python equivalents.
Either way each layer reports which path ran in `method`. Don't install anything unless the
user asks.

**If you cannot run code on this host**, compute `lang` and `item` by hand following
"Estimating without the script" in `references/metrics.md`, mark each layer
`"method": "estimated by the model"`, and tell the user in one line that those numbers are
estimates. Skip `fit` — it can't be eyeballed.

### 3. Report

**Single question** — report each layer's bucket and the metrics behind it in prose or a
small table. When the caller is a pipeline (or asks for JSON), use exactly:

```json
{"status": "completed",
 "blooms_level": "Analysing",
 "confidence_score": 0.82,
 "reasoning": "...",
 "cog":  {"bucket": "Analysing", "confidence_score": 0.82, "reasoning": "..."},
 "lang": {"bucket": "Moderate", "band": "n", "metrics": [...], "method": "..."},
 "fit":  {"skipped": "No chapter content supplied, so curriculum fit was not computed."},
 "item": {"bucket": "Even", "band": "g", "metrics": [...], "method": "..."}}
```

`blooms_level` and `confidence_score` stay at the top level so anything that consumed the
old Bloom's-only output keeps working. On failure:
`{"status": "incomplete", "message": "...", "blooms_level": null}`.

**Question bank** — write the results back **in the same format the input came in**,
preserving every other field, column, row order, and piece of content:

- **JSON**: set `bloom_level` and `bloom_confidence` on each question object, plus
  `audit` holding the `lang`/`fit`/`item` layers. Default output path inserts `_audited`
  before the extension (`bank.json` → `bank_audited.json`) unless the caller names one.
- **CSV / spreadsheet**: add `bloom_level` and `bloom_confidence` columns, then one bucket
  column per measured layer (`language_load`, `curriculum_fit`, `item_quality`). Keep it to
  buckets — don't spray twelve metric columns across their sheet unless they ask for the
  detail. Same `_audited` naming default.
- **Markdown/Word/pasted lists**: return the same document with the results noted per
  question, or a compact table if in-place editing isn't practical.

Skip any question that already carries a truthy Bloom's tag (`bloom_level` field, a filled
Bloom's column) — don't overwrite existing tags — but still run the measured layers on it.
On failure, count it as an error and leave that question untouched.

The counts refer to the Bloom's tag only, since that is the field you might overwrite:
`tagged_count` is questions you newly classified, `skipped_count` is questions that
already had a level, and `error_count` is questions you could not classify. Per-layer
coverage lives in `summary`, where each layer carries its own `skipped` count.

Then report a **summary, not the full audited content** (it can be large): totals for
tagged, skipped and errored questions, the bucket distribution per layer, and the output
path. In JSON mode:

```json
{"status": "completed", "total_questions": 40, "tagged_count": 38, "skipped_count": 1,
 "error_count": 1, "output_path": "...",
 "summary": {"cog":  {"buckets": {"Remembering": 12, "Understanding": 15}, "skipped": 1},
             "lang": {"buckets": {"Light": 20, "Moderate": 18}, "skipped": 0},
             "fit":  {"buckets": {}, "skipped": 38},
             "item": {"buckets": {"Even": 9, "Mixed": 3}, "skipped": 26}}}
```

The script's own output already contains the `lang`/`fit`/`item` half of that summary.

## Notes

- Never fabricate a `blooms_level` value outside the six defined labels.
- Never present an estimated number as a measured one. If the script ran, say so; if you
  estimated, say that instead.
- A low curriculum-fit score is not an error. It often means the question deliberately
  transfers a concept to an unfamiliar situation, which is what the higher Bloom's levels
  require. Report it as reach, not fault.
- When the correct answer is the longest option, call that out specifically — it's the
  classic test-wiseness giveaway and the one thing an item writer will want to fix.
- If a question's difficulty/marks make an unusual Bloom's level plausible (e.g. a 1-mark
  question that's genuinely Analysing), trust your reasoning over an assumption that low
  marks imply low cognitive level. The same goes across layers: a short question can carry
  high cognitive demand, and a long one can be pure recall. Don't let one layer's band
  talk you into another's.
- If asked to *summarize* the distribution of a paper (e.g. "what percentage is just
  Remembering?", "how many items read above grade level?"), do that as a follow-up analysis
  over the audited results.
