# verify_komura_2026_mdmt_reliable.R
#
# Claim under test: the four columns mdmt_reliable_1..4 carry the four adjectives
# listed under "Reliable:" in the study's S2 File
# (10.1371/journal.pone.0340449.s002, "User Instructions for Frontend Interface
# (translated in English)", section 7 "Questionnaire Screens" -> "Trust
# Evaluation (MDMT)"), in the order that file numbers them:
#   1. Reliable
#   2. Predictable
#   3. Dependable
#   4. Consistent
# scored 0 = "not at all" .. 7 = "very much so", stored raw.
#
# Two falsifiable predictions computed from the LIVE IRW table:
#
# A. SUBSCALE IDENTITY AND DIRECTION (route 3). The paper's Table 2 prints the
#    MDMT "Reliability" mean (SD) per AI-strategy condition, alongside three
#    sibling dimensions with DIFFERENT published values. If these four items
#    are the Reliability block, are keyed with the positive pole at resp = 7,
#    and are stored raw, the per-condition mean of the four must reproduce the
#    Reliability row and must NOT match Capability/Ethicality/Sincerity.
#    (Published Random n = 46 -- paper Table 1 -- so the six rows whose
#    cov_aitype is "unknown" belong to the Random condition; 40 + 6 = 46.)
#
# B. SEMANTIC PAIRING (route 8, corroborative only). Of the four adjectives,
#    "Reliable" and "Dependable" are near-synonyms while "Predictable" and
#    "Consistent" are not synonyms of them. If items 1 and 3 are the ones
#    carrying that near-synonymous pair, r(1,3) must be the single largest
#    off-diagonal correlation in the 4x4 matrix.
#
# What this does NOT establish, stated up front: nothing here separates item 1
# from item 3, or item 2 from item 4. The paper publishes no per-item
# statistics, all four items share the same 0-7 response scale, none is
# reverse-keyed, and the source ties text to code only by the S2 File's own
# 1..4 numbering matching the trailing digit of the workbook headers. So the
# ORDER WITHIN the subscale is not verified against the data -- hence PARTIAL.

suppressMessages(library(irw))

TABLE <- "komura_2026_mdmt_reliable"

# Paper Table 2, "MDMT trust scale results by AI strategy condition".
PUB <- data.frame(
  dim  = c("Reliability", "Capability", "Ethicality", "Sincerity"),
  vertical_m = c(4.76, 4.81, 4.71, 4.92), vertical_sd = c(1.13, 1.26, 1.22, 1.08),
  horizontal_m = c(4.08, 4.00, 4.21, 4.32), horizontal_sd = c(1.37, 1.52, 1.35, 1.27),
  random_m = c(4.09, 4.22, 4.11, 4.31), random_sd = c(1.30, 1.31, 1.30, 1.05),
  stringsAsFactors = FALSE)
PUB_N <- c(vertical = 52, horizontal = 50, random = 46)   # paper Table 1
TOL_MEAN <- 0.02
TOL_SD   <- 0.02

d <- as.data.frame(irw::irw_fetch(TABLE))
d$cond <- ifelse(d$cov_aitype == "unknown", "random", d$cov_aitype)

items <- paste0("mdmt_reliable_", 1:4)
ids <- sort(unique(d$id))
M <- sapply(items, function(i) {
  s <- d[d$item == i, ]
  s$resp[match(ids, s$id)]
})
rownames(M) <- ids
cond <- d$cond[match(ids, d$id)]

cat("=== A. Subscale mean (SD) by condition vs paper Table 2 ===\n")
sc <- rowMeans(M)
obs <- t(sapply(c("vertical", "horizontal", "random"), function(k)
  c(n = sum(cond == k), m = mean(sc[cond == k]), sd = sd(sc[cond == k]))))
print(round(obs, 3))

