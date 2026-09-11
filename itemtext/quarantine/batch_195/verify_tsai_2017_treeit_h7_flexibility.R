# verify_tsai_2017_treeit_h7_flexibility.R -- Step 5b mapping check (batch_195).
# Built from references/verify_template.R.
#
# CLAIM: live item codes H7-1..H7-3 are the S3 File (.xlsx) column names (data/tsai_2017_treeit.py
# melts by column name, no rename, resp kept 1-5), and H7-k is the k-th statement printed under
# "H7. Flexibility" in the study's S1 File (Appendix 1, Treeit Heuristic Evaluation,
# pone.0180102.s001; header and description line at the foot of p.4, the three statements at the
# top of p.5):
#   H7-1 "Shortcuts for experienced users."
#   H7-2 "Shortcuts or macros for frequently used operations."
#   H7-3 "Skill acquisition through chunking."
# S1 prints the block header (label match to the code prefix) but no per-item codes, so the
# within-block tie is presentation order (mapping_basis=paper_order).
#
# ROUTES (what would break if the mapping were wrong):
#   A. Route 3, published totals: paper Table 3 reports per construct Cronbach's alpha over the
#      heuristic means and each heuristic's item-total r; Table 4 the construct means. Rebuilding
#      each heuristic as the mean of its Hk-* columns must reproduce them. H7 sits in System
#      Support (H7, H8, H9, H11, H12): H7 item-total r 0.749, alpha 0.855, mean 4.031.
#   A2. Controls, scored against the WHOLE System Support profile (5 item-total r + alpha + mean),
#      not H7's own r alone: shifting the H7 window one column left [H6-4,H7-1,H7-2] or right
#      [H7-2,H7-3,H8-1], dropping any one H7 column, widening by one column either side,
#      substituting any other heuristic's columns in the H7 slot, and replacing any single H7
#      column with any foreign H-column must NOT reproduce it.
#   B. Block size: S1 prints 3 statements under H7; the xlsx has 3 H7 columns.
#   C. Live table == the xlsx H7-* columns (per-item response-level counts 1..5).
#   D. (not scored) within-block and cross-heuristic identical-answer counts and correlations.
#
# NOT ESTABLISHED: the order of the three statements within H7. A heuristic mean (and therefore
# every Table 3/4 statistic) is invariant to permuting its columns, no per-item statistic is
# published, and all three items share range and polarity. Route D shows H7-1/H7-2 answered
# identically by 96/101 respondents (r 0.98) with H7-3 apart (41/101, r 0.27), which fits the two
# near-synonymous "Shortcuts" statements being H7-1/H7-2 -- but the same file has content-unrelated
# cross-heuristic pairs at the same level (H7-3 = H14-1 in 96/101), so it is not scored, and it
# could never order H7-1 vs H7-2 in any case. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "tsai_2017_treeit_h7_flexibility"
SI <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0180102.s003"
CACHE <- "itemtext/.cache/tsai_2017_treeit_h7_flexibility/s003.xlsx"  # fallback if offline
H7 <- paste0("H7-", 1:3)
TOL <- 0.0015

tmp <- tempfile(fileext = ".xlsx")
got <- tryCatch({ download.file(SI, tmp, mode = "wb", quiet = TRUE); TRUE }, error = function(e) FALSE)
if (!got || file.size(tmp) < 1000) {
  cands <- c(CACHE, sub("^itemtext/", "", CACHE), file.path("..", "..", CACHE), file.path("..", "..", "..", CACHE))
  hit <- cands[file.exists(cands)]
  if (!length(hit)) stop("S3 xlsx neither downloadable nor cached")
  tmp <- hit[1]; cat("(using cached S3 xlsx)\n")
}
raw <- as.data.frame(readxl::read_excel(tmp, col_names = FALSE, .name_repair = "minimal"))
hdr <- as.character(unlist(raw[2, ]))
dat <- raw[-(1:2), , drop = FALSE]
names(dat) <- hdr
num <- function(cc) sapply(dat[cc], function(v) as.numeric(v))
ok <- TRUE

