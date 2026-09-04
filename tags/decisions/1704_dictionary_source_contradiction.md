# Decision: when the dictionary and the source disagree

**Status: ACCEPTED by Ben, 2026-09-03.** In force in
`references/vocab.md`, with a pointer from `SKILL.md` Step 2. Written in the
form #1760 established — the case as it was put, so the answer's basis stays
legible later.

Raised by the two-path comparison (#1704), P7's general clause. The specific
dictionary defect that surfaced it is filed separately as #1864.

---

## The situation

The fetched source is a real work, plainly on topic, and its numbers match the
dictionary exactly — and it describes a **different instrument** from the one
the table name and the dictionary description claim.

`celik_2026_bpns` is the clean case. The dictionary's Mendeley URL fetches a
deposit of Turkish undergraduates, n=653, which is the dictionary's own n. The
deposit carries an Attitude Scale toward Distance Learning and the Big Five
Inventory. The string "BPNS" appears **zero times**, and neither does "basic
psychological need". Two agents, one in each arm, grepped for it independently
before concluding.

`sumner_2022_asi` is the softer case and shows why a blanket rule is needed:
the dictionary says a 29-item Aberrant Salience Inventory with ~929
respondents, the supplied DOI resolves to a paper about a Formal Thought
Disorder scale, and the sample sizes match closely (324+610=934). Two agents
read that one in opposite directions.

## Why it needed a rule

Four agents hit this shape in a forty-table run and each decided alone:

| what they did | agents |
|---|---|
| abstained on the instrument fields, tagged the rest | 2 |
| tagged from the fetched source | 1 |
| tagged from the dictionary description | 1 |

That is not a distribution of judgement, it is a missing convention — the same
diagnosis #1760 made about `sample` and #1837 about `construct type`.

## The decision

**Split the row by what the disagreement actually touches.**

| field | ruling |
|---|---|
| `construct_name`, `construct type` | **blank** — these name the instrument, which is what is in dispute |
| `sample`, `age range`, `child age`, `item format`, `measurement tool`, `primary language(s)` | **tag from the source** |

Record the contradiction in `Notes`, naming what the source actually describes.

Two clauses guard it:

- **Do not resolve it by preferring one side.** Neither is authoritative. The
  dictionary is a human-maintained sheet with known defects; a source can be the
  right paper carrying a wrong description. Where you *can* tell which is right
  — the source names the instrument somewhere, or describes a battery the table
  is plainly one scale of — there is no contradiction and the rule does not
  apply.
- **Report it.** A contradiction is a fixable dictionary defect. The whole
  `celik_2026_*` family turned out to share one, and it only became visible
  because two independent agents wrote it down.

## The argument for the split

A mislabelled dictionary row is worse for tagging than a missing one. A missing
row makes the tagger abstain; a wrong one makes it **confidently** tag an
instrument the table may not contain, under a table name that says otherwise,
and nothing downstream can tell the difference — the row looks exactly like a
correct one.

But that argument only reaches the fields that name the instrument. However the
dispute resolves, the respondents were recruited the way the source says they
were, in the language the source says, on the response format the source shows.
Blanking those too would throw away evidence nobody disputes, and it would cost
coverage on three of the four columns that actually publish.

## What was rejected, and why

- **Tag from the source, note the conflict.** The majority behaviour would then
  be to assert an instrument the table may not contain. The `Notes` field is not
  read by anything downstream, so the assertion would publish unqualified.
- **Abstain entirely and flag the row.** Safest, and it was rejected on cost:
  `primary language(s)`, `item format` and `measurement tool` all publish, all
  are supported by the source regardless of the dispute, and the untagged
  population is 1,427 tables. Throwing away three publishable columns to avoid
  one wrong instrument name is a bad trade.

## What this does not settle

- **How often it happens.** Four sightings in forty tables is not a rate; the
  denominator is tables where an agent thought to check, and nothing prompts
  them to.
- **Whether the tagger reliably notices.** Both `celik` sightings involved an
  agent grepping the fetched text for the instrument name. Nothing in `SKILL.md`
  tells them to, and this decision does not add it — a detection step is a
  separate change with its own cost.
