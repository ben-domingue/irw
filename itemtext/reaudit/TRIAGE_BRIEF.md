# Brief: IRW item-text re-audit, full triage (irw#2255)

This is the pilot brief (2026-09-19) with three changes, marked **[new]**: an upstream-originator
rights check, a generic User-Agent rule, and the WPAI naming-condition ruling.

IRW (Item Response Warehouse) holds ~4,300 item-response tables. ~1,400 have published item
text (`<table>__items`). This triage covers tables that have NEVER had item text, to find which
could. **You are triaging, not extracting**: do not transcribe item wording beyond a short
quote proving it exists.

Your unit is a **deposit** (one source: a data DOI, paper DOI or data URL), which may cover
several IRW tables. Your slice is a JSON list; each element has `deposit`, `stratum`,
`tables` (name, n_items, n_participants), `refs` (DOIs/URLs/reference), and `old_audit`.
In a large family, still give every table its own verdict: siblings differ.

## What to decide, per table

For each table, one `verdict`:

- `OBTAINABLE` -- you found the item wording (all or nearly all items) at a specific, reachable,
  public source: the paper, its supplement, the deposit's codebook/questionnaire, a data-file
  header or variable labels, or the instrument's own published form. You can say which source
  and where in it (table/appendix/file name). The item codes in IRW must be plausibly mappable to
  it (e.g. counts match n_items). Rights: not blocked (see below), **including upstream**.
- `NOT_PUBLISHED` -- you reached the sources and the wording is not in any of them (e.g. data file
  has only codes Q1..Q20, paper describes the scale without items, no supplement). List what you
  checked.
- `RIGHTS_BLOCK` -- wording exists but its originator (or distributor) reserves a right (below).
  Quote the clause and give the URL and the sha256 of the page you fetched.
- `NOT_ITEM_TEXT` -- the table is not a set of worded items: e.g. reaction-time/physiological
  measures, ratings of unnamed stimuli with no text, model/benchmark outputs with no prompt text,
  sports/game results, simulated data. Say what it is. (A cognitive test whose questions are
  published IS item text.)
- `UNREACHABLE` -- you could not get to the source (paywall with no open copy, captcha, dead
  link, repository down). Not the same as NOT_PUBLISHED: say what blocked you.
- `NEEDS_HUMAN` -- genuinely ambiguous, including any rights case that looks like it would ship
  but rests on a judgment (see below). Say what the decision is, as one question.

## Rights test (current rules -- do not use any older test)

Read `/home/ben/irw-queue-runner/itemtext/.claude/skills/irw-auto-itemtext/SKILL.md`, sections
"Standing exclusion" and "Rights on the wording" (lines ~247-400). Summary:
- The deposit licence governs response data, NOT the instrument's wording.
- Find the instrument's ORIGINATOR and read their terms. Translations/adaptations inherit them.
- A clause that RESERVES A RIGHT blocks: fee, permission required, licence request, non-commercial,
  no-derivatives, no-redistribution, "contact the author for other uses", "free for research use
  only".
- A clause that only DISCLAIMS FITNESS ("not for clinical use") does not block; quote it.
- Silence is permission -- **but only after the upstream check below**. A copyright notice on an
  article is not a term on the instrument.
- First check `/home/ben/irw-queue-runner/itemtext/instrument_rights_register.csv`: a `block` row
  for the instrument settles it as RIGHTS_BLOCK; cite the register row. A name match is a lead,
  confirm by reading the items.
- A `ship`-shaped conclusion that rests on judgment rather than silence -> NEEDS_HUMAN.
- A courtesy request ("please let us know if you use it") attached to a research-use grant blocks.
- **[new] A condition on the instrument's NAME is not a block.** Ruled by Ben 2026-09-19 (WPAI):
  "no permission, no fees" plus "cannot be called the WPAI if questions or responses are changed"
  ships, because IRW reproduces the form unaltered. Contrast "alteration of the wording is not
  permitted" (FATCOD), which is a no-derivatives term and blocks. Quote the clause either way.

### [new] Upstream-originator check -- required before any `silence`

In the checkpoint that tested the pilot's verdicts, **both** rights blocks were one level upstream
of where the pilot stopped, and the pilot had marked both `silence`:
- a scale distributed by a company (PARED Insights, for the RUTIIQ) whose page requires a licence
  request and reserves licensing costs; the paper and the deposit said nothing;
- a climate battery "following Hickman et al. (2021)", whose items come from a CC BY-NC-ND article.

