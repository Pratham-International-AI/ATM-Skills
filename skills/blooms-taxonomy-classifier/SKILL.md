---
name: blooms-taxonomy-classifier
description: Classify assessment/exam questions into a Bloom's Taxonomy cognitive level (Remembering, Understanding, Applying, Analysing, Evaluating, Creating) with a confidence score and reasoning. Handles a single question or an entire question-bank JSON file. Use when asked to tag, classify, audit, or report on the cognitive level of exam/quiz questions.
---

# Bloom's Taxonomy Classifier

You classify assessment questions — individually or in bulk — into one of the six Bloom's Taxonomy levels, following the definitions in `references/blooms-taxonomy.md`. Read that file before classifying anything; it has the level definitions, keyword hints, and the exact output contract. Bloom's Taxonomy is curriculum-independent, so this skill works on questions from any curriculum as-is; if the user's curriculum profile defines a different cognitive framework, say so and classify against Bloom's only if they confirm.

## When to use this skill

- "What Bloom's level is this question?"
- "Tag this question bank with Bloom's levels."
- "Audit this exam paper for cognitive-level balance."

## Inputs

One of:
- **A single question** — the question text, plus optionally: surrounding context/passage, and MCQ option texts.
- **A question-bank file** — a JSON file shaped like `{"questions": [ {...}, {...} ]}`, where each question object has at least a `text` field and optionally `context` / `options`.

## Workflow — single question

1. Assemble the full question as the model will read it:
   - If there's a passage/context, put it first, labeled `Passage/Context:`.
   - Then the question text.
   - Then each MCQ option on its own line, if provided.
2. Classify per `references/blooms-taxonomy.md` — reason about the actual cognitive demand, don't just pattern-match a verb.
3. Return exactly:
   ```json
   {"status": "completed", "blooms_level": "...", "confidence_score": 0.00, "reasoning": "..."}
   ```
   If you genuinely cannot classify it (e.g. the text is empty or nonsensical), return `{"status": "incomplete", "message": "...", "blooms_level": null}` instead of guessing.

## Workflow — question-bank file

1. Read the input JSON file and parse `questions` (an array).
2. For each question:
   - If it already has a truthy `bloom_level` field, **skip it** (count as skipped) — don't overwrite existing tags.
   - Otherwise, classify it using the single-question workflow above.
   - On success, set `question["bloom_level"]` and `question["bloom_confidence"]` (the confidence score) directly on the object. On failure, count it as an error and leave the question untouched.
3. Write the full, updated JSON back out:
   - Default output path: the input path with `_tagged` inserted before the extension (e.g. `bank.json` → `bank_tagged.json`), unless the caller specified an output path.
   - Preserve every other field on each question and the overall file structure — only add `bloom_level` / `bloom_confidence`.
4. Report a summary, not the full tagged content (it can be large):
   ```json
   {"status": "completed", "total_questions": N, "tagged_count": N, "skipped_count": N, "error_count": N, "output_path": "..."}
   ```

## Notes

- Never fabricate a `blooms_level` value outside the six defined labels.
- If asked to also *summarize* the cognitive-level distribution of a paper/bank (e.g. "X% Remembering, Y% Applying..."), do that as a follow-up analysis over the tagged results — it's not part of the core classification contract above.
- If a question's difficulty/marks make an unusual Bloom's level plausible (e.g. a 1-mark question that's genuinely Analysing), trust your reasoning over an assumption that low marks imply low cognitive level.
