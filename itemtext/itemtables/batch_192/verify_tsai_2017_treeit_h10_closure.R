# verify_tsai_2017_treeit_h10_closure.R -- Step 5b mapping check (batch_192).
#
# CLAIM: live item codes H10-1, H10-2, H10-3 are the S3 File (.xlsx) column names, and they
# correspond to items 1, 2, 3 of the "H10. Closure" block of the study's S1 File (Appendix 1,
# Treeit Heuristic Evaluation). S1 prints the block header "H10. Closure" but does not print
# per-item codes, so the block tie is a label match and the within-block tie is presentation order.
#
# ROUTES (what would break if the mapping were wrong):
#   A. Published totals: the paper's Table 3 reports, per construct, Cronbach's alpha over the
#      heuristic means and each heuristic's item-total correlation, and Table 4 the construct mean.
#      Rebuilding every heuristic as the mean of its Hk-* columns must reproduce them. If the H10-*
#      columns were not the Closure heuristic, H10's item-total r (0.903) and the User-Interface
#      Design alpha (0.892) would not reproduce.
#   B. Block structure: per-heuristic item counts in S1 vs the xlsx columns.
#   C. Live table == the xlsx H10-* columns (per-item response-level counts), so A/B speak to it.
#
# NOT ESTABLISHED: the order of the three items within the H10 block. No per-item statistic is
# published. That tie rests on S1's presentation order only. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "tsai_2017_treeit_h10_closure"
SI <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0180102.s003"

tmp <- tempfile(fileext = ".xlsx")
download.file(SI, tmp, mode = "wb", quiet = TRUE)
raw <- as.data.frame(readxl::read_excel(tmp, col_names = FALSE, .name_repair = "minimal"))
hdr <- as.character(unlist(raw[2, ]))
dat <- raw[-(1:2), , drop = FALSE]
names(dat) <- hdr
ok <- TRUE

# ---- Route B: block sizes, S1 appendix (s001.pdf, hard-coded from the PDF) vs xlsx columns
s1_counts <- c(H1 = 6, H2 = 4, H3 = 3, H4 = 4, H5 = 7, H6 = 4, H7 = 3, H8 = 4, H9 = 4,
               H10 = 3, H11 = 4, H12 = 3, H13 = 2, H14 = 3)
cols <- lapply(names(s1_counts), function(h) grep(paste0("^", h, "-[0-9]+$"), hdr, value = TRUE))
names(cols) <- names(s1_counts)
xl_counts <- sapply(cols, length)
cat("Route B -- items per heuristic, S1 appendix vs S3 xlsx columns\n")
print(rbind(S1 = s1_counts, xlsx = xl_counts))
cat(sprintf("blocks agreeing: %d/14 (H8 differs: S1 prints 4 items, data has 3)\n",
            sum(s1_counts == xl_counts)))
if (s1_counts["H10"] != 3 || xl_counts["H10"] != 3) ok <- FALSE

# ---- Route A: reproduce Table 3 alphas / item-total r and Table 4 construct mean
M <- sapply(cols, function(cc) rowMeans(sapply(dat[cc], function(v) as.numeric(v))))
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
  cat(sprintf("%-4s alpha published %.3f observed %.3f | mean published %.3f observed %.3f\n",
              nm, p$a, a, p$mean, mu))
  for (i in seq_along(p$h))
    cat(sprintf("     %-4s item-total published %.3f observed %.3f\n", p$h[i], p$itc[i], itc[i]))
  worst <- max(worst, abs(a - p$a), abs(itc - p$itc), abs(mu - p$mean))
}
cat(sprintf("largest deviation across 3 alphas, 14 item-total r, 3 means: %.4f (tol 0.0015)\n", worst))
if (worst > 0.0015) ok <- FALSE

# ---- Route C: live table equals the xlsx H10 columns (303-row table; export deliberate)
d <- irw::irw_fetch(TABLE)
cat("\nRoute C -- response-level counts per item, xlsx vs live\n")
for (it in c("H10-1", "H10-2", "H10-3")) {
  x <- table(factor(as.numeric(dat[[it]]), levels = 1:5))
  l <- table(factor(d$resp[d$item == it], levels = 1:5))
  cat(sprintf("%-6s xlsx %s | live %s\n", it, paste(x, collapse = "/"), paste(l, collapse = "/")))
  if (!all(x == l)) ok <- FALSE
}

# Circumstantial only (not scored): inter-item r within H10.
R <- cor(sapply(dat[c("H10-1","H10-2","H10-3")], as.numeric))
cat(sprintf("\nH10 inter-item r: 1-2 %.3f, 1-3 %.3f, 2-3 %.3f (item 2, 'Complete 7-stages of actions', is the outlier;\n",
            R[1,2], R[1,3], R[2,3]),
    "consistent with the jargon item sitting at position 2, but it is not evidence of order)\n", sep = "")
cat("NOT ESTABLISHED: order within the H10 block (no per-item statistics published).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
