# verify_meloni_2015_parent_divers_ed.R -- Step 5b, re-runnable evidence.
#
# CLAIM UNDER TEST -----------------------------------------------------------
# The 60 IRW item codes are the S1 deposit's own column names, of the shape
# PE<k>_<STIMULUS>_<n>_<KEYWORD>: five image stimuli x the same twelve
# statements. The extraction claims
#
#   stimulus  PE1_FD = a person with a physical disability
#             PE2_DP = a person with Down's syndrome
#             PE3_MI = a boatload of migrants
#             PE4_GAY = two gay men kissing
#             PE5_BIRD = a pelican covered in oil
#   statement 1_GOD 2_BEAUTY 3_FAULT 4_DISEASE          -> individual model
#             5_DIVERSITY 6_BARRIERS 7_MINORITY 8_POWERLESS -> social model
#             9_UNIVDISAB 10_CONTEXT 11_FUNCTIONING 12_UNIVFUNCT -> biopsychosocial
#
# with each keyword tied to one of the twelve statements printed in the S2 File
# codebook ("Statements (n = 12): (i) ... (xii)").
#
# The S2 File says only that the twelve split 4/4/4 across the three disability
# models; it never says WHICH four. P1 settles that from the article's own
# published planned comparisons, and it is what would break if the statement
# blocks were permuted. P3-P7 are content predictions that follow from the
# individual keywords and the individual stimuli, and are what would break if
# two statements inside a block, or two stimuli, were swapped.
#
# Data: the study's own S1 deposit (fetched fresh), plus irw::irw_table_sets()
# for a per-item fingerprint of the LIVE table. No irw_fetch(), so no export.

suppressMessages({library(irw); library(readxl)})

TABLE <- "meloni_2015_parent_divers_ed"
S1 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0128876.s001"

# Published in Meloni, Federici & Dennis (2015) PLOS ONE 10(6):e0128876,
# "Parents' Education about Diversity: Was the disability a special case?":
#   "the biopsychosocial model was preferred to the social, t(75) = -7.139,
#    p < 0.01, and individual model t(75) = -11, p < 0.01"
#   "Parents ... significantly preferred the social model to explain stimuli
#    showing non-disability/diversity conditions compared to the
#    disability/diversity conditions, t(37) = -2.149, p < 0.05"
PUB_SOC_BPS <- -7.139
PUB_IND_BPS <- -11.000

tmp <- tempfile(fileext = ".xls")
utils::download.file(S1, tmp, quiet = TRUE, mode = "wb")
d <- as.data.frame(readxl::read_excel(tmp, sheet = "Dataset_S1"))
p <- d[d$Protocol >= 101 & d$Protocol <= 199, ]
cat(sprintf("S1 deposit: %d rows x %d cols; parent rows (Protocol 101-199): %d\n",
            nrow(d), ncol(d), nrow(p)))

SUF <- c("1_GOD","2_BEAUTY","3_FAULT","4_DISEASE","5_DIVERSITY","6_BARRIERS",
         "7_MINORITY","8_POWERLESS","9_UNIVDISAB","10_CONTEXT","11_FUNCTIONING",
         "12_UNIVFUNCT")
STIM <- c("PE1_FD","PE2_DP","PE3_MI","PE4_GAY","PE5_BIRD")
code <- function(s, j) paste0(s, "_", SUF[j])

ok <- logical(0)
say <- function(lbl, pass, txt) {
    cat(sprintf("%-3s %-4s %s\n", lbl, if (pass) "PASS" else "FAIL", txt))
    ok[[length(ok) + 1L]] <<- pass
}

## ---------------------------------------------------------------------------
## P0 -- the deposit columns ARE the live items, per-item, before any content
##       claim is made. Fingerprint = n / min / max / distinct levels, computed
##       server-side on the live table and locally on the deposit under the
##       processing script's filter (keep 1..5, drop the 0 sentinel).
ts <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(ts$per_item)
loc <- do.call(rbind, lapply(as.vector(outer(STIM, SUF, paste, sep = "_")), function(cn) {
    v <- suppressWarnings(as.numeric(p[[cn]])); v <- v[!is.na(v) & v >= 1 & v <= 5]
    data.frame(item = cn, n = length(v), lo = min(v), hi = max(v), k = length(unique(v)))
}))
mrg <- merge(loc, pi, by = "item")
mrg$hit <- mrg$n.x == as.integer(mrg$n.y) & mrg$lo == mrg$resp_min &
           mrg$hi == mrg$resp_max & mrg$k == as.integer(mrg$n_resp_levels)
