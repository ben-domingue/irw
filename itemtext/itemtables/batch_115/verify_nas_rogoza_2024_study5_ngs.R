# verify_nas_rogoza_2024_study5_ngs.R
#
# CLAIM UNDER TEST (mapping_basis = paper_order):
#   NGS1 = Genialny   / Brilliant
#   NGS2 = Wspaniały  / Glorious
#   NGS3 = Potężny    / Powerful
#   NGS4 = Prestiżowy / Prestigious
#
# The .sav (OSF u93eq, "Study 5 NAS.sav") carries NO variable labels and NO value
# labels, so the adjective behind each column code is an ORDER inference from two
# sources that agree: the study's own "Study 5 Codebook - Daily.docx" (Polish, under
# the heading NGS: Genialny / Wspaniały / Potężny / Prestiżowy) and the paper's own
# Study 5 Measures paragraph ("...and the NGS (Brilliant, Glorious, Powerful,
# Prestigious)"). Both are order sources; this script tests that order against data.
#
# FALSIFIABLE PREDICTION. Two of the four adjectives are self-excellence terms
# (Brilliant, Glorious) and two are status/dominance terms (Powerful, Prestigious).
# If the claimed order is right, the two pairs are {NGS1,NGS2} and {NGS3,NGS4}, and
# a two-block structure should appear in the correlation matrix and in the item
# locations. This is what would break if the assignment were permuted ACROSS the
# pair boundary -- in particular it discriminates against the one rival ordering
# on record, the order in which Edershile & Wright (2021), the ESM study these four
# items were taken from, list them: Glorious, Prestigious, Brilliant, Powerful.
# Under that rival, the pairs would be {NGS1,NGS3} and {NGS2,NGS4}.
#
# WHAT THIS DOES NOT ESTABLISH: nothing here separates Brilliant from Glorious, or
# Powerful from Prestigious. Every check below is symmetric within a pair. The
# recorded status is therefore PARTIAL, not VERIFIED.
#
# Check 3 is corroboration of the CODE axis only (live table == the .sav the
# codebook describes), not of the adjective assignment; it is reported separately
# and is not what carries the verdict.

suppressMessages({library(irw); library(dplyr); library(tidyr)})

TABLE <- "nas_rogoza_2024_study5_ngs"
IT    <- c("NGS1","NGS2","NGS3","NGS4")
ADJ   <- c("Genialny/Brilliant","Wspanialy/Glorious","Potezny/Powerful","Prestizowy/Prestigious")

# Published per-item descriptives, from the deposit's own Mplus output
# "Codebooks, Data and Scripts/Study 5/Multilevel CFA/CFA DD.out" (osf.io/download/3g28k/),
# SAMPLE STATISTICS section. Keyed to the .sav column codes, not to adjectives.
PUB <- data.frame(item = IT,
                  n    = c(8201, 8196, 8194, 8192),
                  mean = c(32.381, 32.924, 24.477, 23.427),
                  skew = c(0.530, 0.549, 0.993, 1.071),
                  pct0 = c(24.34, 22.96, 36.42, 38.96))

d <- irw::irw_fetch(TABLE)
d <- d[d$item %in% IT, ]

w <- d %>% group_by(id, wave, item) %>% mutate(.rep = row_number()) %>% ungroup() %>%
     select(id, wave, .rep, item, resp) %>%
     pivot_wider(names_from = item, values_from = resp)
m <- as.matrix(w[, IT])
R <- cor(m, use = "pairwise.complete.obs")

cat("=== Check 1: two-block correlation structure ===\n")
cat(sprintf("%-6s %-24s\n", "code", "claimed adjective"))
for (i in seq_along(IT)) cat(sprintf("%-6s %-24s\n", IT[i], ADJ[i]))
cat("\ncorrelation matrix (all", nrow(m), "observations):\n")
print(round(R, 3))

within_pairs <- list(c("NGS1","NGS2"), c("NGS3","NGS4"))
cross_pairs  <- list(c("NGS1","NGS3"), c("NGS1","NGS4"), c("NGS2","NGS3"), c("NGS2","NGS4"))
wv <- sapply(within_pairs, function(p) R[p[1], p[2]])
cv <- sapply(cross_pairs,  function(p) R[p[1], p[2]])
cat(sprintf("\nclaimed within-pair r: NGS1-NGS2 %.3f (Brilliant/Glorious), NGS3-NGS4 %.3f (Powerful/Prestigious)\n", wv[1], wv[2]))
cat(sprintf("cross-pair r: %s\n", paste(sprintf("%s-%s %.3f", sapply(cross_pairs, `[`, 1), sapply(cross_pairs, `[`, 2), cv), collapse = ", ")))
cat(sprintf("min within-pair %.3f  vs  max cross-pair %.3f\n", min(wv), max(cv)))
ok1 <- min(wv) > max(cv)
cat("Check 1:", if (ok1) "PASS" else "FAIL", "\n")

