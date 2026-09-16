# verify_sun_2024_price_value.R -- batch_182, Step 5b mapping check.
#
# CLAIM: the live IRW table sun_2024_price_value (codes Pricevalue1..Pricevalue3)
# carries the three "Price value" items that Sun, Tohirovich Dedahanov, Li & Young
# Shin (2024, Heliyon 10:e36620, doi:10.1016/j.heliyon.2024.e36620, PMC11385760,
# section 4.2 Measurement) prints as "1. ...; 2. ...; 3. ...", with code suffix K
# <-> the paper's list number K.
#
# What can be checked:
#  (A) live code -> deposited column. Live table joined to the study's own
#      mmc1.xlsx (Europe PMC supplementaryFiles for PMC11385760) on id == NO; each
#      live item compared respondent-by-respondent with the same-named deposit
#      column and with the other two Pricevalue columns.
#  (B) deposited block -> paper construct. Paper Table 7 prints the HTMT matrix
#      for the six constructs (15 cells). HTMT is an exact function of the item
#      correlation matrix, so it is recomputed from the deposit under the
#      processing script's block assignment, and all 720 assignments of the six
#      construct labels to the six 3-column blocks are scored. PV's Table 6 row
#      (AVE 0.967, CR 0.984, alpha 0.983) is also compared; note it alone cannot
#      separate PV from TTF (0.968/0.985/0.983), which is why HTMT carries (B).
#
# NOT ESTABLISHED: order of the three items WITHIN the PV block. Every statistic
# the paper publishes for PV is symmetric in its items (HTMT, alpha, CR, AVE,
# Fornell-Larcker, paths) except Table 6's per-item "Standard deviation" column
# (0.002 / 0.003 / 0.002), a bootstrap SD of the SmartPLS loading that ties for
# PV1 and PV3 and depends on resampling. The code<->wording tie within the block
# rests on the paper's list numbers alone. Status PARTIAL.

suppressMessages({ library(irw); library(readxl) })

TABLE <- "sun_2024_price_value"
PV    <- paste0("Pricevalue", 1:3)
SUPPL <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11385760/supplementaryFiles"

get_xlsx <- function() {
  for (p in c(file.path("itemtext", ".cache", TABLE, "mmc1.xlsx"),
              file.path(".cache", TABLE, "mmc1.xlsx")))
    if (file.exists(p)) return(p)
  zf <- tempfile(fileext = ".zip"); dir <- tempfile(); dir.create(dir)
  download.file(SUPPL, zf, mode = "wb", quiet = TRUE)   # no email / UA header sent
  unzip(zf, files = "mmc1.xlsx", exdir = dir)
  file.path(dir, "mmc1.xlsx")
}
s <- as.data.frame(read_excel(get_xlsx()))
d <- irw::irw_fetch(TABLE)
cat(sprintf("deposit mmc1.xlsx: %d rows x %d cols; live rows: %d\n\n", nrow(s), ncol(s), nrow(d)))

## ---- (A) live item vs deposit column, per respondent ----------------------
ids <- sort(unique(d$id))
L <- sapply(PV, function(it) { x <- d[d$item == it, ]; x$resp[match(ids, x$id)] })
S <- as.matrix(s[match(ids, s$NO), PV])
cat(sprintf("(A) live ids %d, matched in deposit %d of %d rows; NA live=%s deposit=%s\n",
            length(ids), sum(!is.na(match(ids, s$NO))), nrow(s), anyNA(L), anyNA(S)))
agree <- matrix(NA_real_, 3, 3, dimnames = list(paste0("live:", PV), PV))
for (i in 1:3) for (j in 1:3) agree[i, j] <- 100 * mean(L[, i] == S[, j])
print(round(agree, 1))
offd <- agree[row(agree) != col(agree)]
A_ok <- length(ids) == nrow(s) && !anyNA(L) && !anyNA(S) &&
        all(abs(diag(agree) - 100) < 1e-9) && max(offd) < 100
cat(sprintf("diagonal all 100%%: %s ; largest off-diagonal: %.1f%%\n\n",
            all(abs(diag(agree) - 100) < 1e-9), max(offd)))

## ---- (B) HTMT (paper Table 7) and Table 6 row ------------------------------
BLK <- list(PV  = PV,                         PR = paste0("Risk", 1:3),
            PE  = paste0("PerformanceE", 1:3), INN = paste0("innovation", 1:3),
            TTF = paste0("TTF", 1:3),          U  = paste0("Usage", 1:3))
PUB <- c("PR-PV" = 0.128, "PE-PV" = 0.534, "PE-PR" = 0.269,
         "INN-PV" = 0.558, "INN-PR" = 0.027, "INN-PE" = 0.446,
         "TTF-PV" = 0.435, "TTF-PR" = 0.178, "TTF-PE" = 0.308, "TTF-INN" = 0.353,
         "U-PV" = 0.408, "U-PR" = 0.055, "U-PE" = 0.338, "U-INN" = 0.343, "U-TTF" = 0.274)
