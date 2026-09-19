# verify_tsai_2017_treeit_h1_consistency.R -- Step 5b mapping check (batch_193).
# Built from references/verify_template.R.
#
# CLAIM: live item codes H1-1..H1-6 are the S3 File (.xlsx) column names (data/tsai_2017_treeit.py
# melts by column name, no rename), and H1-k is the k-th item printed under "H1. Consistency" on
# page 1 of the study's S1 File (Appendix 1, Treeit Heuristic Evaluation). S1 prints the block
# header but no per-item codes: the block tie is a label match, the within-block tie is order.
#
# ROUTES (what would break if the mapping were wrong):
#   A. Published totals (route 3): paper Table 3 reports, per construct, Cronbach's alpha over the
#      heuristic means and each heuristic's item-total r; Table 4 the construct means. Rebuilding
#      each heuristic as the mean of its Hk-* columns must reproduce them. H1's item-total r is
#      0.763 in User-Interface Design (alpha 0.892).
#   A2. Boundary sensitivity: shifting the H1 window one column left (BI4,H1-1..H1-5) or right
#      (H1-2..H1-6,H2-1) must NOT reproduce H1's 0.763 / alpha 0.892.
#   B. Block size: S1 prints 6 items under H1; the xlsx has 6 H1 columns.
#   C. Live table == the xlsx H1-* columns (per-item response-level counts).
#   D. (not scored) a-priori content-partner correlations -- printed to show they are uninformative.
#
# NOT ESTABLISHED: the order of the six items within the H1 block. No per-item statistics are
# published, H1-3..H1-6 agree on 95-97 of 101 respondents pairwise (r 0.95-0.97), so no data
# route separates them. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "tsai_2017_treeit_h1_consistency"
SI <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0180102.s003"

tmp <- tempfile(fileext = ".xlsx")
download.file(SI, tmp, mode = "wb", quiet = TRUE)
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
cat(sprintf("H1: S1 %d, xlsx %d (blocks agreeing overall: %d/14; H8 is the known mismatch)\n",
            s1_counts["H1"], xl_counts["H1"], sum(s1_counts == xl_counts)))
if (s1_counts["H1"] != 6 || xl_counts["H1"] != 6) ok <- FALSE

# ---- Route A
M <- sapply(cols, function(cc) rowMeans(num(cc)))
alpha <- function(X) { k <- ncol(X); k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X))) }
pub <- list(
  UI  = list(h = c("H1","H2","H6","H10","H13"), a = 0.892, itc = c(0.763, 0.862, 0.913, 0.903, 0.755), mean = 4.431),
  SS  = list(h = c("H7","H8","H9","H11","H12"), a = 0.855, itc = c(0.749, 0.863, 0.768, 0.856, 0.806), mean = 4.031),
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
cat(sprintf("largest deviation across 3 alphas, 14 item-total r, 3 means: %.4f (tol 0.0015)\n", worst))
if (worst > 0.0015) ok <- FALSE

# ---- Route A2: shift the H1 window by one column
ui_with <- function(h1cols) {
  MM <- M[, c("H1","H2","H6","H10","H13")]; MM[, "H1"] <- rowMeans(num(h1cols))
  c(itc = cor(MM[, "H1"], rowSums(MM)), a = alpha(MM))
}
j <- match("H1-1", hdr)
wins <- list(published = hdr[j:(j + 5)], shift_left = hdr[(j - 1):(j + 4)], shift_right = hdr[(j + 1):(j + 6)])
cat("\nRoute A2 -- H1 window boundary sensitivity (published H1 item-total 0.763, UI alpha 0.892)\n")
for (w in names(wins)) {
  v <- ui_with(wins[[w]])
  cat(sprintf("%-12s [%s] item-total %.3f alpha %.3f\n", w, paste(wins[[w]], collapse = ","), v["itc"], v["a"]))
}
vl <- ui_with(wins$shift_left); vr <- ui_with(wins$shift_right); vp <- ui_with(wins$published)
if (abs(vp["itc"] - 0.763) > 0.0015) ok <- FALSE
if (abs(vl["itc"] - 0.763) <= 0.0015 && abs(vl["a"] - 0.892) <= 0.0015) ok <- FALSE
if (abs(vr["itc"] - 0.763) <= 0.0015 && abs(vr["a"] - 0.892) <= 0.0015) ok <- FALSE

# ---- Route C: live table equals the xlsx H1 columns (606-row table; export deliberate)
d <- irw::irw_fetch(TABLE)
cat("\nRoute C -- response-level counts 1..5 per item, xlsx vs live\n")
h1 <- paste0("H1-", 1:6)
for (it in h1) {
  x <- table(factor(as.numeric(dat[[it]]), levels = 1:5))
  l <- table(factor(d$resp[d$item == it], levels = 1:5))
  cat(sprintf("%-5s xlsx %s | live %s\n", it, paste(x, collapse = "/"), paste(l, collapse = "/")))
  if (!all(x == l)) ok <- FALSE
}

# ---- Route D (not scored)
X1 <- num(h1)
cat("\nWithin-H1 identical answers (of 101) / r:\n")
for (a in 1:5) for (b in (a + 1):6)
  cat(sprintf("  %s~%s %3d  r %.3f\n", h1[a], h1[b], sum(X1[, a] == X1[, b]), cor(X1[, a], X1[, b])))
partners <- list("H1-1" = "H7-3", "H1-2" = "H5-2", "H1-5" = "H12-1", "H1-6" = "H2-3")
cat("Content partners (predicted H1 item should be the argmax; NOT scored):\n")
for (p in names(partners)) {
  v <- sapply(h1, function(it) cor(X1[, it], as.numeric(dat[[partners[[p]]]])))
  cat(sprintf("  %-6s predicted %s: r %s -> argmax %s\n", partners[[p]], p,
              paste(sprintf("%.3f", v), collapse = " "), h1[which.max(v)]))
}
cat("NOT ESTABLISHED: order of the six items within the H1 block (no per-item statistics published;\n",
    "H1-3..H1-6 near-identical in the data; content-partner correlations do not discriminate).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
