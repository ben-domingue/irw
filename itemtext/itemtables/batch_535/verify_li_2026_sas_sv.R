# verify_li_2026_sas_sv.R -- Step 5b mapping evidence, re-runnable.
# (Copied from references/verify_template.R and adapted.)
#
# CLAIM UNDER TEST: live codes SA1..SA10 carry the wording Li & Mao (2026, PLOS ONE
# 21(5):e0349016, doi:10.1371/journal.pone.0349016) print against those same codes in
# Table 2 ("Descriptive Statistics and Predictability of Items"), which lists each
# code, its English item wording and its Mean(SD).
#
# data/li_2026_sas_sv.py melts the deposit columns by name, so the IRW code IS the
# deposit column name (SA1..SA10, figshare 10.6084/m9.figshare.32109184 "Original
# data.xlsx"). The paper ties code -> text explicitly; what this script tests is that
# the live SA-k is the column the paper summarised as SA-k, via route 1 (per-item
# descriptives). Means alone tie at 3.59 (SA5/SA10) and nearly tie at 3.50/3.51
# (SA2/SA9) and 3.29/3.30 (SA8/SA4), so the test uses the (mean, SD) PAIR: every
# published pair is distinct, and each live item must reproduce its own row exactly
# (to the paper's 2-decimal rounding) and be strictly closer to it than to any other.
#
# Also checked: the published scale total 34.89 (SD 7.38) against the live row sum,
# which pins resp as stored raw on 1..6 (1 = strongly disagree), as the paper states.
#
# WHAT THIS DOES NOT ESTABLISH: that the authors' own Table 2 attaches the right
# sentence to each code. That tie is the paper's (paper_explicit); it is corroborated
# only by the paper's order being the canonical Kwon et al. (2013) SAS-SV order.

suppressMessages(library(irw))
TABLE <- "li_2026_sas_sv"
IT <- paste0("SA", 1:10)
PUB_M  <- c(3.22, 3.50, 3.79, 3.30, 3.59, 3.40, 3.70, 3.29, 3.51, 3.59)
PUB_SD <- c(1.11, 1.20, 1.03, 1.16, 1.08, 1.11, 1.13, 1.18, 1.12, 1.14)
names(PUB_M) <- names(PUB_SD) <- IT

d <- as.data.frame(irw::irw_fetch(TABLE))
obs_m  <- tapply(d$resp, d$item, mean)[IT]
obs_sd <- tapply(d$resp, d$item, sd)[IT]

cat(sprintf("%-5s %8s %8s %8s %8s %8s\n", "item", "pub_M", "obs_M", "pub_SD", "obs_SD", "nearest"))
ok_exact <- ok_near <- logical(10)
for (k in seq_along(IT)) {
  dist <- sqrt((obs_m[k] - PUB_M)^2 + (obs_sd[k] - PUB_SD)^2)
  nearest <- names(which.min(dist))
  ok_exact[k] <- round(obs_m[k], 2) == PUB_M[k] && round(obs_sd[k], 2) == PUB_SD[k]
  ok_near[k]  <- nearest == IT[k] && sum(dist == min(dist)) == 1
  cat(sprintf("%-5s %8.2f %8.4f %8.2f %8.4f %8s\n", IT[k], PUB_M[k], obs_m[k],
              PUB_SD[k], obs_sd[k], nearest))
}
pp <- outer(seq_along(IT), seq_along(IT), function(i, j)
  sqrt((PUB_M[i] - PUB_M[j])^2 + (PUB_SD[i] - PUB_SD[j])^2))
diag(pp) <- Inf
cat(sprintf("\nsmallest published (M,SD) separation between two items: %.3f\n", min(pp)))
cat(sprintf("items reproducing their own row exactly at 2dp: %d/10\n", sum(ok_exact)))
cat(sprintf("items uniquely nearest their own row: %d/10\n", sum(ok_near)))

w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
tot <- rowSums(w[, paste0("resp.", IT)])
cat(sprintf("scale total: live %.2f (SD %.2f) vs published 34.89 (7.38)\n", mean(tot), sd(tot)))
tot_ok <- round(mean(tot), 2) == 34.89 && round(sd(tot), 2) == 7.38

pass <- all(ok_exact) && all(ok_near) && min(pp) > 0 && tot_ok
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
