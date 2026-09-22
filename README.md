# ATM Skills

This kit teaches an AI assistant (Claude, ChatGPT, or any capable LLM) to do two jobs that
normally need an experienced examiner:

1. **Write exam items** from a chapter: MCQs, fill-in-the-blanks, short answers, and
   long answers, each with a ready-to-use marking scheme.
2. **Audit items** across four measures: the thinking level they demand (Bloom's
   Taxonomy), how hard they are to read, whether their vocabulary matches the chapter
   taught, and whether MCQ options are balanced.

The kit doesn't assume any particular board or syllabus. You describe your curriculum's
rules in a document called a curriculum profile, and the AI follows those rules. A complete
profile for CBSE Class 10 (Science and English) is included as the worked example.

**A note on quality.** The CBSE Class 10 profile is the configuration we have evaluated
extensively, and we stand behind the items it produces. Profiles you write for other
curricula run through the same system, but the output is only as good as the profile, so
review the results yourself before putting them in front of students.

## What's inside

```
atm-skills/
  README.md                          ← you are here
  LICENSE                            ← Apache 2.0
  automatic-item-generation/         ← Skill 1: item generator
    SKILL.md
    curriculum-profiles/             ← the "describe your curriculum" part
      TEMPLATE.md                    ← blank profile to copy and fill in
      cbse-class10/                  ← the worked example
        profile.md                   ← start here: identity, audience, subjects
        science-rules.md             ← how CBSE Science items must be written
        english-rules.md             ← how CBSE English Literature items must be written
        value-points.md              ← marking-scheme structure by subject and marks
        worked-examples.md           ← model items that pass every rule
    references/
      item-writing-craft.md          ← item-quality rules that apply to any curriculum
      blooms-taxonomy.md
      output-schemas.md
  item-auditor/                      ← Skill 2: item auditor
    SKILL.md
    scripts/
      audit.py                       ← measures reading load, fit, and option balance
    references/
      blooms-taxonomy.md
      level-examples.md              ← classified example items per level
      metrics.md                     ← what each measure means, and its bands
```

The curriculum profiles live inside the generation skill on purpose: installing that one
folder brings the template, the CBSE example, and its worked examples along with it.

A skill is a set of instructions the AI reads when it recognizes a matching task. The
skills hold everything that is true for any curriculum (for example, no MCQ option should
be obviously longer than the others). The curriculum profile holds everything specific to
yours (for example, a 3-mark English answer is marked 2 for content plus 1 for expression).

## How it works: one manual step, then automation

### Step 1, done once per curriculum: write a curriculum profile

Before the AI can generate items for your curriculum, you have to tell it the rules.
Copy `automatic-item-generation/curriculum-profiles/TEMPLATE.md`, work through its
sections, and save it. The sections ask for things an examiner already knows:

| Profile section | What you provide |
|---|---|
| Curriculum identity | Which board or program, and which exam standard to imitate |
| Audience | Students' age, language background, reading level |
| Subjects | What's in and out of scope per subject |
| Cognitive framework | Bloom's Taxonomy (the default) or your own level system |
| Difficulty levels | What Easy, Medium, and Hard mean in your context |
| Formats and marks | Which item types and mark values you use |
| Item quality rubric | Your curriculum's do's and don'ts for items |
| Marking scheme rubric | How many marking points per item, and their structure |
| Worked examples | A few model items your examiners consider excellent (optional, but they anchor the AI better than rules alone) |

If a section is hard to fill, open the matching file in the `cbse-class10/` folder next to
the template and copy its shape. A profile doesn't need to be complete on day one. Treat it as a living
document: whenever the AI makes a mistake your examiners wouldn't, add a rule.

Using CBSE Class 10? Skip this step. The included profile is ready to use.

### Step 2, automated: generate and audit items

Ask in plain language. The AI reads your profile, reads the chapter you give it, and does
the work. Some example requests:

> "Using the CBSE Class 10 profile, generate 5 MCQs (1 mark each) from this chapter PDF,
> Medium difficulty, targeting Remembering and Understanding."

> "Generate ten 3-mark short-answer items for English from `flying-together.pdf`,
> with value points."

> "Using my curriculum profile at `profiles/igcse-biology.md`, make a 20-item bank
> from chapter 4."

> "Tag every item in `question-bank.json` with its Bloom's level."

> "Add a Bloom's level column to `question-bank.xlsx`."

> "Audit this question paper. What percentage is just Remembering?"

> "Is this Class 8 worksheet too hard to read for Class 8?"

> "Check the MCQs in `paper.docx`. Are any of the distractors giveaways?"

Every generated item comes with value points: the marking-scheme bullets an examiner
ticks off when grading, structured the way your profile's marking rubric says.

## The two skills

### Automatic item generation

Give it your curriculum profile, the subject, a chapter (PDF, Word, text, or pasted
content), the item format, marks per item, difficulty, and the Bloom's levels to
target. It returns exactly the number of items you asked for, each with value points.
By default the output is a machine-readable format other tools can consume, but ask for a
spreadsheet or a printable question paper and you'll get that instead.

Some quality rules are built into the skill itself and apply no matter the curriculum:
items come only from the chapter you supplied (no invented facts), each item tests one
concept, no two items repeat the same idea, MCQ options are balanced so the correct answer
doesn't stand out, and item depth matches the marks.

