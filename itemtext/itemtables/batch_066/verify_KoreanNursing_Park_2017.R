# verify_KoreanNursing_Park_2017.R
#
# CLAIM UNDER TEST -----------------------------------------------------------
# The 50 IRW item codes (X0, X1, X1.1, X0.1, ... X0.39) are the mangled column
# names R produced when data/KoreanNursing_Park_2017.R ran
# read.table("Jeehp-14-20_raw data.tab", header = TRUE) over a HEADERLESS
# 741 x 50 matrix of 0/1 scores: the first data row became the header, and
# make.names/make.unique turned its 0s and 1s into X0/X1/X0.1/X1.1/...
# The claim is therefore that the code in position i is question i of the mock
# examination as printed in Supplement 7 of Park et al. (2017), jeehp 14:20 --
# a positional mapping, which the codes themselves preserve no trace of.
#
# The falsifiable prediction: Supplement 7 publishes, per question, the number
# of examinees (of 741) who answered correctly. Because the raw file scores
# 1 = WRONG and 0 = CORRECT, and because the first respondent's row was eaten
# by header = TRUE, the live table must hold exactly
#     (741 - published_correct) - first_row_value
# rows with resp == 1 for the item at that position. First-row values are
# read off the item code itself (X0 -> 0, X1 -> 1), so nothing here is fitted.
#
# Two pairs of items tie on that count (q2/q34 at 527, q31/q45 at 560), so a
# second published statistic is checked as the tie-break: the item-total
# correlation printed in the same Supplement 7 table, recomputed on the live
# data with correctness = 1 - resp.
#
# This does NOT re-check item counts or the resp set (validate_items.R did).
# Sources: https://www.jeehp.org/upload/media/jeehp-14-20-suppl7.pdf
#          https://doi.org/10.7910/DVN/ECDLXG (Jeehp-14-20_raw data.tab)

suppressMessages(library(irw))
TABLE <- "KoreanNursing_Park_2017"

ITEMS <- c("X0","X1","X1.1","X0.1","X0.2","X0.3","X1.2","X0.4","X0.5","X0.6",
           "X0.7","X0.8","X1.3","X0.9","X0.10","X0.11","X0.12","X0.13","X0.14","X0.15",
           "X0.16","X0.17","X0.18","X0.19","X0.20","X0.21","X0.22","X0.23","X0.24","X0.25",
           "X0.26","X0.27","X1.4","X1.5","X0.28","X0.29","X0.30","X0.31","X0.32","X1.6",
           "X0.33","X0.34","X0.35","X1.7","X0.36","X0.37","X0.38","X1.8","X1.9","X0.39")

# Supplement 7, "No. of correct answers / Total" per question, q1..q50.
# q5's table omits the count; 622 is its published 84% correct-answer rate x 741.
PUB_CORRECT <- c(332,213,333,417,622,664,210,472,538,407,504,642,26,497,619,639,726,438,678,373,
                 377,656,263,362,556,436,604,561,364,265,181,355,192,213,730,225,257,603,467,650,
                 460,548,503,505,181,521,543,39,71,199)

# The response of the examinee whose row became the header = the digit in the code.
FIRST_ROW <- as.integer(sub("^X([01]).*$", "\\1", ITEMS))

# Supplement 7, "No. of correct answers" in the High 27% and Low 27% groups.
# q5's row is blank there too; 182/154 are its option-3 counts from the same
# page's upper/lower-27% response-distribution table.
PUB_HIGH <- c(121,80,99,143,182,194,82,146,172,125,161,184,3,165,167,183,200,151,191,122,
              135,184,93,112,161,154,177,158,131,106,74,115,80,82,200,86,80,187,162,190,
              151,179,156,151,56,157,166,11,25,58)
PUB_LOW  <- c(57,40,73,87,154,162,40,106,112,101,109,165,9,103,157,160,191,87,172,72,
              73,165,53,79,134,93,140,141,72,46,35,73,34,37,190,41,59,137,85,154,
              87,116,101,113,43,123,123,9,14,45)

# Supplement 7, "Item-total correlation" per question.
PUB_ITC <- c(0.26,0.16,0.13,0.20,0.15,0.16,0.20,0.18,0.30,0.11,0.25,0.13,-0.04,0.25,0.06,0.17,
             0.20,0.26,0.17,0.18,0.25,0.15,0.16,0.13,0.12,0.25,0.21,0.10,0.22,0.27,0.20,0.19,
             0.18,0.17,0.23,0.20,0.09,0.29,0.31,0.24,0.29,0.29,0.21,0.16,0.06,0.17,0.20,0.00,
             0.05,0.09)

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