R <- abs(cor(s[, unlist(BLK)]))
mono <- function(a) { r <- R[a, a]; mean(r[upper.tri(r)]) }
htmt <- function(a, b) mean(R[a, b]) / sqrt(mono(a) * mono(b))
score <- function(blk) {
  obs <- sapply(names(PUB), function(n) { p <- strsplit(n, "-")[[1]]; htmt(blk[[p[1]]], blk[[p[2]]]) })
  list(obs = obs, resid = max(abs(obs - PUB)))
}
id <- score(BLK)
cat("(B) paper Table 7 HTMT vs recomputed from mmc1.xlsx (processing-script blocks):\n")
for (n in names(PUB))
  cat(sprintf("  %-8s published %.3f  observed %.4f  diff %+.4f\n", n, PUB[n], id$obs[n], id$obs[n] - PUB[n]))
cat(sprintf("largest residual, identity assignment: %.4f\n", id$resid))

perms <- function(v) if (length(v) == 1) list(v) else
  do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(r) c(v[i], r))))
P <- perms(1:6)
res <- sapply(P, function(p) { b <- BLK[p]; names(b) <- names(BLK); score(b)$resid })
ord <- order(res)
pv_on <- sapply(P, function(p) names(BLK)[p][1])   # which block the PV label sits on
cat(sprintf("all %d label->block assignments scored; best %.4f (identity=%s), second-best %.4f\n",
            length(P), res[ord[1]], identical(P[[ord[1]]], 1:6), res[ord[2]]))
pv_alt <- min(res[pv_on != "PV"])
cat(sprintf("best assignment with the PV label NOT on the Pricevalue block: %.4f\n", pv_alt))

alpha <- function(m) { k <- ncol(m); k / (k - 1) * (1 - sum(apply(m, 2, var)) / var(rowSums(m))) }
plsA <- function(m) {                   # PLS mode-A outer loadings
  z <- scale(m); wt <- rep(1, ncol(m))
  for (it in 1:200) { sc <- scale(z %*% wt); wt <- as.vector(cor(z, sc)) }
  as.vector(cor(z, sc))
}
live <- L; colnames(live) <- PV
l <- plsA(live)
obs6 <- c(AVE = mean(l^2), CR = sum(l)^2 / (sum(l)^2 + sum(1 - l^2)), alpha = alpha(live))
T6 <- rbind(INN = c(.927, .975, .961), PR = c(.916, .970, .963), PE = c(.963, .987, .981),
            PV = c(.967, .984, .983), TTF = c(.968, .985, .983), U = c(.952, .978, .975))
# Compared on AVE and alpha only. The published PV CR (0.984) is internally
# inconsistent with the published PV AVE (0.967): for three standardized loadings
# <= 1 with sum of squares 3*0.967, sum(l) lies in [2.949, 2.950], so CR under
# the usual rho_c formula must lie in [0.9887, 0.9888]. The same holds for the
# TTF (AVE .968 -> CR >= .9890, printed .985) and U (AVE .952 -> ~.9835, printed
# .978) rows, while INN, PR and PE are consistent. That is a property of the
# paper's Table 6, not of the data, so CR is printed but not scored.
colnames(T6) <- c("AVE", "CR", "alpha")
dist6 <- apply(T6[, c("AVE", "alpha")], 1, function(p) max(abs(p - obs6[c("AVE", "alpha")])))
cr_bound <- function(ave) { ss <- 3 * ave; lo <- 2 + sqrt(ss - 2); hi <- sqrt(3 * ss)
  c(lo^2 / (lo^2 + 3 - ss), hi^2 / (hi^2 + 3 - ss)) }
cat(sprintf("\nTable 6, live Pricevalue items: AVE %.4f CR %.4f alpha %.4f\n", obs6[1], obs6[2], obs6[3]))
for (r in rownames(T6)) {
  b <- cr_bound(T6[r, "AVE"])
  cat(sprintf("  published %-4s AVE %.3f CR %.3f alpha %.3f  max|diff| AVE,alpha %.4f  (CR implied by its own AVE: %.4f-%.4f)\n",
              r, T6[r, 1], T6[r, 2], T6[r, 3], dist6[r], b[1], b[2]))
}
cat(sprintf("  best-matching row on AVE/alpha: %s (%.4f); runner-up %s (%.4f)\n",
            names(which.min(dist6)), min(dist6), names(sort(dist6))[2], sort(dist6)[2]))
cat("  (PV and TTF rows differ by only 0.001, so Table 6 is corroborating only --\n",
    "   the HTMT permutation carries the construct assignment.)\n", sep = "")

B_ok <- id$resid <= 0.001 && identical(P[[ord[1]]], 1:6) && pv_alt > 20 * id$resid &&
        dist6["PV"] <= 0.001

cat("\nper-item live means:", paste(sprintf("%s %.3f", PV, colMeans(live)), collapse = ", "), "\n")
cat("NOT ESTABLISHED: order within the PV block. HTMT/alpha/AVE/CR are invariant to\n",
    "permuting Pricevalue1..3; the only per-item published figure (Table 6 bootstrap SD\n",
    "0.002/0.003/0.002) ties and is resampling-dependent. Status PARTIAL.\n", sep = "")

cat(sprintf("\n(A) code = same-named deposit column: %s; (B) block = paper's Price value: %s\n", A_ok, B_ok))
cat(if (A_ok && B_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