rel <- PUB[PUB$dim == "Reliability", ]
pub_m  <- c(vertical = rel$vertical_m,  horizontal = rel$horizontal_m,  random = rel$random_m)
pub_sd <- c(vertical = rel$vertical_sd, horizontal = rel$horizontal_sd, random = rel$random_sd)
for (k in names(pub_m))
  cat(sprintf("  %-11s observed %.3f (%.3f) n=%d | published Reliability %.2f (%.2f) n=%d | dM=%.4f dSD=%.4f\n",
              k, obs[k, "m"], obs[k, "sd"], obs[k, "n"],
              pub_m[[k]], pub_sd[[k]], PUB_N[[k]],
              abs(obs[k, "m"] - pub_m[[k]]), abs(obs[k, "sd"] - pub_sd[[k]])))
okA <- all(abs(obs[names(pub_m), "m"] - pub_m) <= TOL_MEAN) &&
       all(abs(obs[names(pub_sd), "sd"] - pub_sd) <= TOL_SD) &&
       all(obs[names(PUB_N), "n"] == PUB_N)

cat("\n  Distance to each published MDMT dimension (sum |dM| over 3 conditions):\n")
dists <- sapply(seq_len(nrow(PUB)), function(j) {
  pm <- c(vertical = PUB$vertical_m[j], horizontal = PUB$horizontal_m[j], random = PUB$random_m[j])
  sum(abs(obs[names(pm), "m"] - pm))
})
names(dists) <- PUB$dim
print(round(dists, 3))
okA2 <- names(which.min(dists)) == "Reliability" &&
        min(dists[names(dists) != "Reliability"]) > 10 * max(dists["Reliability"], 1e-6)

cat("\n  Reversed reading (7 - resp), same comparison:\n")
scr <- rowMeans(7 - M)
obsr <- sapply(c("vertical", "horizontal", "random"), function(k) mean(scr[cond == k]))
cat(sprintf("    %.3f / %.3f / %.3f vs published %.2f / %.2f / %.2f -> sum|dM| = %.3f\n",
            obsr[1], obsr[2], obsr[3], pub_m[[1]], pub_m[[2]], pub_m[[3]],
            sum(abs(obsr - pub_m))))
okA3 <- sum(abs(obsr - pub_m)) > sum(abs(obs[names(pub_m), "m"] - pub_m))

cat("\n=== B. Correlation matrix (semantic pairing, corroborative) ===\n")
C <- cor(M, use = "pairwise.complete.obs")
print(round(C, 3))
off <- C; diag(off) <- NA
mx <- which(off == max(off, na.rm = TRUE), arr.ind = TRUE)[1, ]
cat(sprintf("  largest off-diagonal r = %.3f between %s and %s\n",
            max(off, na.rm = TRUE), items[mx[["row"]]], items[mx[["col"]]]))
cat(sprintf("  r(1,3) = %.3f ; next largest = %.3f\n",
            C[1, 3], max(off[!(row(off) == 1 & col(off) == 3) & !(row(off) == 3 & col(off) == 1)], na.rm = TRUE)))
okB <- setequal(c(items[mx[["row"]]], items[mx[["col"]]]),
                c("mdmt_reliable_1", "mdmt_reliable_3"))

cat("\n=== NOT ESTABLISHED ===\n")
cat("  Item 1 vs item 3, and item 2 vs item 4, are not separated by any route here.\n")
cat("  Prediction B pins {1,3} as the near-synonym pair but not which is which.\n")
cat("  Verification status is therefore PARTIAL, not VERIFIED.\n\n")

cat("A (Reliability row reproduced): ", okA, "\n")
cat("A2 (nearest published dimension is Reliability, by >10x): ", okA2, "\n")
cat("A3 (raw beats reversed): ", okA3, "\n")
cat("B (r(1,3) is the largest off-diagonal): ", okB, "\n\n")

if (okA && okA2 && okA3 && okB) cat("VERDICT: PASS\n") else cat("VERDICT: FAIL\n")
