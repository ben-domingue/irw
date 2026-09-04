# verify_carver_2017_puggs_pilot1_det_core.R
#
# CLAIM UNDER TEST (the mapping, not the plumbing):
#   IRW item code "Qk" (k = 1..13) carries the statement numbered k in the S4
#   Table CODE BOOK of Carver et al. 2017 (PLoS ONE 10.1371/journal.pone.0169808),
#   NOT the statement numbered k in the S3 Table QUESTIONNAIRE. The two documents
#   number the same 13 core-idea statements DIFFERENTLY, so exactly one of them
#   can be right, and shipping the wrong one would put wrong wording on 10 of the
#   13 items while passing every set-based gate.
#
#   Worked example of the disagreement:
#     S3 questionnaire #2 = "Traits and disorders caused by a single gene are not
#                            very common"   (a TRUE statement)
#     S4 code book     #2 = "The majority of human traits and diseases are caused
#                            by a single gene"  (a FALSE statement)
#   -- and the "not very common" statement is code book #7.
#
#   Also under test: resp 1..4 = Strongly disagree / Disagree / Agree / Strongly
#   agree (code book "Primary code"), i.e. higher resp = more agreement.
#
# Everything below is computed from the study's own raw file (S5 Table, first
# pilot). Live per-item n are hard-coded from irw::irw_table_sets(per_item=TRUE)
# -- a server-side aggregate -- so this script needs no Redivis access and never
# exports the table.
#
# The permutation, S3 questionnaire position -> code book number of the SAME
# statement (verified by reading both documents):
#   S3: 1  2  3  4  5  6  7  8  9 10 11 12 13
#   CB: 2  7  4 10  5 12  3  8 11  1  9  6 13
# Fixed points: 5 (Alzheimer), 8 (Personality), 13 (damaged gene -> cancer).

TABLE <- "carver_2017_puggs_pilot1_det_core"
S5 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0169808.s005")

LIVE_N <- c(Q1=200, Q2=185, Q3=205, Q4=191, Q5=131, Q6=194, Q7=148,
            Q8=189, Q9=168, Q10=185, Q11=205, Q12=173, Q13=183)

# Truth value of code-book statement 1..13 (the code book prints "(true)"/"(false)"
# after each). FALSE statements are the determinism-positive ones: agreeing with
# them favours genetic determinism, which is how the code book's "det" secondary
# code is directed.
CB_FALSE <- c(1, 2, 5, 8, 10, 13)
S3_TO_CB <- c(2, 7, 4, 10, 5, 12, 3, 8, 11, 1, 9, 6, 13)

items <- paste0("Q", 1:13)

cache <- file.path("..", "..", ".cache", TABLE, "s005.xlsx")
if (!file.exists(cache)) {
    cache <- tempfile(fileext = ".xlsx")
    utils::download.file(S5, cache, quiet = TRUE, mode = "wb")
}
suppressMessages(library(readxl))
d <- as.data.frame(readxl::read_excel(cache, sheet = "Sheet1"))

raw <- sapply(items, function(i) suppressWarnings(as.numeric(d[[i]])))
dk  <- colSums(raw == 5, na.rm = TRUE)          # "don't know" (code 5)
m   <- raw
m[!(m %in% 1:4)] <- NA                          # script's filter: drop 5 and 99

## ---------------------------------------------------------------- (A) identity
cat("(A) per-item n: raw S5 column, filtered as the IRW script filters, vs live\n")
cat(sprintf("%-6s %8s %8s %6s\n", "item", "raw", "live", "ok"))
okA <- TRUE
for (i in items) {
    n <- sum(!is.na(m[, i])); hit <- n == LIVE_N[[i]]; okA <- okA && hit
    cat(sprintf("%-6s %8d %8d %6s\n", i, n, LIVE_N[[i]], if (hit) "OK" else "MISMATCH"))
}
cat(sprintf("all 13 per-item n reproduce: %s\n\n", okA))

## ------------------------------------------------------- (B) keying / polarity
# Under each hypothesis, sign every column by the truth value of the statement it
# would then carry, and correlate each column with the signed mean of the OTHER 12.
# A statement placed on the wrong side of the determinism boundary shows up as a
# negative item-rest correlation.
itemrest <- function(det_positions) {
    key <- ifelse(1:13 %in% det_positions, 1, -1)
    s <- sweep(m, 2, key, "*")
    sapply(1:13, function(j)
        suppressWarnings(cor(s[, j], rowMeans(s[, -j], na.rm = TRUE),
                             use = "pairwise.complete.obs")))
}
det_cb <- CB_FALSE                                  # code book numbering
det_s3 <- which(S3_TO_CB %in% CB_FALSE)             # questionnaire numbering
r_cb <- itemrest(det_cb); r_s3 <- itemrest(det_s3)

cat("(B) item-rest correlation under each numbering (determinism-keyed)\n")
cat(sprintf("%-6s %10s %10s   %s\n", "item", "codebook", "S3 quest.", "differs?"))
for (j in 1:13)
    cat(sprintf("%-6s %10.3f %10.3f   %s\n", items[j], r_cb[j], r_s3[j],
                if ((j %in% det_cb) != (j %in% det_s3)) "<-- keyed oppositely" else ""))
