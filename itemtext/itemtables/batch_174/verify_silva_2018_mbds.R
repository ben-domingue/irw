# verify_silva_2018_mbds.R -- Step 5b mapping check for silva_2018_mbds.
#
# Claim: live item MBDS<n> is item <n> of the 25-item Male Body Dissatisfaction
# Scale, whose wording (reduced 12-item form, English + Portuguese) is printed
# against those item numbers in Da Silva, Maroco, Ochner & Campos (2017), Eat
# Weight Disord 22:515-525, Table 5.
#
# Route 1 (per-item descriptives). The same paper's Table 2 publishes per-item
# mean and SD of the weighted item score (importance/10 x Likert, 0.1-5.0)
# separately for Brazil and Portugal, on 932 men from the same Brazil/Portugal
# data collection. The live table holds the 802 of them with complete MBDS
# responses (429 BR, 373 PT), so small residuals are expected.
#
# Test: (a) every item's published BR mean, PT mean, BR SD and PT SD sit within
# tolerance of its own live value; (b) under a 4-D profile distance, each live
# item's nearest published profile among the 12 reduced-form items is its own
# number, i.e. the mapping is distinguished item by item, not just on average.
# Also printed for information: nearest among all 25 published items.

suppressMessages(library(irw))

TABLE <- "silva_2018_mbds"

# Da Silva et al. 2017, Table 2: item, BR mean, BR SD, PT mean, PT SD
pub25 <- read.table(header = TRUE, text = "
item brM brSD ptM ptSD
1  1.92 1.10 1.74 0.96
2  1.61 0.92 1.41 0.87
3  1.93 1.15 1.79 1.02
4  2.41 1.45 2.10 1.27
5  1.23 0.85 1.28 0.91
6  1.35 1.27 1.21 1.14
7  1.63 1.34 1.14 1.04
8  1.72 0.98 1.65 0.88
9  1.36 1.24 1.74 1.22
10 1.23 0.59 1.27 0.67
11 1.40 0.93 1.41 0.88
12 1.54 1.32 1.43 1.15
13 2.01 1.39 1.81 1.22
14 1.66 1.04 1.54 0.98
15 1.84 1.19 1.74 1.08
16 2.00 1.42 1.70 1.18
17 1.21 0.76 1.33 0.87
18 1.75 0.91 1.54 0.77
19 1.35 1.01 1.42 0.92
20 1.63 0.97 1.54 0.85
21 1.37 0.85 1.33 0.82
22 1.19 0.56 1.21 0.68
23 1.66 0.97 1.54 0.86
24 1.84 1.39 1.50 1.14
25 1.38 0.69 1.38 0.67
")
REDUCED <- c(1, 2, 4, 6, 8, 9, 12, 15, 16, 19, 21, 23)
TOL <- 0.08

d <- irw::irw_fetch(TABLE)
stopifnot("cov_country" %in% names(d))
d$num <- as.integer(sub("^MBDS", "", d$item))

obs <- do.call(rbind, lapply(REDUCED, function(n) {
  s <- d[d$num == n, ]
  br <- s$resp[s$cov_country == 1]; pt <- s$resp[s$cov_country == 2]
  data.frame(item = n, brM = mean(br), brSD = sd(br), ptM = mean(pt), ptSD = sd(pt),
             nBR = length(br), nPT = length(pt))
}))

vars <- c("brM", "brSD", "ptM", "ptSD")
P12 <- as.matrix(pub25[pub25$item %in% REDUCED, vars]); rownames(P12) <- REDUCED
P25 <- as.matrix(pub25[, vars]); rownames(P25) <- pub25$item
O <- as.matrix(obs[, vars]); rownames(O) <- obs$item

cat(sprintf("%-7s %5s %5s | %-17s | %-17s | %-17s | %-17s | %6s %9s %9s\n",
            "item", "nBR", "nPT", "BR mean pub/obs", "BR SD pub/obs", "PT mean pub/obs",
            "PT SD pub/obs", "maxdev", "nn(12)", "nn(25)"))
ok_tol <- TRUE; ok_nn <- TRUE
for (i in seq_len(nrow(O))) {
  n <- REDUCED[i]
  dev <- abs(O[i, ] - P12[as.character(n), ])
  d12 <- sqrt(colSums((t(P12) - O[i, ])^2)); o12 <- order(d12)
  d25 <- sqrt(colSums((t(P25) - O[i, ])^2)); o25 <- order(d25)
  nn12 <- as.integer(names(d12)[o12[1]]); nn25 <- as.integer(names(d25)[o25[1]])
  cat(sprintf("MBDS%-3d %5d %5d | %.2f / %.3f     | %.2f / %.3f     | %.2f / %.3f     | %.2f / %.3f     | %6.3f %4d(%.3f<%.3f) %4d\n",
              n, obs$nBR[i], obs$nPT[i],
              P12[as.character(n), "brM"], O[i, "brM"], P12[as.character(n), "brSD"], O[i, "brSD"],
              P12[as.character(n), "ptM"], O[i, "ptM"], P12[as.character(n), "ptSD"], O[i, "ptSD"],
              max(dev), nn12, d12[o12[1]], d12[o12[2]], nn25))
  if (max(dev) > TOL) ok_tol <- FALSE
  if (nn12 != n) ok_nn <- FALSE
}

cat(sprintf("\nall 48 cells within %.2f of Table 2: %s\n", TOL, ok_tol))
cat(sprintf("every live item's nearest published profile (of the 12) is its own number: %s\n", ok_nn))
cat("Printed nn(12) as nearest(own distance < runner-up distance).\n")
cat("Not established: the Portuguese wording respondents actually read beyond what\n",
    "Table 5 reprints (the Carvalho et al. 2013 form itself was not retrievable), and\n",
    "nn(25) is informational only -- items outside the reduced form are not in the table.\n", sep = "")

cat(if (ok_tol && ok_nn) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
