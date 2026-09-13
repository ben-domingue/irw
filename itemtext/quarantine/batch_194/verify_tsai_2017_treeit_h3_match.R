# verify_tsai_2017_treeit_h3_match.R -- Step 5b mapping check (batch_194).
#
# CLAIM: live item codes H3-1, H3-2, H3-3 are the S3 File (.xlsx) column names
# (data/tsai_2017_treeit.py melts by column name, no rename) and correspond, in that order,
# to the three statements of the "H3. Match" block of the study's S1 File
# (Appendix 1, Treeit Heuristic Evaluation, pone.0180102.s001, p.2):
#   H3-1 "User model matches system image."
#   H3-2 "Actions provided by the system match the actions performed by users."
#   H3-3 "Objects in the system match the objects of the task."
# S1 prints the block header "H3. Match" (a label match to the code prefix) but no per-item
# codes, so the within-block tie is presentation order (mapping_basis=paper_order).
#
# ROUTES (what would break if the mapping were wrong):
#   A. Route 3, published totals: paper Table 3 reports the Navigation construct's alpha over
#      heuristic means (0.865) and each heuristic's item-total r (H3 0.915, H4 0.860, H5 0.870,
#      H14 0.768); Table 4 the construct mean (4.164). Rebuilding each heuristic as the mean of its
#      Hk-* xlsx columns must reproduce them. Controls: (i) any other heuristic's columns in the H3
#      slot, (ii) the H3 column window shifted one column left or right, must NOT reproduce 0.915.
#   B. Block size: S1 prints 3 statements under H3; the xlsx has 3 H3 columns.
#   C. Live table == xlsx H3 columns, per-item response-level counts (so A/B speak to the live table).
#   D. Informational only, NOT scored (post hoc): H3-2 is the only H3 statement about "actions";
#      its mean r with the six other non-H8 checklist statements containing "action"
#      (H1-1, H2-4, H5-7, H10-2, H13-1, H13-2) is compared with H3-1/H3-3's. This pattern was
#      noticed from H3-2's top correlates before the keyword set was formalised, and the S3 file's
#      cross-heuristic identical answers (H3-3 = H4-3 in 99/101 rows) make correlations weak
#      content evidence -- so it is printed, not used for the verdict.
#
# NOT ESTABLISHED: the order of the three statements within H3. A heuristic mean (and so every
# Table 3/4 statistic) is invariant to permuting its columns, no per-item statistic is published,
# and all three items share range and polarity. Any of the 6 permutations passes A-C. Hence PARTIAL.

suppressMessages(library(irw))
TABLE <- "tsai_2017_treeit_h3_match"
SI <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0180102.s003"
CACHE <- "itemtext/.cache/tsai_2017_treeit_h3_match/s003.xlsx"  # fallback if offline
IT <- c("H3-1", "H3-2", "H3-3")

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
num <- function(cc) sapply(dat[cc], as.numeric)
ok <- TRUE

# ---- Route B: block size
s1_h3 <- 3L
xl_h3 <- length(grep("^H3-[0-9]+$", hdr))
cat(sprintf("Route B -- H3 statements in S1: %d, H3 columns in S3 xlsx: %d\n", s1_h3, xl_h3))
if (xl_h3 != s1_h3) ok <- FALSE

# ---- Route A: Navigation construct, paper Table 3 / Table 4
nav <- c("H3", "H4", "H5", "H14")
pub_itc <- c(H3 = 0.915, H4 = 0.860, H5 = 0.870, H14 = 0.768)
pub_alpha <- 0.865; pub_mean <- 4.164
M <- sapply(nav, function(h) rowMeans(num(grep(paste0("^", h, "-[0-9]+$"), hdr, value = TRUE))))
alpha <- function(X) { k <- ncol(X); k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X))) }
a <- alpha(M); itc <- sapply(nav, function(h) cor(M[, h], rowSums(M))); mu <- mean(rowMeans(M))
cat("\nRoute A -- Navigation construct, paper Table 3 (alpha, item-total r) / Table 4 (mean)\n")
cat(sprintf("alpha published %.3f observed %.3f | mean published %.3f observed %.3f\n", pub_alpha, a, pub_mean, mu))
for (h in nav) cat(sprintf("  %-4s item-total published %.3f observed %.3f\n", h, pub_itc[h], itc[h]))
worst <- max(abs(a - pub_alpha), abs(itc - pub_itc), abs(mu - pub_mean))
cat(sprintf("largest deviation: %.4f (tol 0.0015)\n", worst))
if (worst > 0.0015) ok <- FALSE

