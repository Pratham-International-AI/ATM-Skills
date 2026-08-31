---
name: blooms-taxonomy-classifier
description: Classify assessment/exam questions into a Bloom's Taxonomy cognitive level (Remembering, Understanding, Applying, Analysing, Evaluating, Creating) with a confidence score and reasoning. Handles a single question or a whole question bank in any format (JSON, CSV, spreadsheet, markdown, or pasted text). Use when asked to tag, classify, audit, or report on the cognitive level of exam/quiz questions.
---

# Bloom's Taxonomy Classifier

You classify assessment questions — individually or in bulk — into one of the six Bloom's Taxonomy levels, following the definitions in `references/blooms-taxonomy.md` and the worked classifications in `references/level-examples.md`. Read both before classifying anything; the first has the level definitions, keyword hints, and the output contract, the second anchors the judgment calls. Bloom's Taxonomy is curriculum-independent, so this skill works on questions from any curriculum as-is; if the user's curriculum profile defines a different cognitive framework, say so and classify against Bloom's only if they confirm.

**Calibration:** if the user supplies their own per-level example questions (e.g. from their curriculum profile or question bank), those override `references/level-examples.md` — match their conventions, not the defaults.

## When to use this skill

- "What Bloom's level is this question?"
- "Tag this question bank with Bloom's levels."
- "Add a Bloom's level column to this spreadsheet of questions."
- "Audit this exam paper for cognitive-level balance."

## Inputs

Questions in whatever form the user has them:

- **A single question** — the question text, plus optionally: surrounding context/passage, and MCQ option texts.
- **A question bank in any format** — JSON (e.g. `{"questions": [...]}`), CSV or a spreadsheet with a question column, a markdown/Word document, or questions pasted straight into the conversation. Don't ask the user to convert their file; work with what they have.

## Workflow — single question

1. Assemble the full question as the model will read it:
   - If there's a passage/context, put it first, labeled `Passage/Context:`.
   - Then the question text.
   - Then each MCQ option on its own line, if provided.
2. Classify per `references/blooms-taxonomy.md` — reason about the actual cognitive demand, don't just pattern-match a verb.
3. Report the level, confidence score, and one-line reasoning. When the caller is a pipeline (or asks for JSON), use exactly:
   ```json
   {"status": "completed", "blooms_level": "...", "confidence_score": 0.00, "reasoning": "..."}
   ```
   If you genuinely cannot classify it (e.g. the text is empty or nonsensical), say so (in JSON mode: `{"status": "incomplete", "message": "...", "blooms_level": null}`) instead of guessing.

## Workflow — question bank (any file format)

1. Read the input and locate the questions (a `questions` array in JSON, the question column in CSV/spreadsheets, numbered items in a document).
2. For each question:
   - If it already carries a truthy level tag (`bloom_level` field, a filled Bloom's column, etc.), **skip it** (count as skipped) — don't overwrite existing tags.
   - Otherwise, classify it using the single-question workflow above.
   - On failure, count it as an error and leave that question untouched.
3. Write the results back **in the same format the input came in**, preserving every other field, column, row order, and piece of content — only add the level and confidence:
   - JSON: set `bloom_level` and `bloom_confidence` on each question object; default output path inserts `_tagged` before the extension (`bank.json` → `bank_tagged.json`) unless the caller names one.
   - CSV / spreadsheet: add `bloom_level` and `bloom_confidence` columns (same `_tagged` naming default).
   - Markdown/Word/pasted lists: return the same document with the level noted per question, or a compact table if in-place editing isn't practical.
4. Report a summary, not the full tagged content (it can be large): totals for tagged, skipped, and errored questions, plus the output path. In JSON mode:
   ```json
   {"status": "completed", "total_questions": N, "tagged_count": N, "skipped_count": N, "error_count": N, "output_path": "..."}
   ```

## Notes

- Never fabricate a `blooms_level` value outside the six defined labels.
- If asked to also *summarize* the cognitive-level distribution of a paper/bank (e.g. "X% Remembering, Y% Applying..."), do that as a follow-up analysis over the tagged results — it's not part of the core classification contract above.
- If a question's difficulty/marks make an unusual Bloom's level plausible (e.g. a 1-mark question that's genuinely Analysing), trust your reasoning over an assumption that low marks imply low cognitive level.
