# verify_he_2019_flipped_classroom_attitudes.R -- Step 5b mapping check (batch_338).
#
# Claim: live item attitude_k carries the wording of Table 6 row "No. k" in He et al.
# (2019) PLOS ONE 10.1371/journal.pone.0214624. data/he_2019_flipped_classroom.py
# builds attitude_k from S7 File column header k (number-preserving rename), so the
# chain is  live attitude_k == S7 column k == Table 6 row k.
#
# Route: per-item, per-group mean AND SE. Table 6 prints mean+-SE for the FC and LBL
# groups; the authors computed them over ALL 1-5 and the "9" not-applicable code
# (reproduces to the printed precision only when 9s are included). The live table
# drops 9s, so the live link is checked against S7 with 9s dropped, exactly.
# Groups are identified by size (FC n=81, LBL n=56; paper Table 2), NOT by the live
# cov_group label, which is inverted in the response table (see provenance note).

suppressMessages({ library(irw); library(readxl) })
TABLE <- "he_2019_flipped_classroom_attitudes"
S7 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0214624.s007"

# Table 6, rows 1..12: FC mean, FC SE, LBL mean, LBL SE
PUB <- matrix(c(
 4.00,.081, 3.30,.067,   3.94,.077, 3.86,.065,   4.15,.083, 3.12,.063,
 4.28,.071, 4.20,.100,   4.22,.105, 3.30,.072,   3.44,.129, 3.39,.170,
 4.28,.083, 3.50,.067,   4.26,.078, 3.34,.166,   4.36,.090, 4.14,.082,
 4.42,.068, 3.09,.053,   4.02,.080, 2.59,.150,   4.28,.077, 3.09,.069),
 ncol = 4, byrow = TRUE, dimnames = list(1:12, c("FCm","FCse","LBLm","LBLse")))

tf <- tempfile(fileext = ".xls")
download.file(S7, tf, mode = "wb", quiet = TRUE)
s <- as.data.frame(read_excel(tf))
stopifnot(sum(s$group == 1) == 81, sum(s$group == 0) == 56)   # 1 = FC, 0 = LBL
se <- function(x) sd(x) / sqrt(length(x))
SRC <- t(sapply(as.character(1:12), function(k) {
  fc <- s[[k]][s$group == 1]; lb <- s[[k]][s$group == 0]
  c(FCm = mean(fc), FCse = se(fc), LBLm = mean(lb), LBLse = se(lb)) }))

# (1) S7 column k (9s included) vs Table 6 row k
cat("(1) S7 column k (incl. code 9) vs Table 6 row k\n")
cat(sprintf("%-3s %22s %22s\n", "k", "FC pub | src", "LBL pub | src"))
for (k in 1:12) cat(sprintf("%-3d %5.2f/%.3f | %5.2f/%.3f  %5.2f/%.3f | %5.2f/%.3f\n", k,
  PUB[k,1], PUB[k,2], SRC[k,1], SRC[k,2], PUB[k,3], PUB[k,4], SRC[k,3], SRC[k,4]))
dm <- max(abs(SRC[, c(1,3)] - PUB[, c(1,3)])); ds <- max(abs(SRC[, c(2,4)] - PUB[, c(2,4)]))
cat(sprintf("max |mean diff| %.4f (tol .0051, i.e. 2dp rounding); max |SE diff| %.4f (tol .0006)\n", dm, ds))
ok1 <- dm <= .0051 && ds <= .0006

# Does the route separate every item? Nearest Table 6 row for each S7 column must be itself,
# with a margin: distance to the second-nearest row.
D <- as.matrix(dist(rbind(PUB, SRC)))[13:24, 1:12]
nearest <- apply(D, 1, which.min)
margin <- apply(D, 1, function(r) sort(r)[2])
cat(sprintf("nearest Table-6 row per S7 column: %s\n", paste(nearest, collapse = " ")))
cat(sprintf("smallest distance to a WRONG row: %.3f (vs. max own-row distance %.4f)\n",
            min(margin), max(diag(D))))
ok2 <- all(nearest == 1:12)

# (2) live attitude_k vs S7 column k with 9s dropped
d <- irw::irw_fetch(TABLE)
ids_n <- tapply(d$id, d$cov_group, function(x) length(unique(x)))
cat("\n(2) live cov_group sizes:", paste(names(ids_n), ids_n, collapse = ", "), "\n")
fc_lab <- names(ids_n)[ids_n == 81]; lb_lab <- names(ids_n)[ids_n == 56]
cat(sprintf("    FC (n=81) is labelled '%s' in the live table; LBL (n=56) is '%s'\n", fc_lab, lb_lab))
worst <- 0
for (k in 1:12) {
  it <- paste0("attitude_", k)
  for (g in list(c(1, fc_lab), c(0, lb_lab))) {
    x <- s[[as.character(k)]][s$group == as.numeric(g[1])]; x <- x[x >= 1 & x <= 5]
    y <- d$resp[d$item == it & d$cov_group == g[2]]
    worst <- max(worst, abs(mean(x) - mean(y)), abs(length(x) - length(y)))
  }
}
cat(sprintf("    max |live - S7(9s dropped)| over 24 item x group mean/n cells: %.2e\n", worst))
ok3 <- worst < 1e-9

cat("Not established: the administered (presumably Chinese) wording -- item_text is the paper's\n",
    "English Table 6 rendering; nor whether Table 6 order equals questionnaire order (not needed:\n",
    "the tie is through the numbers, not the order).\n", sep = "")
cat(if (ok1 && ok2 && ok3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
