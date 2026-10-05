# verify_enders_2022_covid_vax_misinfo.R -- Step 5b re-runnable check (batch_570)
#
# CLAIM. COVVAXINFO_1..5 carry:
#   COVVAXINFO_2  "The COVID-19 vaccine can give you COVID-19."                                   (Table 1 row 1, 18%)
#   COVVAXINFO_4  "The COVID-19 vaccine is a scam by the pharmaceutical companies to make money." (Table 1 row 2, 15%)
#   COVVAXINFO_5  "The COVID-19 vaccine will alter your DNA."                                     (Table 1 row 3, 12%)
#   COVVAXINFO_1, COVVAXINFO_3  = {"causes infertility" (row 4, 11%), "shed" (row 5, 11%)} in
#                                 UNKNOWN order -- shipped with blank item_text.
# Table 1 of Enders et al. (2022, PLOS ONE e0276082) is sorted by % agreeing; its "(Item N)"
# labels are rank positions, not codes (same trap as batch_568/569).
#
# DERIVATION. data/enders_2022_conspiracy_vaccine.py keeps the Qualtrics column names
# (COVVAXINFO_1..5) as `item`; Raw Data.csv (OSF 6a7et) has no question-text row and no codebook;
# Analyses.do (lines 166-174, 512-514) only uses covvaxinfo_1..5 and dichotomises at >3 -- no
# per-item names. So the mapping rests on the data vs Table 1's % agree.
#
# ROUTE 1. Published % agree ("agree"/"strongly agree" = resp >= 4, the do-file's dich cut):
#   18/15/12/11/11. Score every one of the 120 assignments of the five rows to the five codes by
#   total absolute deviation. PASS requires: (i) the best assignments put row1->_2, row2->_4,
#   row3->_5; (ii) the only assignments achieving the minimum differ solely in swapping rows 4/5
#   between _1 and _3 (the unresolved pair); (iii) every other assignment is clearly worse
#   (margin >= 1 point of summed deviation); (iv) the published 5-item scale alpha .93, M 2.16,
#   SD 1.06 is reproduced (direction/scale identity check).

suppressMessages(library(irw))

TABLE <- "enders_2022_covid_vax_misinfo"
d <- as.data.frame(irw::irw_fetch(TABLE))
it <- paste0("COVVAXINFO_", 1:5)

obs <- sapply(it, function(i) 100 * mean(d$resp[d$item == i] >= 4, na.rm = TRUE))
ROWS <- c("give you COVID-19", "scam by pharma", "alter your DNA", "causes infertility", "shed chemicals")
PUB <- c(18, 15, 12, 11, 11)

cat("Live % agree (resp >= 4):\n")
for (i in it) cat(sprintf("  %-13s %7.3f  (rounds to %d)\n", i, obs[i], round(obs[i])))
cat("Table 1:", paste(sprintf("%s %d", ROWS, PUB), collapse = " | "), "\n\n")

perms <- as.matrix(expand.grid(rep(list(1:5), 5)))
perms <- perms[apply(perms, 1, function(z) length(unique(z)) == 5), ]   # perms[k, code] = Table 1 row
dev <- apply(perms, 1, function(p) sum(abs(obs - PUB[p])))
exact <- apply(perms, 1, function(p) sum(round(obs) == PUB[p]))
o <- order(dev)
cat("Best assignments (code -> Table 1 row), by summed |deviation|:\n")
for (k in o[1:6]) cat(sprintf("  _1..5 -> rows %s   sumdev %.3f   exact-rounded %d/5\n",
                              paste(perms[k, ], collapse = ","), dev[k], exact[k]))

best <- perms[dev <= min(dev) + 1e-9, , drop = FALSE]
ok_i  <- all(best[, 2] == 1 & best[, 4] == 2 & best[, 5] == 3)
ok_ii <- nrow(best) == 2 && all(sort(best[, 1]) == c(4, 5)) && all(sort(best[, 3]) == c(4, 5))
margin <- sort(unique(round(dev, 9)))[2] - min(dev)
ok_iii <- margin >= 1
cat(sprintf("\n  minimum sumdev %.3f attained by %d assignments; next-best margin %.3f\n",
            min(dev), nrow(best), margin))

# (iv) published 5-item scale
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- w[complete.cases(w[, it]), it]
alpha <- 5 / 4 * (1 - sum(apply(X, 2, var)) / var(rowSums(X))); s <- rowMeans(X)
cat(sprintf("  scale: alpha %.4f  M %.4f  SD %.4f  (published .93 / 2.16 / 1.06)\n", alpha, mean(s), sd(s)))
ok_iv <- round(alpha, 2) == 0.93 && round(mean(s), 2) == 2.16 && round(sd(s), 2) == 1.06

cat("\nDATA/SOURCE DEFECT: Table 1 prints 12% for the DNA row, but COVVAXINFO_5's live value 12.567\n",
    "rounds to 13; no assignment reproduces all five rounded percentages. The claim is the best fit,\n",
    "not an exact reproduction.\n",
    "NOT established: which of COVVAXINFO_1 (", sprintf("%.3f", obs[1]), ") and COVVAXINFO_3 (",
    sprintf("%.3f", obs[3]), ") is 'infertility' vs 'shed' -- both print as 11%, so their text is shipped blank.\n",
    "Also not established: 5 = strongly agree vs 4 (the >=4 cut shows only that {4,5} are the agree pair).\n", sep = "")
cat(if (ok_i && ok_ii && ok_iii && ok_iv) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
