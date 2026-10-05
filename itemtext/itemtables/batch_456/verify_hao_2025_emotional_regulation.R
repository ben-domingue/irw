# verify_hao_2025_emotional_regulation.R -- Step 5b check for batch_456.
#
# Claim: ER1..ER4 are FLLRS (Guo & Li 2022, Front Psychol 13:1046340) ego-resilience
# items 1, 2, 3, 6 -- the four ER items retained after EFA, taken in Appendix 1 order.
# Hao et al. never tie ER1..ER4 to wording, so the order is inferred (paper_order).
#
# Route: cross-sample per-item statistics. Guo & Li Table 1 publishes per-item M (SD)
# and EFA loadings on a 7-point scale in a different sample (N=313 Chinese university
# EFL learners). Hao's sample is 650 junior-high students with data on a 1-5 scale, so
# levels cannot match; the prediction is that the RANK ORDER carries over.
#   Guo means: item1 4.86, item2 4.57, item3 5.60, item6 6.29  -> rank 6 > 3 > 1 > 2
#   Guo SDs:   1.499, 1.479, 1.386, 1.030                       -> item6 smallest
#   Guo loadings: .804, .756, .734, .544                        -> item6 weakest
# All four Guo means are distinct, so a full rank match is a 1-in-24 event under a
# random permutation of the four texts.
#
# Does NOT establish: this is a different population and a different response scale,
# so it is corroboration rather than a same-sample identity. The ER1-vs-ER2 and
# ER3-vs-ER4 live gaps are 0.33 and 0.08; the latter is small.

suppressMessages(library(irw))
TABLE <- "hao_2025_emotional_regulation"
ITEMS <- c("ER1", "ER2", "ER3", "ER4")
GUO_NO <- c(1, 2, 3, 6)
GUO_M  <- c(4.86, 4.57, 5.60, 6.29)
GUO_SD <- c(1.499, 1.479, 1.386, 1.030)
GUO_L  <- c(0.804, 0.756, 0.734, 0.544)

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, ITEMS]
m  <- colMeans(w, na.rm = TRUE)
s  <- sapply(w, sd, na.rm = TRUE)
it <- sapply(ITEMS, function(i) cor(w[[i]], rowSums(w[, setdiff(ITEMS, i)]), use = "complete.obs"))
guo_m_5pt <- (GUO_M - 1) * 4 / 6 + 1

cat(sprintf("%-4s %-6s %8s %9s %8s | %7s %7s | %7s %8s\n", "item", "FLLRS#",
            "guo_M", "guo_M@5pt", "live_M", "guo_SD", "live_SD", "guo_L", "live_itc"))
for (k in 1:4)
  cat(sprintf("%-4s %-6d %8.2f %9.2f %8.3f | %7.3f %7.3f | %7.3f %8.3f\n", ITEMS[k], GUO_NO[k],
              GUO_M[k], guo_m_5pt[k], m[k], GUO_SD[k], s[k], GUO_L[k], it[k]))

rank_match <- all(unname(rank(-m)) == rank(-GUO_M))
rho <- cor(m, GUO_M, method = "spearman")
er4_top_mean <- which.max(m) == 4
er4_low_sd   <- which.min(s) == 4
er4_low_itc  <- which.min(it) == 4
cat(sprintf("\nmean rank live: %s ; Guo: %s ; Spearman rho = %.2f ; full rank match: %s (1/24 by chance)\n",
            paste(ITEMS[order(-m)], collapse = " > "),
            paste(ITEMS[order(-GUO_M)], collapse = " > "), rho, rank_match))
cat(sprintf("ER4 (FLLRS item 6) highest mean: %s ; smallest SD: %s ; weakest corrected item-total: %s\n",
            er4_top_mean, er4_low_sd, er4_low_itc))
cat("Note: cross-sample corroboration (university N=313 7-pt vs junior-high N=650 1-5);\n",
    "orders all four items but is not a same-sample identity -- recorded as PARTIAL.\n", sep = "")
cat(if (rank_match && er4_low_sd && er4_low_itc) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
