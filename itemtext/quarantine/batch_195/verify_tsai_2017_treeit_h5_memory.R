# verify_tsai_2017_treeit_h5_memory.R -- Step 5b mapping check (batch_195).
# Built from references/verify_template.R.
#
# CLAIM: live item codes H5-1..H5-7 are the S3 File (.xlsx) column names (data/tsai_2017_treeit.py
# melts by column name, no rename, resp kept 1-5), and H5-k is the k-th statement printed under
# "H5. Memory" in the study's S1 File (Appendix 1, Treeit Heuristic Evaluation, pone.0180102.s001;
# header, description line and statements 1-4 on p.3, statements 5-7 at the top of p.4):
#   H5-1 "Recognition vs. recall (e.g., menu vs. commands)."
#   H5-2 "Externalize information through visualization."
#   H5-3 "The ways to execute the system follow perceptual procedures."
#   H5-4 "The ways to execute the system follow a hierarchical structure."
#   H5-5 "When executing the system, the system initially follows the default values of the setting."
#   H5-6 "Concrete examples (DD/MM/YY, e.g., 10/20/99)."
#   H5-7 "Generic rules and actions (e.g., drag objects)."
# S1 prints the block header (label match to the code prefix) but no per-item codes, so the
# within-block tie is presentation order (mapping_basis=paper_order).
#
# ROUTES (what would break if the mapping were wrong):
#   A. Route 3, published totals: paper Table 3 reports per construct Cronbach's alpha over the
#      heuristic means and each heuristic's item-total r; Table 4 the construct means. Rebuilding
#      each heuristic as the mean of its Hk-* columns must reproduce them. H5 sits in Navigation
#      {H3,H4,H5,H14}: item-total r 0.870, alpha 0.865, mean 4.164.
#   A2. Controls, scored against the WHOLE Navigation profile (4 item-total r + alpha + mean, tol
#      0.0015 each), not H5's own item-total alone: shifting the 7-column H5 window one or two columns
#      left/right, dropping its first or last column, widening it by one column either side, or
#      substituting any other heuristic's columns in the H5 slot must NOT reproduce it. Every single
#      foreign-column replacement (one H5 column swapped for one non-H5 column) is also enumerated
#      and the survivors printed; they are expected only where the foreign column is (near-)identical
#      to the H5 column it replaces.
#   B. Block size: S1 prints 7 statements under H5; the xlsx has 7 H5 columns.
#   C. Live table == the xlsx H5-* columns (per-item response-level counts 1..5).
#   D. (not scored) within-block and cross-heuristic identical-answer counts.
#
# NOT ESTABLISHED: the order of the seven statements within H5. A heuristic mean (and therefore
# every Table 3/4 statistic) is invariant to permuting its columns, no per-item statistic is
# published, and all seven items share range and polarity. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "tsai_2017_treeit_h5_memory"
SI <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0180102.s003"
CACHE <- "itemtext/.cache/tsai_2017_treeit_h5_memory/s003.xlsx"  # fallback if offline
H5 <- paste0("H5-", 1:7)
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
cat(sprintf("H5: S1 %d, xlsx %d (blocks agreeing overall: %d/14; H8 is the known mismatch)\n",
            s1_counts["H5"], xl_counts["H5"], sum(s1_counts == xl_counts)))
if (s1_counts["H5"] != 7 || xl_counts["H5"] != 7 || !identical(cols$H5, H5)) ok <- FALSE

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
  cat(sprintf("%-4s alpha published %.3f observed %.4f | mean published %.3f observed %.4f\n", nm, p$a, a, p$mean, mu))
  for (i in seq_along(p$h))
    cat(sprintf("     %-4s item-total published %.3f observed %.4f\n", p$h[i], p$itc[i], itc[i]))
  worst <- max(worst, abs(a - p$a), abs(itc - p$itc), abs(mu - p$mean))
}
cat(sprintf("largest deviation across 3 alphas, 14 item-total r, 3 means: %.4f (tol %.4f)\n", worst, TOL))
if (worst > TOL) ok <- FALSE

# ---- Route A2: controls in the H5 slot, scored against the whole Navigation profile.
NAVH <- c("H3","H4","H5","H14")
NAVPUB <- c(pub$NAV$itc, pub$NAV$a, pub$NAV$mean)
nav_with <- function(h5vec) {
  MM <- M[, NAVH]; MM[, "H5"] <- h5vec
  v <- c(sapply(NAVH, function(h) cor(MM[, h], rowSums(MM))), alpha(MM), mean(rowMeans(MM)))
  names(v) <- c(NAVH, "alpha", "mean"); v
}
hits <- function(v) all(abs(v - NAVPUB) <= TOL)
show <- function(lbl, cc, v) cat(sprintf("%-12s [%s] %s | max|dev| %.4f%s\n", lbl, paste(cc, collapse = ","),
  paste(sprintf("%s %.4f", names(v), v), collapse = " "), max(abs(v - NAVPUB)), if (hits(v)) "  <- REPRODUCES" else ""))
