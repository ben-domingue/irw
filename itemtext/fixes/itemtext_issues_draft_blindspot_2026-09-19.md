# Issues-page entries owed from the no-`public_note` audit, 2026-09-19

Found by screening the 182 live item-text tables that carry an EMPTY `public_note` and are
therefore invisible to `check_issues_page.R`, which builds its whole inventory from
`public_note` (the `short_dark_triad` / `yin_2022_gad7` blind spot). 27 of the 182 were
candidates on structured fields; 10 already had hand-written entries, 3 were already recorded
drops, and 14 were unaccounted for. These are the 3 of those 14 that clear the bar. The other
7 went into `fixes/issues_page_dropped.csv`; 3 (`ali_2021_phq9`, `conner_2017_lot`,
`pemaiw_qiu_2020_dass`) are pilot-era backfills whose code->text derivation was never recorded
and need a mapping re-check before they can be ruled either way; 1 (`cucchi_2018_pts`) is an
IRI rights matter, not a page entry, and its withdrawal has ALREADY SHIPPED.

CORRECTION, same day: `cucchi_2018_pts` was first reported here as still published, on the
strength of `live_tables.csv`, which lists it as `published` in `irw_text`. It is not.
`get_itemtext` against irw_version 393 (released 2026-09-19T15:05:07Z) returns
`available: false`, 0 items -- the IRI withdrawal shipped. The snapshot file is dated
2026-09-19 and its mtime is later than that release, so it over-reports a withdrawn table
rather than merely lagging; treat a `published` row in it as a claim to verify, not a fact,
and re-run refresh_live_tables.py. The three tables the entries above describe WERE each
confirmed live against v393 by the same route.

DO NOT paste while datapages/irw#212 is open -- it appends at the same closing marker.
Backfill the `public_note` for each of these three in its provenance row at the same time,
or the checker stays blind to them and they will not appear in its tally.

```yaml
- table: ali_2021_isi
  issue: |-
    The item text is the canonical Insomnia Severity Index wording (Morin et al., 2011), not the
    wording in the study's own S1 File. The extraction silently normalised the source's column
    headers toward the canonical form, so six of the seven shipped items differ from the deposit:
    the source reads "Difficult falling asleep", "Difficult staying asleep" and "Problems waking
    up too early" where the shipped text reads "Difficulty falling asleep", "Difficulty staying
    asleep" and "Problem waking up too early". Those headers are abbreviated spreadsheet labels
    rather than administered sentences, so neither form is certainly what respondents read, and
    the instructions are the standard ISI preamble because the study publishes none. Items 1-3
    carry fewer responses (103/94/105 against 167-168) because those severity anchors are
    sometimes skipped as inapplicable.
- table: ojelabi_2019_sf36
  issue: |-
    The item text is the canonical RAND 36-Item Health Survey 1.0 wording, transcribed from RAND's
    own instrument page, not from the study: the article publishes no item wording and the PLOS S1
    workbook's headers are bare codes sf1..sf36 with no variable labels. Which canonical item each
    code carries is therefore an IRW reconstruction rather than anything the source states. It is
    verified two ways -- per-item response ranges reproduce the SF-36's block structure exactly
    (0 out-of-range responses, while all 35 cyclic shifts of the mapping produce 2-23 violations),
    and the workbook's own SF-6D health-state code is an exact function of the SF-6D input items
    under this numbering -- but a reader should know it was solved rather than read off a key. Two
    shipped option lists are one level wider than the sample used: sf21 never takes "Very severe"
    pain and sf2 never takes "Much worse".
- table: pierro_2018_selfforgive_s3
  issue: |-
    The item text here is the English wording printed in the study's own PLOS ONE article (its
    rendering of a 4-item adaptation of Wohl et al.'s State Self-Forgiveness Scale), but the scale
    was administered in Italian to 85 Italian respondents and neither the article nor its SPSS
    deposit publishes the Italian form, so these are not the sentences respondents read. Unlike
    the sibling tables pierro_2018_selfforgive_s1 and _s2, the two reverse-worded items
    (sforgiver1 "rejecting of myself", sforgiver3 "dislike toward myself") are stored RAW here,
    not reverse-recoded, so their anchors read as printed; this was confirmed by reproducing the
    paper's published composite. Only the endpoints of the 4-point scale are labelled, so
    option_text is blank for resp 2 and 3. The stem "I feel..." is printed once in the paper and
    is repeated on each item row here so every item carries its own referent.
```
