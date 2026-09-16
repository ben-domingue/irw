# verify_wolters2026_wi.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: the live item codes wi_1..wi_14 carry the CANONICAL Whiteley
# Index (WI-14) item numbering, i.e. wi_n is the instrument's item n. The figshare
# deposit's headers are the bare codes WI_1..WI_14 with no variable labels, so
# nothing at the source ties a code to a sentence; the tie rests on the assumption
# that the study numbered the scale in its published order. That assumption is what
# this script tests -- not the item/resp sets, which validate_items.R already checked.
#
# ROUTE 1 (per-item published statistic, profile form). Axelsson, Osterman &
# Hedman-Lagerlof (2023), BMC Psychiatry, doi:10.1186/s12888-023-05151-7 (CC BY),
# Table S5 of Supplement 1 (PMC10483785)
# sha256 ae7fbc4c2cc18434a1070b3b0e72cd5a74bb7c92825aa5b95169c6040ff74c40, prints
# one-factor loadings for all 14 WI-14 items under the same numbering, in an
# independent (Swedish) yes/no administration. Item-rest correlations computed from the live
# table should track that profile if -- and only if -- the numbering agrees.
#
# ROUTE 6 (keying polarity). WI-14 item 9 ("Is it easy for you to forget about
# yourself...") is the scale's single reverse-keyed item. Its sign in the live data
# tells us whether the stored values are raw answers or Whiteley SCORES.

suppressMessages(library(irw))
TABLE <- "wolters2026_wi"

# Axelsson et al. (2023) Table S5, one-factor loadings, WI-14 #1..#14.
PUBLISHED <- c(0.89, 0.38, 0.53, 0.90, 0.63, 0.73, 0.23,
               0.68, 0.62, 0.58, 0.60, 0.88, 0.68, 0.83)

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
colnames(w) <- sub("resp.", "", colnames(w), fixed = TRUE)
its <- paste0("wi_", 1:14)
m <- as.matrix(w[, its])
tot <- rowSums(m)
irest <- sapply(1:14, function(i) cor(m[, i], tot - m[, i]))
p <- colMeans(m)

cat(sprintf("%-6s %8s %12s %12s\n", "item", "p(=1)", "item-rest r", "published FL"))
for (i in 1:14)
    cat(sprintf("%-6s %8.2f %12.2f %12.2f\n", its[i], p[i], irest[i], PUBLISHED[i]))

rho <- cor(irest, PUBLISHED, method = "spearman")
set.seed(1)
null <- replicate(20000, cor(irest, sample(PUBLISHED), method = "spearman"))
pval <- mean(null >= rho)
cat(sprintf("\nROUTE 1: Spearman(item-rest, published loadings) = %.2f; permutation p = %.3f\n",
            rho, pval))

cat(sprintf("ROUTE 6: wi_9 item-rest r = %+.2f (p endorsed = %.2f, n = %d).\n",
            irest[9], p[9], nrow(m)))
cat("  Raw yes/no coding would make the scale's one reverse-keyed item NEGATIVE here;\n")
cat("  it is positive, so the deposit stores Whiteley SCORES (1 = the health-anxiety\n")
cat("  answer), and wi_9's shipped option_text is flipped to Yes=0 / No=1 accordingly.\n")

cat("\nWhat this does NOT establish: the loading profile is a rank agreement across 14\n")
cat("items, not a per-item identification. It rules out a random permutation of the\n")
cat("item text, but a swap between two items of similar loading (e.g. wi_8 0.68 and\n")
cat("wi_13 0.68, or wi_10 0.58 and wi_11 0.60) would not be detected. Status PARTIAL.\n\n")

ok <- rho >= 0.35 && pval <= 0.05 && irest[9] > 0
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
