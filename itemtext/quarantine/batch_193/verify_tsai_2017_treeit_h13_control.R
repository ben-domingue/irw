# verify_tsai_2017_treeit_h13_control.R -- Step 5b mapping check (batch_193).
#
# CLAIM: live item codes H13-1 and H13-2 are the S3 File (.xlsx) column names, and they carry,
# in that order, the two statements of the "H13. Control" block of the study's S1 File
# (Appendix 1, Treeit Heuristic Evaluation, pone.0180102.s001, page 8):
#   H13-1 "Users are initiators of actors, not responders to actions."
#   H13-2 "Avoid surprising actions, unexpected outcomes, tedious sequences of actions, etc."
# mapping_basis = paper_order: data/tsai_2017_treeit.py melts by column name (no rename), the
# column names carry no text, and S1 prints the block header plus two unnumbered statements.
#
# ROUTES (what would break if the mapping were wrong):
#   A. Published totals (route 3): rebuilding every heuristic as the mean of its Hk-* columns
#      must reproduce paper Table 3 (construct alphas, each heuristic's item-total r, including
#      H13 0.755) and Table 4 construct means. If the H13-* columns were not the Control
#      heuristic, the H13 item-total r and the User-Interface Design alpha would not reproduce.
#   B. Block structure: S1 prints 2 statements under H13; the xlsx has exactly 2 H13 columns.
#   C. Live table == xlsx H13 columns: per-item response-level counts. The two count vectors
#      differ, so each live code is pinned to its source column.
#
# NOT ESTABLISHED: which of the two statements is H13-1 and which is H13-2. A heuristic mean is
# invariant to swapping its items, Table 3 publishes no per-item statistic, and the two items
# share no distinguishing range or polarity. A swap would pass every check below. Hence PARTIAL.

suppressMessages(library(irw))
TABLE <- "tsai_2017_treeit_h13_control"
SI <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0180102.s003"

tmp <- tempfile(fileext = ".xlsx")
download.file(SI, tmp, mode = "wb", quiet = TRUE)
raw <- as.data.frame(readxl::read_excel(tmp, col_names = FALSE, .name_repair = "minimal"))
hdr <- as.character(unlist(raw[2, ]))
dat <- raw[-(1:2), , drop = FALSE]
names(dat) <- hdr
ok <- TRUE

# ---- Route B: block sizes, S1 appendix (hard-coded from s001.pdf) vs xlsx columns
s1_counts <- c(H1 = 6, H2 = 4, H3 = 3, H4 = 4, H5 = 7, H6 = 4, H7 = 3, H8 = 4, H9 = 4,
               H10 = 3, H11 = 4, H12 = 3, H13 = 2, H14 = 3)
cols <- lapply(names(s1_counts), function(h) grep(paste0("^", h, "-[0-9]+$"), hdr, value = TRUE))
names(cols) <- names(s1_counts)
xl_counts <- sapply(cols, length)
cat("Route B -- items per heuristic, S1 appendix vs S3 xlsx columns\n")
print(rbind(S1 = s1_counts, xlsx = xl_counts))
cat(sprintf("blocks agreeing: %d/14 (H8 differs: S1 prints 4, data has 3); H13 S1 %d vs xlsx %d\n",
            sum(s1_counts == xl_counts), s1_counts["H13"], xl_counts["H13"]))
if (s1_counts["H13"] != 2 || xl_counts["H13"] != 2) ok <- FALSE

# ---- Route A: reproduce Table 3 alphas / item-total r and Table 4 construct means
M <- sapply(cols, function(cc) rowMeans(sapply(dat[cc], function(v) as.numeric(v))))
alpha <- function(X) { k <- ncol(X); k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X))) }
pub <- list(
  UI  = list(h = c("H1","H2","H6","H10","H13"), a = 0.892, itc = c(0.763, 0.862, 0.913, 0.903, 0.755), mean = 4.431),
  SS  = list(h = c("H7","H8","H9","H11","H12"), a = 0.855, itc = c(0.749, 0.863, 0.768, 0.856, 0.806), mean = 4.031),
  NAV = list(h = c("H3","H4","H5","H14"),       a = 0.865, itc = c(0.915, 0.860, 0.870, 0.768), mean = 4.164))
cat("\nRoute A -- paper Table 3 (alpha, item-total r) and Table 4 (construct mean)\n")
worst <- 0; h13dev <- NA
for (nm in names(pub)) {
  p <- pub[[nm]]; X <- M[, p$h]
  a <- alpha(X); itc <- sapply(p$h, function(h) cor(X[, h], rowSums(X))); mu <- mean(rowMeans(X))
  cat(sprintf("%-4s alpha published %.3f observed %.3f | mean published %.3f observed %.3f\n",
              nm, p$a, a, p$mean, mu))
  for (i in seq_along(p$h))
    cat(sprintf("     %-4s item-total published %.3f observed %.3f\n", p$h[i], p$itc[i], itc[i]))
  if ("H13" %in% p$h) h13dev <- abs(itc["H13"] - p$itc[p$h == "H13"])
  worst <- max(worst, abs(a - p$a), abs(itc - p$itc), abs(mu - p$mean))
}
cat(sprintf("largest deviation across 3 alphas, 14 item-total r, 3 means: %.4f (tol 0.0015); H13 item-total dev %.4f\n",
            worst, h13dev))
if (worst > 0.0015) ok <- FALSE

# Control: the H13 item-total r must NOT reproduce if the H13 block is replaced by another
# 2-item pair from the same construct's neighbours -- shows route A is sensitive to the block.
alt <- M[, c("H1","H2","H6","H10","H13")]
alt[, "H13"] <- rowMeans(sapply(dat[c("H10-1","H10-2")], as.numeric))
cat(sprintf("control: H13 replaced by mean(H10-1,H10-2) gives item-total %.3f (published 0.755)\n",
            cor(alt[, "H13"], rowSums(alt))))

# ---- Route C: live table equals the xlsx H13 columns (202-row table; export deliberate)
d <- as.data.frame(irw::irw_fetch(TABLE))
cat("\nRoute C -- response-level counts 1..5 per item, xlsx vs live\n")
for (it in c("H13-1", "H13-2")) {
  x <- table(factor(as.numeric(dat[[it]]), levels = 1:5))
  l <- table(factor(d$resp[d$item == it], levels = 1:5))
  cat(sprintf("%-6s xlsx %s | live %s | mean %.3f\n", it, paste(x, collapse = "/"),
              paste(l, collapse = "/"), mean(d$resp[d$item == it])))
  if (!all(x == l)) ok <- FALSE
}

# Circumstantial only (not scored)
a1 <- as.numeric(dat[["H13-1"]]); a2 <- as.numeric(dat[["H13-2"]])
cat(sprintf("\nH13 inter-item r %.3f; identical answers %d/101\n", cor(a1, a2), sum(a1 == a2)))
cat(sprintf("H13-2 vs H10-2 ('Complete 7-stages of actions'): r %.3f, identical %d/101 -- the S3 file's\n",
            cor(a2, as.numeric(dat[["H10-2"]])), sum(a2 == as.numeric(dat[["H10-2"]]))),
    "known cross-heuristic identical-answer pattern; NOT used as evidence of order.\n", sep = "")
cat("NOT ESTABLISHED: whether H13-1/H13-2 are in S1 presentation order (a swap passes every check).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
