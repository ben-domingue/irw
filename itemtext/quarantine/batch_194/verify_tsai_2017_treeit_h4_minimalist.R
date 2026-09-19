# verify_tsai_2017_treeit_h4_minimalist.R -- Step 5b mapping check (batch_194).
#
# CLAIM: live item codes H4-1..H4-4 are the S3 File (.xlsx) column names
# (data/tsai_2017_treeit.py melts by column name, no rename) and correspond, in that order,
# to the four statements of the "H4. Minimalist" block of the study's S1 File
# (Appendix 1, Treeit Heuristic Evaluation, pone.0180102.s001, pp.2-3):
#   H4-1 "The interface provides concise information. Less is more."
#   H4-2 "Though the system provides simple information, it is not equivalent to abstract and general."
#   H4-3 "The system provides simple information and makes it efficient to operate."
#   H4-4 "Progressive levels of details."
# S1 prints the block header "H4. Minimalist" (a label match to the code prefix) but no per-item
# codes, so the within-block tie is presentation order (mapping_basis=paper_order).
#
# ROUTES (what would break if the mapping were wrong):
#   A. Route 3, published totals: paper Table 3 reports each construct's alpha over heuristic means
#      and each heuristic's item-total r (Navigation: alpha 0.865; H3 0.915, H4 0.860, H5 0.870,
#      H14 0.768); Table 4 the construct means. Rebuilding every heuristic as the mean of its
#      Hk-* xlsx columns must reproduce all of them -- pins that the H4-* columns form the H4
#      heuristic. (Table 4 SDs are not compared: their definition is unstated and a
#      mean-of-heuristic-means composite does not reproduce them.) Sensitivity: any other heuristic's columns in the H4 slot must NOT reproduce 0.860.
#   A2. Window shift: the published values are recomputed with the H4 window moved one column
#      left [H3-3,H4-1..H4-3] and right [H4-2..H4-4,H5-1]; both must miss the published H4
#      item-total r 0.860 and Navigation alpha 0.865 (scored). Worth checking despite H3-3 answering
#      identically to H4-3 in 99/101 rows.
#   B. Block size: S1 prints 4 statements under H4; the xlsx has 4 H4 columns.
#   C. Live table == xlsx H4 columns, per-item response-level counts (so A/B speak to the live table).
#   D. Route 8, semantic coherence (circumstantial): H4-1..H4-3 all concern simple/concise
#      information; H4-4 ("Progressive levels of details.") is a different design idea. Prediction:
#      H4-4 is the odd one out -- its correlations with the other three are all below every
#      correlation among H4-1..H4-3.
#
# NOT ESTABLISHED: the order of H4-1, H4-2, H4-3 among themselves -- pairwise identical answers
# 96-99/101 (r 0.97-0.99), means 4.218-4.267, no per-item statistic published; item-total r and
# alpha are invariant to permutation within the block. D rests on semantic coherence only and is
# weakened by the S3 file's cross-heuristic straight-lining (H4-3 identical to H3-3 in 99/101).
# Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "tsai_2017_treeit_h4_minimalist"
SI <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0180102.s003"
CACHE <- "itemtext/.cache/tsai_2017_treeit_h4_minimalist/s003.xlsx"  # fallback if offline
IT <- c("H4-1", "H4-2", "H4-3", "H4-4")

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
num <- function(cc) sapply(dat[cc], as.numeric)
cols <- function(h) grep(paste0("^", h, "-[0-9]+$"), hdr, value = TRUE)

# ---- Route B: block size
s1_h4 <- 4L
xl_h4 <- length(cols("H4"))
cat(sprintf("Route B -- H4 statements in S1: %d, H4 columns in S3 xlsx: %d\n", s1_h4, xl_h4))
if (xl_h4 != s1_h4) ok <- FALSE

# ---- Route A: all three constructs, paper Table 3 / Table 4
cons <- list(
  "System Support"        = list(h = c("H7", "H8", "H9", "H11", "H12"), alpha = 0.855, mean = 4.031,
                                 itc = c(0.749, 0.863, 0.768, 0.856, 0.806)),
  "User-Interface Design" = list(h = c("H1", "H2", "H6", "H10", "H13"), alpha = 0.892, mean = 4.431,
                                 itc = c(0.763, 0.862, 0.913, 0.903, 0.755)),
  "Navigation"            = list(h = c("H3", "H4", "H5", "H14"), alpha = 0.865, mean = 4.164,
                                 itc = c(0.915, 0.860, 0.870, 0.768)))
