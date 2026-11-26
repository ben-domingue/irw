# Subject tags for the covariance family

**Status: ACCEPTED by Ben, 2026-11-18** (#3645). The rules themselves live in
`data/covariance/README.md`, "Subject tags"; this file is the record of why, and
of how the first 232 rows were made.

## The question

`irw_cov` had no way to find a table by subject (the TAM corpora, the ability
batteries, the TPB matrices). Conjoint had solved the same problem with its own
closed vocabulary (`2919_conjoint_topic_tags.md`), and the issue was first
written that way.

## What was decided

1. **Core's columns, not a cov vocabulary.** A 16-code `domain` list was drafted
   bottom-up from the 232 tables and turned out to recreate core's
   `construct type` and `sample` under new names, while mixing what a matrix
   measures (personality, mental health) with where its sample came from (work,
   health care). Reusing core's columns, values and rules (#1837, #1760, #1704)
   means one filter finds core and cov tables alike and no new boundaries needed
   writing. Ben: agreed.
2. **New values only where core has none, shared with core otherwise** (Ben:
   "i am ok having new codes as needed, but codes should intersect with core when
   possible"). The first is `construct type` = `Socioeconomic/attainment`, for
   the status-attainment path models and area indicators, which none of the
   seven values described. Crime counts and votes went to `Behavioral` under
   core's rule 3 instead of `Other`.
3. **`framework`, a cov-only optional field**, for the theory searches that
   `construct type` cannot answer (TPB, RAA, HAPA, TAM, UTAUT, SCCT, HBM,
   status_attainment). Fifteen tables carry one.
4. **Pooled tables** (groups from many studies, mostly MASEM): `sample` is the
   union of the groups' settings and the frame is blank. Ben took the
   recommendation over leaving `sample` blank on pooled tables.
5. **Storage:** `data/covariance/tags.csv`, joined into `cov_metadata` by
   `metadata/22_cov.R` and checked by core's own `normalize_multiselect()`
   against `TAG_VOCAB` plus the cov additions. Not the Sheet or `03_tags.R`, for
   the reasons conjoint gave.

## How the first 232 rows were made

A ten-table pilot at the boundaries, put to Ben. Then two blind passes over every
table, from the record fields only (`population` for every group, citation,
`variables`, `notes`), each pass seeing the rules but not the other's answers
or the pilot. Agreement:

| | identical | any shared value |
|---|---|---|
| construct type | 91.4% | 100% |
| sample setting atoms | 96.1% | |
| sample frame atoms | 88.4% | |
| framework | 100% | |
| all three columns | 78.4% | |

The 54 disagreements were settled by hand. The rulings that came out of them,
all applications of core's existing rules rather than new ones:

- **A named population is not a described recruitment.** "High-school students"
  with no account of how they were reached takes its setting and a blank frame
  (core: silence is not `General/non-specific`). This settled the classic
  ability batteries.
- **An online form is not `Internet-based`.** Only an online recruitment channel
  is (a panel, crowdwork, social media, an advert); students surveyed online by
  their university are `Educational`.
- **A diagnosis restricts; a clinic does not.** Patients with one diagnosis or
  procedure are `Clinical, Targeted/specific`; a general-practice or
  psychiatric-outpatient pool is `Clinical, General/non-specific`.
- **A language requirement that only matches the instrument's language is not
  a restriction.**
- **Self-esteem, mindfulness, self-compassion and resilience scales carry
  `Affective/mental health`** (with `Personality` where the pass gave it),
  because that is how core tags the same instruments (RSES, MAAS, SCS, CD-RISC).
- **Coping and rated job performance are `Behavioral`**; problematic
  phone or social-media use is `Behavioral, Affective/mental health`.
- **Team-level data are `Non-person unit`** (`mathieu_2015_cohesion4`, whose n
  counts teams).

## Tables added after the passes

Eleven tables from batch AK (#3646) landed on main while the PR was open. They
were tagged by one rater under the rules above, not by two blind passes; their
`notes` give the non-obvious calls. One of them, `li_2019_fallhealthbelief26`,
is the first table carrying `HBM`. New tables from then on are tagged in
batches: an intake PR need not tag its tables, and CI lists untagged tables
rather than failing on them, so intake is never blocked by tagging.

## Second batch (2026-11-25)

The 155 tables built after the first passes (batches AL to AX) were tagged the
same way: two blind passes from the record fields, adjudicated by hand.

| | identical |
|---|---|
| construct type | 90.3% |
| sample | 83.2% |
| framework | 100% |
| all three columns | 74.2% |

The 41 disagreeing cells (40 tables) were settled by the 11-18 rulings above,
and each settled cell's `notes` says how. Most sample disagreements were one
pass adding `General/non-specific` to a named population with no account of
recruitment, which the "named population" ruling leaves blank. Two calls are
new applications rather than new rules:

- **A quota panel is not `Representative`** even when the source calls it
  nationally representative (`rottweiler_2024_misogyny8`,
  `schnell_2023_maps7`), following `shek_2023_covidmentalhealth22`. Both
  passes had given `Representative`. Random selection of schools or invitees
  (`baceviciene_2020_bodyappr6`, the padmanabhanunni tables) keeps it.
- **A trial cohort reached through the trial is `Program-based`**, also for a
  secondary analysis (`abduljawad_2022_hospice9`, `elam_2021_alcoholprs7`), as
  `dibaj_2025_ber5`. A one-off message experiment is not
  (`zulkiewicz_2024_antiindustry7`).

**Open for Ben (#3564):** dyad and couple tables, where each row is a pair and
the variables are each member's own scores (`nothel_2023_albs10`,
`pirchio_2018_prejudice7`, `schnettler_2024_ftowcdyad6`,
`wang_2021_attachexplore12`). The team ruling covers aggregated team scores,
not this. For now they are tagged as people, which is the reversible choice.

## Still open

- The `cov_standard.qmd` bar and framework list.
- Multi-country survey programmes pooled by country (ISSP, WVS) follow the pooled
  rule (frame blank), although each group is a national sample.
