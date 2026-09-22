#!/usr/bin/env python3
"""
Item Audit - deterministic measurement layers for assessment items.

This script MEASURES and TAGS; it never says an item is good or bad. Each layer
returns numbers plus a plain-description band, and one bucket tag per layer so a
report is readable at a glance.

Layers computed here (the cognitive-demand layer is the model's own judgment and
is not part of this script):

  lang  Language load     word count, sentence complexity, type-token ratio, Flesch-Kincaid
  fit   Curriculum fit    share of the item's content words found in the chapter supplied
  item  Item quality      distractor plausibility, option similarity, longest option (MCQ only)

No third-party packages are required: every metric has a plain-Python
implementation. If spaCy (with en_core_web_md) or textstat happen to be installed
the script uses them instead, and every result carries `method` so the report can
say how it was computed. English text only: the tokenizer is ASCII-alphabetic.

Two deliberate differences from verify.py, the web backend this was ported from.
Do not "fix" them back to match it:

  - Sentence complexity ignores a subordinator that OPENS a question, so an
    ordinary stem ("Which of the following is a noble gas?") reads Simple rather
    than Complex. verify.py leans on spaCy's parser; here the regex fallback is
    the default path, and unpatched it marked most exam stems Complex.
  - The curriculum-fit labels say "chapter", not "grade". verify.py could resolve
    a server-side grade corpus; this script only ever sees the chapter the user
    supplied, so nothing here knows the grade.

Usage
    python3 audit.py --in request.json --out report.json
    cat request.json | python3 audit.py
    python3 audit.py --self-test

Request JSON
    {
      "grade": 10,                       # optional; enables the readability band
      "layers": ["lang", "fit", "item"], # optional; default all three
      "material": "full chapter text",   # optional; required by the `fit` layer
      "items": [
        {"id": "q1",
         "text": "Why did the lady in red outsmart Horace Danby?",
         "options": ["...", "..."],      # optional; MCQ only
         "answer": "B",                  # option text, a letter, or a 1-based position
         "grade": 10}                    # optional per-item override
      ]
    }

Report JSON
    {"results": [{"id": ..., "lang": {...}, "fit": {...}, "item": {...}}],
     "summary": {...}, "capabilities": {...}}

Each layer is either {"bucket", "band", "metrics": [...], "method"} or
{"skipped": "plain-language reason"}.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from functools import lru_cache
from itertools import combinations
from typing import Optional

LAYERS = [
    {"id": "lang", "name": "Language load",
     "measure": "Words - sentence - TTR - Flesch-Kincaid", "needs": None},
    {"id": "fit", "name": "Curriculum fit",
     "measure": "Chapter-vocabulary overlap", "needs": "the chapter you teach from"},
    {"id": "item", "name": "Item quality",
     "measure": "Distractor plausibility", "needs": "MCQ with answer key"},
]
LAYER_IDS = [l["id"] for l in LAYERS]

# Band colour codes. They describe demand, not quality:
#   g  lower demand / within typical range
#   n  middle of the range
#   a  higher demand / outside the typical range
G, N, A = "g", "n", "a"

# Every threshold lives here so they can be rechecked in one place.
BANDS = {
    # Language load
    "reading_load": [(10, "Light read", G), (29, "Moderate read", N), (math.inf, "Heavy read", A)],
    "complexity": ["Simple", "Compound", "Complex", "Compound-complex"],
    "ttr": [(0.82, "Repeated wording", G), (0.95, "Some variety", N), (math.inf, "Highly varied", A)],
    "fk_tolerance": 1.5,            # FK grade may sit this far above the item's grade and still read "around"
    # Curriculum fit
    "match": [(0.75, "Low match", A), (0.90, "Moderate match", N), (math.inf, "Strong match", G)],
    # Item quality
    "plausibility": [(0.18, "Distractors far from answer", N), (0.50, "Balanced distance", G),
                     (math.inf, "Distractors close to answer", A)],
    "opt_sim": [(0.25, "Distinct options", G), (0.64, "Moderately similar", N), (math.inf, "Very similar", A)],
    "longest_ratio": 1.5,           # longest option vs the mean of the others
}
TTR_MIN_WORDS = 8                   # TTR is only meaningful on longer text
FK_MIN_WORDS = 8                    # ditto Flesch-Kincaid: "Define power." scores grade 14.7


def _band(table, value):
    """Map a number onto (label, colour) using an ascending list of (upper_bound, label, colour)."""
    for upper, label, colour in table:
        if value <= upper:
            return label, colour
    return table[-1][1], table[-1][2]


# --------------------------------------------------------------------------- optional backends
@lru_cache(maxsize=1)
def _nlp():
    try:
        import spacy
        return spacy.load("en_core_web_md")
    except Exception:
        return None


@lru_cache(maxsize=1)
def _textstat():
    try:
        import textstat
        return textstat
    except Exception:
        return None


def capabilities() -> dict:
    nlp = _nlp()
    return {
        "spacy": nlp is not None,
        "vectors": bool(nlp is not None and nlp.vocab.vectors.size),
        "textstat": _textstat() is not None,
    }


_WORD = re.compile(r"[A-Za-z][A-Za-z'\-]*")
_STOP = set("""a an the and or but if of to in on at by for with from as is are was were be been being
am do does did have has had not no nor so than that this these those there here it its it's he she they
we you i me him her them us my your his their our who whom whose which what when where why how all any
each few more most other some such only own same too very can will just should now then also into over
under about above below between after before during out up down off again further once s t""".split())


def words(text: str) -> list:
    return [w.lower() for w in _WORD.findall(text or "")]


def content_lemmas(text: str) -> list:
    """Content words as lemmas (spaCy) or lowercased tokens minus stopwords (fallback)."""
    nlp = _nlp()
    if nlp:
        doc = nlp(text or "")
        return [t.lemma_.lower() for t in doc if t.is_alpha and not t.is_stop and len(t) > 1]
    return [w for w in words(text) if w not in _STOP and len(w) > 1]


MATERIAL_MAX_CHARS = 150_000
_MATERIAL_CHUNK = 4_000


@lru_cache(maxsize=8)
def material_lemmas(text: str) -> frozenset:
    """Lemma set of a long reference text (a chapter or textbook).

    Streams the text through spaCy in ~4k-char pieces with the parser and NER off:
    a 62k-char chapter as a single doc peaks near 775 MB RSS. Cached so re-running
    layers over the same chapter does not lemmatize it twice."""
    text = (text or "")[:MATERIAL_MAX_CHARS]
    nlp = _nlp()
    if not nlp:
        return frozenset(w for w in words(text) if w not in _STOP and len(w) > 1)
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()] or [text]
    pieces, cur = [], ""
    for p in paras:
        if len(cur) + len(p) > _MATERIAL_CHUNK and cur:
            pieces.append(cur)
            cur = ""
        cur = (cur + "\n" + p) if cur else p
    if cur:
        pieces.append(cur)
    out = set()
    for doc in nlp.pipe(pieces, disable=["parser", "ner"], batch_size=4):
        out.update(t.lemma_.lower() for t in doc if t.is_alpha and not t.is_stop and len(t) > 1)
    return frozenset(out)


def sentences(text: str) -> list:
    nlp = _nlp()
    if nlp:
        return [s.text.strip() for s in nlp(text or "").sents if s.text.strip()]
    parts = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    return [p for p in parts if p]


# --------------------------------------------------------------------------- language load
def word_count(text: str) -> int:
    return len(words(text))


def type_token_ratio(text: str) -> Optional[float]:
    ws = words(text)
    if not ws:
        return None
    return round(len(set(ws)) / len(ws), 2)


def flesch_kincaid(text: str) -> Optional[float]:
    if not (text or "").strip():
        return None
    ts = _textstat()
    if ts:
        try:
            return round(float(ts.flesch_kincaid_grade(text)), 1)
        except Exception:
            pass
    # Fallback: the FK formula with a vowel-group syllable count.
    ws = words(text)
    if not ws:
        return None
    sents = max(1, len(re.findall(r"[.!?]+", text)) or 1)
    syll = sum(max(1, len(re.findall(r"[aeiouy]+", w))) for w in ws)
    return round(0.39 * len(ws) / sents + 11.8 * syll / len(ws) - 15.59, 1)


_SUBORD = re.compile(r"\b(because|although|though|when|whenever|if|unless|while|since|after|before|"
                     r"which|that|who|whose|whom|where|so that|even if|as if|until)\b", re.I)
_COORD = re.compile(r"(,\s*(and|but|or|so|yet)\b|;)", re.I)


def sentence_complexity(text: str):
    """0 Simple, 1 Compound, 2 Complex, 3 Compound-complex. The most complex sentence wins."""
    nlp = _nlp()
    best = 0
    if nlp:
        doc = nlp(text or "")
        for sent in doc.sents:
            indep = 1 + sum(1 for t in sent if t.dep_ == "conj" and t.pos_ in ("VERB", "AUX")
                            and t.head.pos_ in ("VERB", "AUX"))
            sub = any(t.dep_ in ("advcl", "ccomp", "relcl", "acl", "csubj", "csubjpass") for t in sent)
            best = max(best, (1 if indep > 1 else 0) + (2 if sub else 0))
    else:
        for s in sentences(text):
            comp = 1 if _COORD.search(s) else 0
            # "Which of the following...", "When did..." open with a subordinator
            # that is really the interrogative. Ignore that one; the same word
            # later in the sentence ("the gas which turns lime water milky") is a
            # genuine subordinate clause and still counts.
            question = s.rstrip().endswith("?")
            sub = 0
            for m in _SUBORD.finditer(s):
                if m.start() == 0 and question:
                    continue
                sub = 2
                break
            best = max(best, comp + sub)
    return best, BANDS["complexity"][best]


def parse_grade(grade) -> Optional[int]:
    """'Grade 6', 'P6', 'Class 6', 6 -> 6. None when absent or unparseable."""
    if grade is None or grade == "":
        return None
    m = re.search(r"\d+", str(grade))
    return int(m.group()) if m else None


def fk_band(fk: Optional[float], grade: Optional[int]):
    if fk is None:
        return "No text", N
    if grade is None:
        return f"Grade {fk}", N
    return ("Above grade level", A) if fk > grade + BANDS["fk_tolerance"] else ("Around grade level", G)


def language_load_bucket(higher_demand: int):
    """Turn 'how many of the four metrics sit in the higher-demand band' into one bucket tag.

    Equal weights: 0 of 4 -> Light, 1-2 -> Moderate, 3-4 -> Heavy. Change here if you
    decide that, say, Flesch-Kincaid above grade alone should already read Heavy."""
    if higher_demand == 0:
        return "Light", G
    if higher_demand <= 2:
        return "Moderate", N
    return "Heavy", A


def language_load(text: str, grade: Optional[int]) -> dict:
    n = word_count(text)
    if n == 0:
        # Without words there is nothing to measure, and a "0 words / Light read" bucket
        # would read as a finding rather than as missing input.
        return {"skipped": "No question text to measure."}
    load_label, load_col = _band(BANDS["reading_load"], n)
    score, cx_label = sentence_complexity(text)
    ttr = type_token_ratio(text)
    fk = flesch_kincaid(text)
    fk_label, fk_col = fk_band(fk, grade)
    ttr_ok = n >= TTR_MIN_WORDS and ttr is not None
    ttr_label, ttr_col = _band(BANDS["ttr"], ttr) if ttr_ok else ("Too short to judge", N)
    # Flesch-Kincaid divides by sentence and word counts, so on a fragment it swings
    # wildly: "Define power." scores grade 14.7 off two words and four syllables.
    # Guard it the way TTR is guarded rather than reporting a confident wrong number.
    fk_ok = n >= FK_MIN_WORDS and fk is not None
    if not fk_ok:
        fk_label, fk_col = "Too short to judge", N

    higher = sum([load_col == A, score >= 2, ttr_ok and ttr_col == A, fk_ok and fk_col == A])
    bucket, bcol = language_load_bucket(higher)
    return {
        "bucket": bucket, "band": bcol,
        "metrics": [
            {"id": "words", "name": "Reading load", "value": n, "display": f"{n} words",
             "label": load_label, "band": load_col, "min": 0, "max": 40, "zone": [0, 29]},
            {"id": "complexity", "name": "Sentence complexity", "value": score, "display": cx_label,
             "label": cx_label, "band": G if score == 0 else (N if score == 1 else A),
             "min": 0, "max": 3},
            {"id": "ttr", "name": "Vocabulary variety", "value": ttr,
             "display": f"{ttr:.2f}" if ttr is not None else "-",
             "label": ttr_label, "band": ttr_col, "min": 0, "max": 1, "zone": [0.82, 0.95],
             "note": "Type-Token Ratio" + ("" if ttr_ok else f" - needs {TTR_MIN_WORDS}+ words")},
            {"id": "fk", "name": "Readability", "value": fk,
             "display": (f"Grade {fk}" if fk_ok else "-"),
             "label": fk_label, "band": fk_col, "min": 0, "max": 12,
             "zone": [max(0, grade - 1), grade + BANDS["fk_tolerance"]] if grade is not None else None,
             "note": "Flesch-Kincaid grade"
                     + (f" - item grade {grade}" if grade is not None else "")
                     + ("" if fk_ok else f" - needs {FK_MIN_WORDS}+ words")},
        ],
        "method": "spaCy + textstat" if (_nlp() and _textstat()) else "plain-Python fallback",
    }


# --------------------------------------------------------------------------- curriculum fit
def curriculum_fit(text: str, material: str) -> dict:
    """Chapter-vocabulary match: the share of the item's content words that appear in the
    chapter the user supplied. Without a chapter this layer does not run - there is
    nothing meaningful to compare against."""
    if not (material or "").strip():
        return {"skipped": "No chapter content supplied, so curriculum fit was not computed. "
                           "Add the chapter or textbook you teach from and run this layer again."}
    lem = content_lemmas(text)
    if not lem:
        return {"skipped": "No content words to compare."}
    ref = material_lemmas(material)
    match = sum(1 for w in lem if w in ref) / len(lem)
    m_label, m_col = _band(BANDS["match"], match)
    bucket, bcol = {G: ("In chapter", G), N: ("Mixed", N), A: ("Beyond chapter", A)}[m_col]
    note = "share of the question's words found in the chapter supplied"
    truncated = len(material) > MATERIAL_MAX_CHARS
    if truncated:
        note += (f" - only the first {MATERIAL_MAX_CHARS:,} characters were compared, "
                 "so this match is understated; audit one chapter at a time")
    return {
        "bucket": bucket, "band": bcol,
        "truncated": truncated,
        "metrics": [
            {"id": "match", "name": "Chapter vocabulary match", "value": round(match * 100),
             "display": f"{round(match * 100)}%", "label": m_label, "band": m_col,
             "min": 0, "max": 100, "zone": [75, 100],
             "note": note},
        ],
        "source": "material",
        "method": "spaCy lemmas" if _nlp() else "stopword-filtered tokens",
    }


# --------------------------------------------------------------------------- item quality
def _similarity(a: str, b: str) -> float:
    nlp = _nlp()
    if nlp and nlp.vocab.vectors.size:
        da, db = nlp(a), nlp(b)
        if da.has_vector and db.has_vector and da.vector_norm and db.vector_norm:
            return max(0.0, min(1.0, float(da.similarity(db))))
    # Fallback: Jaccard over content words, then character trigrams for one-word options.
    sa, sb = set(content_lemmas(a)), set(content_lemmas(b))
    if sa and sb:
        return len(sa & sb) / len(sa | sb)
    ta = {a.lower()[i:i + 3] for i in range(max(1, len(a) - 2))}
    tb = {b.lower()[i:i + 3] for i in range(max(1, len(b) - 2))}
    return len(ta & tb) / max(1, len(ta | tb))


_OPT_PREFIX = re.compile(r"^\(?([A-Ha-h])[\).:\-]\s*")


def _norm_opt(s) -> str:
    return re.sub(r"\s+", " ", str(s)).strip().strip(".").casefold()


def resolve_answer_key(key: str, opts: list) -> Optional[int]:
    """Which option does this answer key name? None if it names none of them.

    Accepts the option text, a letter A-H (bare, or as "B)" / "(b)"), a labelled
    option ("B) Nitrogen"), or a 1-based position. The position form matters:
    the sister generator skill emits exactly that (see
    automatic-item-generation/references/output-schemas.md, "answer": "1 | 2 | 3 | 4"),
    so a bank it produced has to resolve here or the whole layer silently skips.
    """
    k = _norm_opt(key)
    for i, o in enumerate(opts):
        if _norm_opt(o) == k:
            return i
    raw = str(key).strip()
    m = _OPT_PREFIX.match(raw)
    if m:                                   # "B) Nitrogen" or a bare "(b)"
        body = _norm_opt(_OPT_PREFIX.sub("", raw))
        for i, o in enumerate(opts):
            if body and _norm_opt(o) == body:
                return i
        i = "abcdefgh".index(m.group(1).lower())
        return i if i < len(opts) else None
    if re.fullmatch(r"[A-Ha-h]", raw):
        i = "abcdefgh".index(raw.lower())
        return i if i < len(opts) else None
    if re.fullmatch(r"\d{1,2}", raw):       # 1-based position
        i = int(raw) - 1
        return i if 0 <= i < len(opts) else None
    return None


def item_quality(options: list, answer: Optional[str]) -> dict:
    opts = [str(o).strip() for o in (options or []) if str(o).strip()]
    if len(opts) < 3:
        return {"skipped": "Not a multiple-choice item (needs 3 or more options)."}
    # B6: similarity over numbers-only options is meaningless (the tokenizer is
    # word-based), and would read as a real "distractors far from answer" finding.
    if not any(_WORD.search(o) for o in opts):
        return {"skipped": "Options contain no words (numbers or symbols only), so option "
                           "similarity cannot be measured."}
    key = str(answer if answer is not None else "").strip()
    if not key:
        return {"skipped": "No answer key for this item, so distractors cannot be compared with the answer."}
    key_idx = resolve_answer_key(key, opts)
    if key_idx is None:
        return {"skipped": f"The answer key {key!r} does not match any of the {len(opts)} options, "
                           "so distractors cannot be compared with the answer."}
    key_text = opts[key_idx]
    distractors = [o for i, o in enumerate(opts) if i != key_idx]

    plaus = sum(_similarity(d, key_text) for d in distractors) / len(distractors)
    pair = [_similarity(a, b) for a, b in combinations(opts, 2)]
    opt_sim = sum(pair) / len(pair)
    lengths = [word_count(o) for o in opts]
    longest_i = max(range(len(opts)), key=lambda i: lengths[i])
    others = [l for i, l in enumerate(lengths) if i != longest_i]
    mean_others = sum(others) / len(others)
    tied = sum(1 for l in lengths if l == lengths[longest_i]) > 1
    one_longer = (not tied
                  and lengths[longest_i] >= BANDS["longest_ratio"] * mean_others
                  and lengths[longest_i] - mean_others >= 2)

    p_label, p_col = _band(BANDS["plausibility"], plaus)
    s_label, s_col = _band(BANDS["opt_sim"], opt_sim)
    l_label, l_col = ("One option longer", A) if one_longer else ("Even option lengths", G)
    uneven = sum([p_col == A, s_col == A, l_col == A])
    bucket, bcol = ("Even", G) if uneven == 0 else (("Mixed", N) if uneven == 1 else ("Uneven", A))
    vectors = bool(_nlp() and _nlp().vocab.vectors.size)
    return {
        "bucket": bucket, "band": bcol,
        "metrics": [
            {"id": "plausibility", "name": "Distractor plausibility", "value": round(plaus, 2),
             "display": f"{plaus:.2f}", "label": p_label, "band": p_col,
             "min": 0, "max": 1, "zone": [0.18, 0.50],
             "note": f"mean similarity of {len(distractors)} distractors to the answer"},
            {"id": "opt_sim", "name": "Option similarity", "value": round(opt_sim, 2),
             "display": f"{opt_sim:.2f}", "label": s_label, "band": s_col,
             "min": 0, "max": 1, "zone": [0, 0.25],
             "note": f"mean pairwise similarity across {len(opts)} options"},
            {"id": "longest", "name": "Longest option", "value": lengths[longest_i],
             "display": f"{lengths[longest_i]} words", "label": l_label, "band": l_col,
             "min": 0, "max": max(12, lengths[longest_i]),
             "note": ("the answer is the longest option" if longest_i == key_idx
                      else "a distractor is the longest option")
                     + f" - others average {mean_others:.1f}"},
        ],
        "method": "spaCy word vectors" if vectors else "word-overlap fallback",
    }


# --------------------------------------------------------------------------- driver
def normalize_layers(layers) -> list:
    """Accept a list, a comma-separated string, or None; complain about the rest.

    A bare string used to be iterated character by character, which quietly
    selected no layers at all and still exited 0 with a success-shaped report.
    """
    if layers is None:
        return list(LAYER_IDS)
    if isinstance(layers, str):
        layers = layers.split(",")
    picked, unknown = [], []
    for l in layers:
        l = str(l).strip().lower()
        if not l:
            continue
        (picked if l in LAYER_IDS else unknown).append(l)
    if unknown:
        extra = " ('cog' is the model's own judgment, not this script's)" if "cog" in unknown else ""
        print(f"[warn] ignoring unknown layer id(s): {', '.join(unknown)}{extra}", file=sys.stderr)
    if not picked:
        raise ValueError(f"no valid layers selected; choose from: {', '.join(LAYER_IDS)}")
    return picked


def audit(items: list, material: str = "", grade=None, layers: Optional[list] = None) -> dict:
    layers = normalize_layers(layers)
    material = str(material or "")
    doc_grade = parse_grade(grade)
    results = []
    for i, it in enumerate(items or []):
        if not isinstance(it, dict):
            results.append({"id": i + 1, "error": f"item {i + 1} is not an object, so it was not audited"})
            continue
        text = str(it.get("text") or "").strip()
        row = {"id": it.get("id", i + 1), "text": text}
        g = parse_grade(it.get("grade"))
        if g is None:
            g = doc_grade
        # One malformed field should cost its own row, not the whole batch.
        try:
            if "lang" in layers:
                row["lang"] = language_load(text, g)
            if "fit" in layers:
                row["fit"] = curriculum_fit(text, material)
            if "item" in layers:
                row["item"] = item_quality(it.get("options") or [], it.get("answer"))
        except Exception as e:
            row["error"] = f"{type(e).__name__}: {e}"
        results.append(row)
    return {"results": results, "summary": summarize(results, layers), "capabilities": capabilities()}


def summarize(results: list, layers: list) -> dict:
    """Counts per bucket, so a report can say 'across the set' without judging."""
    out = {"items": len(results), "errors": sum(1 for r in results if r.get("error"))}
    for lid in layers:
        counts, skipped = {}, 0
        for r in results:
            layer = r.get(lid) or {}
            if layer.get("skipped") or r.get("error"):
                skipped += 1
                continue
            b = layer.get("bucket")
            if b:
                counts[b] = counts.get(b, 0) + 1
        out[lid] = {"buckets": counts, "skipped": skipped}
    return out


_SELF_TEST = {
    "grade": 10,
    "material": "Madam Loisel borrowed a diamond necklace from Madame Forestier. She lost it at "
                "the ball. The family fell into debt and poverty for ten years. At the end of the "
                "story Madam Loisel was shocked to learn the necklace had been an imitation.",
    "items": [
        {"id": "q1", "text": "Why was Madam Loisel shocked at the end of the story?"},
        {"id": "q2",
         "text": "An old person suffering from weakening ciliary muscles has which defect, "
                 "corrected by which lens?",
         "options": ["hypermetropia and convex lens",
                     "presbyopia and bifocal lens",
                     "myopia and concave lens",
                     "myopia and bifocal lens"],
         "answer": "B"},
    ],
}


def main() -> int:
    ap = argparse.ArgumentParser(description="Measure language load, curriculum fit and item quality.")
    ap.add_argument("--in", dest="infile", help="request JSON (default: stdin)")
    ap.add_argument("--out", dest="outfile", help="report JSON (default: stdout)")
    ap.add_argument("--material", help="path to a chapter text file; overrides request 'material'")
    ap.add_argument("--layers", help="comma-separated subset of: " + ", ".join(LAYER_IDS))
    ap.add_argument("--grade", help="grade for the whole set, e.g. 10 or 'Class 10'")
    ap.add_argument("--self-test", action="store_true", help="run on a built-in sample and print the report")
    args = ap.parse_args()

    if args.self_test:
        req = _SELF_TEST
    else:
        try:
            raw = open(args.infile, encoding="utf-8").read() if args.infile else sys.stdin.read()
        except OSError as e:
            ap.error(f"could not read {args.infile}: {e.strerror}")
        if not raw.strip():
            ap.error("no input: pass --in FILE or pipe request JSON on stdin")
        try:
            req = json.loads(raw)
        except json.JSONDecodeError as e:
            ap.error(f"input is not valid JSON (line {e.lineno}, column {e.colno}): {e.msg}")
        if not isinstance(req, dict):
            ap.error('input JSON must be an object with an "items" array, not a '
                     + type(req).__name__)

    material = req.get("material", "")
    if args.material:
        try:
            material = open(args.material, encoding="utf-8").read()
        except OSError as e:
            ap.error(f"could not read {args.material}: {e.strerror}")
    layers = args.layers if args.layers else req.get("layers")

    try:
        report = audit(
            items=req.get("items", []),
            material=material,
            grade=args.grade if args.grade is not None else req.get("grade"),
            layers=layers,
        )
    except ValueError as e:
        ap.error(str(e))
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.outfile:
        with open(args.outfile, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"wrote {args.outfile}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
