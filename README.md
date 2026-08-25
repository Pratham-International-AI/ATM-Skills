# ATM Skills — AI-Assisted Assessment Authoring, for Any Curriculum

This kit teaches an AI assistant (Claude, ChatGPT, or any capable LLM) to do two jobs that
normally take an experienced examiner:

1. **Write exam questions** from a chapter — MCQs, fill-in-the-blanks, short answers, and
   long answers — each with a ready-to-use marking scheme.
2. **Tag questions by thinking level** using Bloom's Taxonomy (is this question testing
   memory, understanding, application, analysis…?), so you can check that a paper isn't
   just rote recall.

It is **curriculum-agnostic**: the kit doesn't assume any particular board or syllabus.
Instead, *you* describe your curriculum's rules in a document called a **curriculum profile**,
and the AI follows those rules. We include a complete, battle-tested profile for
**CBSE Class 10 (Science and English)** as the worked example.

> **A note on quality.** The CBSE Class 10 profile is the configuration we have evaluated
> extensively — we stand behind the quality of questions generated with it. Profiles you
> write for other curricula run through the exact same system, but their output quality
> depends on the quality of your profile, and you should review and validate the results
> yourself before using them with students.

---

## What's in the box

```
atm-skills/
  README.md                          ← you are here
  curriculum-profiles/               ← the "describe your curriculum" part
    TEMPLATE.md                      ← blank profile to copy and fill in
    cbse-class10/                    ← the validated worked example
      profile.md                     ← start here: identity, audience, subjects
      science-rules.md               ← how CBSE Science questions must be written
      english-rules.md               ← how CBSE English Literature questions must be written
      value-points.md                ← marking-scheme structure by subject and marks
  skills/                            ← the "automation" part
    automatic-item-generation/       ← Skill 1: question generator
      SKILL.md
      references/
        item-writing-craft.md        ← universal question-quality rules (any curriculum)
        blooms-taxonomy.md
        output-schemas.md
    blooms-taxonomy-classifier/      ← Skill 2: thinking-level tagger
      SKILL.md
      references/
        blooms-taxonomy.md
```

A **skill** is a set of instructions the AI reads when it recognizes a matching task. The
skills hold everything that's true for *any* curriculum (e.g. "no MCQ option should be
obviously longer than the others"). The **curriculum profile** holds everything specific to
*yours* (e.g. "a 3-mark English answer is marked 2 for content + 1 for expression").

---

## How it works: one manual step, then automation

### Step 1 (manual, once per curriculum): create a curriculum profile

Before the AI can generate questions for your curriculum, you tell it the rules. Copy
`curriculum-profiles/TEMPLATE.md`, fill in its eight sections, and save it. The sections ask
for things an examiner already knows:

| Profile section | What you provide |
|---|---|
| Curriculum identity | Which board/program and exam standard to imitate |
| Audience | Students' age, language background, reading level |
| Subjects | What's in and out of scope per subject |
| Cognitive framework | Bloom's Taxonomy (default) or your own level system |
| Difficulty levels | What Easy / Medium / Hard mean in your context |
| Formats & marks | Which question types and mark values you use |
| Item quality rubric | Your curriculum's do's and don'ts for questions |
| Marking scheme rubric | How many marking points per question, and their structure |

If a section is hard to fill, open the matching file in `curriculum-profiles/cbse-class10/`
to see a finished example. You don't need to be exhaustive on day one — a profile is a living
document; every time you spot the AI making a mistake your examiners wouldn't, add a rule.

**Using CBSE Class 10?** Skip this step entirely — the shipped profile is ready to use.

### Step 2 (automated): generate and tag questions

Once the profile exists, you just ask, in plain language. The AI reads your profile, reads
the chapter you give it, and does the work.

Example requests to type:

> *"Using the CBSE Class 10 profile, generate 5 MCQs (1 mark each) from this chapter PDF,
> Medium difficulty, targeting Remembering and Understanding."*

> *"Generate ten 3-mark short-answer questions for English from `flying-together.pdf`,
> with value points."*

> *"Using my curriculum profile at `profiles/igcse-biology.md`, make a 20-question bank
> from chapter 4."*

> *"Tag every question in `question-bank.json` with its Bloom's level."*

> *"Audit this question paper — what percentage is just Remembering?"*

Every generated question comes with **value points**: the marking-scheme bullets an examiner
(human or AI) ticks off when grading, structured exactly the way your profile's marking
rubric says.

