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

`cdm_timss03` is the one worth a look if anyone is curious: it was expected to
block (TIMSS secure items), and it wrote a CSV instead. Whether it found genuine
released items or was about to ship something it should not have is exactly what
the missing provenance row would have told us.
