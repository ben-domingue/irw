# verify_queiros_2018_qcae.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: live item code QCAE_<n> carries the Portuguese item numbered
# <n> in the study's S1 File (PLOS ONE 10.1371/journal.pone.0197755.s001), and
# resp 1..4 = "Discordo Fortemente" .. "Concordo Fortemente".
#
# The S1 File numbers the 31 Portuguese items 1..31 and the source .xls columns
# are QCAE_1..QCAE_31, so the tie is a number match, not an order inference.
# What follows tests that number match against the data.
#
# Routes: 3 (published composite totals, exact), 6 (keying polarity),
#         7 (marker item), 1 (cross-study per-item mean profile).

suppressMessages(library(irw))

TABLE <- "queiros_2018_qcae"
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
q <- function(i) w[[paste0("QCAE_", i)]]
cat(sprintf("live table: %d rows, %d respondents, %d items, resp %d-%d\n\n",
            nrow(d), nrow(w), length(unique(d$item)), min(d$resp), max(d$resp)))

# ---------------------------------------------------------------------------
# ROUTE 3 -- published composite totals, exact.
# Tables F in S1 File are SPSS GLM tables for seven composites. SPSS prints the
# uncorrected "Total" sum of squares (sum of y^2) and the "Corrected Total"
# (sum of (y - ybar)^2), both to three decimals -- two independent published
# quantities per composite. Reproducing them requires the right item MEMBERSHIP,
# the right REVERSE SET {1,2,17,29} and the right RESPONSE DIRECTION.
# Subscale membership (Reniers et al. 2011; the Portuguese PeR drops item 17):
PT  <- c(15,16,19,20,21,22,24,25,26,27)
OS  <- c(1,3,4,5,6,18,28,30,31)
EC  <- c(8,9,13,14)
PrR <- c(7,10,12,23)
PeR <- c(2,11,29)                       # item 17 dropped, see Results
REV <- c(1,2,17,29)

score <- function(idx) {
    m <- sapply(idx, function(i) if (i %in% REV) 5 - q(i) else q(i))
    rowSums(m)
}
PUB <- list(                            # composite = c(Total SS, Corrected Total SS)
    "QCAE_TOTAL"              = c(4695751, 60192.849),
    "COGNITIVE EMPATHY"       = c(1953397, 32431.788),
    "AFFECTIVE EMPATHY"       = c( 603834, 15474.826),
    "PERSPECTIVE TAKING"      = c( 538857, 13613.653),
    "ONLINE SIMULATION"       = c( 446206,  8951.594),
    "EMOTION CONTAGION"       = c(  80490,  2934.121),
    "PROXIMAL RESPONSIVITY"   = c(  84650,  2614.235),
    "PERIPHERAL RESPONSIVITY" = c(  43818,  2958.100))
SETS <- list(c(PT,OS,EC,PrR,PeR), c(PT,OS), c(EC,PrR,PeR), PT, OS, EC, PrR, PeR)

cat("-- ROUTE 3: S1 File Tables F (SPSS GLM), published vs recomputed --\n")
cat(sprintf("%-24s %14s %14s %14s %14s\n", "composite",
            "pub TotalSS", "obs TotalSS", "pub CorrTotal", "obs CorrTotal"))
r3_worst_ss <- 0; r3_worst_cs <- 0
for (k in seq_along(PUB)) {
    v <- score(SETS[[k]])
    ss <- sum(v^2); cs <- sum((v - mean(v))^2)
    p  <- PUB[[k]]
    cat(sprintf("%-24s %14.0f %14.0f %14.3f %14.3f\n", names(PUB)[k], p[1], ss, p[2], cs))
    r3_worst_ss <- max(r3_worst_ss, abs(ss - p[1]))
    r3_worst_cs <- max(r3_worst_cs, abs(cs - p[2]))
}
cat(sprintf("largest |diff|: Total SS %.3f, Corrected Total %.4f\n", r3_worst_ss, r3_worst_cs))

# Falsification: the same arithmetic with the response direction flipped.
score_flip <- function(idx) {
    m <- sapply(idx, function(i) { x <- 5 - q(i); if (i %in% REV) 5 - x else x })
    rowSums(m)
}
vf <- score_flip(c(PT,OS,EC,PrR,PeR))
cat(sprintf("falsification -- QCAE_TOTAL with resp direction flipped: Total SS %.0f (published %.0f)\n\n",
            sum(vf^2), PUB[["QCAE_TOTAL"]][1]))

