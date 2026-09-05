# verify_de_vries_2022_hexaco_meta.R
#
# This table is BLOCKED on rights: hexaco.org, the only source that publishes the
# HEXACO-PI-R forms, states they may be downloaded "only for the purpose of
# non-profit academic research", and the CC BY PLOS article reproduces just 2 of
# the 96 meta-perception items. No item text was shipped, so there is no shipped
# item_text<->item or option_text<->resp mapping to verify.
#
# What this script makes re-runnable instead is the STRUCTURAL claim recorded in
# provenance/notes: how far the live item codes alone pin the mapping, and where
# they stop. It checks the codes themselves, not counts -- validate_items.R
# already does counts, and a count check would not be evidence.
#
#   ESTABLISHED here : each code names its HEXACO domain AND facet, so a
#                      cross-facet permutation of item text is impossible
#                      (Step 5b exemption 1, self-describing codes).
#   NOT ESTABLISHED  : which of a facet's four HEXACO-100 items each of its four
#                      codes denotes. The within-facet index runs 1-8, i.e. the
#                      200-item HEXACO-PI-R facet numbering, and hexaco.org gates
#                      the 200-item form behind author contact while the public
#                      ScoringKeys_100.pdf lists only 4 items per facet.
#
# Ground truth is read with irw_table_sets() (server-side aggregate), so this
# costs no Redivis export quota.
#
# Run: Rscript verify_de_vries_2022_hexaco_meta.R

suppressMessages(library(irw))

TABLE <- "de_vries_2022_hexaco_meta"

s    <- irw::irw_table_sets(TABLE, source = "core")
live <- sort(s$items)

## --- the 24 HEXACO-PI-R facets, and the domain each belongs to --------------
## (public structure, from hexaco.org's ScoringKeys_100.pdf; Altruism, the
## interstitial 25th facet, is absent from this table by design)
facet_domain <- c(
  sinc = "H", fair = "H", gree = "H", mode = "H",
  fear = "E", anxi = "E", depe = "E", sent = "E",
  sses = "X", socb = "X", soci = "X", live = "X",
  forg = "A", gent = "A", flex = "A", pati = "A",
  orga = "C", dili = "C", perf = "C", prud = "C",
  aesa = "O", inqu = "O", crea = "O", unco = "O"
)

## --- parse: P + domain letter + 4-letter facet + within-facet index ---------
pat    <- "^P([OCAXEH])([a-z]{4})([1-8])$"
parses <- grepl(pat, live)
dom    <- sub(pat, "\\1", live[parses])
fac    <- sub(pat, "\\2", live[parses])
idx    <- as.integer(sub(pat, "\\3", live[parses]))

key      <- paste(dom, fac, sep = "-")
per      <- table(key)
dom_ok   <- sum(facet_domain[fac] == dom)
idx_sets <- tapply(idx, key, function(v) sort(unique(v)))
gt4      <- sum(vapply(idx_sets, function(v) any(v > 4), logical(1)))
is1234   <- names(idx_sets)[vapply(idx_sets,
                function(v) identical(v, 1:4), logical(1))]

cat(sprintf("live item codes                          : %d\n", length(live)))
cat(sprintf("codes matching ^P<domain><facet><1-8>$   : %d\n", sum(parses)))
cat(sprintf("distinct (domain, facet) pairs           : %d\n", length(per)))
cat(sprintf("facets with exactly 4 items              : %d of %d\n",
            sum(per == 4), length(per)))
cat(sprintf("facet abbrev under its correct domain    : %d of %d codes\n",
            dom_ok, length(fac)))
cat(sprintf("Altruism facet present?                  : %s\n",
            if (any(fac %in% c("altr", "alt"))) "YES" else "no (expected)"))
cat(sprintf("facets carrying an index > 4             : %d of %d\n",
            gt4, length(idx_sets)))
cat(sprintf("facets whose index set is exactly {1,2,3,4}: %s\n",
            if (length(is1234)) paste(is1234, collapse = ", ") else "(none)"))
cat("\nwithin-facet index sets (first 6):\n")
for (k in head(names(idx_sets), 6))
  cat(sprintf("  %-8s %s\n", k, paste(idx_sets[[k]], collapse = ",")))

cat("\nExpected (recorded 2026-09-04): 96 live codes, 96 parsed, 24 facet pairs,\n",
    "24 of 24 facets with exactly 4 items, 96 of 96 codes under the right domain,\n",
    "no Altruism, 23 of 24 facets carrying an index > 4 (only C-perf is {1,2,3,4}).\n",
    sep = "")
cat("\nWhat this does NOT establish: nothing about item wording (none was shipped,\n",
    "the table is blocked on rights), and nothing about which HEXACO-100 item each\n",
    "within-facet index 1-8 denotes -- that needs the 200-item form, which the\n",
    "rights holders do not publish.\n", sep = "")

pass <- length(live) == 96 && sum(parses) == 96 && length(per) == 24 &&
        all(per == 4) && dom_ok == 96 && gt4 == 23 &&
        length(is1234) == 1 && is1234 == "C-perf"
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
