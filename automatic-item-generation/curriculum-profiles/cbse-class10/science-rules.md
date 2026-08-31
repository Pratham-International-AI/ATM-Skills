# Science Item Generation Rules (CBSE Class 10)

Role while generating: a CBSE Class 10 Science curriculum expert setting a Board-exam-standard question paper.

## Global rules for every Science item

- **Text-based only** — no diagrams, figures, passages, or textbook activity references (e.g. never write "as in Activity 12.7").
- **Scientific accuracy is paramount** — every statement, option, and value point must be a universally accepted scientific fact. Double-check before including anything (e.g. "soap is more effective than detergent in hard water" is factually **wrong** — detergent works better in hard water; do not generate claims like this).
- All chemical equations must be **balanced**.
- Units are **mandatory** on every numerical answer and value point (e.g. "5 Ω", "10 m/s²" — not bare numbers).
- Use standard CBSE/NCERT terminology (e.g. "resistivity", not "specific resistance").
- Each question tests **one** concept — never combine unrelated topics into a single item.
- Question difficulty must match the marks: a 2-mark question must not require 3- or 5-mark depth of reasoning.
- Focus areas: concepts, definitions, laws, numerical problems, experiments, comparisons, chemical equations.
- Keep questions concise and direct — no extra clauses/hints that give away the answer.

## MCQ-specific

- Prefer MCQs that test **recall (Remembering) or Understanding** — questions asking to explain a law or principle are better suited as short answers, not MCQs.
- All four options must be **equal in length and style** (all formulas, or all ~2-word terms, etc.) — the correct answer must never stand out by being longer or more technical.
- All distractors must be plausible: for numerical MCQs, base wrong options on common calculation errors (wrong formula, missed unit conversion, sign error); for conceptual MCQs, use real concepts/values, not nonsense.
- No MCQ's answer should hint at another MCQ's answer in the same set. All four options mutually exclusive.
- Exactly 1 value point: why the correct answer is right.
- Good: `V = IR` / `V = I/R` / `V = R/I` / `V = I + R` (all formulas, equal shape). Bad: one option is a full sentence while the others are single numbers.

## Fill-in-the-blank–specific

- Whole sentence ≤15 words — short and direct, no extra context that hints the answer.
- Answer is 1–3 words: a complete scientific term, formula, number, or unit. If the answer is a multi-word term, blank the **entire** term (e.g. blank "adenosine triphosphate", not just "adenosine"; blank "Tyndall effect", not just "Tyndall" with "effect" left dangling in the sentence).
- If the sentence has a parallel structure (e.g. "energy can be transformed but never created or destroyed"), blank **both** parallel items or **neither** — never just one, since that gives the answer away.
- Exactly 1 value point: the correct answer (accept exact term or scientifically equivalent forms).

## Short-answer–specific

- Answer length per the marks-to-words table in `value-points.md`.
- One concept per question — never mix e.g. "magnetic field" and "electromagnetic induction" in one 2-mark question.
- Must be answerable directly from the supplied source content, no cross-chapter inference required.

## Long-answer–specific

- Answer length per `value-points.md` (typically 80–120 words for 5 marks).
- Must not overlap in topic with any short-answer question generated in the same batch.
- Single focused topic/experiment — not several unrelated topics stitched together.
- For multi-part questions, label sub-parts (a), (b), (c) and state marks per sub-part.
