# Quarantined batch_018 output — 2026-09-03 rate-limit incident

Eight of batch_018's twelve agents were terminated mid-run by an account-wide
monthly spend limit (HTTP 429, session reset 19:50 PT). Three of them had already
written an `__items.csv` but died before writing provenance or verification.

**These files are NOT trustworthy and must not be merged or shipped.** They were
never gated, never recorded, and in at least one case the agent's last words were
"Now I'll build the CSV", so the file may be a partial write. An items CSV with no
provenance row is indistinguishable from a finished one at merge time, which is
why they are here rather than in the batch directory.

The three tables were returned to `pending` and will be re-extracted from scratch.
Nothing here should be reused; it is kept only so the incident is inspectable.

## Update 2026-09-05 — two of the three were promoted, one was not

The blanket warning above turned out not to fit two of these files, and saying so
here matters more than keeping the warning tidy.

`carver_2017_puggs_pilot1_det_core` and `carver_2017_puggs_pilot2_genom_know` were
**not** ungated: batch_018 carried full `provenance.csv` rows for both (note,
`public_note`, `uploaded=2026-09-03`), `mapping_verification.csv` records both
VERIFIED, and the round log's batch_018 triage lists both as staged into
`itemtables/clean/` with the record counts they actually have. What went wrong was
the opposite of what this README assumed: they were stamped as uploaded and never
reached `irw_text`. The loss surfaced on 2026-09-05 only because both still had
entries on the public issues page describing text nobody could fetch.

Both were re-checked against the round log's own discriminating evidence before
being copied back into `itemtables/clean/`:

- `pilot1_det_core` — 52 records, 13 items Q1-Q13, resp 1-4. Q3 is "Eating habits
  and physical exercise can play an important role in preventing and controlling
  diabetes" and is the highest-mean item in the live response data (3.78, against
  the log's predicted ~3.8). Q7 is "Traits and diseases caused by a single gene are
  not very common" — the statement the S3 questionnaire numbers 2 and the S4 Code
  Book numbers 7, which is the marker that separates the two numberings. The file
  carries the Code Book numbering, which is the one triage proved correct.
- `pilot2_genom_know` — 32 records, 16 items Q10-Q25 as the provenance describes,
  resp 0/1 with `correct_response` populated, matching its public note that `resp`
  is a correctness score rather than the student's answer.

What is *not* proven is byte-identity with the staged copy, which was deleted after
the upload that never happened. The claim is narrower and sufficient: these files
carry the right mapping, item set, record count and schema, and pass the
discriminating content test against live response data.

`cdm_timss03` stays quarantined. It is the file this README was really written
about — it wrote a CSV when it was expected to block on TIMSS secure items, and it
has no provenance row to say which it did.

`cdm_timss03` is the one worth a look if anyone is curious: it was expected to
block (TIMSS secure items), and it wrote a CSV instead. Whether it found genuine
released items or was about to ship something it should not have is exactly what
the missing provenance row would have told us.
