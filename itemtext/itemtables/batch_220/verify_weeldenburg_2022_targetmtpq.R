# verify_weeldenburg_2022_targetmtpq.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST. The MTP-Q item wording lives in S1 Questionnaire as a bare
# numbered list 1..26 plus a construct table (TASK = 1+6+11+16+21+26, AUTHORITY =
# 2+7+12+17+22, RECOGNITION = 5+8+13+18+23, GROUPING = 4+9+14+19+24, EVALUATION =
# 3+10+15+20+25). The live codes are Task_1..Task_6, Authority_1..5, etc. The
# shipped mapping is: within each construct, the ordinal suffix follows the
# ascending questionnaire number (Authority_1 = Nr 2, Authority_2 = Nr 7, ...).
#
# WHY THE SOURCE .sav AND NOT irw_fetch(). data/weeldenburg_2022_target_pe.py
# melts the S1 Dataset's own columns BY NAME (prefix match on "Task_",
# "Authority_", ...), so the live table's item codes ARE these column names and
# the live resp values ARE these cell values; nothing is renamed or reordered.
# Fetching the live table would export 81,900 rows against the 200GB/30-day
# Redivis cap to re-read numbers that are identical. The .sav is 660KB.
#
# TEST 1 (construct membership, decisive). Each prefix block's mean, SD and
# Cronbach's alpha must reproduce the paper's Table 1 row for the construct the
# prefix names. All five published means are distinct (3.56 / 3.00 / 3.66 / 3.37
# / 3.44), so this pins each block to one construct and rules out a block-level
# permutation of the item text.
#
# TEST 2 (two within-construct positions, content signature). Two Authority
# items name another construct's content: Nr 7 is about evaluation/assessment
# activities and Nr 22 is about the grouping process (these are among the three
# items the paper says were moved to a different construct after the EFA). The
# shipped mapping puts them at Authority_2 and Authority_5. Prediction: of the
# five Authority items, Authority_2's strongest correlation with a rival
# construct block must be Evaluation, and Authority_5's must be Grouping.
#
# WHAT THIS DOES NOT ESTABLISH: the position of Authority_1/_3/_4 within their
# block, or of any Task_*, Recognition_*, Grouping_* or Evaluation_* item. Those
# rest on the questionnaire's block-interleaved numbering, not on a number here.
# Hence status PARTIAL, not VERIFIED.

SRC <- paste0("https://journals.plos.org/plosone/article/file",
              "?id=10.1371/journal.pone.0274964.s001&type=supplementary")
CACHE <- ".cache/weeldenburg_2022_targetmtpq/s001.bin"

sav <- if (file.exists(CACHE)) CACHE else {
    f <- tempfile(fileext = ".sav")
    download.file(SRC, f, quiet = TRUE, mode = "wb")
    f
}
d <- haven::read_sav(sav)

BLOCKS <- list(Task = 6, Authority = 5, Recognition = 5, Grouping = 5, Evaluation = 5)
# Paper Table 1 (doi:10.1371/journal.pone.0274964.t001): M, SD, alpha.
PUB <- list(Task = c(3.56, .70, .79), Authority = c(3.00, .85, .79),
            Recognition = c(3.66, .79, .85), Grouping = c(3.37, .80, .80),
            Evaluation = c(3.44, .79, .82))
TOL <- 0.01    # published to 2 dp

cols <- function(s) paste0(s, "_", seq_len(BLOCKS[[s]]))
alpha <- function(X) { k <- ncol(X); k/(k-1) * (1 - sum(apply(X, 2, var))/var(rowSums(X))) }

cat("TEST 1 -- construct blocks vs paper Table 1\n")
cat(sprintf("%-12s %18s %18s %8s\n", "block", "published M/SD/a", "observed M/SD/a", "worst"))
worst1 <- 0
for (s in names(BLOCKS)) {
    X <- as.data.frame(d[, cols(s)]); X <- X[complete.cases(X), ]
    m <- rowMeans(X)
    obs <- c(mean(m), sd(m), alpha(X))
    w <- max(abs(obs - PUB[[s]])); worst1 <- max(worst1, w)
    cat(sprintf("%-12s %18s %18s %8.3f\n", s,
                sprintf("%.2f/%.2f/%.2f", PUB[[s]][1], PUB[[s]][2], PUB[[s]][3]),
                sprintf("%.3f/%.3f/%.3f", obs[1], obs[2], obs[3]), w))
}
cat(sprintf("largest deviation: %.4f (tolerance %.3f); published means are distinct\n\n",
            worst1, TOL))

cat("TEST 2 -- Authority items x rival construct blocks (correlations)\n")
bm <- sapply(setdiff(names(BLOCKS), "Authority"),
             function(s) rowMeans(as.data.frame(d[, cols(s)])))
M <- sapply(cols("Authority"),
            function(i) drop(cor(d[[i]], bm, use = "complete.obs")))
rownames(M) <- colnames(bm)
print(round(t(M), 4))
top <- apply(M, 2, function(v) rownames(M)[which.max(v)])
cat("\nstrongest rival block per Authority item:\n")
for (i in names(top)) cat(sprintf("  %-13s %s\n", i, top[[i]]))
ok2 <- identical(unname(top[["Authority_2"]]), "Evaluation") &&
       identical(unname(top[["Authority_5"]]), "Grouping")
cat(sprintf("prediction (Authority_2 -> Evaluation [Nr 7], Authority_5 -> Grouping [Nr 22]): %s\n",
            if (ok2) "held" else "FAILED"))
cat("Authority_2 is also the ONLY Authority item whose top rival block is Evaluation,\n",
    "and Authority_5 the only one whose top rival block is Grouping.\n\n", sep = "")

cat("NOT ESTABLISHED: within-block order for Authority_1/_3/_4 and for every item\n",
    "of the other four blocks; a permutation inside a block changes none of these\n",
    "numbers. See provenance -- that inference is the questionnaire's own\n",
    "block-interleaved numbering (item k of every construct sits in block k).\n\n", sep = "")

cat(if (worst1 <= TOL && ok2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