alpha <- function(X) { k <- ncol(X); k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X))) }
hmean <- function(cc) rowMeans(num(cc))
stats <- function(colsets) {
  M <- sapply(colsets, hmean)
  list(alpha = alpha(M), itc = sapply(seq_len(ncol(M)), function(j) cor(M[, j], rowSums(M))),
       mean = mean(rowMeans(M)))
}
cat("\nRoute A -- published Table 3 (alpha, item-total r) / Table 4 (construct mean)\n")
devs <- c()
for (cn in names(cons)) {
  p <- cons[[cn]]; s <- stats(lapply(p$h, cols))
  cat(sprintf("%s: alpha %.3f/%.3f  mean %.3f/%.3f\n", cn, p$alpha, s$alpha, p$mean, s$mean))
  cat("   item-total r (published/observed):",
      paste(sprintf("%s %.3f/%.3f", p$h, p$itc, s$itc), collapse = ", "), "\n")
  devs <- c(devs, abs(s$alpha - p$alpha), abs(s$itc - p$itc), abs(s$mean - p$mean))
}
worst <- max(devs)
cat(sprintf("largest deviation over 14 item-total r + 3 alphas + 3 means: %.4f (tol 0.0015)\n", worst))
if (worst > 0.0015) ok <- FALSE

nav <- cons[["Navigation"]]
navsets <- lapply(nav$h, cols); names(navsets) <- nav$h
h4_itc <- function(h4cols) { cs <- navsets; cs[["H4"]] <- h4cols; stats(cs)$itc[2] }
# Sensitivity: any other heuristic in the H4 slot
other <- setdiff(unique(sub("-[0-9]+$", "", grep("^H[0-9]+-[0-9]+$", hdr, value = TRUE))), nav$h)
alt <- sapply(other, function(h) h4_itc(cols(h)))
cat("  H4 item-total r if the H4 slot held another heuristic's columns:",
    paste(sprintf("%s %.3f", names(alt), alt), collapse = ", "), "\n")
if (any(abs(alt - 0.860) < 0.0015)) { cat("  another block also reproduces 0.860 -- route A not discriminating\n"); ok <- FALSE }

# ---- Route A2: window shift (scored)
i <- match(cols("H4"), hdr)
left <- hdr[(min(i) - 1):(max(i) - 1)]; right <- hdr[(min(i) + 1):(max(i) + 1)]
cat(sprintf("\nRoute A2 -- H4 item-total r / Navigation alpha: true window %.3f / %.3f\n",
            h4_itc(cols("H4")), stats(navsets)$alpha))
for (w in list(left = left, right = right)) {
  cs <- navsets; cs[["H4"]] <- w; s <- stats(cs)
  cat(sprintf("   window [%s]: %.3f / %.3f\n", paste(w, collapse = ","), s$itc[2], s$alpha))
  if (abs(s$itc[2] - 0.860) < 0.0015 || abs(s$alpha - 0.865) < 0.0015) { cat("   shifted window reproduces -- not discriminating\n"); ok <- FALSE }
}
cat(sprintf("   (H3-3 identical to H4-3 in %d/101 rows, yet the left shift still misses)\n",
            sum(as.numeric(dat[["H3-3"]]) == as.numeric(dat[["H4-3"]]))))

# ---- Route C: live == xlsx per-item level counts (404-row table; export deliberate)
d <- as.data.frame(irw::irw_fetch(TABLE))
cat("\nRoute C -- response-level counts 1..5 per item, xlsx vs live\n")
for (it in IT) {
  x <- table(factor(as.numeric(dat[[it]]), levels = 1:5))
  l <- table(factor(d$resp[d$item == it], levels = 1:5))
  cat(sprintf("%-5s xlsx %s | live %s\n", it, paste(x, collapse = "/"), paste(l, collapse = "/")))
  if (!all(x == l)) ok <- FALSE
}

# ---- Route D: semantic coherence (scored, but circumstantial)
X <- num(IT)
R <- cor(X); mns <- colMeans(X)
within <- c(R[1, 2], R[1, 3], R[2, 3]); with4 <- R[1:3, 4]
cat(sprintf("\nRoute D -- r among H4-1..H4-3: %s; r with H4-4: %s; means %s\n",
            paste(sprintf("%.3f", within), collapse = "/"), paste(sprintf("%.3f", with4), collapse = "/"),
            paste(sprintf("%.3f", mns), collapse = "/")))
ident <- outer(1:4, 1:4, Vectorize(function(a, b) sum(X[, a] == X[, b])))
cat(sprintf("identical answers: 1-2 %d, 1-3 %d, 2-3 %d | 1-4 %d, 2-4 %d, 3-4 %d (of 101)\n",
            ident[1, 2], ident[1, 3], ident[2, 3], ident[1, 4], ident[2, 4], ident[3, 4]))
if (!(max(with4) < min(within))) ok <- FALSE

cat("NOT ESTABLISHED: order of H4-1, H4-2, H4-3 among themselves (96-99/101 identical answers pairwise,\n",
    "no per-item statistics published; item-total r and alpha are permutation-invariant within the block).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