alpha <- function(r) { k <- 13; mr <- mean(r); k * mr / (1 + (k - 1) * mr) }
cat(sprintf("negative item-rest r: code book %d/13, S3 questionnaire %d/13\n",
            sum(r_cb < 0), sum(r_s3 < 0)))
cat(sprintf("mean item-rest r:     code book %.3f,  S3 questionnaire %.3f\n",
            mean(r_cb), mean(r_s3)))
# The discriminating prediction is confined to the two positions the two documents
# key OPPOSITELY (Q2, Q4): under the right numbering both must sit on the positive
# side, under the wrong one both must invert. The whole-scale mean is a secondary,
# weaker corroboration -- this block's internal consistency is genuinely poor
# (the paper itself reports weak consistency in the first pilot), and Q1 has a
# slightly negative item-rest r under BOTH numberings, so a blanket "all 13
# positive" test would be testing reliability, not the mapping.
okB <- r_cb[2] > 0 && r_s3[2] < 0 && r_cb[4] > 0 && r_s3[4] < 0 &&
       mean(r_cb) > mean(r_s3)
cat(sprintf("discriminating positions: Q2 %+.3f (cb) vs %+.3f (S3); Q4 %+.3f vs %+.3f -- %s\n\n",
            r_cb[2], r_s3[2], r_cb[4], r_s3[4],
            if (okB) "code book numbering" else "INCONCLUSIVE"))

## -------------------------------------------------- (C) content marker items
# C1. "Eating habits and physical exercise can play an important role in preventing
#     and controlling diabetes" is the one near-consensus TRUE statement in the
#     block. Code book puts it at Q3; the questionnaire numbering puts it at Q7.
# C2. The long technical protein/amino-acid statement should draw the most
#     "don't know" of the swapped pair; the easy "most traits and diseases are
#     caused by both genes and environmental factors" the fewest. Code book puts
#     the technical one at Q9 and the easy one at Q11; S3 numbering swaps them.
mn <- colMeans(m, na.rm = TRUE)
cat("(C) content markers\n")
cat(sprintf("  C1 diabetes/lifestyle consensus item -- code book says Q3, S3 says Q7\n"))
cat(sprintf("     mean  Q3=%.2f  Q7=%.2f   |  don't-know  Q3=%d  Q7=%d\n",
            mn[["Q3"]], mn[["Q7"]], dk[["Q3"]], dk[["Q7"]]))
cat(sprintf("     strongly-agree count  Q3=%d  Q7=%d ; strongly-disagree  Q3=%d  Q7=%d\n",
            sum(raw[, "Q3"] == 4, na.rm = TRUE), sum(raw[, "Q7"] == 4, na.rm = TRUE),
            sum(raw[, "Q3"] == 1, na.rm = TRUE), sum(raw[, "Q7"] == 1, na.rm = TRUE)))
okC1 <- mn[["Q3"]] > mn[["Q7"]] && dk[["Q3"]] < dk[["Q7"]]
cat(sprintf("  C2 technical amino-acid item -- code book says Q9, S3 says Q11\n"))
cat(sprintf("     don't-know  Q9=%d  Q11=%d   |  mean  Q9=%.2f  Q11=%.2f\n",
            dk[["Q9"]], dk[["Q11"]], mn[["Q9"]], mn[["Q11"]]))
okC2 <- dk[["Q9"]] > dk[["Q11"]]
cat(sprintf("  (sanity, non-discriminating: Q8 'Personality is caused by genes only'\n"))
cat(sprintf("   is a fixed point of the permutation; mean %.2f, %d strongly-agree of %d)\n\n",
            mn[["Q8"]], sum(raw[, "Q8"] == 4, na.rm = TRUE), LIVE_N[["Q8"]]))

## --------------------------------------------------------- (D) scale direction
cat("(D) resp direction: 4 = strongly agree, so the consensus TRUE statement\n")
cat(sprintf("    must sit near the ceiling -- Q3 mean %.2f of 4, %.0f%% at resp 4\n\n",
            mn[["Q3"]], 100 * mean(m[, "Q3"] == 4, na.rm = TRUE)))
okD <- mn[["Q3"]] > 3.5

cat("Caveat on (B): Q1 has a mildly negative item-rest r under BOTH numberings\n",
    "(-0.078 / 0.000); the first pilot's core-idea block has weak internal\n",
    "consistency by the paper's own account, so (B) is read only at the two\n",
    "positions where the rival numberings make opposite predictions.\n\n", sep = "")

cat("What this does NOT establish: the candidate space tested here is the two\n",
    "numberings the deposit actually publishes, not every permutation of 13\n",
    "statements. (B) separates the two only where they key an item oppositely\n",
    "(Q2, Q4); (C) separates the swapped pairs {Q3,Q7} and {Q9,Q11}. The\n",
    "remaining positions are tied by the code book's own explicit numbering\n",
    "against the S5 file's Q1..Q13 column names, not by these statistics. Nothing\n",
    "here tests the Brazilian Portuguese wording actually administered, which the\n",
    "deposit does not publish.\n\n", sep = "")

cat(if (okA && okB && okC1 && okC2 && okD) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
