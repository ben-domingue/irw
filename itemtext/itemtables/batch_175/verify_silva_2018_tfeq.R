# verify_silva_2018_tfeq.R -- batch_175
#
# STATUS OF THIS TABLE: BLOCKED on the item-wording rights rule (irw#1945; the
# Pearson Terms of Sale & Use already registered for the SCL family). No
# __items.csv was written. This script banks the MAPPING evidence so that, if the
# TFEQ / Eating Inventory rights position is ever ruled the other way, the next
# round does not have to rebuild it. See notes_silva_2018_tfeq.csv.
#
# Claim: the live item codes TFEQ1, TFEQ6, ... TFEQ50 are the S1 xlsx column names,
# melted unchanged by data/silva_2018_body_image.py, and carry the ORIGINAL
# TFEQ-51 item numbers (Stunkard & Messick 1985). The study's own first-author
# doctoral thesis (Silva WR, UNESP 2017, hdl 11449/152823, Anexo 3 p.163) prints
# the administered Portuguese TFEQ-18 keyed by those same numbers, with
# Falso=0/Verdadeiro=1 for items 1-34, 1-4 anchors for 39/43/48/49 and 0-5 for 50.
#
# Two falsifiable predictions, both of which a permuted mapping would break:
#  (A) Route 2, response-range structure: the 13 items numbered <= 34 are 0/1,
#      items 39/43/48/49 are 1-4, item 50 alone is 0-5.
#  (B) Route 5, subscale block structure: Karlsson et al. (2000) assign
#      Cognitive Restraint = 6,28,33,43,48,50; Emotional Eating = 9,20,27;
#      Uncontrolled Eating = 1,15,19,22,24,26,34,39,49 (PLOS 2018 Instruments
#      section and thesis Anexo 3 footnote). Each item's mean correlation with its
#      own block must exceed its mean correlation with the other two blocks, and
#      every within-block correlation must be positive (which also pins the
#      coding direction: True=1, and the 1-4 / 0-5 anchors ascending as printed).
#
# NOT established: order WITHIN a block among items sharing a response format --
# e.g. TFEQ6 vs TFEQ28 vs TFEQ33 (all 0/1 restraint), TFEQ9/20/27, the seven 0/1
# uncontrolled-eating items, TFEQ43 vs TFEQ48, TFEQ39 vs TFEQ49. So this is PARTIAL
# evidence; the code->text tie rests on the thesis's explicit numbering.

suppressMessages(library(irw))

TABLE <- "silva_2018_tfeq"
BLOCKS <- list(
    CR = c(6, 28, 33, 43, 48, 50),
    EE = c(9, 20, 27),
    UE = c(1, 15, 19, 22, 24, 26, 34, 39, 49)
)
EXPECT_RANGE <- function(n) if (n <= 34) "0-1" else if (n == 50) "0-5" else "1-4"

d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.numeric(d$resp)
ok <- TRUE

cat("(A) response-range structure\n")
cat(sprintf("%-7s %8s %8s %6s\n", "item", "expected", "observed", "n"))
for (n in sort(unlist(BLOCKS))) {
    it <- paste0("TFEQ", n)
    r <- d$resp[d$item == it]
    obs <- sprintf("%g-%g", min(r), max(r))
    lev_ok <- obs == EXPECT_RANGE(n) && length(unique(r)) == (max(r) - min(r) + 1)
    cat(sprintf("%-7s %8s %8s %6d %s\n", it, EXPECT_RANGE(n), obs, length(r),
                if (lev_ok) "" else "<-- MISMATCH"))
    ok <- ok && lev_ok
}

w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
items <- paste0("TFEQ", unlist(BLOCKS))
R <- cor(w[, items], use = "pairwise.complete.obs")
blk <- setNames(rep(names(BLOCKS), lengths(BLOCKS)), items)

cat("\n(B) mean r with own block vs other blocks\n")
cat(sprintf("%-7s %-3s %7s %7s %7s\n", "item", "blk", "CR", "EE", "UE"))
hits <- 0
for (it in items) {
    m <- sapply(names(BLOCKS), function(b) {
        o <- setdiff(names(blk)[blk == b], it)
        mean(R[it, o])
    })
    hit <- names(which.max(m)) == blk[[it]]
    hits <- hits + hit
    cat(sprintf("%-7s %-3s %7.3f %7.3f %7.3f %s\n", it, blk[[it]], m["CR"], m["EE"],
                m["UE"], if (hit) "" else "<-- MISS"))
}
within <- unlist(lapply(names(BLOCKS), function(b) {
    o <- names(blk)[blk == b]
    RR <- R[o, o]
    RR[upper.tri(RR)]
}))
cat(sprintf("\nown-block hits: %d/18; within-block r range %.3f..%.3f (%d pairs)\n",
            hits, min(within), max(within), length(within)))
ok <- ok && hits == 18 && min(within) > 0

cat("Does NOT separate items within a block that share a response format (PARTIAL).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
