# ATM Skills

This kit teaches an AI assistant (Claude, ChatGPT, or any capable LLM) to do two jobs that
normally need an experienced examiner:

1. **Write exam questions** from a chapter: MCQs, fill-in-the-blanks, short answers, and
   long answers, each with a ready-to-use marking scheme.
2. **Tag questions by thinking level** using Bloom's Taxonomy, so you can check whether a
   paper actually tests understanding or is mostly rote recall.

The kit doesn't assume any particular board or syllabus. You describe your curriculum's
rules in a document called a curriculum profile, and the AI follows those rules. A complete
profile for CBSE Class 10 (Science and English) is included as the worked example.

**A note on quality.** The CBSE Class 10 profile is the configuration we have evaluated
extensively, and we stand behind the questions it produces. Profiles you write for other
curricula run through the same system, but the output is only as good as the profile, so
review the results yourself before putting them in front of students.

## What's inside

```
atm-skills/
  README.md                          ← you are here
  curriculum-profiles/               ← the "describe your curriculum" part
    TEMPLATE.md                      ← blank profile to copy and fill in
    cbse-class10/                    ← the worked example
      profile.md                     ← start here: identity, audience, subjects
      science-rules.md               ← how CBSE Science questions must be written
      english-rules.md               ← how CBSE English Literature questions must be written
      value-points.md                ← marking-scheme structure by subject and marks
  skills/                            ← the "automation" part
    automatic-item-generation/       ← Skill 1: question generator
      SKILL.md
      references/
        item-writing-craft.md        ← question-quality rules that apply to any curriculum
        blooms-taxonomy.md
        output-schemas.md
    blooms-taxonomy-classifier/      ← Skill 2: thinking-level tagger
      SKILL.md
      references/
        blooms-taxonomy.md
```

A skill is a set of instructions the AI reads when it recognizes a matching task. The
skills hold everything that is true for any curriculum (for example, no MCQ option should
be obviously longer than the others). The curriculum profile holds everything specific to
yours (for example, a 3-mark English answer is marked 2 for content plus 1 for expression).

## How it works: one manual step, then automation

### Step 1, done once per curriculum: write a curriculum profile

Before the AI can generate questions for your curriculum, you have to tell it the rules.
Copy `curriculum-profiles/TEMPLATE.md`, fill in its eight sections, and save it. The
sections ask for things an examiner already knows:

| Profile section | What you provide |
|---|---|
| Curriculum identity | Which board or program, and which exam standard to imitate |
| Audience | Students' age, language background, reading level |
| Subjects | What's in and out of scope per subject |
| Cognitive framework | Bloom's Taxonomy (the default) or your own level system |
| Difficulty levels | What Easy, Medium, and Hard mean in your context |
| Formats and marks | Which question types and mark values you use |
| Item quality rubric | Your curriculum's do's and don'ts for questions |
| Marking scheme rubric | How many marking points per question, and their structure |

If a section is hard to fill, open the matching file in `curriculum-profiles/cbse-class10/`
and copy its shape. A profile doesn't need to be complete on day one. Treat it as a living
document: whenever the AI makes a mistake your examiners wouldn't, add a rule.

Using CBSE Class 10? Skip this step. The included profile is ready to use.

### Step 2, automated: generate and tag questions

Ask in plain language. The AI reads your profile, reads the chapter you give it, and does
the work. Some example requests:

> "Using the CBSE Class 10 profile, generate 5 MCQs (1 mark each) from this chapter PDF,
> Medium difficulty, targeting Remembering and Understanding."

> "Generate ten 3-mark short-answer questions for English from `flying-together.pdf`,
> with value points."

> "Using my curriculum profile at `profiles/igcse-biology.md`, make a 20-question bank
> from chapter 4."

> "Tag every question in `question-bank.json` with its Bloom's level."

> "Audit this question paper. What percentage is just Remembering?"

Every generated question comes with value points: the marking-scheme bullets an examiner
ticks off when grading, structured the way your profile's marking rubric says.

## The two skills

### Automatic item generation

Give it your curriculum profile, the subject, a chapter (PDF, Word, text, or pasted
content), the question format, marks per question, difficulty, and the Bloom's levels to
target. It returns exactly the number of questions you asked for, each with value points,
in a consistent machine-readable format so the results can also feed into other tools.

Some quality rules are built into the skill itself and apply no matter the curriculum:
questions come only from the chapter you supplied (no invented facts), each question tests
one concept, no two questions repeat the same idea, MCQ options are balanced so the correct
answer doesn't stand out, and question depth matches the marks.

One behavior worth knowing about: if you don't give it a profile and don't ask for the CBSE
example, it stops and asks for one. It will not quietly invent rules for a curriculum it
hasn't been given.

### Bloom's taxonomy classifier

Give it a question, or a whole JSON question bank, and it labels each question with one of
the six Bloom's levels plus a confidence score and a one-line reason. It judges the actual
thinking a question demands rather than trigger words; "explain" can be recall or analysis
depending on the question.

Bloom's Taxonomy isn't tied to any curriculum, so this skill works without a profile.

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

Claude Code finds the skills automatically. Mention your profile (or "CBSE Class 10") in
your request and it takes it from there.

### In Claude.ai (Skills)

1. Copy the `curriculum-profiles/` folder into the skill folder, so the profile travels
   with the skill.
2. Zip the skill folder so `SKILL.md` sits at the zip root, with `references/` and
   `curriculum-profiles/` alongside it.
3. Upload the zip under Settings, then Skills.

### In ChatGPT (Custom GPT or Project)

ChatGPT has no auto-invoked skills, but the same content works:

- Custom GPT: paste the body of `SKILL.md` (everything below the `---` frontmatter block)
  into the GPT's Instructions. Upload the `references/*.md` files and your curriculum
  profile files as Knowledge files.
- ChatGPT Projects: same idea. `SKILL.md` body as project instructions, references and
  profile as project files.

### With any other LLM or API

Everything is plain Markdown:

1. Strip the YAML frontmatter from `SKILL.md` and use the rest as your system prompt.
2. Give the model the `references/*.md` files and your curriculum profile, either pasted
   into the prompt, attached as files, or served via retrieval.
3. Supply the inputs listed in `SKILL.md` under "Required inputs" in your user message.

## Common questions

**Do I need to know how to code?** No. The profile is a plain document written in ordinary
language, and the requests are plain sentences. The closest thing to a technical step is
copying folders during setup.

**Can I use this for maths or history under CBSE?** The included profile covers Science and
English only. To add a subject, write a new `<subject>-rules.md` in the profile folder
(use the two existing ones as models) and list it in `profile.md`. Then review the output
carefully, because the new subject hasn't been through our evaluations.

**What if my curriculum doesn't use Bloom's Taxonomy?** Define your own levels in the
profile's "Cognitive framework" section and the generator will use them. The standalone
classifier skill, though, is Bloom's-only.

**Who grades the answers?** This kit is for authoring only; it does not grade student
answers or write feedback. Every question it generates comes with a marking scheme (the
value points), so an examiner, human or automated, has everything needed to grade against.
