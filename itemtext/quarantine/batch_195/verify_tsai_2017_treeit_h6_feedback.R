# verify_tsai_2017_treeit_h6_feedback.R -- Step 5b mapping check (batch_195).
# Built from references/verify_template.R; modelled on the batch_194 sibling
# verify_tsai_2017_treeit_h2_visibility.R.
#
# CLAIM: live item codes H6-1..H6-4 are the S3 File (.xlsx) column names (data/tsai_2017_treeit.py
# melts by column name, no rename, resp kept 1-5), and H6-k is the k-th statement printed under
# "H6. Feedback" in the study's S1 File (Appendix 1, Treeit Heuristic Evaluation,
# pone.0180102.s001, page 4):
#   H6-1 "Information that can be directly perceived, interpreted, and evaluated."
#   H6-2 "The levels of feedback are the same for novice and expert."
#   H6-3 "Concrete and specific, not abstract and general."
#   H6-4 "The response time is reasonable and not too long."
# S1 prints the block header (label match to the code prefix) but no per-item codes, so the
# within-block tie is presentation order (mapping_basis=paper_order).
#
# ROUTES (what would break if the mapping were wrong):
#   A. Route 3, published totals: paper Table 3 reports per construct Cronbach's alpha over the
#      heuristic means and each heuristic's item-total r; Table 4 the construct means. Rebuilding
#      each heuristic as the mean of its Hk-* columns must reproduce them. H6 sits in
#      User-Interface Design: item-total r 0.913, alpha 0.892, mean 4.431.
#   A2. Controls, each scored against the WHOLE UI profile (5 item-total r + alpha + mean), not H6's
#      own item-total alone (batch_194 lesson: a single statistic can fail to reject a shift):
#      H6 window shifted one column left [H5-7,H6-1..H6-3] or right [H6-2..H6-4,H7-1], dropping
#      H6-1 or H6-4, widening left or right by one column, and every other heuristic's columns in
#      the H6 slot, must NOT reproduce it. Single foreign-column replacements are enumerated and
#      printed with their identical-answer count against the column they replace; the only
#      replacements allowed to survive are near-copies (>= 95/101 identical answers), because a
#      copy of a column cannot be told apart from that column by any statistic.
#   B. Block size: S1 prints 4 statements under H6; the xlsx has 4 H6 columns.
#   C. Live table == the xlsx H6-* columns (per-item response-level counts 1..5).
#   D. (not scored) within-block and cross-heuristic identical-answer counts.
#
# NOT ESTABLISHED: the order of the four statements within H6. A heuristic mean (and therefore
# every Table 3/4 statistic) is invariant to permuting its columns, no per-item statistic is
# published, and all four items share range and polarity. Nor can the published statistics say
# whether the H6-3 column holds H6-3 answers or a copy of H2-4's: the two columns are identical in
# all 101 rows, so either reading reproduces Table 3. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "tsai_2017_treeit_h6_feedback"
SI <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0180102.s003"
CACHE <- "itemtext/.cache/tsai_2017_treeit_h6_feedback/s003.xlsx"  # fallback if offline
H6 <- paste0("H6-", 1:4)

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
cat(sprintf("H6: S1 %d, xlsx %d (blocks agreeing overall: %d/14; H8 is the known mismatch)\n",
            s1_counts["H6"], xl_counts["H6"], sum(s1_counts == xl_counts)))
if (s1_counts["H6"] != 4 || xl_counts["H6"] != 4 || !identical(cols$H6, H6)) ok <- FALSE

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
cat(sprintf("largest deviation across 3 alphas, 14 item-total r, 3 means: %.4f (tol 0.0015)\n", worst))
if (worst > 0.0015) ok <- FALSE

# ---- Route A2: window shifts and substitutions in the H6 slot, scored on the whole UI profile.
UIH <- c("H1","H2","H6","H10","H13")
UIPUB <- c(pub$UI$itc, pub$UI$a, pub$UI$mean)
ui_with <- function(h6vec) {
  MM <- M[, UIH]; MM[, "H6"] <- h6vec
  v <- c(sapply(UIH, function(h) cor(MM[, h], rowSums(MM))), alpha(MM), mean(rowMeans(MM)))
  names(v) <- c(UIH, "alpha", "mean"); v
}
hits <- function(v) all(abs(v - UIPUB) <= 0.0015)
show <- function(lbl, cc, v) cat(sprintf("%-12s [%s] %s | max|dev| %.4f%s\n", lbl, paste(cc, collapse = ","),
  paste(sprintf("%s %.4f", names(v), v), collapse = " "), max(abs(v - UIPUB)), if (hits(v)) "  <- REPRODUCES" else ""))
