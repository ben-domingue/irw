# Claims strand: notes on RULES.md (pilot, 2 tables)

## Ambiguities and misfits

1. **Strand name.** §1 calls it `claim`, the task called it CLAIMS, and §5 does not list the allowed `strand` values. I used `claim`. §5 should list the values.
2. **The language column is not an issues-page claim.** §1 files language under "claim (issues page, language)", but the outcome table routes `claim_edit` only to `itemtext_issues.qmd`. The bitew finding is a missing `language` value in the item-text table. That is a rebuild of the item text, so it lands as `fix`, which §2 routes to "data/ or itemtext script, then table_changes.csv". Adding metadata to item text is closer to a rebuild than to a response-table fix. Either split `fix` into `fix_data`/`fix_itemtext`, or say explicitly that language backfills are `fix`.
3. **Absent claims.** The tables that predate the 2026-09-01 schema make no language claim at all. So "the public text must match live data" has nothing to test, and the finding is an omission. §1 should say that a missing required field counts as a claim to check.
4. **Stale leads.** The #1646 list says "pre-2026-08-17 and never re-checked", but gilbert_meta_35's callout was rewritten on 2026-08-25. The rules should require checking the site repo's `git log -S<table> -- itemtext_issues.qmd` first and recording which wording was audited. Separately, `itemtext/fixes/itemtext_issues_suggestions.md` still holds a drafted replacement that names the wrong four items (i/j/k/l, where the live data omits b/h/k/l). The audit has no outcome for "a draft in our own repo is wrong". I mentioned it in the dossier only; a `housekeeping` note column would help.
5. **`redivis_reads` is one value but both tables used two kinds of read.** Each needed aggregate SQL on the response table plus a row read of the small item-text table. I wrote `aggregate+rows:N`. The schema should allow a combination, or say that item-text rows count separately.
6. **Group granularity.** The bitew fix applies to three sibling tables (tier B), which are not in the pilot. §4 does not say whether a group can pull in tables outside the worklist. I named them in the evidence and did not add rows.
7. **Evidence bar for "no wording is published".** Under the rights rule, "couldn't find" means no restriction. The claims strand has no equivalent rule. I scoped my check to the deposit (as the itemtext skill does) and said so. RULES should set the same scope for claims.
8. **Which copy of the site counts as live.** Three datapages worktrees exist locally, on different branches. I took the public page as authoritative and confirmed it matches `origin/main`. RULES should name the rendered page as the source, with `origin/main` as the fallback.

## Scriptable vs human

**Scriptable** (these took most of the minutes):
- Pull each callout from `origin/main:itemtext_issues.qmd` plus `git log -S` for its last-edit date.
- Per table, per item, run aggregate SQL: n, n_id, min/max resp, and the item set. Diff that against the `irw_itemtext` item set. This alone confirms or refutes every "X of Y items" claim, and did so for gilbert_meta_35.
- Item-rest correlations to check reverse keying against inverted option labels. This is generic: flag any item whose option map is inverted relative to its siblings and check the sign of its correlation.
- Fetch the deposit (Dataverse API `?format=original`, PLOS `type=supplementary`) and count non-Latin script characters. This settles the "is the administered wording in the deposit?" half of every tier-C/B language case.
- Grep the paper's full-text XML for `(Amharic|translated|version of the questionnaire|language)`. That surfaces the administered-language sentence for a human to confirm.

**Needs a human** (or at least a careful reader):
- Deciding whether a sentence like "self-administered Amharic version" really states the administered language. A PLOS abstract can mention a language that was only used for consent, for example.
- Judging whether a claim's *reasoning* ("no wording is published") is still true once someone finds a new source.
- Deciding group scope when siblings sit in another tier or issue.
- Any claim whose truth depends on the order of items in a codebook (the gilbert_meta_35 e/j placement rests on "letter order" plus keying). A script can supply the keying sign, but not the order argument.
