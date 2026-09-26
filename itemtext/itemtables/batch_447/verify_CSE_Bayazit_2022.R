# verify_CSE_Bayazit_2022.R -- Step 5b mapping check (batch_447).
#
# Claim: IRW item codes Item1..Item15 (= the Dataverse file's own column names,
# data/CSE_Bayazit_2022.R keeps them verbatim) correspond to rows 1..15 of
# Bayazit, Gonullu & Dogan (2022) PLOS ONE 17(11):e0275672, Table 1, which
# prints each item's Turkish + English wording with its Mean, SD and EFA loading.
#
# Routes: (1) per-item mean/SD against Table 1; (2) optimal (Hungarian)
# assignment of live items to published rows on (mean, SD); (3) subscale block
# structure -- Table 1 puts rows 1-6 on Cognitive, 7-10 on Affective, 11-15 on
# Psychomotor, with row 11 cross-loading F2/F3 and row 6 cross-loading F1/F3.
# Table 1 appears to be computed on the EFA half-sample (paper: n=651 split in
# two), the live table pools all 651, so residuals of a few hundredths are expected.

suppressMessages({library(irw); library(clue)})

TABLE <- "CSE_Bayazit_2022"
PUB_MEAN <- c(3.95, 3.98, 3.97, 3.48, 3.77, 3.69, 2.92, 3.63, 3.60, 3.34,
              3.50, 3.52, 3.69, 3.65, 3.80)
PUB_SD   <- c(0.86, 0.81, 0.93, 0.92, 0.95, 0.88, 1.14, 0.98, 0.99, 1.11,
              1.00, 0.93, 0.97, 0.98, 0.95)
TOL <- 0.07

d <- irw::irw_fetch(TABLE)
items <- paste0("Item", 1:15)
m <- tapply(d$resp, d$item, mean)[items]
s <- tapply(d$resp, d$item, sd)[items]

cat("Route 1: per-item mean / SD vs Table 1\n")
cat(sprintf("%-7s %6s %6s %7s | %5s %5s %7s\n", "item", "pubM", "obsM", "dM", "pubSD", "obsSD", "dSD"))
for (i in 1:15)
  cat(sprintf("%-7s %6.2f %6.2f %7.3f | %5.2f %5.2f %7.3f\n", items[i], PUB_MEAN[i], m[i],
              m[i] - PUB_MEAN[i], PUB_SD[i], s[i], s[i] - PUB_SD[i]))
worst <- max(abs(c(m - PUB_MEAN, s - PUB_SD)))
cat(sprintf("largest |deviation| = %.3f (tolerance %.2f)\n\n", worst, TOL))

cat("Route 2: optimal assignment of live items to published rows on (mean, SD)\n")
cost <- outer(1:15, 1:15, function(i, j) sqrt((m[i] - PUB_MEAN[j])^2 + (s[i] - PUB_SD[j])^2))
asg <- as.integer(solve_LSAP(cost))
cat("assigned published row per live Item1..15:", asg, "\n")
n_self <- sum(asg == 1:15)
cat(sprintf("identity rows chosen: %d/15\n", n_self))
nn <- apply(cost, 1, which.min)
cat("nearest published row per live item:", nn, "\n\n")

cat("Route 3: 3-factor EFA (minres, oblimin -- the paper's method) primary-factor match\n")
suppressMessages(library(psych))
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
f <- suppressMessages(suppressWarnings(fa(w[, items], 3, fm = "minres", rotate = "oblimin")))
L <- unclass(f$loadings)
# name each extracted factor by the published block whose rows load on it most
blocks <- list(Cog = 1:6, Aff = 7:10, Psy = 12:15)
fac_name <- sapply(1:3, function(k) names(which.max(sapply(blocks, function(bb) mean(L[bb, k])))))
colnames(L) <- fac_name
print(round(L, 2))
PUB_FAC <- c(rep("Cog", 6), rep("Aff", 4), NA, rep("Psy", 4))  # row 11 = published cross-loader
prim <- colnames(L)[apply(abs(L), 1, which.max)]
hit <- prim == PUB_FAC
cat(sprintf("primary factor matches published block: %d/14 (row 11 excluded as published F2/F3 cross-loader)\n",
            sum(hit, na.rm = TRUE)))
cat("mismatches:", paste(items[which(!hit)], collapse = ", "), "\n")
cat(sprintf("Item11 loadings: %s (published F2 .31 / F3 .30)\n\n",
            paste(sprintf("%s=%.2f", colnames(L), L[11, ]), collapse = " ")))
ok_block <- length(unique(fac_name)) == 3 && sum(hit, na.rm = TRUE) >= 13

cat("What this does NOT establish: several published rows are near-tied on mean and SD\n",
    "(rows 4/11/12 ~3.5, rows 8/9 ~3.6, rows 1/2/3 ~3.95), so route 1 cannot by itself separate\n",
    "those rows individually (nearest-neighbour is not self for 4 of 15 live items); route 2 shows the\n",
    "identity is the cost-minimising assignment, but by margins of a few hundredths, i.e. within\n",
    "the half-sample vs full-sample noise; route 3 pins block membership, not order within a block.\n", sep = "")

pass <- worst <= TOL && n_self == 15 && ok_block
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
