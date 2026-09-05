# verify_de_vries_2022_hexaco_other.R
#
# This table is BLOCKED: no item text was shipped (the HEXACO-PI-R wording is
# published only by its rights holder, whose terms restrict it to non-profit
# academic research, and the 200-item-pool numbering the codes use is released
# only on request). So there is no item_text<->item mapping to verify.
#
# What this script re-runs is the finding that made the mapping unrecoverable in
# the first place, and it is falsifiable: the 96 live codes are 24 HEXACO facets
# x exactly 4 items, but the within-facet index runs over 1-8, not 1-4. If the
# indices were 1..4 per facet, the published 100-item HEXACO-PI-R form could be
# mapped positionally and this table would not be blocked on recoverability.
#
# Uses irw_table_sets() (server-side aggregates), NOT irw_fetch() -- the item set
# is all this needs and the corpus sits against a 200GB/30-day export cap.

suppressMessages(library(irw))

TABLE <- "de_vries_2022_hexaco_other"

s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
items <- sort(s$items)

cat(sprintf("live item codes: %d | resp set: %s\n",
            length(items), paste(sort(s$resp), collapse = ",")))

m <- regmatches(items, regexec("^P([OCAXEH])([a-z]+)([0-9]+)$", items))
ok_parse <- all(vapply(m, length, 1L) == 4L)
cat(sprintf("codes parsing as P<HEXACO letter><facet><index>: %d of %d\n",
            sum(vapply(m, length, 1L) == 4L), length(items)))

facet <- vapply(m, function(x) paste0(x[2], x[3]), "")
idx   <- as.integer(vapply(m, function(x) x[4], ""))

per_facet <- table(facet)
cat(sprintf("distinct facets: %d | items per facet: %s\n",
            length(per_facet), paste(sort(unique(per_facet)), collapse = ",")))

cat("\nwithin-facet index sets (first 8 facets shown):\n")
for (f in head(sort(unique(facet)), 8))
    cat(sprintf("  %-6s %s\n", f, paste(sort(idx[facet == f]), collapse = ",")))

cat("\nindex frequency across all 96 items:\n")
print(table(idx))

max_idx <- max(idx)
n_facets_1to4 <- sum(vapply(split(idx, facet),
                            function(v) identical(sort(v), 1:4), TRUE))
cat(sprintf("\nmax within-facet index: %d (would be 4 if the 100-item form's 4-per-facet numbering)\n",
            max_idx))
cat(sprintf("facets whose 4 indices are exactly 1,2,3,4: %d of %d\n",
            n_facets_1to4, length(per_facet)))

cat("\nNote: this establishes each item's FACET and that no 1-4 positional map onto\n",
    "the published 100-item HEXACO-PI-R exists. It establishes NO item wording, and\n",
    "none was shipped -- the table is blocked on the rights holder's non-commercial\n",
    "clause, which no data check can settle either way.\n", sep = "")

pass <- ok_parse &&
        length(per_facet) == 24 && all(per_facet == 4) &&
        max_idx == 8 && n_facets_1to4 < 24

cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
