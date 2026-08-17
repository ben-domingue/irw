# Draft: Harvard Dataverse allowlist request

**Status:** draft, not sent. Ben to review/edit and send.
**Where to send:** email **support@dataverse.harvard.edu** — that is the
contact route; there is no web form (an earlier version of this file said
there was, which was wrong). Their stated turnaround is within 24 business
hours, Mon-Fri. Contact page: https://support.dataverse.harvard.edu/support
**Alternative worth considering:** they hold open virtual office hours,
Wednesdays 11:00-13:00 ET, RSVP by emailing the same address. For a
"please allowlist our harvester" conversation that may get further faster
than a ticket — it's a policy question, not a bug report.
**Context:** see `BATCH_LOG.md`, 2026-08-17 entry.

Facts below were verified 2026-08-17 and are worth re-checking before
sending, since the block may lift on its own.

---

**Subject:** API access for an academic harvester — Item Response Warehouse
(Stanford)

Hello,

I lead the Item Response Warehouse (IRW), an NSF-supported open-science
project at Stanford that aggregates openly-licensed item-response datasets
into a single standardized format for psychometric research
(https://itemresponsewarehouse.org). Harvard Dataverse has been one of our
most valuable sources — a substantial share of the datasets we have
standardized and credited originate there.

Since roughly 2026-08-14, all programmatic access to dataverse.harvard.edu
from our client returns HTTP 202 with an empty body and the header
`x-amzn-waf-action: challenge`, i.e. an AWS WAF JavaScript bot-challenge.
This affects every endpoint we use:

- `/api/search`
- `/api/datasets/:persistentId`
- `/api/access/datafile/{id}`

We reproduce it from multiple networks and it is not specific to any query,
so we assume it is a general anti-crawler measure rather than anything
targeted at us. We have not attempted to work around the challenge, and we
do not intend to — we would rather be allowlisted, or told what access
pattern you would prefer.

Our client is deliberately conservative and identifies itself:

- User-Agent: `irw-discovery-scout/1.0 (research; contact
  itemresponsewarehouse@stanford.edu)`
- Rate-limited per domain, with pagination capped per query
- Runs on a schedule (roughly weekly/monthly), not continuously
- Reads only published, openly-licensed datasets; we skip anything without
  an explicit open license (CC0 / CC BY / equivalent)
- Every dataset we redistribute is credited with its DOI and original
  license, and links back to the Harvard Dataverse record

Would it be possible to allowlist this client — by User-Agent, by source IP
range, or via an API token, whichever you prefer? We are equally happy to
adjust our request rate, restrict our crawl window, or move to a different
access pattern if that suits your infrastructure better.

If there is a more appropriate contact or a formal process for harvester
registration, I would be glad to be pointed there.

Thank you for maintaining such a valuable resource.

Best regards,
Ben Domingue
Graduate School of Education, Stanford University
itemresponsewarehouse@stanford.edu

---

## Notes before sending

- Confirm the block is still active: `curl -sI https://dataverse.harvard.edu/api/info/version`
  (look for `x-amzn-waf-action: challenge`). If it is gone, no need to send.
- Their support site (`support.dataverse.harvard.edu`) returns 403 Akamai
  "Access Denied" to command-line clients, so it can't be checked from here
  — it loads normally in a browser. Unrelated to the Dataverse WAF block;
  just means don't try to verify the contact page with curl.
- The NSF-support claim and the exact project description should be checked
  against how IRW is normally described publicly — adjust to taste.
- If they ask for specifics: the search connector is
  `from_dataverse()` in `irw_discover_updated.py`; the file-listing and
  download paths are `_dataverse_files()` / `polite_get()` in
  `irw_batch_updated.py`.