One behavior worth knowing about: if you name a curriculum it has no profile for, it stops
and asks for one rather than quietly inventing rules. (Say nothing about curriculum at all
and it falls back to the bundled CBSE Class 10 example.)

### Item auditor

Give it an item, or a whole item bank in whatever format you keep it (JSON, CSV, a
spreadsheet, or items pasted into the chat), and it measures four things:

| Layer | What it tells you |
|---|---|
| Cognitive demand | The Bloom's level, with a confidence score and a one-line reason. It judges the actual thinking an item demands rather than trigger words; "explain" can be recall or analysis depending on the item. |
| Language load | Word count, sentence complexity, vocabulary variety, and reading grade level, so you can catch a Class 6 item written in Class 10 English. |
| Curriculum fit | How much of the item's vocabulary appears in the chapter you teach from. Needs you to supply the chapter; it asks once, and skips this measure if you'd rather not. |
| Item quality | For MCQs with an answer key: whether the options work as good distractors, meaning plausible enough to tempt a student who hasn't understood, distinct from one another, and none given away by being conspicuously longer. Metrics for other item types are still to be added. |

For files, it hands back a copy in the same format with the results filled in, for
example new columns added to your spreadsheet. Your original is left untouched.

The auditor measures, it doesn't grade. An item tagged "heavy read" is a more demanding
item, which may be exactly what you intended. You get the numbers and what's typical for
the grade; the judgment stays yours. Item quality is the exception: a distractor nobody
would pick, or an answer given away by its length, is a fault rather than a choice, so
that layer does tell you when the options aren't working.

The three measured layers run through a small Python script bundled with the skill. It
uses only the standard library, so there is nothing to install. If you happen to have
spaCy or textstat in your environment it uses those for more exact figures, and every
result says which way it was computed. On a host with no code execution, the skill
estimates what it can by hand and labels those numbers as estimates.

Nothing here is tied to a curriculum except curriculum fit, which uses the chapter you
supply, so this skill works without a profile.

## Setting it up

### Quick install (recommended)

```bash
npx skills add Pratham-International-AI/ATM-Skills
```

This installs both skills into agents that support the skills format (Claude Code, Codex,
and others), and the curriculum profiles come along automatically because they sit inside
the generation skill.

### In Claude Code, manually

Copy the skill folders into your skills directory:

```bash
# project-scoped (this project only)
cp -r automatic-item-generation  /path/to/your/project/.claude/skills/
cp -r item-auditor              /path/to/your/project/.claude/skills/

# or personal (all projects)
cp -r automatic-item-generation  ~/.claude/skills/
cp -r item-auditor              ~/.claude/skills/
```

Claude Code finds the skills automatically. Mention your profile (or "CBSE Class 10") in
your request and it takes it from there.

### In Claude.ai (Skills)

Zip a skill folder so `SKILL.md` sits at the zip root, then upload the zip under Settings,
then Skills. For the generation skill, `references/` and `curriculum-profiles/` travel
inside the folder, so one zip carries everything. Same for the auditor's `scripts/`: its
measurement script runs wherever code execution is available.

### In ChatGPT (Custom GPT or Project)

- Custom GPT: paste the body of `SKILL.md` (everything below the `---` frontmatter block)
  into the GPT's Instructions. Upload the `references/*.md` files and your curriculum
  profile files as Knowledge files.
- ChatGPT Projects: same idea. `SKILL.md` body as project instructions, references and
  profile as project files.

The auditor's `scripts/audit.py` needs code execution, which a Custom GPT has only if you
enable Code Interpreter. Without it the skill still gives you the Bloom's level exactly,
estimates language load and item quality by hand, and tells you which numbers are
estimates. Upload `references/metrics.md` alongside the other reference files so it knows
how.

### With any other LLM or API

Everything is plain Markdown:

1. Strip the YAML frontmatter from `SKILL.md` and use the rest as your system prompt.
2. Give the model the `references/*.md` files and your curriculum profile, either pasted
   into the prompt, attached as files, or served via retrieval.
3. Supply the inputs the skill asks for in your user message (the generator lists them
   under "Required inputs", the auditor under "Inputs").
4. For the auditor, either give the model a way to run `scripts/audit.py` (it needs only
   the Python standard library), or let it fall back to estimating. `references/metrics.md`
   tells it how, and requires it to label estimates as such.

## Common questions

**Do I need to know how to code?** No. The profile is a plain document written in ordinary
language, and the requests are plain sentences. The closest thing to a technical step is
copying folders during setup.

**Can I use this for maths or history under CBSE?** The included profile covers Science and
English only. To add a subject, write a new `<subject>-rules.md` in the profile folder
(use the two existing ones as models) and list it in `profile.md`. Then review the output
carefully, because the new subject hasn't been through our evaluations.

**What if my curriculum doesn't use Bloom's Taxonomy?** Define your own levels in the
profile's "Cognitive framework" section and the generator will use them. In the auditor,
only the cognitive-demand layer is Bloom's-specific; language load, curriculum fit, and
item quality don't depend on a cognitive framework at all, so you still get those three.

**Who grades the answers?** This kit is for authoring only; it does not grade student
answers or write feedback. Every item it generates comes with a marking scheme (the
value points), so an examiner, human or automated, has everything needed to grade against.

## License

Apache License 2.0. See [LICENSE](LICENSE).
