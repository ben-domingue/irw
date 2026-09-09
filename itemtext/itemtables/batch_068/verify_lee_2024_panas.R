# verify_lee_2024_panas.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST. The IRW codes PANAS1..PANAS20 are the raw column names of the
# study's own supplementary workbook (data/lee_2024_cloninger.py melts them by name,
# so there is no positional step), but those names carry no wording. The shipped
# item_text assigns adjective k of the K-PANAS to PANAS{k}, using the item numbering
# the K-PANAS's own authors print for that instrument:
#
#   Park H, Lee J-M, Koo S, Chung S-Y, Lee S, Cho YI (2022) "A PANAS Structure
#   Analysis: On the Validity of a Bifactor Model in Korean College Students",
#   Sustainability 14:16456, doi:10.3390/su142416456 -- Table 3 labels items
#   C1..C20, and Table 1 gives their correlation matrix and means (N = 875 Korean
#   college students). Lee et al. (2024) state they administered "the version of
#   PANAS translated into Korean by Park and Lee (2016)", which is the version that
#   paper (by Park and Lee) analyses.
#
# This script tests that numbering against the live IRW data three ways: the
# published PA/NA subscale means by sex from Lee et al. (2024) Table 2, the
# congruence of the 20x20 correlation matrix with Park et al. (2022) Table 1, and a
# permutation null over within-polarity relabellings.

suppressMessages(library(irw))
TABLE <- "lee_2024_panas"

ADJ <- c("interested","irritable","distressed","alert","excited","ashamed","upset",
         "inspired","strong","nervous","guilty","determined","scared","attentive",
         "hostile","jittery","enthusiastic","active","proud","afraid")
PA <- c(1,4,5,8,9,12,14,17,18,19)   # positive-affect positions implied by ADJ
NA_ <- setdiff(1:20, PA)