---

## The two skills, in brief

### 1. Automatic Item Generation (`skills/automatic-item-generation/`)

Give it: your curriculum profile, the subject, a chapter (PDF, Word, text, or pasted
content), the question format, marks per question, difficulty, and the Bloom's levels to
target. It returns exactly the number of questions you asked for, each with value points, in
a consistent, machine-readable format (so results can also feed into other tools).

Built-in quality guarantees, regardless of curriculum: questions come only from the chapter
you supplied (no invented facts), each question tests one concept, no two questions repeat
the same idea, MCQ answer options are balanced so the right answer doesn't stand out, and
question depth matches the marks.

**Important honesty rule:** if you don't give it a curriculum profile (and don't ask for the
CBSE example), it stops and asks for one — it will not quietly improvise rules for a
curriculum it hasn't been given.

### 2. Bloom's Taxonomy Classifier (`skills/blooms-taxonomy-classifier/`)

Give it a question (or a whole JSON question bank) and it labels each question with one of
the six Bloom's levels — Remembering, Understanding, Applying, Analysing, Evaluating,
Creating — plus a confidence score and a one-line reason. It judges the *actual thinking*
a question demands, not just trigger words ("explain" can be recall or analysis).

Bloom's Taxonomy is curriculum-independent, so this skill works for any curriculum without
a profile.

---

## Setting it up

### In Claude Code

Copy the skill folders into your skills directory, and keep `curriculum-profiles/` in your
project so the AI can read it:

```bash
# project-scoped (this project only)
cp -r skills/automatic-item-generation  /path/to/your/project/.claude/skills/
cp -r skills/blooms-taxonomy-classifier /path/to/your/project/.claude/skills/
cp -r curriculum-profiles               /path/to/your/project/

# or personal (all projects)
cp -r skills/automatic-item-generation  ~/.claude/skills/
cp -r skills/blooms-taxonomy-classifier ~/.claude/skills/
```

Claude Code auto-discovers the skills; mention your profile (or "CBSE Class 10") in your
request and it finds the rest.

### In Claude.ai (Skills)

1. Copy the `curriculum-profiles/` folder **into** the skill folder (so the profile travels
   with the skill).
2. Zip the skill folder so `SKILL.md` sits at the zip root, with `references/` and
   `curriculum-profiles/` alongside it.
3. Upload the zip under Settings → Skills.

### In ChatGPT (Custom GPT or Project)

ChatGPT has no auto-invoked skills, but the same content works:

- **Custom GPT:** paste the body of `SKILL.md` (everything below the `---` frontmatter
  block) into the GPT's *Instructions*. Upload the `references/*.md` files **and your
  curriculum profile files** as *Knowledge* files.
- **ChatGPT Projects:** same idea — `SKILL.md` body as project instructions, references and
  profile as project files.

### With any other LLM or API

Everything is plain Markdown:

1. Strip the YAML frontmatter from `SKILL.md`; use the rest as your system prompt.
2. Give the model the `references/*.md` files and your curriculum profile — concatenated
   into the prompt, attached as files, or via retrieval.
3. Supply the inputs listed in `SKILL.md` under "Required inputs" in your user message.

---

## Frequently asked

**Do I need to know how to code?** No. The profile is a plain document you write in ordinary
language; the requests are plain sentences. The only technical-ish part is copying folders
during setup.

**Can I use this for maths / history / another subject under CBSE?** The shipped CBSE profile
covers Science and English only. To add a subject, write a new `<subject>-rules.md` in the
profile folder (use the two existing ones as models) and list it in `profile.md` — then
review the output carefully, since the new subject hasn't been through our evaluations.

**What if my curriculum doesn't use Bloom's Taxonomy?** Define your own levels in the
profile's "Cognitive framework" section; the generator will use them. The standalone
classifier skill, however, is Bloom's-specific.

**Who grades the answers?** This kit is for authoring only: it generates questions *with*
marking schemes so an examiner (human or automated) can grade against them. Automated grading
and student feedback are not part of this kit — they exist in the wider ATM project as
prompt-based services (see the project's `PROMPTS.md`).

**How do I trust the output?** For CBSE Class 10, we've run extensive evaluations and stand
by it. For your own profile: start small (5–10 questions), have a subject examiner review
them against your rubric, tighten the profile where the AI drifted, and repeat. Treat the
profile like you'd treat guidelines for a new human item-writer.