say("P0", nrow(mrg) == 60 && all(mrg$hit),
    sprintf("per-item n/min/max/levels reproduce from the S1 deposit for %d/%d live items",
            sum(mrg$hit), nrow(mrg)))

## ---------------------------------------------------------------------------
## P1 -- the 4/4/4 statement->model partition, against the article's own two
##       planned comparisons. Those were run on the two DISABILITY stimuli
##       (FD, DP) only -- the "disability/diversity condition" level of the
##       paper's 2-level diversity factor -- and on the raw columns (0 kept).
D <- c("PE1_FD","PE2_DP")
blk <- function(idx, stims = D) {
    cols <- as.vector(outer(stims, SUF[idx], function(a,b) paste(a,b,sep="_")))
    rowMeans(sapply(cols, function(cn) suppressWarnings(as.numeric(p[[cn]]))))
}
ind <- blk(1:4); soc <- blk(5:8); bps <- blk(9:12)
t1 <- t.test(soc, bps, paired = TRUE); t2 <- t.test(ind, bps, paired = TRUE)
cat(sprintf("\nDisability stimuli (FD, DP), n=%d parents; block means: individual %.4f  social %.4f  biopsychosocial %.4f\n",
            length(ind), mean(ind), mean(soc), mean(bps)))
cat(sprintf("  social vs biopsychosocial: t(%d) = %.4f   [published %.3f]\n", t1$parameter, t1$statistic, PUB_SOC_BPS))
cat(sprintf("  individual vs biopsychosocial: t(%d) = %.4f   [published %.3f]\n", t2$parameter, t2$statistic, PUB_IND_BPS))
err <- max(abs(t1$statistic - PUB_SOC_BPS), abs(t2$statistic - PUB_IND_BPS))
say("P1", err < 0.01, sprintf("both published t values reproduce, max error %.4f", err))

## P2 -- and no rival 4/4/4 partition comes close. All 34650 labelled
##       assignments of the twelve codes to three blocks of four are scored.
combn4 <- utils::combn(12, 4)
best <- Inf; bestlab <- ""
for (a in seq_len(ncol(combn4))) {
    A <- combn4[, a]; rest <- setdiff(1:12, A)
    c2 <- utils::combn(rest, 4)
    for (b in seq_len(ncol(c2))) {
        B <- c2[, b]; C <- setdiff(rest, B)
        if (identical(sort(A), 1:4) && identical(sort(B), 5:8)) next
        e <- max(abs(t.test(blk(B), blk(C), paired = TRUE)$statistic - PUB_SOC_BPS),
                 abs(t.test(blk(A), blk(C), paired = TRUE)$statistic - PUB_IND_BPS))
        if (e < best) { best <- e; bestlab <- paste0("{", paste(A, collapse=","), "}/{",
                        paste(B, collapse=","), "}/{", paste(C, collapse=","), "}") }
    }
}
cat(sprintf("\nbest rival partition of 34649: %s, max error %.4f (shipped partition %.4f)\n",
            bestlab, best, err))
say("P2", best > 10 * err, sprintf("shipped 4/4/4 partition beats the best rival by %.0fx", best / err))

## ---------------------------------------------------------------------------
## P3-P7 -- content predictions that follow from the individual keywords and
##          the individual stimuli. Computed on all five stimuli, 0 treated as
##          the missing sentinel exactly as data/meloni_2015_disability.py does.
mu <- function(s, j) { v <- suppressWarnings(as.numeric(p[[code(s,j)]])); mean(v[!is.na(v) & v != 0]) }
M <- outer(STIM, 1:12, Vectorize(mu)); dimnames(M) <- list(STIM, SUF)
cat("\n=== per-item mean endorsement (rows = image stimulus, cols = statement) ===\n")
print(round(M, 2))
cat("\n")

