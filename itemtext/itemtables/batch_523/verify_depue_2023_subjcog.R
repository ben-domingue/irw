# verify_depue_2023_subjcog.R -- Step 5b mapping check for depue_2023_subjcog (batch_523).
#
# Claim: the self-describing IRW codes (deposit column names, kept as-is by
# data/depue_2023_covid_older_adults.py; the M2_/M3_ prefixes stripped and
# M2_/M3_CognFunct_post renamed CognFunct_now) carry the question text that the
# deposits' ReadThisFirst.txt gives for those columns, and resp keeps the
# deposit's coding (1 = "a lot more than before" / "Yes, it has decreased";
# 0-10 rating with 10 = "very good"). Checked against the per-item statistics
# the two papers publish:
#   (A) De Pue et al. 2021 Sci Rep 11:4636 Table 2 (T1, N = 640): M (SD) and
#       N decrease / no change / increase for the six change questions
#       (for the five subdomains 1-2 = more problems = "decrease", 4-5 = increase);
#   (B) De Pue et al. 2023 Sci Rep 13:9708 Table 3 (n = 371 completers): % reporting
#       more problems (resp 1-2) per subdomain at T1, T2, T3, and the general
#       0-10 cognitive functioning rating M (SD) at Pre, T2, T3.
# The per-subdomain % vector over three waves is what separates the five
# near-tied 1-5 items (Recalling and Forgetfulness are identical in (A)).

suppressMessages(library(irw))
TABLE <- "depue_2023_subjcog"
SUB <- c("Remembering", "Concentration", "Doing_two_things", "Recalling", "Forgetfulness")
A <- rbind(Cognitive_functioning = c(1.94, 0.31, 50, 576, 14),
           Remembering      = c(2.93, 0.40, 53, 575, 12),
           Concentration    = c(2.91, 0.44, 78, 539, 23),
           Doing_two_things = c(2.97, 0.35, 37, 584, 19),
           Recalling        = c(2.92, 0.41, 63, 560, 17),
           Forgetfulness    = c(2.92, 0.40, 63, 560, 17))
P <- rbind(Remembering = c(7, 7, 16), Concentration = c(12, 13, 17),
           Doing_two_things = c(5, 9, 15), Recalling = c(9, 11, 26), Forgetfulness = c(8, 10, 21))
G <- c(Pre = 7.75, T2 = 7.49, T3 = 7.68); GS <- c(0.99, 1.20, 1.24)

d <- as.data.frame(irw::irw_fetch(TABLE))
ok <- TRUE
cat("(A) 2021 Table 2, T1 N=640: published M (SD) dec/same/inc | live\n")
for (it in rownames(A)) {
  v <- d$resp[d$item == it & d$wave == 1]
  L <- if (it == "Cognitive_functioning") c(mean(v), sd(v), sum(v == 1), sum(v == 2), sum(v == 3))
       else c(mean(v), sd(v), sum(v <= 2), sum(v == 3), sum(v >= 4))
  cat(sprintf("%-22s %.2f (%.2f) %3d/%3d/%2d | %.2f (%.2f) %3d/%3d/%2d\n", it,
              A[it,1], A[it,2], A[it,3], A[it,4], A[it,5], L[1], L[2], L[3], L[4], L[5]))
  if (abs(L[1] - A[it,1]) > 0.006 || abs(L[2] - A[it,2]) > 0.006 || any(L[3:5] != A[it,3:5])) ok <- FALSE
}
ids3 <- unique(d$id[d$wave == 3])
cat(sprintf("\n(B) 2023 Table 3, n=%d completers: %% more problems (resp 1-2) T1/T2/T3, published | live\n", length(ids3)))
LP <- t(sapply(SUB, function(it) sapply(1:3, function(w)
  100 * mean(d$resp[d$item == it & d$wave == w & d$id %in% ids3] <= 2))))
for (it in SUB) cat(sprintf("%-18s %s | %s\n", it, paste(sprintf("%2d%%", P[it, ]), collapse = " "),
                            paste(sprintf("%4.1f%%", LP[it, ]), collapse = " ")))
if (max(abs(LP - P)) > 0.5) ok <- FALSE
cat(sprintf("largest |deviation| over 15 percentages: %.2f points\n", max(abs(LP - P))))
D <- sapply(SUB, function(j) rowSums(abs(LP - matrix(P[j, ], 5, 3, byrow = TRUE))))  # D[live i, published j]
best <- rownames(D)[apply(D, 2, which.min)]
runner <- apply(D, 2, function(v) sort(v)[2])
cat("best-matching live item per published subdomain:", best, "\n")
cat("runner-up summed |diff| (points):", sprintf("%.1f", runner), "\n")
if (!all(best == SUB)) ok <- FALSE
# the direction: a flipped 1-5 coding would put the "more problems" share at resp 4-5
flip <- sapply(SUB, function(it) 100 * mean(d$resp[d$item == it & d$wave == 3 & d$id %in% ids3] >= 4))
cat("T3 share at resp 4-5 (what a flipped coding would report):", sprintf("%.1f%%", flip), "\n")

g <- rbind(Pre = { v <- d$resp[d$item == "CognFunct_pre"]; c(mean(v), sd(v)) },
           T2  = { v <- d$resp[d$item == "CognFunct_now" & d$wave == 2]; c(mean(v), sd(v)) },
           T3  = { v <- d$resp[d$item == "CognFunct_now" & d$wave == 3]; c(mean(v), sd(v)) })
cat("\n0-10 general cognitive functioning rating, published | live\n")
for (k in 1:3) cat(sprintf("%-3s %.2f (%.2f) | %.2f (%.2f)\n", names(G)[k], G[k], GS[k], g[k, 1], g[k, 2]))
if (max(abs(g[, 1] - G)) > 0.006 || max(abs(g[, 2] - GS)) > 0.011) ok <- FALSE
cat("(CognFunct_pre asked at T2 only, retrospectively; CognFunct_now at T2 and T3.)\n")
cat("\nEvery item is pinned: Cognitive_functioning by its 1-3 range and (A); the five subdomains by\n",
    "their T1/T2/T3 % vectors (B); CognFunct_pre vs _now by the Pre vs T2 means (7.75 vs 7.49).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
