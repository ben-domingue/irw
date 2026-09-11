# verify_tsai_2017_treeit_h14_document.R -- Step 5b mapping check (batch_193).
#
# CLAIM: live item codes H14-1, H14-2, H14-3 are the S3 File (.xlsx) column names
# (data/tsai_2017_treeit.py melts by column name, no rename) and correspond, in that order,
# to the three statements of the "H14. Document" block of the study's S1 File
# (Appendix 1, Treeit Heuristic Evaluation, pone.0180102.s001, p.8):
#   H14-1 "The system provides context-sensitive help."
#   H14-2 "Four types of help: task-oriented, alphabetically ordered, semantically organized, search."
#   H14-3 "The system has help embedded in contents."
# S1 prints the block heading "H14. Document" (a label match to the code prefix) but no
# per-item codes, so the within-block tie is presentation order (mapping_basis=paper_order).
#
# ROUTES (what would break if the mapping were wrong):
#   A. Route 3, published totals: paper Table 3 reports the Navigation construct's alpha over
#      heuristic means (0.865) and each heuristic's item-total r (H3 0.915, H4 0.860, H5 0.870,
#      H14 0.768); Table 4 the construct mean (4.164). Rebuilding each heuristic as the mean of its
#      Hk-* xlsx columns must reproduce them -- pins that the H14-* columns are the H14 heuristic.
#   B. Block size: S1 prints 3 statements under H14; the xlsx has 3 H14 columns.
#   C. Live table == xlsx H14 columns, per-item response-level counts (so A/B speak to the live table).
#   D. Route 8, semantic coherence (circumstantial): H14-2 is a feature-list/jargon statement,
#      while H14-1 and H14-3 both ask whether the system gives help in context. Prediction:
#      H14-2 is the odd one out -- r(H14-1,H14-3) exceeds both correlations with H14-2 and H14-2
#      has the lowest mean.
#
# NOT ESTABLISHED: the order of H14-1 vs H14-3 -- 98/101 respondents answer them identically
# (means 3.980 vs 3.941, counts 1/6/14/53/27 vs 2/6/14/53/26); no per-item statistic is published.
# D is weakened by the S3 file's cross-heuristic straight-lining: H14-1 matches H7-3 ("Skill
# acquisition through chunking.") in 96/101 rows and H5-6 in 95/101, content-unrelated items, so a
# correlation pattern here is not strong content evidence. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "tsai_2017_treeit_h14_document"
SI <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0180102.s003"
CACHE <- "itemtext/.cache/tsai_2017_treeit_h14_document/s003.xlsx"  # fallback if offline
IT <- c("H14-1", "H14-2", "H14-3")

tmp <- tempfile(fileext = ".xlsx")
got <- tryCatch({ download.file(SI, tmp, mode = "wb", quiet = TRUE); TRUE }, error = function(e) FALSE)
if (!got) {
  cands <- c(CACHE, sub("^itemtext/", "", CACHE), file.path("..", "..", CACHE))
  f <- cands[file.exists(cands)][1]
  if (is.na(f)) stop("S3 xlsx neither downloadable nor cached")
  tmp <- f
}
raw <- as.data.frame(readxl::read_excel(tmp, col_names = FALSE, .name_repair = "minimal"))
hdr <- as.character(unlist(raw[2, ]))
dat <- raw[-(1:2), , drop = FALSE]
names(dat) <- hdr
ok <- TRUE

# ---- Route B: block size
s1_h14 <- 3L
xl_h14 <- length(grep("^H14-[0-9]+$", hdr))
cat(sprintf("Route B -- H14 statements in S1: %d, H14 columns in S3 xlsx: %d\n", s1_h14, xl_h14))
if (xl_h14 != s1_h14) ok <- FALSE

