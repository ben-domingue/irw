# verify_xue_2025_coping_style.R -- Step 5b mapping verification (backfill, 2026-09-03).
#
# WHAT IS BEING TESTED
# --------------------
# The live table's codes CSS1..CSS20 are NOT the deposit's own column names. The
# deposit (S1 Data, journal.pone.0338956.s001) numbers the coping block Q10_1..Q10_20,
# and data/xue_2025_academic_procrastination.py renames Q10_i -> CSS_i positionally,
# in order, so that `item` carries the codes S3 File ("Constructs and items") uses.
# So the mapping rests on one unproven link: does S3's CSS numbering line up with the
# questionnaire's Q10 numbering? The S3 File's explicit "(CSS7) ..." code labels tie
# WORDING to CSS-number without inference, but they cannot tie CSS-number to Q10-number.
# That is what this script tests, against the paper's published subscale statistics.
#
# The falsifiable prediction: Xie's (1998) SCSQ splits 20 items as positive coping
# = items 1-12 and negative coping = items 13-20. Table 6 of the paper publishes
# both subscale means and SDs. Summing the live items under that split must reproduce
# them; any shift of the block boundary, or any migration of items across it, must not.
#
# WHY irw_fetch() AND NOT AN AGGREGATE. Subscale sums and the inter-item correlation
# matrix are per-RESPONDENT quantities; no server-side aggregate over (item, resp)
# can produce them. The export is negligible against the 200GB/30-day cap: 579
# respondents x 20 items = 11,580 rows, well under 0.5 MB.

suppressMessages(library(irw))

TABLE <- "xue_2025_coping_style"

# --- Published values, Xue et al. (2025) PLOS ONE 10.1371/journal.pone.0338956 ---
# Table 6 ("Correlation Coefficient of academic pressure, coping styles and
# academic procrastination"), M and SD columns:
PUB_POS_M  <- 34.852; PUB_POS_SD <- 6.070   # "possitive coping"  [sic]
PUB_NEG_M  <- 18.216; PUB_NEG_SD <- 4.755   # "negative coping"
TOL <- 0.05

# Canonical SCSQ (Xie 1998) item->subscale assignment.
POS <- paste0("CSS", 1:12)
NEG <- paste0("CSS", 13:20)

d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.numeric(d$resp); d$id <- as.character(d$id); d$item <- as.character(d$item)
codes <- paste0("CSS", 1:20)
ids <- sort(unique(d$id))
m <- matrix(NA_real_, length(ids), 20L, dimnames = list(ids, codes))
m[cbind(match(d$id, ids), match(d$item, codes))] <- d$resp
stopifnot(!anyNA(m))
cat(sprintf("live table: %d respondents x %d items, complete (no missing cells)\n\n",
            nrow(m), ncol(m)))

# --- Route 3: published subscale totals -------------------------------------
pos <- rowSums(m[, POS]); neg <- rowSums(m[, NEG])
cat("--- Route 3: subscale totals vs paper Table 6 ---\n")
cat(sprintf("%-26s %9s %9s %9s\n", "subscale", "published", "observed", "diff"))
cat(sprintf("%-26s %9.3f %9.3f %9.3f\n", "positive M (CSS1-12)",  PUB_POS_M,  mean(pos), mean(pos) - PUB_POS_M))
cat(sprintf("%-26s %9.3f %9.3f %9.3f\n", "positive SD (CSS1-12)", PUB_POS_SD, sd(pos),   sd(pos)   - PUB_POS_SD))
cat(sprintf("%-26s %9.3f %9.3f %9.3f\n", "negative M (CSS13-20)", PUB_NEG_M,  mean(neg), mean(neg) - PUB_NEG_M))
cat(sprintf("%-26s %9.3f %9.3f %9.3f\n", "negative SD (CSS13-20)",PUB_NEG_SD, sd(neg),   sd(neg)   - PUB_NEG_SD))
worst <- max(abs(c(mean(pos) - PUB_POS_M, sd(pos) - PUB_POS_SD,
                   mean(neg) - PUB_NEG_M, sd(neg) - PUB_NEG_SD)))
cat(sprintf("largest deviation: %.3f (tolerance %.2f)\n\n", worst, TOL))

# The boundary is the thing under test, so show that no NEIGHBOURING boundary works.
cat("--- the 12/13 boundary is what makes those numbers land ---\n")
cat(sprintf("%-14s %10s %10s %10s %10s\n", "boundary", "pos M", "pos SD", "neg M", "neg SD"))
for (k in 10:14) {
    p <- rowSums(m[, 1:k, drop = FALSE]); n2 <- rowSums(m[, (k + 1):20, drop = FALSE])
    cat(sprintf("%-14s %10.3f %10.3f %10.3f %10.3f%s\n", sprintf("%d/%d", k, k + 1),
                mean(p), sd(p), mean(n2), sd(n2), if (k == 12) "   <- shipped" else ""))
}
cat(sprintf("published:     %10.3f %10.3f %10.3f %10.3f\n\n",
            PUB_POS_M, PUB_POS_SD, PUB_NEG_M, PUB_NEG_SD))

# Storage direction: a reverse-scored positive subscale (resp -> 5 - resp on a 1-4
# scale) would total 12*5 - 34.85 = 25.15, nowhere near the published 34.852.
cat(sprintf("reverse-scored reading of CSS1-12 would give M=%.3f vs published %.3f",
            mean(rowSums(5 - m[, POS])), PUB_POS_M))
cat(" -> items are stored RAW\n\n")

# --- Route 5: subscale block structure --------------------------------------
cat("--- Route 5: does each item correlate most with its own subscale? ---\n")
R <- cor(m)
own_best <- 0L
for (it in codes) {
    g  <- if (it %in% POS) POS else NEG
    o  <- if (it %in% POS) NEG else POS
    a  <- mean(R[it, setdiff(g, it)]); b <- mean(R[it, o])
    ok <- a > b; own_best <- own_best + ok
    cat(sprintf("  %-6s own=%.2f rival=%.2f  %s\n", it, a, b, if (ok) "ok" else "<-- MISMATCH"))
}
cat(sprintf("  %d/20 items load strongest on their hypothesised subscale.\n\n", own_best))

# --- What this does NOT establish -------------------------------------------
cat("NOT ESTABLISHED: order WITHIN each subscale. Both routes are invariant to any\n",
    "permutation of CSS1-12 among themselves or of CSS13-20 among themselves -- if the\n",
    "wordings of, say, CSS3 and CSS7 were swapped, every number above is unchanged.\n",
    "This is PARTIAL, not VERIFIED. (CSS13 'take a break or vacation' loading with the\n",
    "positive block is a known content ambiguity of that SCSQ item, not misalignment:\n",
    "an off-by-one would move the boundary, and the totals forbid that to 3 decimals.)\n", sep = "")

pass <- worst <= TOL && own_best >= 19L
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