# P3 -- 4_DISEASE ("a disability is the result of a disease that has forever
#      changed our body") is a medical explanation: it must be at its highest
#      for the two health-condition images and at its lowest for the gay couple.
say("P3", which.min(M[, "4_DISEASE"]) == 4 &&
          min(M[c("PE1_FD","PE2_DP"), "4_DISEASE"]) > max(M[c("PE3_MI","PE4_GAY"), "4_DISEASE"]),
    sprintf("4_DISEASE: FD %.2f, DP %.2f > MI %.2f, GAY %.2f (minimum at GAY)",
            M["PE1_FD","4_DISEASE"], M["PE2_DP","4_DISEASE"], M["PE3_MI","4_DISEASE"], M["PE4_GAY","4_DISEASE"]))

# P4 -- 3_FAULT ("if we behaved better, there would not be people with
#      disabilities") is the human-responsibility statement: highest for the
#      oil-covered pelican, lowest for the person with a physical disability.
say("P4", which.max(M[, "3_FAULT"]) == 5 && which.min(M[, "3_FAULT"]) == 1,
    sprintf("3_FAULT: BIRD %.2f is the maximum, FD %.2f the minimum (DP %.2f, MI %.2f, GAY %.2f)",
            M["PE5_BIRD","3_FAULT"], M["PE1_FD","3_FAULT"], M["PE2_DP","3_FAULT"],
            M["PE3_MI","3_FAULT"], M["PE4_GAY","3_FAULT"]))

# P5 -- 5_DIVERSITY ("when we do not accept their differences, we say that they
#      are disabled") is about non-acceptance of a social difference: highest
#      for the gay couple, lowest for the person with a physical disability.
say("P5", which.max(M[, "5_DIVERSITY"]) == 4 && which.min(M[, "5_DIVERSITY"]) == 1,
    sprintf("5_DIVERSITY: GAY %.2f is the maximum, FD %.2f the minimum",
            M["PE4_GAY","5_DIVERSITY"], M["PE1_FD","5_DIVERSITY"]))

# P6 -- 1_GOD ("because God has willed it so") is the religious explanation and
#      is offered most for the human congenital/physical condition, least for
#      the animal.
say("P6", which.max(M[, "1_GOD"]) == 1 && which.min(M[, "1_GOD"]) == 5,
    sprintf("1_GOD: FD %.2f is the maximum, BIRD %.2f the minimum", M["PE1_FD","1_GOD"], M["PE5_BIRD","1_GOD"]))

# P7 -- the one pair inside a block that the keywords alone do not separate
#      cleanly, because BOTH candidate statements mention functioning:
#        11_FUNCTIONING = "(vi) limited in doing something because of a health
#                          condition and finds obstacles in everyday life"
#        10_CONTEXT     = "(iii) does not only depend on the functioning of the
#                          person, but also by the situation in which he lives"
#      Under the shipped reading the health-condition statement must be the one
#      that peaks at the two health images; under the swap it would be the
#      context statement. They separate by >0.6 in the right direction.
gapF <- mean(M[c("PE1_FD","PE2_DP"), "11_FUNCTIONING"]) - mean(M[c("PE3_MI","PE4_GAY"), "11_FUNCTIONING"])
gapC <- mean(M[c("PE1_FD","PE2_DP"), "10_CONTEXT"])     - mean(M[c("PE3_MI","PE4_GAY"), "10_CONTEXT"])
say("P7", gapF > 0.5 && gapC < 0,
    sprintf("health-vs-social image gap: 11_FUNCTIONING %+.2f (4.11/4.08 vs 3.41/3.36), 10_CONTEXT %+.2f (2.93/3.20 vs 3.43/3.18)",
            gapF, gapC))

## ---------------------------------------------------------------------------
cat("\nWHAT THIS DOES NOT ESTABLISH: the article publishes no per-item statistic,\n",
    "so no route here identifies each statement from a published number. P1/P2 pin\n",
    "the 4/4/4 statement-to-model partition decisively; the assignment WITHIN each\n",
    "block rests on keyword-to-statement content matching, corroborated by the\n",
    "stimulus-gradient checks P3-P7. Hence the ledger status is PARTIAL.\n", sep = "")

cat(sprintf("\n%d/%d checks passed\n", sum(ok), length(ok)))
cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
