# verify_zhou_2024_smart_home_intention.R -- Step 5b mapping check (batch_254).
# Copied from references/verify_template.R.
#
# Claim: live item <code> carries the wording the paper's Table 1 (t001, image
# table) prints against the same code ("PU1: I believe that ...").
# data/zhou_2024_smart_home_intention.py melts the S1 .xls columns PU1..PR2 BY
# NAME, so the IRW code IS the source column name, and the paper labels each
# wording with that code (explicit code labels).
#
# Falsifiable checks run here:
#   A. live <code> equals S1 column <code> id-for-id (200 ids), and no other
#      item column reaches full agreement -- breaks if the script had shifted
#      or renamed a column.
#   B. Refit the paper's six-factor CFA (Table 4, t004) on the live data and
#      compare every unstandardized Coef. and Std. Estimate, plus the per-
#      construct alphas. Table 4 prints the same codes as Table 1; each item's
#      (Coef, Std) pair is distinct within its construct, so any swap of two
#      codes -- within or across constructs -- changes the printed numbers.
# NOT established: that the English in Table 1 is the wording respondents read
# (administered presumably in Chinese; no Chinese text is in the deposit).

suppressMessages({ library(irw); library(lavaan) })
TABLE <- "zhou_2024_smart_home_intention"
items <- c("PU1","PU2","PU3","PEOU1","PEOU2","UI1","UI2","ITS1","ITS2","PV1","PV2","PR1","PR2")
# Table 4 (t004): Coef., Std. Estimate
PUB_COEF <- c(1.000,0.849,0.939, 1.000,0.953, 1.000,0.827, 1.000,1.105, 1.000,1.001, 1.000,0.999)
PUB_STD  <- c(0.682,0.623,0.621, 0.830,0.776, 0.763,0.664, 0.833,0.858, 0.845,0.816, 0.836,0.739)
names(PUB_COEF) <- names(PUB_STD) <- items
PUB_ALPHA <- c(PU=0.677, PEOU=0.784, UI=0.672, ITS=0.832, PV=0.816, PR=0.760)
TOL <- 0.0015
pass <- TRUE

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id","item","resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))

# ---- A. live vs S1 -------------------------------------------------------
tf <- tempfile(fileext = ".xls")
ok <- tryCatch({ download.file("https://doi.org/10.1371/journal.pone.0300574.s001", tf,
                               mode = "wb", quiet = TRUE,
                               headers = c("User-Agent" = "Mozilla/5.0")); TRUE },
               error = function(e) FALSE)
if (ok) {
  s1 <- as.data.frame(readxl::read_excel(tf, sheet = "Sheet1"))
  names(s1)[names(s1) == "ID"] <- "id"
  m <- merge(w, s1[, c("id", items)], by = "id", suffixes = c(".live", ".s1"))
  cat(sprintf("A. live vs S1: live ids %d, S1 rows %d, matched %d\n", nrow(w), nrow(s1), nrow(m)))
  if (nrow(m) != nrow(w)) pass <- FALSE
  for (a in items) {
    ag <- sapply(items, function(b) sum(m[[paste0(a, ".live")]] == m[[paste0(b, ".s1")]], na.rm = TRUE))
    best_other <- max(ag[names(ag) != a])
    cat(sprintf("   live %-5s = S1 %-5s %3d/%d ; best other S1 column %3d\n", a, a, ag[a], nrow(m), best_other))
    if (ag[a] != nrow(m) || best_other == nrow(m)) pass <- FALSE
  }
} else cat("A. S1 download failed -- check A skipped; check B alone decides\n")

# ---- B. Table 4 CFA reproduction -----------------------------------------
mod <- "PU=~PU1+PU2+PU3\nPEOU=~PEOU1+PEOU2\nUI=~UI1+UI2\nITS=~ITS1+ITS2\nPV=~PV1+PV2\nPR=~PR1+PR2"
f <- cfa(mod, data = w)
pe <- parameterEstimates(f); ss <- standardizedSolution(f)
coef <- setNames(pe$est[pe$op == "=~"], pe$rhs[pe$op == "=~"])[items]
std  <- setNames(ss$est.std[ss$op == "=~"], ss$rhs[ss$op == "=~"])[items]
cat("\nB. Table 4 CFA, published vs live\n")
cat(sprintf("%-6s %8s %8s %9s %9s\n", "item", "pubCoef", "liveCoef", "pubStd", "liveStd"))
for (i in items) cat(sprintf("%-6s %8.3f %8.3f %9.3f %9.3f\n", i, PUB_COEF[i], coef[i], PUB_STD[i], std[i]))
worst <- max(abs(c(coef - PUB_COEF, std - PUB_STD)))
cat(sprintf("largest |diff| over 26 values: %.4f (tol %.4f)\n", worst, TOL))
if (worst > TOL) pass <- FALSE

grp <- list(PU=items[1:3], PEOU=items[4:5], UI=items[6:7], ITS=items[8:9], PV=items[10:11], PR=items[12:13])
cat("\nalpha per construct (published / live)\n")
for (g in names(grp)) {
  v <- var(w[, grp[[g]]]); k <- length(grp[[g]])
  a <- k / (k - 1) * (1 - sum(diag(v)) / sum(v))
  cat(sprintf("  %-5s %.3f / %.3f\n", g, PUB_ALPHA[g], a))
  if (abs(a - PUB_ALPHA[g]) > 0.002) pass <- FALSE
}

# Swap sensitivity: what Table 4 would read if the two codes of a pair swapped.
cat("\nswap sensitivity (e.g. PEOU1<->PEOU2 would print Coef", sprintf("%.3f", 1/PUB_COEF["PEOU2"]),
    "and Std", PUB_STD["PEOU2"], "for PEOU1)\n")
cat("Not established: that Table 1's English is the administered (Chinese) wording.\n")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