slot <- function(cols) { X <- M; X[, "H3"] <- rowMeans(num(cols)); c(itc = cor(X[, "H3"], rowSums(X)), alpha = alpha(X)) }
other <- setdiff(unique(sub("-[0-9]+$", "", grep("^H[0-9]+-[0-9]+$", hdr, value = TRUE))), nav)
alt <- sapply(other, function(h) slot(grep(paste0("^", h, "-[0-9]+$"), hdr, value = TRUE))["itc"])
names(alt) <- other
cat("  control (i) item-total r if the 'H3' slot held another heuristic's columns:",
    paste(sprintf("%s %.3f", names(alt), alt), collapse = ", "), "\n")
if (any(abs(alt - 0.915) < 0.0015)) { cat("  another block also reproduces 0.915 -- not discriminating\n"); ok <- FALSE }
pos <- match(IT, hdr)
left <- hdr[pos - 1]; right <- hdr[pos + 1]
sl <- slot(left); sr <- slot(right)
cat(sprintf("  control (ii) window shifted left [%s]: item-total %.3f, alpha %.3f\n", paste(left, collapse = ","), sl["itc"], sl["alpha"]))
cat(sprintf("  control (ii) window shifted right [%s]: item-total %.3f, alpha %.3f\n", paste(right, collapse = ","), sr["itc"], sr["alpha"]))
if (abs(sl["itc"] - 0.915) < 0.0015 || abs(sr["itc"] - 0.915) < 0.0015) ok <- FALSE

# ---- Route C: live == xlsx per-item level counts (303-row table; export deliberate)
d <- as.data.frame(irw::irw_fetch(TABLE))
X <- num(IT)
cat("\nRoute C -- response-level counts 1..5 per item, xlsx vs live\n")
for (it in IT) {
  x <- table(factor(X[, it], levels = 1:5))
  l <- table(factor(d$resp[d$item == it], levels = 1:5))
  cat(sprintf("%-5s xlsx %s | live %s | mean %.3f\n", it, paste(x, collapse = "/"), paste(l, collapse = "/"), mean(X[, it])))
  if (!all(x == l)) ok <- FALSE
}
R <- cor(X)
cat(sprintf("within-H3 r: (1,2) %.3f (1,3) %.3f (2,3) %.3f; identical answers 1-2 %d, 1-3 %d, 2-3 %d of %d\n",
            R[1, 2], R[1, 3], R[2, 3], sum(X[, 1] == X[, 2]), sum(X[, 1] == X[, 3]), sum(X[, 2] == X[, 3]), nrow(X)))

# ---- Route D: informational, not scored
allh <- grep("^H[0-9]+-[0-9]+$", hdr, value = TRUE)
act <- c("H1-1", "H2-4", "H5-7", "H10-2", "H13-1", "H13-2")
rest <- setdiff(allh, c(IT, act, grep("^H8-", allh, value = TRUE)))
A <- num(allh)
cat("\nRoute D (informational, NOT scored) -- mean r with the 'action' statements vs the other", length(rest), "items\n")
for (it in IT) cat(sprintf("  %-5s action-set %.3f (%s) | others %.3f\n", it, mean(cor(A[, it], A[, act])),
                           paste(sprintf("%.2f", cor(A[, it], A[, act])), collapse = "/"), mean(cor(A[, it], A[, rest]))))
cat(sprintf("  caveat: H3-3 identical to content-unrelated H4-3 in %d/101, H4-1 %d/101; H3-1 to H5-2 in %d/101\n",
            sum(A[, "H3-3"] == A[, "H4-3"]), sum(A[, "H3-3"] == A[, "H4-1"]), sum(A[, "H3-1"] == A[, "H5-2"])))

cat("\nNOT ESTABLISHED: order of H3-1/H3-2/H3-3 within the block (every published statistic is permutation-invariant; no per-item statistics published).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
