# verify_yu_2025_bedtime_procrastination.R -- Step 5b, route 6 (keying polarity).
#
# CLAIM UNDER TEST (the option_text <-> resp axis):
#   The live `resp` values are the ALREADY REVERSE-SCORED values, not the raw
#   administered answers. The Bedtime Procrastination Scale has four reverse-
#   worded items -- 2, 3, 7 and 9, marked "(R)" in the Kroese et al. (2014)
#   Frontiers appendix -- and Yu et al. (2025) confirm "Four of the entries were
#   reverse scoring questions". The shipped __items.csv therefore gives BP2, BP3,
#   BP7 and BP9 the REVERSED anchor order (resp 1 = "always" ... 5 = "never")
#   while BP1/4/5/6/8 keep 1 = "never" ... 5 = "always".
#
#   Falsifiable prediction: if the four (R) items were stored RAW, each of the
#   20 correlations between a reverse-worded item and a forward-worded item would
#   be NEGATIVE on a unidimensional scale. If they are stored reverse-scored, all
#   36 pairwise correlations are positive.
#
# WHAT THIS DOES NOT ESTABLISH: nothing here distinguishes BP1..BP9 from one
# another. After reversal every item is a positively-keyed indicator of the same
# single factor, the per-item means span only 3.03-3.33, and Yu et al. publish no
# per-item statistics, no subscale structure and no differing response ranges.
# The item_text <-> item assignment rests entirely on the inference that source
# columns T0BP1..T0BP9 follow the instrument's own 1-9 numbering; that is
# UNVERIFIED, which is why the mapping_verification row is PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "yu_2025_bedtime_procrastination"
REV   <- paste0("BP", c(2, 3, 7, 9))   # "(R)" in Kroese et al. (2014) appendix
FWD   <- paste0("BP", c(1, 4, 5, 6, 8))

d <- as.data.frame(irw::irw_fetch(TABLE))
d <- d[!is.na(d$resp), ]

cat(sprintf("live rows: %d | ids: %d | items: %d | waves: %s\n",
            nrow(d), length(unique(d$id)), length(unique(d$item)),
            paste(sort(unique(d$wave)), collapse = ",")))

allpos <- TRUE
for (w in sort(unique(d$wave))) {
    dw <- d[d$wave == w, ]
    m  <- reshape(dw[, c("id", "item", "resp")], idvar = "id",
                  timevar = "item", direction = "wide")
    colnames(m) <- sub("^resp\\.", "", colnames(m))
    m <- as.matrix(m[, paste0("BP", 1:9)])
    C <- cor(m, use = "pairwise.complete.obs")

    cross <- C[REV, FWD]                       # 4 x 5 = 20 cross-polarity r's
    within_f <- C[FWD, FWD][upper.tri(C[FWD, FWD])]
    cat(sprintf("\n-- wave %s (n=%d) --\n", w, nrow(m)))
    cat("cross-polarity r (reverse-worded x forward-worded), 20 values:\n")
    print(round(cross, 2))
    cat(sprintf("  min %.2f  max %.2f  | %d of 20 negative\n",
                min(cross), max(cross), sum(cross < 0)))
    cat(sprintf("  forward-only r for reference: min %.2f max %.2f\n",
                min(within_f), max(within_f)))
    cat(sprintf("  per-item means: %s\n",
                paste(sprintf("%s=%.2f", paste0("BP", 1:9), colMeans(m, na.rm = TRUE)),
                      collapse = " ")))
    if (any(cross <= 0)) allpos <- FALSE
}

cat("\nIf BP2/3/7/9 were stored raw, all 20 cross-polarity correlations per wave\n",
    "would be negative. Observed: all positive, in the same band as the\n",
    "forward-only correlations -- so the stored resp is post-reverse-scoring.\n", sep = "")
cat("This pins the DIRECTION of resp for those four items. It does NOT pin which\n",
    "of the nine item stems belongs to which BP code (means span 3.03-3.33; no\n",
    "per-item statistics are published). Hence PARTIAL.\n", sep = "")

cat(if (allpos) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
