# verify_mobility.R -- Step 5b route 1 (per-item source statistics), exact-count form.
#
# CLAIM: IRW item_N carries the text documented for column "Item N" of ltm::Mobility.
# The IRW table was built from that data frame, so the falsifiable prediction is that
# each live item's endorsement COUNT equals the colSums of the matching source column.
# All eight source counts are pairwise DISTINCT (6745, 2651, 6349, 3080, 586, 939,
# 448, 732), so any permutation of the eight item codes -- including a swap of the two
# nearest, item_5 (586) and item_8 (732) -- breaks the match. That is what makes this
# a mapping check rather than a count check.
#
# The item TEXT comes from ltm's Mobility.Rd, which enumerates "Item 1" .. "Item 8"
# with the same labels the data frame uses as column names, so pinning code -> column
# pins code -> text.

suppressMessages(library(irw))
suppressMessages(library(ltm))

TABLE <- "mobility"
data(Mobility)

src_n  <- colSums(Mobility)                 # names: "Item 1" .. "Item 8"
src_nn <- nrow(Mobility)

d <- irw::irw_fetch(TABLE)
live_n  <- tapply(d$resp, d$item, sum)[paste0("item_", 1:8)]
live_nn <- tapply(d$resp, d$item, length)[paste0("item_", 1:8)]

cat(sprintf("source rows: %d ; live rows per item: %s\n\n",
            src_nn, paste(unique(live_nn), collapse = ",")))
cat(sprintf("%-8s %-8s %10s %10s %8s\n", "live", "source", "src_yes", "live_yes", "diff"))
ok <- TRUE
for (i in 1:8) {
    d_i <- live_n[i] - src_n[i]
    if (!isTRUE(all.equal(as.numeric(live_n[i]), as.numeric(src_n[i])))) ok <- FALSE
    cat(sprintf("%-8s %-8s %10d %10d %8d\n",
                paste0("item_", i), paste("Item", i),
                as.integer(src_n[i]), as.integer(live_n[i]), as.integer(d_i)))
}

cat(sprintf("\nsource counts pairwise distinct: %s (min gap %d)\n",
            length(unique(src_n)) == 8L, min(diff(sort(src_n)))))
cat(sprintf("row count agrees for every item: %s\n",
            all(live_nn == src_nn)))

# What this does NOT establish: nothing about the wording itself -- Mobility.Rd's
# English is a third-party rendering of a survey administered in Bengali (see
# provenance). It establishes only that code item_N indexes source column "Item N",
# which is the item the Rd's "Item N" entry describes.

cat(if (ok && all(live_nn == src_nn)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