cat("\n=== Check 1b: the rival ordering (Edershile & Wright 2021: Glorious, Prestigious, Brilliant, Powerful) ===\n")
riv_within <- c(R["NGS1","NGS3"], R["NGS2","NGS4"])
riv_cross  <- c(R["NGS1","NGS2"], R["NGS1","NGS4"], R["NGS3","NGS2"], R["NGS3","NGS4"])
cat(sprintf("rival within-pair r: NGS1-NGS3 %.3f, NGS2-NGS4 %.3f ; min %.3f\n", riv_within[1], riv_within[2], min(riv_within)))
cat(sprintf("rival cross-pair max r: %.3f\n", max(riv_cross)))
ok1b <- min(riv_within) < max(riv_cross)
cat("The rival ordering produces NO block structure:", if (ok1b) "confirmed (rival ruled out)" else "NOT confirmed", "\n")

cat("\n=== Check 2: item location separates the two blocks in the predicted direction ===\n")
loc <- d %>% group_by(item) %>%
       summarise(mean = mean(resp, na.rm = TRUE), sd = sd(resp, na.rm = TRUE),
                 pct0 = 100 * mean(resp == 0, na.rm = TRUE), .groups = "drop")
loc <- loc[match(IT, loc$item), ]
for (i in seq_along(IT))
    cat(sprintf("%-6s %-24s mean %6.3f  sd %6.3f  %%at 0 %5.2f\n", IT[i], ADJ[i], loc$mean[i], loc$sd[i], loc$pct0[i]))
ok2 <- min(loc$mean[1:2]) > max(loc$mean[3:4]) && max(loc$pct0[1:2]) < min(loc$pct0[3:4])
cat(sprintf("excellence pair means %.3f/%.3f vs status pair %.3f/%.3f; floor %% %.2f/%.2f vs %.2f/%.2f\n",
            loc$mean[1], loc$mean[2], loc$mean[3], loc$mean[4],
            loc$pct0[1], loc$pct0[2], loc$pct0[3], loc$pct0[4]))
cat("Check 2 (Brilliant/Glorious endorsed higher and floored less than Powerful/Prestigious):",
    if (ok2) "PASS" else "FAIL", "\n")

cat("\n=== Check 3 (CODE-AXIS CORROBORATION ONLY, not adjective evidence) ===\n")
cat("live table vs the deposit's own Mplus SAMPLE STATISTICS, per item:\n")
skewf <- function(x) { x <- x[!is.na(x)]; mean((x - mean(x))^3) / sd(x)^3 }
obs <- d %>% group_by(item) %>%
       summarise(n = sum(!is.na(resp)), mean = mean(resp, na.rm = TRUE),
                 skew = skewf(resp), pct0 = 100 * mean(resp == 0, na.rm = TRUE), .groups = "drop")
obs <- obs[match(IT, obs$item), ]
cat(sprintf("%-6s %8s %8s | %9s %9s | %7s %7s | %7s %7s\n",
            "item", "n(pub)", "n(obs)", "mean(pub)", "mean(obs)", "sk(pub)", "sk(obs)", "%0(pub)", "%0(obs)"))
for (i in seq_along(IT))
    cat(sprintf("%-6s %8d %8d | %9.3f %9.3f | %7.3f %7.3f | %7.2f %7.2f\n",
                IT[i], PUB$n[i], obs$n[i], PUB$mean[i], obs$mean[i], PUB$skew[i], obs$skew[i], PUB$pct0[i], obs$pct0[i]))
ok3 <- all(obs$n == PUB$n) && max(abs(obs$mean - PUB$mean)) < 0.01 && max(abs(obs$pct0 - PUB$pct0)) < 0.01
cat("Check 3:", if (ok3) "PASS" else "FAIL",
    sprintf("(largest mean deviation %.4f)\n", max(abs(obs$mean - PUB$mean))))
cat("Check 3 establishes that live item NGSk is .sav column NGSk. It says nothing\n",
    "about which adjective NGSk holds -- checks 1 and 2 are what address that.\n", sep = "")

cat("\nNOT ESTABLISHED by any check above: Brilliant vs Glorious, and Powerful vs\n",
    "Prestigious. All checks are symmetric within each pair, so 8 of the 24 possible\n",
    "orderings survive. Status recorded as PARTIAL.\n", sep = "")

cat(if (ok1 && ok1b && ok2 && ok3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