j <- match("H6-1", hdr)
wins <- list(published = hdr[j:(j + 3)], shift_left = hdr[(j - 1):(j + 2)], shift_right = hdr[(j + 1):(j + 4)],
             drop_first = hdr[(j + 1):(j + 3)], drop_last = hdr[j:(j + 2)],
             widen_left = hdr[(j - 1):(j + 3)], widen_right = hdr[j:(j + 4)])
cat("\nRoute A2 -- H6 slot controls vs published UI profile:",
    paste(sprintf("%s %.3f", c(UIH, "alpha", "mean"), UIPUB), collapse = " "), "\n")
for (w in names(wins)) {
  v <- ui_with(rowMeans(num(wins[[w]])))
  show(w, wins[[w]], v)
  if (w == "published" && !hits(v)) ok <- FALSE
  if (w != "published" && hits(v)) ok <- FALSE
}
others <- setdiff(names(cols), UIH)
cat("other heuristic's columns in the H6 slot:\n")
for (h in others) { v <- ui_with(M[, h]); show(h, h, v); if (hits(v)) ok <- FALSE }
# Single-column replacement: which foreign columns can stand in for one H6 column undetected?
allH <- grep("^H[0-9]+-[0-9]+$", hdr, value = TRUE)
A <- num(allH)
und <- character(0); und_same <- integer(0)
for (o in setdiff(allH, H6)) for (k in 1:4) {
  w <- H6; w[k] <- o
  if (hits(ui_with(rowMeans(num(w))))) { und <- c(und, sprintf("%s<-%s", H6[k], o)); und_same <- c(und_same, sum(A[, H6[k]] == A[, o])) }
}
cat(sprintf("single foreign-column replacements tried: %d\n", 4 * length(setdiff(allH, H6))))
cat("replacements that still reproduce the UI profile (identical answers with the replaced column):",
    if (length(und)) paste(sprintf("%s (%d/101)", und, und_same), collapse = ", ") else "none", "\n")
if (length(und) && any(und_same < 95)) ok <- FALSE

# ---- Route C: live table equals the xlsx H6 columns (404-row table; export deliberate, siblings did the same)
d <- irw::irw_fetch(TABLE)
cat("\nRoute C -- response-level counts 1..5 per item, xlsx vs live\n")
for (it in H6) {
  x <- table(factor(as.numeric(dat[[it]]), levels = 1:5))
  l <- table(factor(d$resp[d$item == it], levels = 1:5))
  cat(sprintf("%-5s xlsx %s | live %s | mean %.3f\n", it, paste(x, collapse = "/"), paste(l, collapse = "/"),
              mean(as.numeric(dat[[it]]), na.rm = TRUE)))
  if (!all(x == l)) ok <- FALSE
}

# ---- Route D (not scored)
X6 <- num(H6)
cat("\nWithin-H6 identical answers (of 101) / r  [not scored]:\n")
for (a in 1:3) for (b in (a + 1):4)
  cat(sprintf("  %s~%s %3d  r %.3f\n", H6[a], H6[b], sum(X6[, a] == X6[, b]), cor(X6[, a], X6[, b])))
cat("Most-identical columns outside H6 [not scored]:\n")
for (it in H6) {
  s <- sapply(setdiff(allH, H6), function(o) sum(A[, it] == A[, o])); o <- order(-s)[1:3]
  cat(sprintf("  %s: %s\n", it, paste(sprintf("%s %d", names(s)[o], s[o]), collapse = "; ")))
}
cat(sprintf("H6-3 == H2-4 in %d/101 rows\n", sum(A[, "H6-3"] == A[, "H2-4"])))
cat("NOT ESTABLISHED: order of the four statements within H6 -- heuristic means are permutation-\n",
    "invariant, no per-item statistics are published; nor whether the H6-3 column holds H6-3 answers\n",
    "or a copy of H2-4's (identical in every row).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
