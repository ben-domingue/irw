# verify_abdullah_2024_blqol.R -- Step 5b mapping check (batch_420)
#
# Claim: live items QOL1_R..QOL5_R are the BLQoL-M items the validation paper
# (Mahd-Ab.lah et al. 2021, IJERPH 18:2487, PMC7967615) codes QOL1..QOL5, whose
# wording its Table 2 prints (work/school, social, hobbies, intimate
# relationships, emotion); and live resp is stored REVERSED (live = 8 - raw), so
# raw 1 "never/not related to me" is live 7 and raw 7 "always" is live 1.
#
# The 2021 CFA sample (n = 323) is the same 323 respondents as the 2024 PeerJ
# deposit this table was built from. Published values compared:
#   Table 5 (CFA, n = 323) raw-scale Mean/SD: QOL1 2.19/0.91, QOL2 2.17/0.90,
#     QOL3 2.22/0.98 (rows 4/5 discussed below).
#   Figure 2 (CFA path diagram): standardised loadings qol1 .87, qol2 .77,
#     qol3 .88, qol4 .33, qol5 .43; one residual covariance qol1<->qol5 = .18.
#
# What this does NOT establish: the code->text tie inside the paper itself
# (Table 2 prints wording against QOL1..QOL5 on its EFA sample; that is taken as
# given, mapping_basis=paper_explicit). The qol4 loading (.33) cannot be
# reproduced from the live table because the processing script dropped the
# 133 respondents coded 0 on QOL4_R in the source .sav; it is not tested here.

suppressMessages({library(irw); library(lavaan)})
TABLE <- "abdullah_2024_blqol"
ok <- TRUE

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))

# --- 1. Direction + items 1-3: raw = 8 - live reproduces Table 5 -----------
pub_m <- c(QOL1_R = 2.19, QOL2_R = 2.17, QOL3_R = 2.22)
pub_s <- c(QOL1_R = 0.91, QOL2_R = 0.90, QOL3_R = 0.98)
cat("Table 5 (raw scale) vs live, reversed (8 - resp) and as stored:\n")
cat(sprintf("%-7s %6s %8s %6s %8s %10s\n", "item", "pubM", "8-live", "pubSD", "sd", "live(as-is)"))
for (it in names(pub_m)) {
    x <- w[[it]]; m <- mean(8 - x, na.rm = TRUE); s <- sd(x, na.rm = TRUE)
    cat(sprintf("%-7s %6.2f %8.3f %6.2f %8.3f %10.3f\n", it, pub_m[it], m, pub_s[it], s, mean(x, na.rm = TRUE)))
    if (abs(m - pub_m[it]) > 0.006 || abs(s - pub_s[it]) > 0.006) ok <- FALSE
}
# the three means are distinct at 2 dp, so a permutation of 1-3 would break this
cat("\n")

# --- 2. Items 4 vs 5 (and 1): Figure 2 CFA with qol1<->qol5 residual --------
fit_one <- function(q4, q5, lab) {
    dd <- data.frame(qol1 = w$QOL1_R, qol2 = w$QOL2_R, qol3 = w$QOL3_R,
                     qol4 = w[[q4]], qol5 = w[[q5]])
    f <- cfa("qol =~ qol1 + qol2 + qol3 + qol4 + qol5\nqol1 ~~ qol5", dd,
             std.lv = TRUE, missing = "ml")
    s <- standardizedSolution(f)
    lam <- s$est.std[s$op == "=~"]
    rc <- s$est.std[s$lhs == "qol1" & s$rhs == "qol5" & s$op == "~~"]
    cat(sprintf("%-38s loadings %s | resid r(qol1,qol5) = %.2f\n", lab,
                paste(sprintf("%.2f", lam), collapse = " "), rc))
    list(lam = lam, rc = rc)
}
cat("Figure 2 published: loadings 0.87 0.77 0.88 0.33 0.43 | resid r(qol1,qol5) = 0.18\n")
a <- fit_one("QOL4_R", "QOL5_R", "as shipped (qol4=QOL4_R, qol5=QOL5_R)")
b <- fit_one("QOL5_R", "QOL4_R", "alternative (qol4=QOL5_R, qol5=QOL4_R)")
pub <- c(0.87, 0.77, 0.88, NA, 0.43)
dev_a <- max(abs(a$lam[-4] - pub[-4]), abs(a$rc - 0.18))
dev_b <- max(abs(b$lam[-4] - pub[-4]), abs(b$rc - 0.18))
cat(sprintf("max deviation on qol1/2/3/5 loadings + residual r: shipped %.3f, alternative %.3f (tol 0.03)\n",
            dev_a, dev_b))
if (dev_a > 0.03 || dev_b <= 0.03) ok <- FALSE

# --- 3. Descriptive: QOL4_R thinning, consistent with "not related to me" ---
n <- colSums(!is.na(w[, paste0("QOL", 1:5, "_R")]))
cat("\nlive n per item:", paste(names(n), n, collapse = ", "), "\n")
cat("QOL4_R (intimate relationships) is the only item with ~40% absent: the source\n",
    ".sav codes 133/323 as 0 there, dropped by data/abdullah_2024_bloating.py's 1-7 filter.\n",
    "Informative about content, not a proof; not scored.\n", sep = "")
cat("Caveat: 2021 Table 5 prints Mean/SD 3.30/1.61 for QOL4 and 1.44/1.01 for QoL5; these\n",
    "match QOL5_R (8-live 3.24/1.53) and QOL4_R-with-0-as-raw-1 respectively, i.e. the Mean/SD\n",
    "cells of rows 4/5 follow the .sav's column order (QOL5_R stored before QOL4_R), while\n",
    "the same table's loadings and Figure 2 follow the names. Not scored.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
