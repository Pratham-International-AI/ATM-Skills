# Output Schemas

This is the canonical output contract — use it verbatim when the results feed a pipeline or the requester doesn't ask for a particular format. If the user wants a different artifact (a spreadsheet, a printable question paper, rows appended to their existing file), produce that instead; these schemas then define the information every item must still carry, not the container.

Every item, regardless of format, carries `blooms_level` (one of the six Bloom's Taxonomy labels — see `blooms-taxonomy.md`) and `marks` (positive integer).

## mcq_questions

```json
{
  "mcq_questions": [
    {
      "blooms_level": "Understanding",
      "marks": 1,
      "question": "string",
      "options": ["string", "string", "string", "string"],
      "answer": "1 | 2 | 3 | 4",
      "value_points": ["string"]
    }
  ]
}
```
`options` must have exactly 4 entries, text only (no "A)"/"1." prefixes). `answer` is the correct option's position (1-indexed) as a string.

## fill_blank_questions

```json
{
  "fill_blank_questions": [
    {
      "blooms_level": "Remembering",
      "marks": 1,
      "question": "Sentence with _____ for the blank",
      "answer": "string",
      "value_points": ["string"]
    }
  ]
}
```

## short_answer_questions

```json
{
  "short_answer_questions": [
    {
      "blooms_level": "Applying",
      "marks": 2,
      "question": "string",
      "value_points": ["string", "string"]
    }
  ]
}
```
`value_points` needs at least 2 entries.

## long_answer_questions

```json
{
  "long_answer_questions": [
    {
      "blooms_level": "Analysing",
      "marks": 5,
      "question": "string",
      "value_points": ["string", "string", "string"]
    }
  ]
}
```
`value_points` needs at least 3 entries.

## Final response envelope

Wrap whichever of the four arrays above applies, plus a status:

```json
{
  "status": "completed",
  "message": "questions generated",
  "no_questions": 5,
  "mcq_questions": [ ... ]
}
```

If generation cannot proceed (no usable source text, unsupported file type, requested count/format combination impossible, etc.), return instead:

```json
{
  "status": "incomplete",
  "message": "human-readable reason",
  "no_questions": 0
}
```

Never mix formats in one response — only the array matching the requested `question_format` key is present.
