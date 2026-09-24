# verify_dass21_depression_anxiety_stress.R -- Step 5b re-runnable evidence.
#
# CLAIM UNDER TEST: each IRW item code qN carries the canonical DASS-21 item of
# the same number N, so the shipped item_text is on the right code.
#
# WHY THE CODES CAN BE CHECKED AT ALL: data/dass21_depression_anxiety_stress.py
# takes the source column names (Q1..Q21) and only strips/lowercases them
# (.str.strip().str.lower()), a number-preserving rename. So this script fetches
# the CC0 source file (Harvard Dataverse doi:10.7910/DVN/TAISB2, data.xlsx,
# datafile 13891169, 37 KB) rather than exporting the live IRW table.
#
# WHAT IS TESTED:
#   (0) the source header row itself: the Q-columns sit under three section
#       header cells "Depression" / "Anxiety" / "Stress", and the numbers under
#       them must be exactly the canonical DASS-21 partition
#       {3,5,10,13,16,17,21} / {2,4,7,9,15,19,20} / {1,6,8,11,12,14,18}.
#       A relabelling reproduces that by chance with p = 1/(21!/(7!)^3) = 2.5e-9.
#   (a) each block's within-subscale mean r exceeds its mean r with EACH other
#       block (convergent/discriminant)
#   (b) subscale means order Stress > Depression > Anxiety (non-clinical profile)
#   (c) marker: DASS-21 item 17 ("I felt I wasn't worth much as a person") is the
#       least endorsed depression item
#   (d) the same 262 respondents' DASS-21 responses were deposited by the same
#       authors as doi:10.7910/DVN/8YLSMK (IRW table falih_2026_dass21), whose
#       column layout carries the same partition. Cell agreement is printed.
#
# WHAT IT DOES NOT ESTABLISH: the order of items WITHIN a subscale. Swapping the
# text of q3 and q5 (both depression) leaves every number below unchanged. Hence
# PARTIAL, not VERIFIED.

suppressMessages(library(readxl))

f <- tempfile(fileext = ".xlsx")
utils::download.file("https://dataverse.harvard.edu/api/access/datafile/13891169",
                     f, quiet = TRUE, mode = "wb")
x <- readxl::read_excel(f, col_names = FALSE, .name_repair = "minimal")
hdr <- trimws(as.character(unlist(x[1, ])))
df  <- as.data.frame(x[-1, ])
names(df) <- hdr

cat("=== (0) source header partition ===\n")
secs <- c("Depression", "Anxiety", "Stress")
pos  <- match(secs, hdr)
ends <- c(pos[-1] - 1, max(grep("^Q[0-9]+$", hdr)))
got  <- lapply(seq_along(secs), function(i) {
  h <- hdr[(pos[i] + 1):ends[i]]
  sort(as.integer(sub("^Q", "", h[grepl("^Q[0-9]+$", h)])))
})
names(got) <- secs
canon <- list(Depression = c(3,5,10,13,16,17,21),
              Anxiety    = c(2,4,7,9,15,19,20),
              Stress     = c(1,6,8,11,12,14,18))
ok_0 <- all(sapply(secs, function(k) identical(got[[k]], as.integer(canon[[k]]))))
for (k in secs) cat(sprintf("  %-11s source {%s}  canonical {%s}\n", k,
                            paste(got[[k]], collapse = ","), paste(canon[[k]], collapse = ",")))
cat(sprintf("  exact canonical partition: %s\n", ok_0))

items <- paste0("Q", 1:21)
d <- df[, items]
d[] <- lapply(d, function(v) { v <- suppressWarnings(as.numeric(v)); v[v < 0 | v > 3] <- NA; v })
code <- setNames(items, 1:21)
C <- cor(d, use = "pairwise.complete.obs")
mr <- function(a, b) {
  A <- code[as.character(a)]; B <- code[as.character(b)]
  m <- C[A, B, drop = FALSE]
  if (identical(A, B)) mean(m[upper.tri(m)]) else mean(m)
}

cat("\n=== (a) within- vs between-subscale mean correlation ===\n")
wi <- sapply(secs, function(k) mr(canon[[k]], canon[[k]]))
for (k in secs) cat(sprintf("  within  %-11s r = %.3f\n", k, wi[k]))
pr <- combn(secs, 2)
for (i in seq_len(ncol(pr)))
  cat(sprintf("  between %-11s r = %.3f\n", paste(pr[, i], collapse = "-"),
              mr(canon[[pr[1, i]]], canon[[pr[2, i]]])))
ok_a <- all(sapply(secs, function(k)
  all(wi[k] > sapply(setdiff(secs, k), function(o) mr(canon[[k]], canon[[o]])))))
cat(sprintf("  every block more coherent internally than with either other: %s\n", ok_a))

cat("\n=== (b) subscale mean levels (expect Stress > Depression > Anxiety) ===\n")
sm <- sapply(canon, function(v) mean(as.matrix(d[, code[as.character(v)]]), na.rm = TRUE))
for (k in secs) cat(sprintf("  %-11s mean = %.3f\n", k, sm[k]))
ok_b <- sm["Stress"] > sm["Depression"] && sm["Depression"] > sm["Anxiety"]
cat(sprintf("  ordering holds: %s\n", ok_b))

cat("\n=== (c) marker: DASS-21 item 17 lowest of the depression block ===\n")
im <- sort(colMeans(d[, code[as.character(canon$Depression)]], na.rm = TRUE))
for (k in names(im)) cat(sprintf("  %-4s mean = %.3f\n", k, im[k]))
ok_c <- names(im)[1] == "Q17"
cat(sprintf("  lowest depression item is Q17: %s\n", ok_c))

cat("\n=== (d) cross-deposit identity with doi:10.7910/DVN/8YLSMK ===\n")
ok_d <- NA
g <- tempfile(fileext = ".tab")
r <- try(utils::download.file("https://dataverse.harvard.edu/api/access/datafile/13638063",
                              g, quiet = TRUE), silent = TRUE)
if (!inherits(r, "try-error")) {
  b <- utils::read.delim(g, check.names = FALSE)
  bi <- c(paste0("Q", 1:16, "_A"), paste0("Q", 17:21))
  A <- sapply(df[, items], as.numeric); B <- as.matrix(b[, bi])
  eq <- A == B
  cat(sprintf("  respondent ids in same order: %s\n", all(as.numeric(df[["No."]]) == b$NO)))
  cat(sprintf("  cells equal: %d of %d; rows fully equal: %d of %d\n",
              sum(eq), length(eq), sum(apply(eq, 1, all)), nrow(eq)))
  w <- which(!eq, arr.ind = TRUE)
  for (i in seq_len(nrow(w)))
    cat(sprintf("  differs: No.%s %s  TAISB2=%s  8YLSMK=%s\n", df[["No."]][w[i, 1]],
                items[w[i, 2]], A[w[i, 1], w[i, 2]], B[w[i, 1], w[i, 2]]))
  ok_d <- sum(!eq) <= 2
} else cat("  (8YLSMK fetch failed -- corroboration only, not part of the verdict)\n")

cat("\nNot established by any of the above: the order of items WITHIN a subscale.\n")
cat(if (ok_0 && ok_a && ok_b && ok_c) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
