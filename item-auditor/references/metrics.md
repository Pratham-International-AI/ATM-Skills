# Audit metrics reference

This file defines every metric the audit reports outside Bloom's Taxonomy: what it
measures, how it is computed, and the bands it is read against. (For the cognitive-demand
layer see `blooms-taxonomy.md` and `level-examples.md`.)

`scripts/audit.py` implements all of this. Read this file when you need to explain a
number to a user, or when you cannot run the script and have to estimate the metrics
yourself — see **Estimating without the script** at the end.

## The framing rule

**The audit measures and tags. It never says an item is good or bad.** Bands describe
*demand*, not quality: a "Heavy read" question is not a worse question, it is a more
demanding one, which may be exactly right for the class. Report the number and the band;
leave the verdict to the teacher.

Band codes, used by every metric:

| Code | Meaning |
|---|---|
| `g` | Lower demand, or inside the typical range |
| `n` | Middle of the range |
| `a` | Higher demand, or outside the typical range |

Each layer also rolls its metrics up into one **bucket** — a single word for the layer, so
a report is scannable.

## Layer `lang` — Language load

How hard the item is to *read*, independent of how hard it is to *think about*. Runs on
every item. Computed over the question text (not the passage).

| Metric | What it is | Bands |
|---|---|---|
| **Reading load** | Word count of the question | ≤10 Light read `g` · ≤29 Moderate read `n` · >29 Heavy read `a` |
| **Sentence complexity** | The most complex sentence in the item, 0–3 | 0 Simple `g` · 1 Compound `n` · 2 Complex `a` · 3 Compound-complex `a` |
| **Vocabulary variety** | Type-Token Ratio: distinct words ÷ total words | ≤0.82 Repeated wording `g` · ≤0.95 Some variety `n` · >0.95 Highly varied `a` |
| **Readability** | Flesch-Kincaid grade level | Within `grade + 1.5` → Around grade level `g` · above → Above grade level `a` |

TTR and readability each need at least **8 words** to mean anything; below that they
report "Too short to judge" and are left out of the bucket. Flesch-Kincaid in particular
swings wildly on a fragment ("Define power." scores grade 14.7 off two words), so a
confident-looking number there would be worse than none. The web tool this was ported
from guards TTR but not readability; this is a third deliberate difference from it.

Sentence complexity is `(1 if more than one independent clause) + (2 if any subordinate
clause)`, so: 0 simple, 1 compound, 2 complex, 3 compound-complex.

