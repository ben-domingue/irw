# beck_2021_iesr (item text) — rights

**Lead, as stated** (harvest query, source `provenance`): text_source=canonical_instrument, uploaded 2026-08-18
(batch_008), source_ref "German IES-R form, (c) Maercker & Schuetzwohl 1998". It has never been checked against
the 2026-09-04 rulings or #1891. Round log L17850 lists it as a knock-on of the IES-R block. L17975–17976 records
Ben's ruling of 2026-09-11: "beck_2021_iesr (German IES-R, (c) Maercker & Schützwohl): research that rights
holder's terms before deciding — no action yet."

## What was checked independently

1. **Live.** It is in irw_text **v28.0 (current)**: 88 rows, 22 items `iesr_1..22`, language German. There are two
   layers of wording:
   - `item_text`, `instructions` and `option_text` hold the German IES-R. These match the UZH PDF verbatim,
     including daß/bißchen/mußte.
   - `item_text_translated` holds **22 of 22 Weiss & Marmar (1997) English IES-R items**, e.g. "Any reminder
     brought back feelings about it.", "I stayed away from reminders of it.", "My feelings about it were kind of
     numb.", "I felt watchful and on guard." The only difference from Weiss's text is that contractions are
     expanded ("did not"). The 2026-09-01 language backfill added this column with text_source
     `official_instrument_english` (`language_backfill/backfill_provenance.csv`). It is the holder's canonical
     English, not the study's own text.
2. **German rights holder's terms.** UZH, Psychopathologie und Klinische Intervention (Maercker's department),
   https://www.psychologie.uzh.ch/de/bereiche/hea/psypath/ForschungTools/Erhebungsverfahren-f%C3%BCr-Forschungs--und-Therapiezwecke.html
   (fetched 2026-09-29, sha256 d7cd649f…b909ad; Wayback 20260516043303), which lists the IES-R form:
   > "Unsere Abteilung hat verschiedene klinische Erhebungsinstrumente entwickelt bzw. unterstützt und validiert.
   > Diese können hier frei heruntergeladen und in der Forschung und klinischen Praxis frei eingesetzt werden."
   > ("…can be freely downloaded here and freely used in research and clinical practice.")

   The form PDF (sha256 f741b93e…755fa) carries only "© Maercker & Schützwohl, 1998". The UZH test description
   PDF has no terms. No fee, no non-commercial clause and no redistribution bar was found. The grant is positive
   but scoped to a purpose ("research and clinical practice"), with no "only" in it.
3. **Register.** Row `IES-R` (verdict `block`; covers "incl. translations/derivatives"; pattern
   `^IES[_-]?R?[_ ]?[0-9]{1,2}$` matches `iesr_n`). Its clause is third-party (CamCOPS: Weiss "declined
   2015-07-28"). Ben ruled on 09-11 to keep it. The 2026-09-08 originator ruling says translations are covered
   derivatives.
4. **Precedent in the same group.** For ali_2021_iesr, Ben ruled a partial withdrawal: remove the canonical Weiss
   preamble and keep "the study's own item wording". That partial withdrawal is still owed. No
   `withdrawals.csv` row exists.

## Verdict

There are two findings with different strengths.
- **English column (Weiss verbatim):** squarely inside the kept IES-R block row. It came from the holder's
  canonical text rather than the study, which is the same basis on which Ali's Weiss preamble is being withdrawn.
  On its own this would be a **partial `withdraw`, high confidence**.
- **German wording:** the evidence is clear. The German holder grants free research and clinical use and states
  no restriction. The policy is not clear, because two readings conflict. (a) The IES-R row plus the 09-08
  originator ruling means Weiss's block reaches an authorised translation, so everything is withdrawn. (b) Under
  the #1897 silence rule and the UZH grant, the German text ships. A related question is whether "free for
  research and clinical practice" is a scoped use restriction under the HEXACO rule.

- **proposed_outcome:** `needs_ruling`. Recommend deciding it together with ali_2021_iesr. The default if the
  ruling is (a): withdraw the whole table. If (b): partial withdrawal of the `*_translated` English columns.
- **confidence:** high on the facts. The outcome turns on policy.
- **group:** `rights:IES-R`
- **minutes:** ~30 · **redivis_reads:** rows:88
