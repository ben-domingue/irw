# verify_pellerin2020_cpc_optimism.R
#
# CLAIM UNDER TEST -- the mapping of the three IRW item codes onto the three
# CPC-12 optimism items (Lorenz et al. 2016, PLOS ONE 11:e0152892, S1 Appendix,
# items 4-6 of the 12-item scale):
#
#   Opt_1 = CPC-12 item 4  "I am looking forward to the life ahead of me."      (AFF1)
#   Opt_2 = CPC-12 item 5  "The future holds a lot of good in store for me."    (AFF5)
#   Opt_3 = CPC-12 item 6  "Overall, I expect more good things to happen to me
#                           than bad."                                          (LOT-R 10)
#
# Nothing in the Pellerin & Raufaste deposit labels Opt_1..Opt_3, so the
# assignment is inferred from the CPC-12's own item order. Two falsifiable
# predictions follow from the CONTENT of those three sentences:
#
#   (P1) Item 4 is the only one that references the respondent's remaining
#        lifespan ("the life ahead of me"). Its correlation with Age must be
#        distinctly more negative than the other two.
#   (P2) Items 4 and 5 come from the same parent scale (AFF, a future-orientation
#        questionnaire) while item 6 is imported from the LOT-R. So the item
#        assigned to 4 must sit closer to the item assigned to 5 than to the item
#        assigned to 6.
#
# DATA: the study's own OSF file (https://osf.io/45aq3/, data.PsyR_lockdown2020.csv),
# read in its WIDE form. This is the exact file data/pellerin2020_covid_resources.py
# melts into the IRW table -- item codes are its literal column names, and the live
# per-item n (1010) equals the number of complete Opt_1..Opt_3 rows here. Using it
# rather than irw::irw_fetch() also keeps this script off the 200GB Redivis export
# quota; the analysis needs the items side by side, which the long table does not give.

CSV <- "https://osf.io/download/dc6me/"
d <- read.csv(CSV)

w0 <- d[d$Wave == 0, ]
w0 <- w0[complete.cases(w0[, c("Opt_1", "Opt_2", "Opt_3")]), ]
o  <- w0[, c("Opt_1", "Opt_2", "Opt_3")]
n  <- nrow(o)
cat(sprintf("wave-0 complete cases: %d (paper N = 674)\n\n", n))

# --- context: subscale membership (pins the block, not the order) -------------
cat(sprintf("Optimism scale column == rowMeans(Opt_1..Opt_3): max |diff| = %.2g\n",
            max(abs(w0$Optimism - rowMeans(o)))))
cat(sprintf("Optimism M = %.2f, SD = %.2f   (paper Table 1: M = 4.84, SD = 1.31)\n\n",
            mean(w0$Optimism), sd(w0$Optimism)))

# Steiger (1980) test for two dependent, overlapping correlations (common index).
steiger <- function(r12, r13, r23, n) {
    r12 <- unname(r12); r13 <- unname(r13); r23 <- unname(r23)
    rm <- (r12 + r13) / 2
    f  <- (1 - r23) / (2 * (1 - rm^2))
    h  <- (1 - f * rm^2) / (1 - rm^2)
    z  <- (atanh(r12) - atanh(r13)) * sqrt((n - 3) / (2 * (1 - r23) * h))
    c(z = z, p = 2 * pnorm(-abs(z)))
}

# --- P1: age gradient ---------------------------------------------------------
ra <- sapply(o, function(x) cor(x, w0$Age))
r  <- cor(o)
cat("P1  correlation with Age (item 4 should be the most negative):\n")
for (i in 1:3) cat(sprintf("      r(%s, Age) = %+.3f\n", names(ra)[i], ra[i]))
s1 <- steiger(ra[1], ra[2], r[1, 2], n)
cat(sprintf("      Opt_1 vs Opt_2 difference: z = %+.2f, p = %.4f\n", s1["z"], s1["p"]))
s1b <- steiger(ra[1], ra[3], r[1, 3], n)
cat(sprintf("      Opt_1 vs Opt_3 difference: z = %+.2f, p = %.4f\n\n", s1b["z"], s1b["p"]))
p1 <- ra[1] < ra[2] && ra[1] < ra[3] && s1["p"] < 0.05 && s1b["p"] < 0.05

# --- P2: parent-scale block ---------------------------------------------------
cat("P2  inter-item correlations (Opt_1 should sit closer to Opt_2 than to Opt_3):\n")
cat(sprintf("      r(Opt_1, Opt_2) = %.3f\n      r(Opt_1, Opt_3) = %.3f\n      r(Opt_2, Opt_3) = %.3f\n",
            r[1, 2], r[1, 3], r[2, 3]))
s2 <- steiger(r[1, 2], r[1, 3], r[2, 3], n)
cat(sprintf("      difference: z = %+.2f, p = %.5f\n\n", s2["z"], s2["p"]))
p2 <- r[1, 2] > r[1, 3] && s2["p"] < 0.05

# --- what this does NOT establish --------------------------------------------
s3 <- steiger(ra[2], ra[3], r[2, 3], n)
cat(sprintf("LIMIT: Opt_2 and Opt_3 are near-synonymous expectancy statements, and the\n"))
cat(sprintf("       age route does not separate them (r = %+.3f vs %+.3f, z = %+.2f, p = %.2f).\n",
            ra[2], ra[3], s3["z"], s3["p"]))
cat("       Their assignment rests on P2 alone -- i.e. on the assumption that the two\n")
cat("       AFF-derived items cohere more tightly with each other than with the\n")
cat("       LOT-R-derived one. Recorded as PARTIAL, not VERIFIED, for that reason.\n\n")

cat(if (p1 && p2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
