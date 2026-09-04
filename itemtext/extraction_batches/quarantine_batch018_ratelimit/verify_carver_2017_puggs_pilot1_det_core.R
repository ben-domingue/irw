# verify_carver_2017_puggs_pilot1_det_core.R
#
# CLAIM UNDER TEST -- the mapping, not the plumbing.
#
# The live item codes Q1..Q13 are the raw column names of the study's own pilot-1
# data file (PLOS S5 Table); data/carver_2017_puggs_items.py melts them unchanged.
# So the only question is WHICH of the 13 determinism statements each Qn carries.
# The study publishes the 13 statements TWICE, in TWO DIFFERENT ORDERS:
#
#   A. S4 Table, "Code Book used in the first pilot study" -- numbered variable list.
#   B. S3 Table, "Initial PUGGS questionnaire, used in the first pilot study" -- the
#      questionnaire form, whose Q. column numbers the same 13 statements differently.
#
# The shipped item_text uses ordering A (the code book). This script tests A against B.
#
# Two falsifiable predictions distinguish them:
#
#  1. The paper (Results, "Second revision") reports for the statement
#     "Traits and diseases caused by a single gene are not very common":
#     26% "Don't know" and 19.3% correct answers in the first pilot.
#     That statement is item 7 under A and item 2 under B.
#  2. The code book keys each statement true/false, i.e. gives each item's polarity
#     on the determinism scale. A and B disagree about the polarity of exactly two
#     positions, Q2 and Q4. Reverse-scoring by the wrong key drives those items'
#     item-rest correlations negative and depresses coefficient alpha.

suppressWarnings(suppressMessages(library(readxl)))

S5 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0169808.s005"
cands <- file.path(c(".", "..", "../..", "/home/ben/irw-queue/itemtext"),
                   ".cache", "carver_2017_puggs_pilot1_det_core", "s005.xlsx")
cache <- c(cands[file.exists(cands)], "")[1]
if (!file.exists(cache)) {
    cache <- tempfile(fileext = ".xlsx")
    utils::download.file(S5, cache, mode = "wb", quiet = TRUE,
                         headers = c("User-Agent" = "IRW-Finder/1.0 (ben.domingue@gmail.com)"))
}
raw <- suppressMessages(as.data.frame(read_excel(cache, sheet = "Sheet1")))
items <- paste0("Q", 1:13)
N <- nrow(raw)
cat(sprintf("pilot-1 raw file: %d respondents, columns %s..%s present: %s\n\n",
            N, items[1], items[13], all(items %in% names(raw))))

X <- sapply(raw[items], function(v) suppressWarnings(as.numeric(v)))
V <- X; V[!(V %in% 1:4)] <- NA          # the processing script's filter: drop 5 (don't know) and 99

## ---- link raw columns to the live item codes (per-item n, irw_table_sets 2026-09-03) ----
LIVE_N <- c(Q1=200, Q2=185, Q3=205, Q4=191, Q5=131, Q6=194, Q7=148,
            Q8=189, Q9=168, Q10=185, Q11=205, Q12=173, Q13=183)
obs_n <- colSums(!is.na(V))
cat("raw column n after the script's filter vs live per-item n:\n")
cat(sprintf("%-5s %8s %8s\n", "item", "raw", "live"))
for (i in items) cat(sprintf("%-5s %8d %8d\n", i, obs_n[[i]], LIVE_N[[i]]))
link_ok <- all(obs_n[items] == LIVE_N[items])
cat(sprintf("column<->item link: %s\n\n", if (link_ok) "exact for all 13" else "MISMATCH"))

## ---- prediction 1: the paper's published per-item statistic ----
PUB_DK <- 26.0; PUB_CORRECT <- 19.3; TOL <- 0.7
dk  <- 100 * colSums(X == 5, na.rm = TRUE) / N               # "don't know"
agr <- 100 * colSums(X == 3 | X == 4, na.rm = TRUE) / N      # agree + strongly agree = correct, statement is true
cat(sprintf("paper: \"Traits and diseases caused by a single gene are not very common\" -- %.0f%% don't know, %.1f%% correct\n",
            PUB_DK, PUB_CORRECT))
cat(sprintf("%-5s %10s %10s %s\n", "item", "dk%", "correct%", "match"))
hits <- character(0)
for (i in items) {
    m <- abs(dk[[i]] - PUB_DK) <= TOL && abs(agr[[i]] - PUB_CORRECT) <= TOL
    if (m) hits <- c(hits, i)
    cat(sprintf("%-5s %10.1f %10.1f %s\n", i, dk[[i]], agr[[i]], if (m) "<== MATCH" else ""))
}
cat(sprintf("\nunique match: %s   (code book puts that statement at Q7; the questionnaire form puts it at Q2)\n",
            paste(hits, collapse = ",")))
p1_ok <- identical(hits, "Q7")

## ---- prediction 2: keying polarity ----
# TRUE statements (agreement = anti-determinism, so reverse-scored) by position:
KEY_A <- c(3, 4, 6, 7, 9, 11, 12)   # code book ordering  (shipped)
KEY_B <- c(2, 3, 6, 7, 9, 11, 12)   # questionnaire-form ordering (rival)
alpha_and_r <- function(rev_pos) {
    Y <- V
    for (p in rev_pos) Y[, p] <- 5 - Y[, p]
    Y <- Y[complete.cases(Y), , drop = FALSE]
    k <- ncol(Y)
    a <- k / (k - 1) * (1 - sum(apply(Y, 2, var)) / var(rowSums(Y)))
    tot <- rowSums(Y)
    r <- sapply(seq_len(k), function(j) cor(Y[, j], tot - Y[, j]))
    names(r) <- items
    list(alpha = a, r = r, n = nrow(Y))
}
A <- alpha_and_r(KEY_A); B <- alpha_and_r(KEY_B)
cat(sprintf("\nkeying test (n=%d complete cases, 13 items)\n", A$n))
cat(sprintf("  code book ordering (shipped)  alpha = %.3f   min item-rest r = %+.2f  (Q2 %+.2f, Q4 %+.2f)\n",
            A$alpha, min(A$r), A$r[["Q2"]], A$r[["Q4"]]))
cat(sprintf("  questionnaire-form ordering   alpha = %.3f   min item-rest r = %+.2f  (Q2 %+.2f, Q4 %+.2f)\n",
            B$alpha, min(B$r), B$r[["Q2"]], B$r[["Q4"]]))
p2_ok <- A$alpha > B$alpha && min(A$r) > 0 && min(B$r) < 0

cat("\nWhat this does NOT establish: the statistics separate the two published orderings,\n",
    "and pin Q7 outright, but they do not individually distinguish items with similar\n",
    "distributions (e.g. Q5 and Q13 both mean 2.37) from one another -- those rest on the\n",
    "code book's own explicit numbering of the 13 variables, which is a label, not an\n",
    "inference. Nothing here tests the WORDING: the pilots were administered in Brazilian\n",
    "Portuguese and no Portuguese text exists in any of the 8 supplementary files, so the\n",
    "shipped English is a translated substitute.\n", sep = "")

cat(if (link_ok && p1_ok && p2_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
