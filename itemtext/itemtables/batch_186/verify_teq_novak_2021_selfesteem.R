# verify_teq_novak_2021_selfesteem.R
#
# CLAIM UNDER TEST -----------------------------------------------------------
# The IRW item codes Self_esteem_1 .. Self_esteem_10 are the column names of the
# study's own OSF file data_from_excel_12_2_2020.rds (osf.io/5mz8g; data/teq_novak_2021.R
# pivots Self_esteem_1:Self_esteem_10 with no rename). The file carries NO text at
# any level (plain integer columns, no labels), so the text was attached by
# reconstruction, as the Rosenberg Self-Esteem Scale in the widely circulated
# order that is negatively worded at positions 2, 5, 6, 8, 9:
#   1 (+) On the whole, I am satisfied with myself.
#   2 (-) At times I think I am no good at all.
#   3 (+) I feel that I have a number of good qualities.
#   4 (+) I am able to do things as well as most other people.
#   5 (-) I feel I do not have much to be proud of.
#   6 (-) I certainly feel useless at times.
#   7 (+) I feel that I'm a person of worth, at least on an equal plane with others.
#   8 (-) I wish I could have more respect for myself.
#   9 (-) All in all, I am inclined to feel that I am a failure.
#  10 (+) I take a positive attitude toward myself.
# and the stored 0..3 codes run so that a HIGHER code = LOWER self-esteem on every
# item: (+) items 0 = Strongly Agree .. 3 = Strongly Disagree, (-) items
# 0 = Strongly Disagree .. 3 = Strongly Agree.
#
# FOUR FALSIFIABLE PREDICTIONS
# (A) Data already polarity-aligned: all 45 inter-item correlations positive.
# (B) Direction: every RSES item correlates NEGATIVELY with every item of the
#     Satisfaction With Life Scale in the same file (SWLS, no reverse items,
#     item 5 lowest mean = standard 1 = disagree .. 7 = agree coding), and the
#     RSES total correlates positively with the BFI neuroticism total.
# (C) Polarity class via method factor: among all 126 balanced 5/5 splits, the
#     split {1,3,4,7,10} | {2,5,6,8,9} has the LARGEST mean within-block minus
#     between-block correlation. (Rosenberg's 1965 / current UMD-form order would
#     predict {1,2,4,6,7} | {3,5,8,9,10} instead.)
# (D) Same form as the research group's other Czech RSES sample
#     (CV_OASIS_ODSIS_PPE_Novak_2020, OSF osf.io/hvx57 + teybc), whose RAW data
#     show the sign pattern of negatives {2,5,6,8,9} directly and whose analysis
#     script reverses exactly those five. After aligning that sample to this
#     table's direction, the identity alignment of the two samples' 45-r
#     correlation matrices + 10-item mean profiles must rank in the top 5 of all
#     10! = 3,628,800 permutations.
#     Plus marker (route 7): Self_esteem_8 ("wish ... more respect") has the
#     highest mean (least self-esteem) and lowest corrected item-total r.
#
# WHAT THIS DOES NOT ESTABLISH: (D) is carried almost entirely by the polarity
# split and a few distinctive items; 5<->6 and 3<->4 swaps score about as well as
# identity (one swap beats it). And (D) only ties this table to the sibling's
# order, whose within-class order is itself the circulated-order assumption, not
# a label. So polarity class, direction and Self_esteem_8 are pinned; order within
# {1,3,4,7,10} and within {2,5,6,9} is not. PARTIAL.

suppressMessages(library(irw))
TABLE <- "teq_novak_2021_selfesteem"
ok <- TRUE
td <- tempdir()
dl <- function(id, f) { p <- file.path(td, f); if (!file.exists(p)) download.file(paste0("https://osf.io/download/", id, "/"), p, mode = "wb", quiet = TRUE); p }

live <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(live[, c("id", "item", "resp")]), idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
x <- w[, paste0("Self_esteem_", 1:10)]; x <- x[complete.cases(x), ]
cat("live complete cases:", nrow(x), "\n")

src <- readRDS(dl("5mz8g", "data_from_excel_12_2_2020.rds"))
srcx <- src[complete.cases(src[, paste0("Self_esteem_", 1:10)]), paste0("Self_esteem_", 1:10)]
dm <- max(abs(colMeans(srcx) - colMeans(x)))
cat(sprintf("source rds reproduces live item means: max |diff| = %.2e (n %d vs %d)\n", dm, nrow(srcx), nrow(x)))
ok <- ok && dm < 1e-12

R <- cor(x); ut <- upper.tri(R)
cat(sprintf("\n(A) inter-item r: min %.2f, max %.2f, negative: %d of 45\n", min(R[ut]), max(R[ut]), sum(R[ut] < 0)))
ok <- ok && all(R[ut] > 0)

