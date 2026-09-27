# verify_depue_2023_pwi.R -- Step 5b mapping check for depue_2023_pwi (batch_522).
#
# Claim: IRW codes PWI1..PWI8 (deposit columns PWIk_covid / M2_PWIk_post /
# M3_PWIk_post, renamed number-preservingly by data/depue_2023_covid_older_adults.py)
# are, in order, general life satisfaction ("life as a whole"), then the seven
# PWI-A domains standard of living, health, achieving in life, personal
# relationships, safety, community connectedness, future security; PWIk_pre is
# the same domain rated retrospectively for before COVID-19 (asked at T1).
# The deposit has no labels, so the order is taken from ReadThisFirst.txt
# ("PWI_1, a general life satisfaction item") and the papers' domain listing,
# and checked here against the per-domain statistics the papers publish:
#   (A) De Pue et al. 2023 Sci Rep 13:9708 Table 3: M (SD) on the 0-100 scale for
#       each named domain at Pre, T1, T2, T3 (n = 371 completers) -- 32 cells;
#   (B) De Pue et al. 2021 Sci Rep 11:4636 Table 2: per-domain change
#       (current - pre) M (SD) and N decrease / no change / increase (N = 640).
# The live table stores resp on 0-10 (the deposit's x10 undone), so x10 here.

suppressMessages(library(irw))
TABLE <- "depue_2023_pwi"
DOM <- c("General life satisfaction", "Standard of living", "Health", "Achieving in life",
         "Relationships", "Safety", "Community connectedness", "Future security")
# Table 3 (2023): rows = domains in DOM order; cols Pre, T1, T2, T3
PM <- matrix(c(79.84,71.02,74.47,73.29, 81.37,78.89,80.46,80.81, 77.79,75.15,76.71,74.72,
               79.92,76.42,78.30,77.20, 79.76,72.94,75.50,74.88, 81.78,71.94,74.37,74.39,
               78.01,68.01,69.60,67.76, 77.87,67.39,70.81,69.19), 8, byrow = TRUE)
PS <- matrix(c(11.27,17.07,13.73,14.87, 11.22,13.46,11.56,12.14, 12.28,14.75,14.39,15.99,
               12.25,15.19,12.08,14.28, 14.03,19.19,15.73,18.13, 10.00,16.34,15.13,15.97,
               13.19,18.00,17.71,18.32, 11.67,16.73,15.51,16.79), 8, byrow = TRUE)
# Table 2 (2021): change M, SD, N dec, N same, N inc
CH <- matrix(c(-9.63,15.34,317,299,24, -3.98,11.41,140,479,21, -2.88,9.39,130,484,26,
               -3.88,11.09,131,491,18, -7.09,15.09,213,398,29, -10.39,16.10,291,340,9,
               -10.89,17.70,290,323,27, -10.39,14.69,306,328,6), 8, byrow = TRUE)

d <- as.data.frame(irw::irw_fetch(TABLE))
ok <- TRUE
ids3 <- unique(d$id[d$wave == 3])
st <- function(x, it) { v <- 10 * x$resp[x$item == it]; c(mean(v), sd(v)) }
LM <- LS <- matrix(NA, 8, 4)
for (k in 1:8) {
  r <- rbind(st(d[d$id %in% ids3, ], paste0("PWI", k, "_pre")),
             st(d[d$wave == 1 & d$id %in% ids3, ], paste0("PWI", k)),
             st(d[d$wave == 2, ], paste0("PWI", k)), st(d[d$wave == 3, ], paste0("PWI", k)))
  LM[k, ] <- r[, 1]; LS[k, ] <- r[, 2]
}
cat(sprintf("(A) 2023 Table 3, n=%d completers: published M (SD) vs live, Pre/T1/T2/T3\n", length(ids3)))
for (k in 1:8) cat(sprintf("PWI%d%-4s %-24s %s\n", k, "", DOM[k], paste(sprintf("%.2f(%.2f)|%.2f(%.2f)",
    PM[k, ], PS[k, ], LM[k, ], LS[k, ]), collapse = "  ")))
dev <- max(abs(LM - PM), abs(LS - PS)); cat(sprintf("largest |deviation| over 64 numbers: %.3f\n", dev))
if (dev > 0.006) ok <- FALSE
# discrimination: for each published domain, total |mean diff| over 4 moments against every live item
D <- sapply(1:8, function(j) colSums(abs(t(LM) - PM[j, ])))  # D[i,j]: live item i vs published domain j
best <- apply(D, 2, which.min)
runner <- apply(D, 2, function(v) sort(v)[2])
cat("best-matching live item per published domain:", paste0("PWI", best), "\n")
cat("runner-up total |diff| (points, 4 moments):", paste(sprintf("%.2f", runner), collapse = " "), "\n")
if (!all(best == 1:8)) ok <- FALSE

# (B) 2021 Table 2, N=640 at T1: change = current - pre, x10
w1 <- d[d$wave == 1, ]
W <- reshape(w1[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
cat("\n(B) 2021 Table 2 change scores (current - pre), published | live\n")
for (k in 1:8) {
  df <- 10 * (W[[paste0("resp.PWI", k)]] - W[[paste0("resp.PWI", k, "_pre")]]); df <- df[!is.na(df)]
  L <- c(mean(df), sd(df), sum(df < 0), sum(df == 0), sum(df > 0))
  cat(sprintf("PWI%d %-24s %6.2f (%5.2f) %3d/%3d/%2d | %6.2f (%5.2f) %3d/%3d/%2d\n", k, DOM[k],
              CH[k,1], CH[k,2], CH[k,3], CH[k,4], CH[k,5], L[1], L[2], L[3], L[4], L[5]))
  if (abs(L[1] - CH[k,1]) > 0.02 || abs(L[2] - CH[k,2]) > 0.02 || any(abs(L[3:5] - CH[k,3:5]) > 1)) ok <- FALSE
}
cat("(residuals: PWI1 mean -9.62 vs -9.63 (rounding); PWI5 has 639 non-missing pairs, 212 vs 213 decreases)\n")
cat("\nEach of the 8 domains is pinned at 4 moments + change score; pre vs current pinned by the Pre column.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