j <- match("H5-1", hdr)
wins <- list(published = hdr[j:(j + 6)],
             shift_left1 = hdr[(j - 1):(j + 5)], shift_left2 = hdr[(j - 2):(j + 4)],
             shift_right1 = hdr[(j + 1):(j + 7)], shift_right2 = hdr[(j + 2):(j + 8)],
             drop_first = hdr[(j + 1):(j + 6)], drop_last = hdr[j:(j + 5)],
             widen_left = hdr[(j - 1):(j + 6)], widen_right = hdr[j:(j + 7)])
cat("\nRoute A2 -- H5 slot controls vs published Navigation profile:",
    paste(sprintf("%s %.3f", c(NAVH, "alpha", "mean"), NAVPUB), collapse = " "), "\n")
for (w in names(wins)) {
  v <- nav_with(rowMeans(num(wins[[w]])))
  show(w, wins[[w]], v)
  if (w == "published" && !hits(v)) ok <- FALSE
  if (w != "published" && hits(v)) ok <- FALSE
}
cat("other heuristic's columns in the H5 slot:\n")
for (h in setdiff(names(cols), NAVH)) { v <- nav_with(M[, h]); show(h, h, v); if (hits(v)) ok <- FALSE }
cat("other Navigation heuristic's columns in the H5 slot (that heuristic kept in place too):\n")
for (h in setdiff(NAVH, "H5")) { v <- nav_with(M[, h]); show(h, h, v); if (hits(v)) ok <- FALSE }

# Single foreign-column replacement: which non-H5 columns can stand in for one H5 column undetected?
allH <- grep("^H[0-9]+-[0-9]+$", hdr, value = TRUE)
A <- num(allH)
und <- character(0); n_tried <- 0
for (o in setdiff(allH, H5)) for (k in 1:7) {
  n_tried <- n_tried + 1
  vec <- rowMeans(cbind(A[, setdiff(H5, H5[k])], A[, o]))
  if (hits(nav_with(vec))) und <- c(und, sprintf("%s<-%s (identical %d/101)", H5[k], o, sum(A[, H5[k]] == A[, o])))
}
cat(sprintf("single foreign-column replacements tried: %d; still reproducing the Navigation profile: %s\n",
            n_tried, if (length(und)) paste(und, collapse = ", ") else "none"))
# Expected survivors, fixed in advance of re-runs: the two foreign columns that are near-identical to the
# H5 column they replace (a property of the S3 file's duplicated answers, not a failure to locate the
# block). Any other survivor fails the check.
EXPECTED <- c("H5-1<-H2-3", "H5-2<-H3-1")
cat("  (expected: H5-1<-H2-3 and H5-2<-H3-1, the pairs identical in 99/101 and 94/101 rows; see Route D)\n")
if (!all(sub(" \\(.*$", "", und) %in% EXPECTED)) ok <- FALSE

# ---- Route C: live table equals the xlsx H5 columns (707-row table; export deliberate, siblings did the same)
d <- irw::irw_fetch(TABLE)
cat("\nRoute C -- response-level counts 1..5 per item, xlsx vs live\n")
for (it in H5) {
  x <- table(factor(as.numeric(dat[[it]]), levels = 1:5))
  l <- table(factor(d$resp[d$item == it], levels = 1:5))
  cat(sprintf("%-5s xlsx %s | live %s | mean %.3f\n", it, paste(x, collapse = "/"), paste(l, collapse = "/"),
              mean(as.numeric(dat[[it]]), na.rm = TRUE)))
  if (!all(x == l)) ok <- FALSE
}

# ---- Route D (not scored)
X5 <- A[, H5]
cat("\nWithin-H5 identical answers (of 101) / r  [not scored]:\n")
for (a in 1:6) for (b in (a + 1):7)
  cat(sprintf("  %s~%s %3d  r %.3f\n", H5[a], H5[b], sum(X5[, a] == X5[, b]), cor(X5[, a], X5[, b])))
cat("Most-identical columns outside H5 [not scored]:\n")
for (it in H5) {
  s <- sapply(setdiff(allH, H5), function(o) sum(A[, it] == A[, o])); o <- order(-s)[1:3]
  cat(sprintf("  %s: %s\n", it, paste(sprintf("%s %d", names(s)[o], s[o]), collapse = "; ")))
}
cat("NOT ESTABLISHED: order of the seven statements within H5 -- heuristic means are permutation-\n",
    "invariant, no per-item statistics are published, and cross-heuristic identical answers\n",
    "(H5-1 = H2-3 in 99/101, H5-7 = H3-2 in 96/101, H5-6 = H14-1/H14-3 in 95/101, H5-2 = H3-1/H9-1 in\n",
    "94/101) make correlation arguments uninformative.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