# ---- check 1: per-item count of resp == 1, exact ---------------------------
ones <- tapply(d$resp, d$item, sum)[ITEMS]
pred <- (741 - PUB_CORRECT) - FIRST_ROW
cat(sprintf("%-3s %-7s %10s %8s %8s %6s\n",
            "q", "item", "pub_corr", "pred_1s", "live_1s", "ok"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-3d %-7s %10d %8d %8d %6s\n", i, ITEMS[i], PUB_CORRECT[i],
                pred[i], as.integer(ones[i]),
                if (pred[i] == ones[i]) "OK" else "MISMATCH"))
n_exact <- sum(pred == ones)
cat(sprintf("\ncount check: %d/50 exact\n", n_exact))

# ---- check 2: item-total correlation, breaks the two count ties ------------
ids <- sort(unique(d$id))
M <- matrix(NA_real_, nrow = length(ids), ncol = length(ITEMS),
            dimnames = list(as.character(ids), ITEMS))
for (it in ITEMS) {
    x <- d[d$item == it, c("id", "resp")]
    M[as.character(x$id), it] <- 1 - x$resp   # correctness
}
stopifnot(!any(is.na(M)))
tot <- rowSums(M)
obs_itc <- sapply(seq_along(ITEMS), function(j) cor(M[, j], tot))
cat("\nitem-total correlation (live, correctness = 1 - resp) vs Supplement 7:\n")
for (i in seq_along(ITEMS))
    cat(sprintf("%-3d %-7s pub %6.2f  obs %6.2f  diff %6.3f\n",
                i, ITEMS[i], PUB_ITC[i], obs_itc[i], obs_itc[i] - PUB_ITC[i]))
worst <- max(abs(obs_itc - PUB_ITC))
cat(sprintf("largest |diff| = %.3f\n", worst))

# ---- check 3: upper/lower-27% correct counts, the real tie-break ----------
# Rank the 740 live respondents by total correct and take the top and bottom
# 200, as the paper did with 741. One respondent is missing, so each published
# group count may be off by at most 1.
ord <- order(-tot, as.numeric(rownames(M)))
hi <- ord[1:200]; lo <- ord[(length(ord) - 199):length(ord)]
obs_hi <- colSums(M[hi, ITEMS]); obs_lo <- colSums(M[lo, ITEMS])
cat("\nupper/lower-27% correct counts (live 740) vs Supplement 7 (741):\n")
for (i in seq_along(ITEMS))
    cat(sprintf("%-3d %-7s high pub %3d obs %3d | low pub %3d obs %3d %s\n",
                i, ITEMS[i], PUB_HIGH[i], obs_hi[i], PUB_LOW[i], obs_lo[i],
                if (abs(obs_hi[i] - PUB_HIGH[i]) <= 1 && abs(obs_lo[i] - PUB_LOW[i]) <= 1) "OK" else "MISMATCH"))
n_grp <- sum(abs(obs_hi - PUB_HIGH) <= 1 & abs(obs_lo - PUB_LOW) <= 1)
cat(sprintf("group check: %d/50 within 1\n", n_grp))

cat("\nTie-break detail (the only two pairs the count check cannot separate):\n")
for (p in list(c(2, 34), c(31, 45)))
    cat(sprintf("  q%d vs q%d: same live count %d; high/low %d/%d vs %d/%d (published %d/%d vs %d/%d)\n",
                p[1], p[2], as.integer(ones[p[1]]),
                obs_hi[p[1]], obs_lo[p[1]], obs_hi[p[2]], obs_lo[p[2]],
                PUB_HIGH[p[1]], PUB_LOW[p[1]], PUB_HIGH[p[2]], PUB_LOW[p[2]]))

cat("\nWhat this does NOT establish: the five answer options within an item are\n",
    "not checked here -- resp is a 0/1 score, not a chosen option, so the shipped\n",
    "correct_response was read off Supplement 7's own upper/lower-27% response\n",
    "distributions rather than from the live table.\n", sep = "")

pass <- (n_exact == 50) && (n_grp == 50) && (worst <= 0.06)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
