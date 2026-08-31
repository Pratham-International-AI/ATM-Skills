# Curriculum Profile — Template

> **What this is:** a curriculum profile is the document (or small folder of documents) that
> teaches the AI *your* curriculum's rules before it generates anything. The skills
> in this kit are curriculum-agnostic — they know how to write good exam items in general,
> but everything specific to *your* board, exam, or program comes from this profile.
>
> **How to use it:** copy this file (or the whole structure of the `cbse-class10/` example
> folder next to it), fill in every section below, and save it somewhere the AI can read.
> When you ask the AI to generate questions, point it at your profile.
>
> If a section doesn't apply to you, write "Not applicable" rather than deleting it — an
> explicit "no rule here" prevents the AI from inventing one.

---

## 1. Curriculum identity

*Who sets the standard your questions should match?*

- **Curriculum / board / program name:**
- **Grade level or stage:**
- **Exam or assessment standard the items should mirror:** (e.g. "final board examination", "end-of-unit classroom quiz", "professional certification exam")

## 2. Audience

*Who will answer these questions? This shapes vocabulary, sentence length, and how difficulty is calibrated.*

- **Age range:**
- **Language of assessment, and whether students are native speakers:**
- **Reading/comprehension level:**
- **Any context that should influence tone or difficulty:** (e.g. first-generation learners, exam anxiety considerations, accessibility needs)

## 3. Subjects covered

*List each subject this profile supports. For each, say what content is in scope and what is
explicitly out of scope.*

| Subject | In scope | Out of scope |
|---|---|---|
| *(e.g. science)* | *(e.g. NCERT Class 10 chapters)* | *(e.g. diagram-based questions)* |

For each subject, write (or link to) a **subject rules** document covering the non-obvious
conventions: required terminology, forbidden question styles, formatting rules. See
`cbse-class10/science-rules.md` and `cbse-class10/english-rules.md` for worked examples of
the level of detail that works well.

## 4. Cognitive framework

*How do you label the "thinking level" of a question?*

- **Framework:** (default: Bloom's Taxonomy — six levels: Remembering, Understanding, Applying, Analysing, Evaluating, Creating. The skills ship with full Bloom's definitions, so if you use Bloom's you can just write "Bloom's Taxonomy (default)". If you use something else — e.g. Depth of Knowledge — define every level here with a one-line description and typical question keywords.)

## 5. Language difficulty levels

*Define what Easy / Medium / Hard (or your own labels) mean for question wording.*

| Level | Sentence shape |
|---|---|
| Easy | *(e.g. ≤10 words, everyday vocabulary)* |
| Medium | |
| Hard | |

## 6. Question formats and marks

*Which question formats do you use, and what mark values are valid?*

- **Formats:** (e.g. MCQ, fill-in-the-blank, short answer, long answer)
- **Valid marks per item:** (e.g. 1, 2, 3, 5)
- **Expected answer length by marks:**

| Marks | Expected answer length |
|---|---|
| | |

## 7. Item quality rubric

*The rules a question must satisfy to be acceptable — per format and per subject.*

The skills already enforce universal craft rules (MCQ options must not give away the answer,
fill-in-the-blank must blank whole terms, one concept per question, difficulty must match
marks — see `automatic-item-generation/references/item-writing-craft.md`). Here, add
only what is **specific to your curriculum**, e.g.:

- Required or forbidden question styles:
- Terminology conventions:
- Formatting conventions:

## 8. Marking scheme rubric (value points)

*Every generated question comes with "value points" — the marking-scheme bullets an examiner
ticks off. Define how many value points each question needs and how they're structured.*

| Marks | Number of value points | Structure / mark split |
|---|---|---|
| | | |

- **Value point style rules:** (max words per point, whether formulas/units are required, whether alternative phrasings are allowed, any closing catch-all phrase like "(Any other relevant point to be accepted)")
- **Mark splits, if any:** (e.g. content vs. expression vs. accuracy marks, by mark value — these determine how value points are annotated so an examiner can mark against them)

## 9. Worked examples *(optional, strongly recommended)*

*Real examples anchor the AI better than rules alone.*

- **Model questions:** 3–6 questions (with their value points) that your examiners would
  consider excellent, covering your main formats and subjects. For each, add a line on why
  it's good. See `cbse-class10/worked-examples.md` for the level of detail that works.
- **Cognitive-level examples:** 1–2 example questions per level of your cognitive
  framework, each with its correct label and a one-line reason. Add these especially if
  default Bloom's classifications don't match your curriculum's conventions.
