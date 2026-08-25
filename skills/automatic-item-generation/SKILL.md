---
name: automatic-item-generation
description: Generate curriculum-aligned assessment items (MCQ, fill-in-the-blank, short answer, long answer) with marking-scheme value points from source chapter material, targeting specific Bloom's Taxonomy levels and difficulty. Curriculum rules come from a user-supplied curriculum profile; a validated CBSE Class 10 (Science/English) example profile ships with the kit. Use when asked to write exam questions, a question bank, or a question paper.
---

# Automatic Item Generation (AIG)

You generate exam-standard assessment items — complete with marking-scheme value points — from
chapter source material, following the conventions of a **curriculum profile** the user
supplies. The skill itself is curriculum-agnostic: universal item-writing craft lives in this
skill's references; everything board- or program-specific (subject rules, mark structures,
terminology, audience) comes from the profile.

## When to use this skill

- "Generate 5 MCQs on [chapter] for Class 10 Science." (CBSE example profile)
- "Make a question bank of short-answer questions from this chapter, targeting Understanding and Applying."
- "Set a Board-standard question paper from this source text, using my curriculum profile."

## The curriculum profile (required)

A curriculum profile is a Markdown document or folder (entry point: `profile.md`) that defines
the curriculum's identity, audience, subjects, difficulty levels, item quality rules, and
marking rubric. Resolve it in this order:

1. A profile path or pasted profile content the user gives you.
2. If the user names **CBSE Class 10** (or gives no curriculum but the CBSE profile is
   available), use the shipped example: look for `curriculum-profiles/cbse-class10/` next to
   the `skills/` folder, inside this skill's folder, or at the project root.
3. Otherwise **stop and ask** for a profile (point them at `curriculum-profiles/TEMPLATE.md`).
   Never substitute your general knowledge of a curriculum for its profile — the profile is
   the contract the output is judged against.

Quality note to keep in mind: the CBSE Class 10 example profile is evaluation-backed; a
user-authored profile carries whatever quality its author put into it. Follow it faithfully
either way, and flag genuine gaps or contradictions in the profile rather than silently
improvising around them.

## Required inputs

Ask for (or infer from context) whatever is missing:

| Parameter | Values |
|---|---|
| `curriculum_profile` | path to (or content of) a curriculum profile — see above |
| `subject` | one of the subjects the profile covers (CBSE example: `science` or `english`) |
| `total_no_of_questions` | integer |
| `question_format` | `mcq_questions` \| `fill_blank_questions` \| `short_answer_questions` \| `long_answer_questions` |
| `marks` | marks per item, from the profile's valid mark values (drives length/depth) |
| `blooms_types_list` | one or more cognitive levels to target (Bloom's six, unless the profile defines another framework) |
| `sources` and/or `chapter_text` | at least one: file path(s) to source material, and/or raw pasted chapter text |
| `language_difficulty` | one of the profile's difficulty levels (CBSE example: `Easy` \| `Medium` \| `Hard`, default `Medium`) |

If neither `sources` nor `chapter_text` is available, stop and ask — do not generate items
from general knowledge instead of the actual chapter; the value points must trace back to the
supplied source.

## Workflow

1. **Resolve and read the curriculum profile.** Read `profile.md` (or the single profile
   file) fully, then every file it links that applies to this request: the matching subject
   rules and the marking-scheme/value-point rubric.

2. **Extract source text.**
   - `.pdf`, `.txt`, `.md`: read directly (most environments can read these natively).
   - `.docx`: if there's no native reader available, extract via a shell fallback, e.g. `textutil -convert txt -stdout file.docx` (macOS) or `python3 -c "import docx; print('\n'.join(p.text for p in docx.Document('file.docx').paragraphs))"` if `python-docx` is installed.
   - Combine all sources plus any raw `chapter_text` into one pool of source material.
   - If nothing usable comes out of extraction, report `status: incomplete` (see `references/output-schemas.md`) rather than inventing content.

3. **Load the skill's core references:**
   - `references/item-writing-craft.md` — always (universal quality rules; profile rules override on conflict).
   - `references/blooms-taxonomy.md` — always, unless the profile defines a different cognitive framework (then use the profile's).
   - `references/output-schemas.md` — the exact JSON shape for the requested `question_format`.

4. **Generate exactly `total_no_of_questions` items**, each:
   - Sourced only from the supplied chapter material — no outside facts, no invented events/characters/experiments not present in the source.
   - Tagged with a `blooms_level` drawn from `blooms_types_list` (distribute across the requested levels if more than one is given, don't dump them all on one level).
   - Following every rule in the profile's subject and format rules **and** the universal craft rules (MCQ option symmetry, fill-blank sentence rules, word limits, etc.).
   - Carrying value points structured per the profile's marking rubric — every item needs them, no exceptions.
   - Unique in intent — no two items in the batch testing the same fact/concept.

5. **Self-check before returning:**
   - Count matches `total_no_of_questions` exactly.
   - Every item has `value_points` and a valid `blooms_level` from the requested set.
   - MCQs: exactly 4 options, correct `answer` index, options are stylistically symmetric (re-read the MCQ rules — this is the most commonly violated rule).
   - Fact-heavy subjects: spot-check every stated fact, formula, and equation for correctness before finalizing.
   - Re-scan the profile's subject rules top to bottom and confirm each rule is honored.
   - Output matches the schema in `references/output-schemas.md` exactly — correct top-level key, no extra/missing fields.

6. **Return the response envelope** from `references/output-schemas.md` — `status`, `message`, `no_questions`, and the single array keyed by `question_format`.

## Common failure modes to avoid

- Generating from **general knowledge of a curriculum** instead of its profile — the profile, not your prior, defines the rules.
- Letting the correct MCQ option "stand out" (longer, more precise, more technical than distractors) — the single most common quality bug; actively check option symmetry.
- Generating a question whose depth doesn't match its marks (e.g. a 5-mark-depth question tagged as 2 marks).
- Forgetting value points on fill-blank or MCQ items because they seem "obvious."
- Blanking only part of a multi-word term in fill-in-the-blank items.
- Pulling in outside facts not present in the supplied source material.
