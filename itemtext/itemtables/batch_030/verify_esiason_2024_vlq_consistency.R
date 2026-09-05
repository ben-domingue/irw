# verify_esiason_2024_vlq_consistency.R
#
# This table is BLOCKED ON RIGHTS. No __items.csv was written, so there is no
# item_text <-> item mapping in the corpus to verify. The instrument is the
# Valued Living Questionnaire (Wilson & Groom, 2002), Part 2 (consistency
# ratings). The source study's CC BY deposit (PLOS ONE 10.1371/journal.pone.0300777,
# S1/S2 Data) publishes NO item wording -- the REDCap export's headers are the bare
# codes fam2, marr2, ... -- so the wording could only come from the instrument
# itself, whose own page footer states:
#
#   "Copyright (c) 2002, by Kelly Wilson. You may reproduce and use this form at
#    will for the purpose of treatment and research. You may not distribute it
#    without the express written consent of the author."
#    -- VLQ form, footer of both pages (Wilson & Groom 2002, rev. 4 October 2006)
#
# That is a quotable rights-holder bar on redistribution, which fires
# itemtext_standard.md's 2026-09-04 no-redistribution ruling (the DSES/Fetzer
# "Permission of author required to distribute or copy" case), and that ruling
# explicitly overrides the source deposit's open licence.
#
# WHAT THIS SCRIPT RE-RUNS is the mapping evidence that would support the
# extraction if the block were ever lifted, so that an unblock needs no fresh
# investigation. There are two strands, neither statistical in the first instance:
#
#   (a) EXEMPTION -- self-describing item codes. The IRW item codes ARE the source
#       spreadsheet's column names (data/esiason_2024_nmosd.py melts VLQ_CONSISTENCY
#       by name; no positional assignment), and each is a mnemonic for one of the
#       VLQ's ten published domains, in the instrument's own printed order:
#         fam2 Family / marr2 Marriage / par2 Parenting / fri2 Friends /
#         wor2 Work / edu2 Education / rec2 Recreation / spi2 Spirituality /
#         cit2 Citizenship / phsy2 Physical self-care.
#       A permutation of item_text across these codes could not be silent.
#
#   (b) ROUTE 8 -- semantic coherence of the response data, which is what this
#       script actually TESTS, because (a) is an argument and not a number.
#       Two falsifiable predictions follow from the domain labels alone:
#         P1. Parenting and Marriage are the only two VLQ domains that do not apply
#             to every adult, so par2 and marr2 must carry the FEWEST non-missing
#             responses of the ten.
#         P2. The same study administered the identical ten domains twice, as
#             importance (suffix 1) and consistency (suffix 2). If the mnemonics
#             mean what they say, each consistency item must pair with its OWN
#             importance counterpart -- i.e. same-domain r must beat that item's
#             mean cross-domain r -- for the great majority of domains.
#
# WHAT THIS DOES NOT ESTABLISH: it says nothing about any shipped wording, because
# none was shipped. P1 distinguishes par2/marr2 from the other eight; P2 ties each
# consistency code to its importance twin but cannot prove that "fam" means Family
# rather than some other domain -- only the mnemonic itself does that. The block is
# on the rights clause, not on the mapping.

suppressMessages(library(irw))

TABLE <- "esiason_2024_vlq_consistency"
PAIR  <- "esiason_2024_vlq_importance"

# code -> canonical VLQ domain, and the importance-half code for the same domain.
DOM <- c(fam2 = "Family", marr2 = "Marriage/couples/intimate relations",
         par2 = "Parenting", fri2 = "Friends/social life", wor2 = "Work",
         edu2 = "Education/training", rec2 = "Recreation/fun",
         spi2 = "Spirituality", cit2 = "Citizenship/Community Life",
         phsy2 = "Physical self care")
IMP <- c(fam2 = "fam1", marr2 = "marr1", par2 = "par1", fri2 = "fri1",
         wor2 = "wor1", edu2 = "edu1", rec2 = "rec1", spi2 = "spi1",
         cit2 = "cit1", phsy2 = "phys1")   # note: importance half spells it phys1

d <- irw::irw_fetch(TABLE)
p <- irw::irw_fetch(PAIR)

## ---- P1: which domains do not apply to everyone -----------------------------
n <- table(d$item)[names(DOM)]
cat("P1 -- non-missing responses per consistency item (N ids =",
    length(unique(d$id)), ")\n")
for (i in names(DOM))
    cat(sprintf("  %-6s %-38s n = %2d  mean = %.2f\n", i, DOM[i], n[i],
                mean(d$resp[d$item == i])))
lowest2 <- names(sort(n))[1:2]
cat("  two lowest-n items:", paste(sort(lowest2), collapse = ", "),
    "-- predicted {marr2, par2}\n")
p1 <- setequal(lowest2, c("marr2", "par2"))
cat("  P1:", if (p1) "HOLDS" else "FAILS", "\n\n")

## ---- P2: does each consistency item pair with its own importance twin? ------
wc <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id", timevar = "item",
              direction = "wide")
wp <- reshape(as.data.frame(p[, c("id", "item", "resp")]), idvar = "id", timevar = "item",
              direction = "wide")
names(wc) <- sub("^resp\\.", "", names(wc))
names(wp) <- sub("^resp\\.", "", names(wp))
w <- merge(wc, wp, by = "id")

cat("P2 -- consistency item vs the ten importance items (pairwise complete r)\n")
cat(sprintf("  %-6s %8s %8s %8s   %s\n", "item", "own", "meanOther", "maxOther", "verdict"))
hits <- 0
for (i in names(DOM)) {
    rs <- sapply(unname(IMP), function(j)
        suppressWarnings(cor(w[[i]], w[[j]], use = "pairwise.complete.obs")))
    names(rs) <- names(IMP)
    own   <- rs[[i]]
    other <- rs[setdiff(names(rs), i)]
    ok    <- is.finite(own) && own > mean(other, na.rm = TRUE)
    hits  <- hits + ok
    cat(sprintf("  %-6s %8.3f %8.3f %8.3f   %s\n", i, own,
                mean(other, na.rm = TRUE), max(other, na.rm = TRUE),
                if (ok) "own > mean(other)" else "-"))
}
cat(sprintf("  P2: %d of 10 domains pair with their own importance twin\n", hits))
p2 <- hits >= 8
cat("  P2:", if (p2) "HOLDS (>= 8 of 10)" else "FAILS", "\n\n")

cat("Note: PASS here means the live consistency items behave as the ten named VLQ\n",
    "domains should -- the two domains that do not apply to every adult are the two\n",
    "with the fewest responses, and each domain's consistency rating tracks its own\n",
    "importance rating. It says NOTHING about any shipped item text: none was\n",
    "shipped, because the VLQ's own footer bars redistribution of the form.\n", sep = "")

cat(if (p1 && p2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
