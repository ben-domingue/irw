# verify_li_2021_knowledge_sharing.R -- Step 5b, route 1 (per-item published statistics).
#
# CLAIM UNDER TEST: the live item codes KS1..KS4 are the same KS1..KS4 the source
# paper analysed, in the same order -- i.e. the KS block was not permuted between
# the S2 workbook and the IRW table, so the appendix's "Knowledge Sharing（KS）"
# items 1-4 attach to the codes they are shipped against.
#
# FALSIFIABLE PREDICTION: Li, Wu & Xiong (2021) PLOS ONE 16(5):e0250878, Table 2
# ("Convergent validity of SIB, KS, OCD, CQ", t002, read as an image -- the values
# are not in the article text) publishes standardized CFA loadings and their SEs
# per item code. A one-factor CFA on the four live items must reproduce them.
# The published loadings are 0.794/0.820/0.880/0.827; KS1 and KS3 are separated
# from everything else outright, while KS2 and KS4 differ by only 0.007 and are NOT
# separated by this route (see Note 1 in the output).
#
# WHAT THIS DOES NOT ESTABLISH: it cannot test that S1 Appendix item n is the
# column named KSn. That link rests on the appendix section being headed
# "Knowledge Sharing（KS）" and numbering its items 1-4 against the S2 header's
# KS1..KS4 (an explicit code-label match), not on anything in the data -- the live
# item means span only 0.31 (4.83..5.14), far too little to separate a permutation
# of the appendix numbering. Hence PARTIAL, not VERIFIED.

suppressMessages({library(irw); library(dplyr); library(tidyr); library(lavaan)})

TABLE <- "li_2021_knowledge_sharing"
ITEMS <- paste0("KS", 1:4)

# Li, Wu & Xiong (2021) PLOS ONE 16(5):e0250878, Table 2 (t002).
PUB_EST <- c(KS1 = 0.794, KS2 = 0.820, KS3 = 0.880, KS4 = 0.827)
PUB_SE  <- c(KS1 = 0.024, KS2 = 0.022, KS3 = 0.018, KS4 = 0.022)
TOL_EST <- 0.01
TOL_SE  <- 0.005

d <- irw::irw_fetch(TABLE)
w <- d |> select(id, item, resp) |> pivot_wider(names_from = item, values_from = resp)
fit <- cfa("KS =~ KS1 + KS2 + KS3 + KS4", data = w, std.lv = TRUE)
s <- standardizedSolution(fit) |> filter(op == "=~")
obs_est <- setNames(s$est.std, s$rhs)[ITEMS]
obs_se  <- setNames(s$se,      s$rhs)[ITEMS]
obs_mean <- tapply(d$resp, d$item, mean)[ITEMS]

cat(sprintf("%-5s %10s %10s %8s %10s %10s %8s %8s\n",
            "item", "pub.est", "obs.est", "diff", "pub.se", "obs.se", "diff", "mean"))
for (i in ITEMS)
    cat(sprintf("%-5s %10.3f %10.3f %8.3f %10.3f %10.3f %8.3f %8.2f\n",
                i, PUB_EST[i], obs_est[i], obs_est[i] - PUB_EST[i],
                PUB_SE[i], obs_se[i], obs_se[i] - PUB_SE[i], obs_mean[i]))

worst_est <- max(abs(obs_est - PUB_EST))
worst_se  <- max(abs(obs_se  - PUB_SE))
cat(sprintf("\nlargest |loading diff| = %.4f (tol %.3f); largest |SE diff| = %.4f (tol %.3f)\n",
            worst_est, TOL_EST, worst_se, TOL_SE))

# How much worse is every rival assignment? Loadings are permuted, data are not.
perms <- list(c(2,1,3,4), c(1,3,2,4), c(1,2,4,3), c(3,2,1,4), c(4,2,3,1), c(1,4,3,2),
              c(2,1,4,3), c(4,3,2,1), c(2,3,4,1), c(4,1,2,3))
cat("\nrival assignments (published loadings permuted), largest |diff|:\n")
for (p in perms)
    cat(sprintf("  %-20s %.4f\n", paste(ITEMS[p], collapse = ","),
                max(abs(obs_est - PUB_EST[p]))))

cat("\nNote 1: KS2 and KS4 are NOT separated by this route -- their published loadings\n",
    "differ by only 0.007 (0.820 vs 0.827) with identical SEs (0.022), so the rival\n",
    "sweep scores the KS2<->KS4 swap at 0.0074, inside the tolerance. KS1 and KS3 are\n",
    "each separated outright (every rival involving them scores >= 0.026).\n",
    "Note 2: this route pins the code<->data alignment, but NOT that S1 Appendix item n\n",
    "is column KSn -- that is an explicit code-label match, and the item means\n",
    "(4.83/5.07/5.14/4.93) could not separate a permuted appendix.\n", sep = "")

cat(if (worst_est <= TOL_EST && worst_se <= TOL_SE) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