# ---- Route B
s1_counts <- c(H1 = 6, H2 = 4, H3 = 3, H4 = 4, H5 = 7, H6 = 4, H7 = 3, H8 = 4, H9 = 4,
               H10 = 3, H11 = 4, H12 = 3, H13 = 2, H14 = 3)
cols <- lapply(names(s1_counts), function(h) grep(paste0("^", h, "-[0-9]+$"), hdr, value = TRUE))
names(cols) <- names(s1_counts)
xl_counts <- sapply(cols, length)
cat("Route B -- items per heuristic, S1 appendix vs S3 xlsx columns\n")
print(rbind(S1 = s1_counts, xlsx = xl_counts))
cat(sprintf("H7: S1 %d, xlsx %d (blocks agreeing overall: %d/14; H8 is the known mismatch)\n",
            s1_counts["H7"], xl_counts["H7"], sum(s1_counts == xl_counts)))
if (s1_counts["H7"] != 3 || xl_counts["H7"] != 3 || !identical(cols$H7, H7)) ok <- FALSE

# ---- Route A
M <- sapply(cols, function(cc) rowMeans(num(cc)))
alpha <- function(X) { k <- ncol(X); k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X))) }
pub <- list(
  SS  = list(h = c("H7","H8","H9","H11","H12"), a = 0.855, itc = c(0.749, 0.863, 0.768, 0.856, 0.806), mean = 4.031),
  UI  = list(h = c("H1","H2","H6","H10","H13"), a = 0.892, itc = c(0.763, 0.862, 0.913, 0.903, 0.755), mean = 4.431),
  NAV = list(h = c("H3","H4","H5","H14"),       a = 0.865, itc = c(0.915, 0.860, 0.870, 0.768), mean = 4.164))
cat("\nRoute A -- paper Table 3 (alpha, item-total r) and Table 4 (construct mean)\n")
worst <- 0
for (nm in names(pub)) {
  p <- pub[[nm]]; X <- M[, p$h]
  a <- alpha(X); itc <- sapply(p$h, function(h) cor(X[, h], rowSums(X))); mu <- mean(rowMeans(X))
  cat(sprintf("%-4s alpha published %.3f observed %.3f | mean published %.3f observed %.3f\n", nm, p$a, a, p$mean, mu))
  for (i in seq_along(p$h))
    cat(sprintf("     %-4s item-total published %.3f observed %.3f\n", p$h[i], p$itc[i], itc[i]))
  worst <- max(worst, abs(a - p$a), abs(itc - p$itc), abs(mu - p$mean))
}
cat(sprintf("largest deviation across 3 alphas, 14 item-total r, 3 means: %.4f (tol %.4f)\n", worst, TOL))
cat(sprintf("[not scored] Table 4 System Support S.D. 0.703 vs SD of the heuristic-mean composite %.3f --\n",
            sd(rowMeans(M[, pub$SS$h]))),
    "  the published S.D. is not a raw composite SD; no control below uses it.\n", sep = "")
if (worst > TOL) ok <- FALSE

# ---- Route A2: controls in the H7 slot, scored against the WHOLE System Support profile.
SSH <- pub$SS$h
SSPUB <- c(pub$SS$itc, pub$SS$a, pub$SS$mean)
ss_with <- function(h7vec) {
  MM <- M[, SSH]; MM[, "H7"] <- h7vec
  v <- c(sapply(SSH, function(h) cor(MM[, h], rowSums(MM))), alpha(MM), mean(rowMeans(MM)))
  names(v) <- c(SSH, "alpha", "mean"); v
}
hits <- function(v) all(abs(v - SSPUB) <= TOL)
show <- function(lbl, cc, v) cat(sprintf("%-12s [%s] %s | max|dev| %.4f%s\n", lbl, paste(cc, collapse = ","),
  paste(sprintf("%s %.4f", names(v), v), collapse = " "), max(abs(v - SSPUB)), if (hits(v)) "  <- REPRODUCES" else ""))
