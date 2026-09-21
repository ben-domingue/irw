# verify_pierro_2018_assessment_s4.R
#
# CLAIM UNDER TEST (mapping_basis = paper_order)
#   pierro_2018_assessment_s4 holds the 12-item Assessment scale of the Regulatory
#   Mode Questionnaire (Kruglanski et al., 2000), and the .sav column codes the IRW
#   script melts unrenamed (assR1, ass2, ass3, ass4, assR5, ass6, ass7, ass8, ass9,
#   ass10, assR11, ass12) are the assessment items in the RMQ scoring key's own
#   within-subscale order -- 30-item numbers Q2, Q6, Q7, Q9, Q10, Q11, Q15, Q19,
#   Q20, Q22, Q27, Q30 -- with the "R" marking the three reverse-worded items
#   (Q2, Q10, Q27), which that key places at within-subscale positions 1, 5 and 11.
#
# WHAT THIS SCRIPT CHECKS against the live IRW data:
#   (a) SCALE IDENTITY AND STORAGE DIRECTION (route 3, published totals). The
#       deposit's own `assessment` composite is the plain unrecoded mean of the 12
#       columns, so if the paper's published statistics are reproduced by the values
#       exactly as stored, the three R columns must ALREADY be reverse-recoded.
#       That is what decides the shipped anchors for assR1/assR5/assR11 are flipped
#       (resp 1 = Strongly Agree ... resp 6 = Strongly Disagree against the printed
#       statement). Published for Study 4: alpha .77, M 3.65, SD .67.
#   (b) WHICH POSITIONS ARE REVERSE-WORDED (route 6, keying polarity). Undo the
#       recoding (7 - x on the three R codes) to recover the raw administered
#       direction; in raw form exactly the reverse-worded items must show negative
#       corrected item-rest correlations. Position 1/5/11 is the RMQ key's
#       prediction, and it is what ties the code numbering to the instrument's
#       item order.
#       NOTE, because it differs from the sibling pierro_2018_assessment_s1: in the
#       STORED (already-recoded) direction the three R items are NOT cleanly the
#       three lowest item-rest values here -- ass2 (0.345) sits between assR5
#       (0.328) and assR11 (0.352). The raw-direction sign test below is the one
#       that separates them, and it is clean.
#   (c) CORROBORATION (route 1, cross-sample/cross-language, suggestive only).
#       The per-item reliability profile is compared with the Swedish RMQ
#       validation's published standardized loadings (Garcia et al., 2017, PeerJ
#       5:e3986, Table 3), keyed to the same 30-item numbering.
#
# WHAT IT DOES NOT ESTABLISH: nothing here separates the nine positively-worded
#   items from one another, nor the three reverse-worded ones from one another.
#   Alpha is permutation-invariant by construction and the sign test pins a
#   polarity CLASS, not an order within it. Their assignment rests on the RMQ
#   scoring key's enumeration. Verification status is PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "pierro_2018_assessment_s4"
ORDER <- c("assR1","ass2","ass3","ass4","assR5","ass6","ass7","ass8","ass9",
           "ass10","assR11","ass12")
REV   <- c("assR1","assR5","assR11")   # within-subscale positions 1, 5, 11

# Pierro et al. (2018) PLoS ONE 13(3):e0193357, Study 4 Measures:
# "the alpha for the assessment scale was .77 ... M of the assessment score was
#  3.65 (SD = .67)".
PUB_ALPHA <- 0.77; PUB_M <- 3.65; PUB_SD <- 0.67
TOL_A <- 0.01; TOL_M <- 0.01

# Garcia et al. (2017) PeerJ 5:e3986 Table 3, standardized loadings (N = 650),
# in canonical Assessment subscale order (2R,6,7,9,10R,11,15,19,20,22,27R,30).
SWED <- c(.26, .46, .53, .55, .07, .63, .49, .66, .64, .48, .42, .44)

alpha <- function(X) { k <- ncol(X); k/(k-1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X))) }
itemrest <- function(X) sapply(colnames(X), function(c) cor(X[[c]], rowSums(X) - X[[c]]))

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id","item","resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- w[complete.cases(w[, ORDER]), ORDER, drop = FALSE]
cat(sprintf("respondents with complete data: %d x %d items\n\n", nrow(X), ncol(X)))

sc <- rowMeans(X)
a_stored <- alpha(X)
Y <- X; Y[, REV] <- 7 - Y[, REV]
a_flipped <- alpha(Y)

cat("(a) scale identity + storage direction -- against Study 4's published numbers\n")
cat(sprintf("    alpha   published %.2f   as stored %.4f  (diff %+.4f)\n", PUB_ALPHA, a_stored, a_stored - PUB_ALPHA))
cat(sprintf("    mean    published %.2f   as stored %.4f  (diff %+.4f)\n", PUB_M, mean(sc), mean(sc) - PUB_M))
cat(sprintf("    SD      published %.2f   as stored %.4f  (diff %+.4f)\n", PUB_SD, sd(sc), sd(sc) - PUB_SD))
cat(sprintf("    alpha if assR1/assR5/assR11 are flipped (7-x): %.4f  (mean %.4f, SD %.4f)\n",
            a_flipped, mean(rowMeans(Y)), sd(rowMeans(Y))))
cat("    -> the stored values already carry the reversal; flipping misses all three published values.\n\n")

raw <- Y   # raw administered direction
ir_raw <- itemrest(raw); ir_st <- itemrest(X)
cat("(b) keying polarity -- corrected item-rest r, raw (un-recoded) vs stored\n")
cat(sprintf("    %-8s %-4s %10s %10s\n", "item", "key", "raw", "stored"))
for (c in ORDER) cat(sprintf("    %-8s %-4s %+10.3f %+10.3f\n", c,
                             if (c %in% REV) "[R]" else "", ir_raw[[c]], ir_st[[c]]))
neg <- names(ir_raw)[ir_raw < 0]
cat(sprintf("\n    negative in raw direction: %s\n", paste(sort(neg), collapse = ", ")))
cat(sprintf("    RMQ scoring key predicts : %s\n", paste(sort(REV), collapse = ", ")))
cat(sprintf("    stored-direction three lowest (NOT clean here): %s\n\n",
            paste(names(sort(ir_st))[1:3], collapse = ", ")))

rho <- suppressWarnings(cor(as.numeric(ir_st[ORDER]), SWED, method = "spearman"))
cat("(c) corroboration -- item profile vs Swedish RMQ loadings (Garcia et al. 2017)\n")
cat(sprintf("    Spearman rho = %.3f\n", rho))
set.seed(1)
nr <- setdiff(seq_along(ORDER), match(REV, ORDER))
perm <- replicate(5000, { s <- SWED; s[nr] <- sample(s[nr])
                          suppressWarnings(cor(as.numeric(ir_st[ORDER]), s, method = "spearman")) })
cat(sprintf("    %.3f of 5000 permutations of the 9 non-reverse assignments reach rho >= observed\n", mean(perm >= rho)))
cat("    -> suggestive, NOT decisive; the nine non-reverse positions rest on the RMQ key's order.\n\n")

cat("NOT ESTABLISHED: the order of the nine positively-worded items among themselves,\n")
cat("nor which of Q2/Q10/Q27 is assR1 vs assR5 vs assR11. Status is PARTIAL.\n\n")

ok <- abs(a_stored - PUB_ALPHA) <= TOL_A &&
      abs(mean(sc) - PUB_M) <= TOL_M && abs(sd(sc) - PUB_SD) <= TOL_M &&
      a_flipped < a_stored && setequal(neg, REV)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
