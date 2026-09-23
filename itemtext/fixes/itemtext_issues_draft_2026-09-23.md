# Issues-page draft — 6 tables uploaded to irw_text_2 on 2026-09-23

Apply after the draft is released. 5 entries for itemtext_issues.qmd, 1 drop for
itemtext/fixes/issues_page_dropped.csv.

## Entries (YAML, paste into the issues list)

```yaml
- table: schmidt_2017_fas
  issue: |-
    The item and response text is the German the study administered, taken from the
    deposited SPSS file's own variable and value labels (including a lowercase first letter
    on the bedroom item and a missing question mark on the holidays item); no printed
    questionnaire is published, so these labels are the only record of the wording. It is
    the study's own German rendering of the HBSC Family Affluence Scale II, not text from
    the HBSC protocol. The English in the `_translated` columns was produced by IRW, not by
    the study's authors.
- table: shin2024_creactability_adaptability
  issue: |-
    The scale was administered in Korean (coaches rating their players), but no Korean
    wording is published, so the item and response text is the English rendering printed in
    the authors' article rather than what raters read. The article lists the three
    adaptability items without numbers, so which wording belongs to Adaptability1-3 follows
    the order listed; the data confirm that order matches the paper's item numbering but
    cannot confirm it for the wording itself.
- table: shin2024_creactability_creativity
  issue: |-
    The scale was administered in Korean (coaches rating their players), but no Korean
    wording is published, so the item and response text is the English rendering printed in
    the authors' article rather than what raters read. The article lists the three
    creativity items without numbers, so which wording belongs to Creativity1-3 follows the
    order listed; the data confirm that order matches the paper's item numbering but cannot
    confirm it for the wording itself. The 'not at all' label for response 1 is absent
    because no rating used it.
- table: shin2024_creactability_quickness
  issue: |-
    The scale was administered in Korean (coaches rating their players), but no Korean
    wording is published, so the item and response text is the English rendering printed in
    the authors' article rather than what raters read. The article lists the three
    quickness items without numbers, so which wording belongs to Quickness1-3 follows the
    order listed; the data confirm that order matches the paper's item numbering but cannot
    confirm it for the wording itself.
- table: wesselmann_2018_drri
  issue: |-
    The five response labels come from the published DRRI-2 form rather than from the
    study, because the deposited SPSS file carries no value labels and the authors' own
    codebook misprints the anchor for 1 as 'Strongly Agree' (it is 'Strongly disagree', as
    the paper states). Item wording is the deposited file's own variable labels, shipped as
    administered; it differs from the DRRI-2 form only in omitting the form's shared
    'During deployment...' stem and the final period on drri2.
```

## Drop (append to fixes/issues_page_dropped.csv, LF, minimal quoting)

```
ngo_2025_green_pbc,"Below the bar, same as its four ngo_2025 siblings: wording is the study's own instrument block matched to the G_PBC columns by printed order; unpublished anchors and an unstated administration language are source gaps, not a text-vs-table mismatch."
```

## Calls worth a second look

- **ngo_2025_green_pbc as a drop.** Its public_note mentions that only an English instrument
  is published for a Vietnamese sample. That is close to the "not what respondents read"
  shape, which does earn entries, but the source never says the survey was in Vietnamese,
  and the four siblings with the same situation were all dropped. Promote it (and the
  siblings) if you read it the other way.
- **shin2024 ×3 are near-identical.** That matches how sibling tables are handled
  elsewhere on the page (e.g. the karajko2025 block), so I kept one entry per table.