j <- match("H7-1", hdr)
wins <- list(published = hdr[j:(j + 2)], shift_left = hdr[(j - 1):(j + 1)], shift_right = hdr[(j + 1):(j + 3)],
             drop_H7_1 = H7[-1], drop_H7_2 = H7[-2], drop_H7_3 = H7[-3],
             widen_left = hdr[(j - 1):(j + 2)], widen_right = hdr[j:(j + 3)])
cat("\nRoute A2 -- H7 slot controls vs published System Support profile:",
    paste(sprintf("%s %.3f", c(SSH, "alpha", "mean"), SSPUB), collapse = " "), "\n")
for (w in names(wins)) {
  v <- ss_with(rowMeans(num(wins[[w]])))
  show(w, wins[[w]], v)
  if (w == "published" && !hits(v)) ok <- FALSE
  if (w != "published" && hits(v)) ok <- FALSE
}
cat("other heuristic's columns in the H7 slot:\n")
for (h in setdiff(names(cols), SSH)) { v <- ss_with(M[, h]); show(h, h, v); if (hits(v)) ok <- FALSE }
allH <- grep("^H[0-9]+-[0-9]+$", hdr, value = TRUE)
und <- character(0); best <- c(dev = Inf); bestlab <- ""
for (o in setdiff(allH, H7)) for (k in 1:3) {
  w <- H7; w[k] <- o
  v <- ss_with(rowMeans(num(w))); dv <- max(abs(v - SSPUB))
  if (dv < best) { best <- dv; bestlab <- sprintf("%s<-%s", H7[k], o) }
  if (hits(v)) und <- c(und, sprintf("%s<-%s", H7[k], o))
}
cat(sprintf("single foreign-column replacements tried: %d; nearest %s max|dev| %.4f; reproducing: %s\n",
            3 * length(setdiff(allH, H7)), bestlab, best, if (length(und)) paste(und, collapse = ", ") else "none"))
if (length(und)) ok <- FALSE

# ---- Route C: live table equals the xlsx H7 columns (303-row table)
d <- irw::irw_fetch(TABLE)
cat("\nRoute C -- response-level counts 1..5 per item, xlsx vs live\n")
for (it in H7) {
  x <- table(factor(as.numeric(dat[[it]]), levels = 1:5))
  l <- table(factor(d$resp[d$item == it], levels = 1:5))
  cat(sprintf("%-5s xlsx %s | live %s | mean %.3f\n", it, paste(x, collapse = "/"), paste(l, collapse = "/"),
              mean(as.numeric(dat[[it]]), na.rm = TRUE)))
  if (!all(x == l)) ok <- FALSE
}

# ---- Route D (not scored)
X7 <- num(H7)
cat("\nWithin-H7 identical answers (of 101) / r  [not scored]:\n")
for (a in 1:2) for (b in (a + 1):3)
  cat(sprintf("  %s~%s %3d  r %.3f\n", H7[a], H7[b], sum(X7[, a] == X7[, b]), cor(X7[, a], X7[, b])))
A <- num(allH)
cat("Most-identical columns outside H7 [not scored]:\n")
for (it in H7) {
  s <- sapply(setdiff(allH, H7), function(o) sum(A[, it] == A[, o])); o <- order(-s)[1:3]
  cat(sprintf("  %s: %s\n", it, paste(sprintf("%s %d", names(s)[o], s[o]), collapse = "; ")))
}
cat("NOT ESTABLISHED: order of the three statements within H7 -- heuristic means are permutation-\n",
    "invariant and no per-item statistics are published. H7-1~H7-2 96/101 identical fits the two\n",
    "'Shortcuts' statements sharing codes 1-2, but content-unrelated H7-3 = H14-1 is also 96/101,\n",
    "so that is circumstantial, and nothing separates H7-1 from H7-2.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