So before writing `rights=silence` for any named or adapted instrument, check and record each of:
1. **The distributor.** Search the instrument's name with "licence", "permission", "request",
   "fee", "distributor". Test publishers, licensing companies (Mapi/ePROVIDE, PAR, Pearson, WPS,
   PARED, Reilly Associates, etc.) and author-run instrument pages all count.
2. **The originating paper.** If the source says the items were adapted, translated, taken or
   "following" another paper, open that paper and read its licence line. CC BY-NC, CC BY-ND and
   CC BY-NC-ND on the originating article block, because the wording originated there.
3. **One more level if the originator itself adapted** (e.g. Wang & Sun -> MSLQ), until you reach
   the wording's first publication or a page that states terms.

Write the chain into `rights`, e.g. `silence (checked: distributor none found; origin Smith 2019
CC BY 4.0)`. A bare `silence` with no chain is incomplete. If an upstream page exists but cannot
be fetched, the verdict is NEEDS_HUMAN, not OBTAINABLE -- say which page.

Study-specific items written by the study's own authors have no upstream; say so
(`silence (own items)`).

## Fetching -- known traps

- **[new] Use a generic User-Agent and put no personal information in any request.** No email
  address, name or institution in headers or query strings -- this includes OpenAlex's and
  Crossref's `mailto=` "polite pool" parameter, which you must not use. With curl use
  `-A "Mozilla/5.0"`; with Python requests set `headers={"User-Agent": "Mozilla/5.0"}`.
  (A pilot agent put an email address in a request header.)
- Use `curl -4` (IPv6 stalls on this machine). Python requests should be fine (IPv4 forced).
- A 200 response is not proof you reached content: OSF returns a JS shell (constant ~4207 bytes of
  CSS, no data); some hosts return captcha/"browser not supported" pages. Check the content.
- figshare: use the API (`https://api.figshare.com/v2/articles/<id>`), not the landing page.
- Dataverse: `https://<host>/api/datasets/:persistentId/?persistentId=doi:...` lists files;
  `/api/access/datafile/<id>` downloads.
- OSF: `https://api.osf.io/v2/nodes/<id>/files/` .
- Crossref/OpenAlex (`https://api.openalex.org/works/doi:<doi>`) give open-access copies of papers.
- **[new, from wave 1]** Hosts that bot-block plain fetches, and what worked instead:
  Zenodo landing pages return 403 to curl, so use the API (`https://zenodo.org/api/records/<id>`, which
  lists files with download links) or the WebFetch tool. For MDPI, Springer (a ~3KB "Client
  Challenge" page) and other publishers, look for a Europe PMC or PMC copy
  (`https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:<doi>&format=json`).
  DataverseNL and some university repositories also block you; say so, and use UNREACHABLE only after
  the API route fails.
- **[new, from wave 1]** Do not use a User-Agent or contact address copied from the repo's processing
  scripts: several carry a personal email address.
- Budget: about 10 fetches per deposit, plus up to 4 for the upstream check. If a deposit needs
  more, give your best verdict and say what a further look would check. Cache downloads under
  your own cache folder (given in your task), never inside the repo.

## The old audit

`old_audit` holds a 2026-08-17 automated audit's verdict for some tables (UNAVAILABLE,
UNAVAILABLE (copyrighted), BLOCKED). **It is known to be unreliable** (it has named the wrong
instrument, cited sources that don't contain wording, and applied a retired rights test). Do not
rely on it. Do your own check first, then record whether you agree: `old_agrees` = yes / no /
na (no old verdict). If no, say why in one line.

## Output

Write the results CSV named in your task, one row per TABLE, columns:
`deposit,table,verdict,instrument,wording_source,evidence,rights,rights_sha256,old_agrees,old_disagree_reason,effort`
- `wording_source`: URL + location (for OBTAINABLE), else blank.
- `evidence`: what you checked and found, one or two sentences.
- `rights`: `register:<instrument>` / `silence (<upstream chain>)` / `quote:"..." <url>` / `n/a`.
- `rights_sha256`: sha256 of the fetched page holding a quoted clause, else blank.
- `effort`: low / medium / high -- how hard a real extraction would be (mapping codes to wording).
Use Python's csv module (QUOTE_MINIMAL). Every table in your slice appears exactly once.

Do NOT edit files in the repo, run git, or touch Redivis. When done, report in under 20 lines:
counts by verdict, count of old-audit disagreements, how many rights calls the upstream check
changed, and anything surprising (table defects, personal data in a source deposit -- list them,
do not act).
