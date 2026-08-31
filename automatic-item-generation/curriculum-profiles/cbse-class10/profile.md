# Curriculum Profile: CBSE Class 10 (India)

> **This is the worked example profile for this kit.** It encodes the CBSE Class 10 Board
> examination standard for Science and English Literature, and it is the configuration this
> system's item-generation quality has been evaluated against. If you are building a profile
> for a different curriculum, copy `../TEMPLATE.md` and use this folder as a reference for
> the level of detail that works.

## 1. Curriculum identity

- **Curriculum / board:** CBSE (Central Board of Secondary Education, India), Class 10
- **Exam standard:** items must match official CBSE Class 10 Board examination style and
  official marking-scheme conventions. The generating role is a CBSE curriculum expert
  setting a Board question paper.

## 2. Audience

- Students aged **14–16**, largely from small-town India, preparing for the Class 10 Board exam.
- **Non-native English speakers** with elementary-to-intermediate English comprehension.
- Implications: keep question and value-point language simple and student-friendly.

## 3. Subjects covered

| Subject | In scope | Out of scope | Rules file |
|---|---|---|---|
| `science` | NCERT Class 10 Science chapter content: concepts, definitions, laws, numerical problems, experiments, comparisons, chemical equations | Diagram/figure-based questions, textbook activity references (e.g. "Activity 12.7") | [`science-rules.md`](science-rules.md) |
| `english` | Literature from prescribed textbooks and supplementary readers only | Grammar, unseen reading comprehension, unseen passages | [`english-rules.md`](english-rules.md) |

## 4. Cognitive framework

**Bloom's Taxonomy (default)** — the six levels defined in the skills' core reference
(Remembering, Understanding, Applying, Analysing, Evaluating, Creating). No overrides.

## 5. Language difficulty levels

| Level | Sentence shape |
|---|---|
| **Easy** | ≤10 words, everyday vocabulary, simple grammar |
| **Medium** | 10–15 words, one clause per sentence, may include one uncommon word |
| **Hard** | 12–20 words, compound sentences, specific/technical vocabulary |

Default to **Medium** when the requester doesn't specify.

## 6. Question formats and marks

- **Formats:** MCQ (exactly 4 options), fill-in-the-blank, short answer, long answer.
- **Valid marks per item:** 1, 2, 3, 5, 6.
- **General conventions (all subjects):**
  - Items are **text-only** — no diagram-based, figure-based, passage-based, or case-based
    questions.
  - Every item in a batch must be **unique in intent** — no two items testing the same
    fact or concept.
  - Long-answer items must not overlap in topic with short-answer items in the same set.

## 7. Item quality rubric

Per-subject and per-format rules live in [`science-rules.md`](science-rules.md) and
[`english-rules.md`](english-rules.md). These apply **on top of** the universal craft rules
in the item-generation skill.

## 8. Marking scheme rubric (value points)

Value-point counts, structure, mark splits, and answer word limits by subject and marks:
[`value-points.md`](value-points.md).

## 9. Worked examples

Model questions for each format, with value points and notes on why each one passes this
profile's rules: [`worked-examples.md`](worked-examples.md).