d <- irw::irw_fetch(TABLE)
w <- reshape(d[, c("id","item","resp")], idvar = "id", timevar = "item",
             direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
X <- as.matrix(w[, paste0("PANAS", 1:20)])
cat(sprintf("live table: %d respondents x %d items\n\n", nrow(X), ncol(X)))

## ---- Route 3: published subscale means by sex -------------------------------
# Lee et al. (2024) PeerJ 12:e18379, Table 2. Sex is cov_gender in the IRW table
# (1 = male n=195, 2 = female n=332), carried through from the workbook's "sex".
PUB <- rbind(PA = c(male = 29.06, female = 26.71),
             NA_ = c(male = 18.91, female = 20.55))
sex <- d$cov_gender[match(w$id, d$id)]
obs <- rbind(PA  = c(male = mean(rowSums(X[sex == 1, PA])),
                     female = mean(rowSums(X[sex == 2, PA]))),
             NA_ = c(male = mean(rowSums(X[sex == 1, NA_])),
                     female = mean(rowSums(X[sex == 2, NA_]))))
cat("Route 3 -- published subscale means (Lee et al. 2024, Table 2) vs observed:\n")
for (r in 1:2) cat(sprintf("  %-3s male %6.2f vs %6.2f   female %6.2f vs %6.2f\n",
                           rownames(PUB)[r], PUB[r,1], obs[r,1], PUB[r,2], obs[r,2]))
route3 <- max(abs(PUB - obs))
cat(sprintf("  largest deviation %.3f (tolerance 0.05)\n", route3))
# The canonical Watson order would put PA at 1,3,5,9,10,12,14,16,17,19; report it
# so the reader can see the alternative is excluded rather than untested.
cPA <- c(1,3,5,9,10,12,14,16,17,19)
cat(sprintf("  canonical-Watson-order PA would give male %6.2f female %6.2f -- excluded\n\n",
            mean(rowSums(X[sex == 1, cPA])), mean(rowSums(X[sex == 2, cPA]))))

## ---- Route 1/5: correlation-matrix congruence with the instrument's own paper -
# Park et al. (2022) Sustainability 14:16456, Table 1, lower triangle, C1..C20.
L <- list(
  c(),
  c(-0.21),
  c(-0.24, 0.59),
  c( 0.34,-0.23,-0.29),
  c( 0.53,-0.17,-0.27, 0.42),
  c(-0.02, 0.16, 0.24,-0.13,-0.04),
  c(-0.02, 0.57, 0.52,-0.18,-0.15, 0.31),
  c( 0.32,-0.09, 0.02, 0.20, 0.20, 0.14, 0.03),
  c( 0.30,-0.06,-0.04, 0.24, 0.22,-0.04, 0.03, 0.45),
  c(-0.03, 0.27, 0.28,-0.09,-0.04, 0.31, 0.32, 0.18, 0.19),
  c(-0.08, 0.21, 0.29,-0.12,-0.12, 0.45, 0.31, 0.10, 0.02, 0.23),
  c( 0.36,-0.07,-0.09, 0.24, 0.27, 0.04,-0.03, 0.34, 0.39, 0.11, 0.09),
  c(-0.13, 0.29, 0.42,-0.18,-0.17, 0.38, 0.38, 0.07,-0.02, 0.44, 0.45, 0.02),
  c( 0.23,-0.004,-0.02, 0.20, 0.15, 0.12, 0.04, 0.33, 0.40, 0.32, 0.04, 0.40, 0.13),
  c(-0.09, 0.36, 0.42,-0.10,-0.12, 0.28, 0.51, 0.06, 0.08, 0.26, 0.40, 0.07, 0.38, 0.08),
  c(-0.16, 0.34, 0.45,-0.21,-0.19, 0.32, 0.35, 0.03,-0.03, 0.47, 0.34,-0.04, 0.52, 0.07, 0.41),
  c( 0.46,-0.09, 0.10, 0.26, 0.35,-0.02,-0.06, 0.37, 0.44, 0.19,-0.05, 0.43,-0.05, 0.41, 0.03,-0.02),
  c( 0.54,-0.21,-0.29, 0.37, 0.58,-0.06,-0.17, 0.24, 0.34,-0.01,-0.14, 0.31,-0.15, 0.23,-0.16,-0.17, 0.57),
  c( 0.47,-0.20,-0.25, 0.36, 0.45,-0.01,-0.15, 0.33, 0.46, 0.09,-0.09, 0.45,-0.11, 0.37,-0.04,-0.15, 0.57, 0.61),
  c(-0.16, 0.37, 0.49,-0.20,-0.18, 0.37, 0.45, 0.05,-0.02, 0.45, 0.41,-0.01, 0.71, 0.10, 0.45, 0.65,-0.05,-0.19,-0.12))
R <- diag(20)
for (i in 2:20) for (j in 1:(i-1)) R[i,j] <- R[j,i] <- L[[i]][j]
C <- cor(X)
iu <- upper.tri(R)
cong <- function(p) cor(R[iu], C[p, p][iu])
identity_r <- cong(1:20)
cat(sprintf("Route 1/5 -- congruence of the 190 off-diagonal correlations with\n"))
cat(sprintf("  Park et al. (2022) Table 1 under the shipped labelling: r = %.4f\n", identity_r))

set.seed(1)
NPERM <- 20000
null <- numeric(NPERM)
for (k in seq_len(NPERM)) {
  p <- 1:20
  p[PA] <- sample(PA); p[NA_] <- sample(NA_)
  null[k] <- cong(p)
}
beat <- sum(null >= identity_r)
cat(sprintf("  %d random relabellings WITHIN polarity blocks: max %.4f, mean %.4f, %d >= shipped\n",
            NPERM, max(null), mean(null), beat))

## ---- single within-block transpositions -------------------------------------
sw <- data.frame()
for (blk in list(PA, NA_)) for (a in seq_along(blk)) for (b in seq_len(a-1)) {
  p <- 1:20; i <- blk[a]; j <- blk[b]; p[c(i,j)] <- c(j,i)
  sw <- rbind(sw, data.frame(i = i, j = j, r = cong(p)))
}
sw <- sw[order(-sw$r), ]
cat("  best 3 single within-block swaps (shipped = ", sprintf("%.4f", identity_r), "):\n", sep = "")
for (k in 1:3) cat(sprintf("    swap %-2d(%s) <-> %-2d(%s): %.4f\n",
                           sw$i[k], ADJ[sw$i[k]], sw$j[k], ADJ[sw$j[k]], sw$r[k]))

## ---- Route 1: per-item means against the same table --------------------------
PUBM <- c(3.48,3.40,3.06,3.08,3.46,2.59,3.02,2.86,2.96,3.22,2.60,NA,2.77,3.19,
          2.37,2.85,3.35,3.44,3.13,2.76)   # C12 printed as "0.09", a typo; dropped
obsm <- colMeans(X)
ok <- !is.na(PUBM)
rho <- cor(PUBM[ok], obsm[ok], method = "spearman")
cat(sprintf("\nRoute 1 -- per-item means vs Park et al. (2022) Table 1 (19 items,\n  C12 dropped as a printing error): Spearman rho = %.3f, Pearson r = %.3f\n",
            rho, cor(PUBM[ok], obsm[ok])))

## ---- what this does NOT establish -------------------------------------------
cat("\nNot established: items 13 (scared) and 20 (afraid) are not separated by any\n",
    "route here -- they are near-synonyms with near-identical published means\n",
    "(2.77 / 2.76) and observed means (", sprintf("%.2f / %.2f", obsm[13], obsm[20]),
    "), and swapping them moves congruence by\n  less than 0.001. Hence PARTIAL, not VERIFIED.\n", sep = "")

pass <- route3 <= 0.05 && identity_r > 0.9 && beat == 0 && rho > 0.85
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
