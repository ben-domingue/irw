# verify_SBD_Smith_2020.R -- Step 5b mapping check for SBD_Smith_2020 (batch_416).
#
# Claim: MBDSk (assigned POSITIONALLY by data/SBD_Smith_2020.r, paste0("MBDS",1:22) over the
# 22 unlabeled columns of OSF c4v7g FACTOR/bpses_pre_for_factor.dat) = item k of the
# "Managing Bipolar Disorder Scale (Original Battery)" form (OSF c4v7g, BPSES - Original battery.docx).
#
# Route: Smith, Erceg-Hurn, McEvoy & Lim preprint (OSF ygav5) Table 2 prints, AGAINST EACH ITEM'S
# WORDING, standardized loadings for a unidimensional CFA and for the final bifactor model on the
# 17 retained items. The authors' own lavaan code (OSF R/03-cfa.pdf) gives both model specs
# (MLR, FIML, std.lv, orthogonal). Refitting both specs to the LIVE data under the claimed mapping
# must reproduce Table 2; a permutation of item texts would not. Item 6 ("Limiting alcohol...")
# is checked by the paper's stated average inter-item r = .21 (vs .40 among the other 17).
# NOT established: the order of MBDS18/19/21/22 among themselves -- these four "general
# self-efficacy" items were excluded before any analysis and no per-item statistic is published.
suppressMessages({library(irw); library(lavaan); library(tidyr)})
TABLE <- "SBD_Smith_2020"
d <- irw::irw_fetch(TABLE)
w <- pivot_wider(as.data.frame(d[, c("id", "item", "resp")]), names_from = item, values_from = resp)
keep <- c(1:5, 7:17, 20)                     # form positions of the 17 retained items
x <- as.data.frame(w[, paste0("MBDS", keep)]); names(x) <- paste0("v", keep)
cat("live respondents:", nrow(w), "(paper/FACTOR: 303)\n\n")

# Table 2, rows 1..17 = form items 1-5,7-17,20 (row text quoted in provenance)
lab  <- c("medication as prescribed","medication side effects","regular appointments","discussing difficulties",
          "seeking help","regular sleep","identify EWS depression","identify EWS (hypo)mania",
          "action EWS depression","action EWS (hypo)mania","pleasant activities","changing thoughts",
          "calm me down (hypo)mania","regular daily routine","stress->depressive","stress->(hypo)manic","communicating illness")
uni  <- c(.39,.37,.37,.44,.56,.59,.75,.75,.82,.85,.73,.73,.81,.66,.70,.71,.47)
gen  <- c(.31,.36,.31,.37,.54,.56,.65,.57,.78,.75,.77,.80,.82,.67,.69,.62,.47)

m1 <- paste("gen =~", paste(names(x), collapse = " + "))
m4 <- '
 gen =~ v1 + v2 + v3 + v4 + v5 + v7 + v8 + v9 + v10 + v11 + v12 + v13 + v14 + v15 + v16 + v17 + v20
 grp1 =~ a*v1 + a*v2
 grp2 =~ v3 + v4 + v5 + v20
 grp3 =~ b*v8 + b*v9
 grp4 =~ c*v10 + c*v11
 grp5 =~ d*v12 + d*v13
 grp6 =~ e*v16 + e*v17
 grp7 =~ v8 + v10
 grp8 =~ v9 + v11 + v14 + v17
 grp9 =~ v1 + v3 + v7 + v15
 grp1 ~~ grp2
 grp3 ~~ grp4
 grp3 ~~ grp6'
std <- function(fit, f) { s <- standardizedSolution(fit); s <- s[s$op == "=~" & s$lhs == f, ]; setNames(s$est.std, s$rhs)[names(x)] }
f1 <- cfa(m1, data = x, estimator = "MLR", missing = "FIML", std.lv = TRUE)
f4 <- cfa(m4, data = x, estimator = "MLR", missing = "FIML", std.lv = TRUE, orthogonal = TRUE)
ou <- std(f1, "gen"); og <- std(f4, "gen")

cat(sprintf("%-4s %-8s %-26s %6s %6s %6s %6s\n", "row", "item", "Table 2 wording", "uniP", "uniL", "genP", "genL"))
for (i in 1:17) cat(sprintf("%-4d %-8s %-26s %6.2f %6.3f %6.2f %6.3f\n", i, paste0("MBDS", keep[i]), lab[i], uni[i], ou[i], gen[i], og[i]))
dev <- max(abs(c(ou - uni, og - gen)))
cat(sprintf("\nlargest |live - Table 2| over 34 loadings: %.3f\n", dev))

# Distinguishability: for each Table 2 row, the live item nearest in (uni, gen) must be the assigned one.
D <- outer(1:17, 1:17, Vectorize(function(i, j) sqrt((uni[i] - ou[j])^2 + (gen[i] - og[j])^2)))
nn <- apply(D, 1, which.min)
cat("rows whose nearest live item is the assigned one:", sum(nn == 1:17), "/ 17\n")
if (any(nn != 1:17)) cat("  mismatched rows:", which(nn != 1:17), "\n")

# Item 6: paper says avg inter-item r = .21 vs .40 among the retained items
R <- cor(as.data.frame(w[, paste0("MBDS", c(keep, 6))]), use = "pairwise.complete.obs")
r6 <- mean(R["MBDS6", paste0("MBDS", keep)]); rk <- R[paste0("MBDS", keep), paste0("MBDS", keep)]
rr <- mean(rk[upper.tri(rk)])
cat(sprintf("MBDS6 avg r with the 17: %.3f (paper .21); avg r among the 17: %.3f (paper .40)\n", r6, rr))
R2 <- cor(as.data.frame(w[, paste0("MBDS", 1:22)]), use = "pairwise.complete.obs")
others <- sapply(paste0("MBDS", c(keep, 18, 19, 21, 22)), function(v) mean(R2[v, setdiff(paste0("MBDS", keep), v)]))
cat(sprintf("next-lowest avg r of any other item with the 17: %.3f (%s)\n", min(others), names(which.min(others))))
cat("NOT established: order of MBDS18/19/21/22 among themselves (only their exclusion as a set is documented).\n")

ok <- dev <= 0.03 && all(nn == 1:17) && abs(r6 - .21) <= .03 && r6 < min(others)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
