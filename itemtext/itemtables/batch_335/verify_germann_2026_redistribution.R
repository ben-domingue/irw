# verify_germann_2026_redistribution.R -- Step 5b mapping check (copied from
# references/verify_template.R).
#
# Claim: redistr1..redistr4 are items 1..4 of SI Table S2.18 ("Economic
# redistribution scale [2017]") of Germann, Godefroidt & Mendez (2026, EJPR,
# doi:10.1017/S1475676526101017, supplementary sup001.pdf), with items 2 and 3
# stored reverse-coded (value label policyitems_rev: 1 = Completely agree).
#
# Route 1 (per-item statistics): Table S2.18 publishes a Mokken item
# scalability coefficient Hi for each item, computed on the 2017 complete
# cases (N = 73186, H = 0.42). Hi = .48/.34/.41/.44 are pairwise distinct at
# two decimals, so recomputing Hi on the live table pins every item. Because Hi
# of an item scored in the wrong direction goes negative, it also pins the
# stored direction of redistr2/redistr3.
# Direction cross-check: every item, as labelled, is scored so that high =
# pro-redistribution, so each must correlate negatively with cov_lr
# (0 = Left .. 10 = Right).

suppressMessages({library(irw); library(mokken)})

TABLE <- "germann_2026_redistribution"
ITEMS <- paste0("redistr", 1:4)
PUB_HI <- c(redistr1 = 0.48, redistr2 = 0.34, redistr3 = 0.41, redistr4 = 0.44)
PUB_H <- 0.42
PUB_N <- 73186
TOL <- 0.005

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
cc <- na.omit(w[, ITEMS])
h <- coefH(as.matrix(cc), se = FALSE, results = FALSE)
hi <- round(h$Hi[ITEMS], 2)

cat(sprintf("complete cases: live %d vs published %d\n", nrow(cc), PUB_N))
cat(sprintf("scale H: live %.2f vs published %.2f\n\n", h$H, PUB_H))
cat(sprintf("%-9s %10s %10s %8s\n", "item", "published", "live Hi", "diff"))
for (i in ITEMS)
  cat(sprintf("%-9s %10.2f %10.2f %8.3f\n", i, PUB_HI[i], hi[i], hi[i] - PUB_HI[i]))

lr <- unique(d[, c("id", "cov_lr")])
m <- merge(w, lr, by = "id")
r_lr <- sapply(ITEMS, function(i) cor(m[[i]], m$cov_lr, use = "pairwise.complete.obs"))
cat("\ncorrelation with cov_lr (0=Left..10=Right), expected all negative:\n")
print(round(r_lr, 3))

# Does the route distinguish every item? Published Hi must be pairwise distinct.
gaps <- min(diff(sort(PUB_HI)))
cat(sprintf("\nsmallest gap between published Hi values: %.2f\n", gaps))

ok <- nrow(cc) == PUB_N &&
      abs(round(h$H, 2) - PUB_H) <= TOL &&
      all(abs(hi - PUB_HI) <= TOL) &&
      all(r_lr < 0) &&
      gaps > 0
cat("Note: this verifies code<->text via Table S2.18's per-item Hi; it does not\n",
    "check the wording against the live VAA screens, which are not archived.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