# ---- Route A: Navigation construct, paper Table 3 / Table 4
nav <- c("H3", "H4", "H5", "H14")
pub_itc <- c(H3 = 0.915, H4 = 0.860, H5 = 0.870, H14 = 0.768)
pub_alpha <- 0.865; pub_mean <- 4.164
M <- sapply(nav, function(h) {
  cc <- grep(paste0("^", h, "-[0-9]+$"), hdr, value = TRUE)
  rowMeans(sapply(dat[cc], as.numeric))
})
alpha <- function(X) { k <- ncol(X); k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X))) }
a <- alpha(M); itc <- sapply(nav, function(h) cor(M[, h], rowSums(M))); mu <- mean(rowMeans(M))
cat("\nRoute A -- Navigation construct, paper Table 3 (alpha, item-total r) / Table 4 (mean)\n")
cat(sprintf("alpha published %.3f observed %.3f | mean published %.3f observed %.3f\n", pub_alpha, a, pub_mean, mu))
for (h in nav) cat(sprintf("  %-4s item-total published %.3f observed %.3f\n", h, pub_itc[h], itc[h]))
worst <- max(abs(a - pub_alpha), abs(itc - pub_itc), abs(mu - pub_mean))
cat(sprintf("largest deviation: %.4f (tol 0.0015)\n", worst))
if (worst > 0.0015) ok <- FALSE
# Sensitivity: an H14 composite built from any other heuristic's columns must NOT reproduce 0.768
other <- setdiff(unique(sub("-[0-9]+$", "", grep("^H[0-9]+-[0-9]+$", hdr, value = TRUE))), nav)
alt <- sapply(other, function(h) {
  cc <- grep(paste0("^", h, "-[0-9]+$"), hdr, value = TRUE)
  X <- M; X[, "H14"] <- rowMeans(sapply(dat[cc], as.numeric)); cor(X[, "H14"], rowSums(X))
})
cat("  item-total r if the 'H14' slot held another heuristic's columns:",
    paste(sprintf("%s %.3f", names(alt), alt), collapse = ", "), "\n")
if (any(abs(alt - 0.768) < 0.0015)) { cat("  another block also reproduces 0.768 -- route A not discriminating\n"); ok <- FALSE }

# ---- Route C: live == xlsx per-item level counts (303-row table; export deliberate)
d <- as.data.frame(irw::irw_fetch(TABLE))
cat("\nRoute C -- response-level counts 1..5 per item, xlsx vs live\n")
for (it in IT) {
  x <- table(factor(as.numeric(dat[[it]]), levels = 1:5))
  l <- table(factor(d$resp[d$item == it], levels = 1:5))
  cat(sprintf("%-6s xlsx %s | live %s\n", it, paste(x, collapse = "/"), paste(l, collapse = "/")))
  if (!all(x == l)) ok <- FALSE
}

# ---- Route D: semantic coherence (scored, but circumstantial)
X <- sapply(dat[IT], as.numeric)
R <- cor(X); mns <- colMeans(X)
cat(sprintf("\nRoute D -- r(1,3) %.3f vs r(1,2) %.3f, r(2,3) %.3f; means %s\n",
            R[1, 3], R[1, 2], R[2, 3], paste(sprintf("%.3f", mns), collapse = "/")))
cat(sprintf("identical answers: 1-3 %d/101, 1-2 %d/101, 2-3 %d/101\n",
            sum(X[, 1] == X[, 3]), sum(X[, 1] == X[, 2]), sum(X[, 2] == X[, 3])))
if (!(R[1, 3] > R[1, 2] && R[1, 3] > R[2, 3] && which.min(mns) == 2)) ok <- FALSE
cat(sprintf("caveat: H14-1 identical to H7-3 in %d/101 and to H5-6 in %d/101 (content-unrelated items)\n",
            sum(X[, 1] == as.numeric(dat[["H7-3"]])), sum(X[, 1] == as.numeric(dat[["H5-6"]]))))

cat("NOT ESTABLISHED: order of H14-1 vs H14-3 (98/101 identical answers, no per-item statistics published).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