sw <- src[, grep("^SWLS_", names(src))]; bf <- src[, grep("^BFIN_", names(src))]
se <- src[, paste0("Self_esteem_", 1:10)]
C <- cor(se, sw, use = "pairwise")
cat("(B) SWLS item means:", paste(round(colMeans(sw, na.rm = TRUE), 2), collapse = " "), "\n")
cat(sprintf("(B) RSES item x SWLS item r: range %.2f .. %.2f, negative %d of %d\n", min(C), max(C), sum(C < 0), length(C)))
rt <- cor(rowSums(se), cbind(SWLS = rowSums(sw), BFIN = rowSums(bf)), use = "pairwise")
cat(sprintf("(B) RSES total r with SWLS total %.3f, with BFI-N total %.3f\n", rt[1], rt[2]))
ok <- ok && all(C < 0) && rt[1] < -0.3 && rt[2] > 0.3

diag(R) <- NA
sp <- combn(10, 5); sp <- sp[, sp[1, ] == 1, drop = FALSE]
con <- apply(sp, 2, function(g) { h <- setdiff(1:10, g)
  mean(c(R[g, g][upper.tri(R[g, g])], R[h, h][upper.tri(R[h, h])])) - mean(R[g, h]) })
o <- order(-con)
cat("\n(C) top balanced splits by within-minus-between r:\n")
for (i in o[1:4]) cat(sprintf("   {%s} | {%s}  %.4f\n", paste(sp[, i], collapse = ","), paste(setdiff(1:10, sp[, i]), collapse = ","), con[i]))
iu <- which(apply(sp, 2, function(g) all(g == c(1, 3, 4, 7, 10))))
i65 <- which(apply(sp, 2, function(g) all(g == c(1, 2, 4, 6, 7))))
cat(sprintf("(C) claimed split rank %d of 126; Rosenberg-1965/UMD-form split rank %d (%.4f)\n", which(o == iu), which(o == i65), con[i65]))
ok <- ok && which(o == iu) == 1

rd <- function(p) { d <- read.csv2(p); if (!"RSES_1" %in% names(d)) NULL else d[, paste0("RSES_", 1:10)] }
s <- do.call(rbind, Filter(Negate(is.null), list(rd(dl("hvx57", "sib_ex.csv")), rd(dl("teybc", "sib_pa.csv")))))
s <- s[complete.cases(s), ]
neg <- c(2, 5, 6, 8, 9)
sr <- cor(s)[1, ]
cat(sprintf("\n(D) sibling raw n=%d; r with RSES_1: %s\n", nrow(s), paste(round(sr[-1], 2), collapse = " ")))
ok <- ok && all(which(sr[-1] < 0) + 1 == neg)
sc <- s; for (i in 1:10) sc[, i] <- if (i %in% neg) 4 - s[, i] else s[, i] - 1
m1 <- colMeans(x); m2 <- colMeans(sc); R1 <- cor(x); R2 <- cor(sc)
cat("(D) means, this table :", paste(sprintf("%.2f", m1), collapse = " "), "\n")
cat("(D) means, sibling aln:", paste(sprintf("%.2f", m2), collapse = " "), "\n")
# enumerate all 10! permutations in chunks (first element fixed per chunk)
perms_of <- function(v) { if (length(v) == 1) return(matrix(v, 1)); do.call(rbind, lapply(seq_along(v), function(i) cbind(v[i], perms_of(v[-i])))) }
z <- function(M) (M - rowMeans(M)) / apply(M, 1, sd)
iu0 <- row(R1)[ut]; iu1 <- col(R1)[ut]
a <- (R1[ut] - mean(R1[ut])) / sd(R1[ut]); mz <- (m1 - mean(m1)) / sd(m1)
idscore <- NA; nge <- 0; better <- character(0)
for (f in 1:10) {
  P <- cbind(f, perms_of(setdiff(1:10, f)))
  B <- matrix(R2[cbind(as.vector(P[, iu0]), as.vector(P[, iu1]))], nrow(P))
  sc1 <- as.vector(z(B) %*% a) / 44
  sc2 <- as.vector(z(matrix(m2[P], nrow(P))) %*% mz) / 9
  tot <- sc1 + sc2
  if (f == 1) { idx <- which(apply(P, 1, function(p) all(p == 1:10))); idscore <- tot[idx]
    cat(sprintf("(D) identity: corr-matrix similarity %.3f, mean-profile r %.3f\n", sc1[idx], sc2[idx])) }
  hit <- which(tot > idscore + 1e-12); nge <- nge + length(hit)
  better <- c(better, apply(P[hit, , drop = FALSE], 1, paste, collapse = ","))
}
cat(sprintf("(D) permutations of 3,628,800 scoring strictly above identity: %d  %s\n", nge, paste(better, collapse = " ; ")))
ok <- ok && nge <= 4

it <- sapply(1:10, function(i) cor(x[, i], rowSums(x[, -i])))
cat(sprintf("\nmarker: Self_esteem_8 mean %.2f (next highest %.2f); item-total %.2f (next lowest %.2f)\n",
            m1[8], max(m1[-8]), it[8], min(it[-8])))
ok <- ok && which.max(m1) == 8 && which.min(it) == 8

cat("\nNot established: order within {1,3,4,7,10} and within {2,5,6,9} (3<->4 and 5<->6 swaps score near identity).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
