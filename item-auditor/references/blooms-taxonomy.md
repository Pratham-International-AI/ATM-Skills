# Bloom's Taxonomy — Reference

Six cognitive levels, lowest to highest order of thinking. Classify into **exactly one** of these — never invent a level, never return two.

| Level | Definition | Typical keywords in the question |
|---|---|---|
| **Remembering** | Memorization, recognition, or recall of facts | list, recite, define, name, match, quote, recall, identify, recognize, label |
| **Understanding** | Demonstrating comprehension by organizing, describing, or summarizing ideas | compare, contrast, demonstrate, outline, rephrase, translate, summarize |
| **Applying** | Correct use of a fact, rule, or idea in a new but structured situation | calculate, predict, apply, solve, illustrate, use, demonstrate, determine, model |
| **Analysing** | Breaking information into parts; drawing inferences or evidence to support a generalization | classify, outline, break down, categorise, analyse, diagram, illustrate |
| **Evaluating** | Judging the value/validity of information or ideas; defending an opinion | choose, support, relate, determine, defend, judge, grade, compare, contrast, argue, justify, importance, criteria, prove, disprove, assess, influence, perceive, value, estimate, deduct |
| **Creating** | Combining parts into a new whole; proposing an original or alternative solution | design, formulate, build, invent, create, compose, generate, derive, modify, develop |

## How to pick the level (not just keyword-matching)

A keyword list is a hint, not the rule. Classify based on **the cognitive demand actually required to answer the question**, not the verb that happens to appear:

- A question using "explain" can be Remembering (recite a memorized definition) or Analysing (explain *why*, requiring breaking down a mechanism) — read the full question and any context/options before deciding.
- MCQs that require picking between plausible distractors based on reasoning (e.g., predicting an outcome from given data) are usually **Applying** or **Analysing**, not Remembering, even though the answer format looks like simple recall.
- If a question gives context/data and asks the student to reach a novel conclusion, judgment, or design — even if phrased simply — lean toward **Evaluating** or **Creating**.
- When genuinely torn between two adjacent levels, pick the **higher** one only if the question truly requires that extra cognitive step to arrive at the answer; otherwise default to the lower, more literal reading.

## Output contract

Every classification (single question or one row in a batch) must produce exactly these three fields:

```json
{
  "reasoning": "one or two sentences on why this level, referencing the specific cognitive demand",
  "confidence_score": 0.00,
  "blooms_level": "Remembering | Understanding | Applying | Analysing | Evaluating | Creating"
}
```

- `confidence_score`: float between 0 and 1, two decimal places. Lower it (below ~0.6) when the question plausibly spans two adjacent levels.
- `reasoning`: must name the specific cognitive operation the student performs (e.g., "requires comparing two given values before selecting the correct formula → Applying"), not a generic restatement of the definition.
- `blooms_level`: must be spelled exactly as one of the six labels above (case-sensitive match matters if this feeds back into a pipeline).