A subordinator that *opens a question* doesn't count: in "Which of the following is a
noble gas?" or "When did India gain independence?", the word is the interrogative, not a
subordinate clause. The same word later in the sentence ("the gas **which** turns lime
water milky") does count. Without this rule the plain-Python path marked most ordinary
exam stems Complex. Note this is a deliberate departure from the web tool's version,
which relies on a real parser instead.

**Bucket:** count how many of the four metrics land in band `a`. 0 → **Light** `g`,
1–2 → **Moderate** `n`, 3–4 → **Heavy** `a`. Equal weights.

Readability only gets a real band when a grade is known. Without one the script still
emits `"band": "n"` and puts the bare score in the label (`"Grade 4.8"`); read that as
"no judgment made", not as a middling result.

## Layer `fit` — Curriculum fit

Whether the item's vocabulary is drawn from what the students have actually been taught.

| Metric | What it is | Bands |
|---|---|---|
| **Chapter vocabulary match** | Share of the item's content words that appear in the chapter supplied | ≤0.75 Low match `a` · ≤0.90 Moderate match `n` · >0.90 Strong match `g` |

Content words means: alphabetic words, stopwords removed, reduced to their dictionary
form. So "borrowed" matches a chapter that says "borrow".

**Bucket:** Strong match → **In chapter** `g` · Moderate → **Mixed** `n` · Low → **Beyond
chapter** `a`.

These labels say "chapter", not "grade", on purpose. The web tool this was ported from
could compare against a grade-wide textbook corpus; the skill only ever sees the one
chapter the user hands it, so it can report what the chapter covers and nothing wider.

**This layer needs a chapter.** With no chapter supplied there is nothing meaningful to
compare against, so the layer does not run and reports why. Ask the user for the chapter
once; if they don't have it or don't want to supply it, skip `fit` and run the rest — do
not substitute a guess.

A low match is not a fault. It may mean the question deliberately transfers a concept to
an unfamiliar situation, which is what the higher Bloom's levels require. Report it as
reach, not error.

## Layer `item` — Item quality

Structural balance of the options. **MCQ only** — needs 3+ options *and* an answer key.
Without either, the layer reports why it was skipped.

| Metric | What it is | Bands |
|---|---|---|
| **Distractor plausibility** | Mean similarity of each distractor to the correct answer | ≤0.18 Distractors far from answer `n` · ≤0.50 Balanced distance `g` · >0.50 Distractors close to answer `a` |
| **Option similarity** | Mean similarity across every pair of options | ≤0.25 Distinct options `g` · ≤0.64 Moderately similar `n` · >0.64 Very similar `a` |
| **Longest option** | Whether one option is conspicuously longer | Longest is ≥1.5× the mean of the others **and** at least 2 words longer → One option longer `a`; otherwise Even option lengths `g` |

Note the plausibility scale is not monotonic: the *middle* is the healthy zone. Distractors
far from the answer make the item too easy to eliminate; distractors very close to the
answer risk more than one defensible answer.

**Bucket:** count how many of the three land in band `a`. 0 → **Even** `g` · 1 → **Mixed**
`n` · 2–3 → **Uneven** `a`.

When the longest option *is* the correct answer, say so explicitly — that is the classic
test-wiseness giveaway, and it's the case worth flagging to an item writer.

## How the numbers are computed

The script prefers precise NLP libraries and falls back to plain Python when they aren't
installed. Every layer reports which path ran in its `method` field — pass that on when a
user asks how a number was produced.

| Metric | Preferred | Fallback |
|---|---|---|
| Word count, TTR | Regex word tokens | Same |
| Readability | `textstat` | Flesch-Kincaid formula with a vowel-group syllable count |
| Sentence complexity | spaCy dependency parse | Subordinator / coordinator regexes |
| Content words | spaCy lemmas | Lowercased tokens minus a stopword list |
| Similarity | spaCy word vectors (`en_core_web_md`) | Jaccard over content words, then character trigrams |

The fallbacks need nothing installed, so the script always runs. The optional upgrades are
`pip install spacy textstat && python -m spacy download en_core_web_md` — only worth it if
someone wants the more exact similarity and complexity figures.

## Limits worth knowing

- **One chapter at a time.** Curriculum fit compares against the first 150,000 characters
  of the material (about 25,000 words). Past that the text is ignored and the match is
  understated, so the layer sets `"truncated": true` and says so in the metric's note.
- **English only.** The tokenizer matches ASCII letters, so accented and non-Latin scripts
  are split or dropped.
- **Options need words.** Item quality is skipped when every option is numbers or symbols
  (`12 / 24 / 36 / 48`). Similarity is measured over words, so a purely numeric set would
  otherwise report "distractors far from answer" on every maths MCQ.
- **Answer keys.** The layer accepts the option's text, a letter (`B`, `b)`, `(b)`), a
  labelled option (`B) Nitrogen`), or a 1-based position (`"2"` — which is what the
  generator skill emits). Anything else is reported as a key that didn't match, which is
  a different thing from no key at all.

## Estimating without the script

On a host with no code execution, you can still report the `lang` and `item` layers by
hand. Do it, and be honest about it: set `"method": "estimated by the model"` on each layer
and add one line to the report saying the numbers are estimates.

- **Reading load** — count the words. This is the one you can do exactly; do it exactly.
- **Sentence complexity** — apply the 0–3 rule above by reading the sentence.
- **Vocabulary variety** — distinct words ÷ total words. Exact if you count carefully.
- **Readability** — estimate, and say so. Don't present a decimal like "Grade 10.7" that
  implies a precision you don't have; say "around grade 10".
- **Distractor plausibility / option similarity** — judge on meaning: are the distractors
  in the same conceptual family as the answer, or obviously off-topic? Report the band
  label only. Set `value` to `null` rather than inventing a decimal that looks measured,
  and still apply the bucket roll-up from the labels.
- **Longest option** — count words per option and apply the 1.5× rule.

Do **not** estimate `fit`. It depends on matching against the whole chapter's vocabulary,
which is not something to eyeball. Skip the layer and say why.