# ---------------------------------------------------------------------------
# ROUTE 6 -- keying polarity. Items are stored RAW here (the deposit's *_R
# recodes were dropped by the IRW build), so the four reverse-WORDED items must
# be exactly the four that correlate NEGATIVELY with their own subscale score.
# The "rest" score is the other items of the subscale, each put the right way up
# (so it is a construct score, not a mixed-direction sum -- Peripheral
# Responsivity is three-quarters reverse-worded and a raw rest-sum there is
# near-zero by construction). The S1 File's Portuguese wording marks 1, 2, 17
# and 29 as the negated items.
cat("-- ROUTE 6: raw item vs reverse-corrected subscale rest --\n")
subs <- list(PT = PT, OS = OS, EC = EC, PrR = PrR, PeR = c(2,11,17,29))
neg <- c()
for (nm in names(subs)) {
    idx <- subs[[nm]]
    for (j in seq_along(idx)) {
        rest <- setdiff(idx, idx[j])
        rs <- rowSums(sapply(rest, function(i) if (i %in% REV) 5 - q(i) else q(i)))
        r <- cor(q(idx[j]), rs)
        cat(sprintf("  %-4s QCAE_%-3d r(raw item, rest score) = %+.3f%s\n", nm, idx[j], r,
                    if (idx[j] %in% REV) "   <- reverse-worded in S1 File" else ""))
        if (r < 0) neg <- c(neg, idx[j])
    }
}
r17 <- cor(q(17), rowSums(sapply(c(2,11,29), function(i) if (i %in% REV) 5 - q(i) else q(i))))
cat(sprintf("negatively-keyed items observed: {%s}; S1 File reverse set: {%s}\n",
            paste(sort(neg), collapse = ","), paste(sort(REV), collapse = ",")))
cat(sprintf("QCAE_17 is the exception at r = %+.3f -- it is unrelated to its own subscale in\n", r17))
cat("this sample, which is exactly why the paper excluded it from every composite; the\n")
cat("expected polarity split is therefore {1,2,29} negative and QCAE_17 ~ 0.\n\n")

# ---------------------------------------------------------------------------
# ROUTE 7 -- marker item. The paper drops exactly one item (17) from every
# published composite "due to an extremely low loading value", so QCAE_17 must
# be the one item whose item-rest correlation inside its own subscale is
# essentially zero. This pins item 17 individually.
per <- c(2, 11, 17, 29)
mp  <- sapply(per, function(i) if (i %in% REV) 5 - q(i) else q(i))
rr  <- sapply(seq_along(per), function(j) cor(mp[, j], rowSums(mp[, -j, drop = FALSE])))
cat("-- ROUTE 7: marker item -- Peripheral Responsivity item-rest (reverse-scored) --\n")
for (j in seq_along(per)) cat(sprintf("  QCAE_%-3d r = %+.3f\n", per[j], rr[j]))
r7_ok <- which.min(rr) == which(per == 17) && rr[which(per == 17)] < 0.10
cat(sprintf("weakest item = QCAE_%d (paper drops item 17)\n\n", per[which.min(rr)]))

# ---------------------------------------------------------------------------
# ROUTE 1 -- cross-study per-item mean profile. gomez_2022_qcae ties number to
# English wording independently, through its deposit's numbered SPSS variable
# labels (mapping_basis data_labels for 27 of its 31 items). If QCAE_<n> here
# were a different item than QCAE<n> there, the mean profiles would not track.
# Its four *r columns are stored already reversed, so reverse ours to compare.
cat("-- ROUTE 1: per-item mean profile vs gomez_2022_qcae (independent number->text tie) --\n")
g <- try(irw::irw_fetch("gomez_2022_qcae"), silent = TRUE)
r1_ok <- NA
if (inherits(g, "try-error")) {
    cat("  gomez_2022_qcae unavailable -- route skipped (not required for the verdict)\n\n")
} else {
    gm <- tapply(g$resp, g$item, mean)
    num <- as.integer(sub("^QCAE0*([0-9]+)r?$", "\\1", names(gm)))
    gm <- gm[order(num)]; num <- sort(num)
    ours <- sapply(num, function(i) mean(if (i %in% REV) 5 - q(i) else q(i)))
    cat(sprintf("%-8s %10s %10s %8s\n", "item", "queiros", "gomez", "diff"))
    for (j in seq_along(num))
        cat(sprintf("QCAE_%-3d %10.3f %10.3f %8.3f\n", num[j], ours[j], gm[j], ours[j] - gm[j]))
    rp <- cor(ours, gm)
    cat(sprintf("profile correlation over %d items: r = %.3f; max |diff| = %.3f\n",
                length(num), rp, max(abs(ours - gm))))
    # within-subscale permutation reference
    set.seed(1)
    for (nm in names(subs)) {
        idx <- subs[[nm]]; k <- match(idx, num)
        base <- sum((ours[k] - gm[k])^2)
        perm <- replicate(20000, { p <- sample(k); sum((ours[p] - gm[k])^2) })
        cat(sprintf("  %-4s identity SSE %.3f beats %.1f%% of within-subscale permutations\n",
                    nm, base, 100 * mean(perm > base)))
    }
    r1_ok <- rp > 0.70
    cat("\n")
}

# ---------------------------------------------------------------------------
cat("WHAT THIS DOES NOT ESTABLISH: it does not separate every item from every\n",
    "other item. Route 3 is a SUM and is therefore permutation-invariant WITHIN a\n",
    "subscale; routes 6 and 7 pin a polarity class and item 17; route 1 is a\n",
    "profile of noisy cross-sample means. Within-subscale identity rests on the\n",
    "number match between the S1 File's numbered items and the QCAE_<n> columns,\n",
    "corroborated but not proved by the data. Hence PARTIAL, not VERIFIED.\n", sep = "")

ok <- r3_worst_ss < 0.5 && r3_worst_cs < 0.01 &&
      identical(sort(unique(neg)), c(1, 2, 29)) && abs(r17) < 0.10 && isTRUE(r7_ok) &&
      (is.na(r1_ok) || isTRUE(r1_ok))
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
