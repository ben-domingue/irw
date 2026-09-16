# verify_wu_2024_resilience.R -- Step 5b re-runnable evidence.
#
# CLAIM UNDER TEST. wu_2024_resilience's B1..B6 are the "Resilience" block of the
# PLOS ONE S1 Data workbook (Wu et al. 2024, doi:10.1371/journal.pone.0312597),
# which the paper identifies as the Brief Resilience Scale (Smith et al., 2008),
# 6 items, half positively and half negatively worded. The shipped file asserts:
#   (A) B1/B3/B5 carry the three POSITIVELY worded BRS items (1, 3, 5) and
#       B2/B4/B6 the three NEGATIVELY worded ones (2, 4, 6), i.e. the block is in
#       canonical BRS order, stored RAW (not reverse-recoded); and
#   (B) option_text runs 1 = Strongly Disagree .. 5 = Strongly Agree, NOT the
#       reverse -- which is the only other reading consistent with (A) alone.
#
# (A) is tested by the sign pattern of the item correlation matrix (route 6).
# (B) is tested by reproducing a number the paper published (route 3): scoring
# resilience with 2/4/6 reversed on a 1=SD..5=SA coding must give the paper's
# r(resilience, SFV addiction) = -0.360; the flipped anchor reading gives +0.360.
#
# WHAT THIS DOES NOT ESTABLISH: the order WITHIN each polarity class. B1/B3/B5
# could be any permutation of BRS items 1/3/5, and B2/B4/B6 of 2/4/6. Hence
# status=PARTIAL, not VERIFIED.
#
# Data source: the PLOS S1 Data workbook itself, i.e. the file
# data/wu_2024_video_addiction.py melts with no rename or recode (it is a bare
# pandas melt of columns B1..B6), so source column B<n> IS live item B<n>.
# Deliberately not calling irw_fetch(): a full export burns the 200GB/30d cap
# and would add nothing here, since the live values are this file's values.

suppressMessages(library(readxl))

URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0312597.s001")
tf <- tempfile(fileext = ".xlsx")
download.file(URL, tf, quiet = TRUE, mode = "wb")
d <- as.data.frame(read_excel(tf, skip = 1))

A <- paste0("A", 1:11); B <- paste0("B", 1:6); D <- paste0("D", 1:14)
for (cc in c(A, B, D)) d[[cc]] <- suppressWarnings(as.numeric(d[[cc]]))
d <- d[stats::complete.cases(d[, c(A, B, D)]), ]
cat(sprintf("S1 Data: %d complete rows over the A, B and D blocks (paper N = 560)\n\n", nrow(d)))

ok <- TRUE

## ---- (A) polarity classes -------------------------------------------------
R <- cor(d[, B])
cat("(A) correlation matrix of B1..B6 (raw, as stored):\n")
print(round(R, 3))
odd <- c("B1", "B3", "B5"); even <- c("B2", "B4", "B6")
same <- c(R[odd, odd][upper.tri(diag(3))], R[even, even][upper.tri(diag(3))])
cross <- as.vector(R[odd, even])
cat(sprintf("\n  same-parity  r: %d of %d positive, range %+.3f .. %+.3f\n",
            sum(same > 0), length(same), min(same), max(same)))
cat(sprintf("  cross-parity r: %d of %d negative, range %+.3f .. %+.3f\n",
            sum(cross < 0), length(cross), min(cross), max(cross)))
a_ok <- all(same > 0) && all(cross < 0)
cat(sprintf("  => two polarity classes {B1,B3,B5} / {B2,B4,B6}, stored raw: %s\n\n",
            if (a_ok) "YES" else "NO"))
ok <- ok && a_ok

## ---- (B) anchor direction, against the paper's published correlations ------
PUB_RES_SFV <- -0.360   # Wu et al. (2024), Table 3 / section 4.3, text
PUB_PP_SFV  <- -0.408   # same sentence, used here as a control
TOL <- 0.01

pp  <- rowMeans(d[, A])
sfv <- rowMeans(d[, D])
res_asshipped <- rowMeans(cbind(d[, odd], 6 - d[, even]))   # 1=SD..5=SA
res_flipped   <- rowMeans(cbind(6 - d[, odd], d[, even]))   # 1=SA..5=SD

r_shipped <- cor(res_asshipped, sfv)
r_flipped <- cor(res_flipped,   sfv)
r_ctrl    <- cor(pp, sfv)

cat("(B) scale-level reproduction of the paper's published correlations:\n")
cat(sprintf("  %-46s published %+.3f   observed %+.3f\n",
            "r(proactive personality, SFV addiction) [control]", PUB_PP_SFV, r_ctrl))
cat(sprintf("  %-46s published %+.3f   observed %+.3f\n",
            "r(resilience, SFV addiction) AS SHIPPED", PUB_RES_SFV, r_shipped))
cat(sprintf("  %-46s published %+.3f   observed %+.3f  <- rejected\n",
            "r(resilience, SFV addiction) FLIPPED anchors", PUB_RES_SFV, r_flipped))
cat(sprintf("  as-shipped mean resilience score %.3f (paper Table 2: 3.317 non-addicts, 2.847 addicts)\n",
            mean(res_asshipped)))
b_ok <- abs(r_shipped - PUB_RES_SFV) <= TOL &&
        abs(r_ctrl    - PUB_PP_SFV)  <= TOL &&
        abs(r_flipped - PUB_RES_SFV) >  TOL
cat(sprintf("  => 1 = Strongly Disagree .. 5 = Strongly Agree: %s\n\n",
            if (b_ok) "CONFIRMED" else "NOT CONFIRMED"))
ok <- ok && b_ok

cat("Note: neither check separates B1 from B3 from B5, nor B2 from B4 from B6.\n",
    "That ordering rests on the block being administered in canonical BRS order,\n",
    "which nothing in the deposit or the paper states. Status is PARTIAL.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
