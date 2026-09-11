# verify_sun_2024_task_tech_fit.R
#
# CLAIM: the live IRW table sun_2024_task_tech_fit (codes TTF1..TTF3) carries the
# three "Task-technology fit" items that Sun, Tohirovich Dedahanov, Li & Young Shin
# (2024, Heliyon 10:e36620, doi:10.1016/j.heliyon.2024.e36620, PMC11385760, section
# 4.2 'Measurement') prints as "1. ...; 2. ...; 3. ...", i.e. that this 3-column
# block of the study's mmc1.xlsx deposit IS the construct the paper calls
# Task-technology fit (TTF), and that code TTFk carries the paper's item k.
#
# What is checked:
#
#  (A) live code -> deposited column. The live table (843 rows; irw_fetch of a
#      table this size is negligible against the export cap, and no server-side
#      route returns per-respondent rows) is joined to mmc1.xlsx on id == NO, and
#      each live item is compared respondent-by-respondent with the deposit column
#      of the same name and with the other two TTF columns.
#
#  (B) deposited block -> paper construct. Paper Table 7 prints the HTMT matrix for
#      its six constructs (15 cells among PV, PR, PE, INN, TTF, U). HTMT is an exact
#      function of the item correlations, so it is recomputed from the deposit under
#      the processing script's block assignment, and ALL 720 assignments of the six
#      construct labels to the six 3-column blocks are scored. Also Table 6's TTF
#      Cronbach alpha (0.983), and AVE (0.968) / CR (0.985) approximated with
#      first-principal-component loadings.
#
#  NOT ESTABLISHED: the order of TTF1..TTF3 WITHIN the block. HTMT, alpha, AVE, CR
#  and every path statistic are invariant to permuting the three items; Table 6's
#  only item-level column is a bootstrap SD of the outer loading (TTF1 0.004, TTF2
#  0.004, TTF3 0.003), which ties and depends on resampling. The paper publishes no
#  per-item means. The tie TTFk <-> printed item k rests on the matching numbers.

suppressMessages({ library(irw); library(readxl) })

TABLE <- "sun_2024_task_tech_fit"
SUPPL <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11385760/supplementaryFiles"
TTF   <- paste0("TTF", 1:3)

## ---- fetch --------------------------------------------------------------
d <- irw::irw_fetch(TABLE)
tz <- tempfile(fileext = ".zip")
download.file(SUPPL, tz, mode = "wb", quiet = TRUE)   # no email / UA header sent
td <- tempfile(); dir.create(td)
unzip(tz, files = "mmc1.xlsx", exdir = td)
s <- as.data.frame(read_excel(file.path(td, "mmc1.xlsx")))
cat(sprintf("deposit mmc1.xlsx: %d rows x %d cols; live rows: %d\n\n", nrow(s), ncol(s), nrow(d)))

## ---- (A) live item vs deposit column, per respondent ----------------------
ids <- sort(unique(d$id))
L <- sapply(TTF, function(it) { x <- d[d$item == it, ]; x$resp[match(ids, x$id)] })
S <- as.matrix(s[match(ids, s$NO), TTF])
cat(sprintf("(A) joined respondents: %d of %d deposit rows; NA live=%s deposit=%s\n",
            length(ids), nrow(s), anyNA(L), anyNA(S)))
agree <- matrix(NA_real_, 3, 3, dimnames = list(paste0("live:", TTF), TTF))
for (i in 1:3) for (j in 1:3) agree[i, j] <- 100 * mean(L[, i] == S[, j])
print(round(agree, 1))
offd <- agree[row(agree) != col(agree)]
A_ok <- length(ids) == nrow(s) && !anyNA(L) && !anyNA(S) &&
        all(abs(diag(agree) - 100) < 1e-9) && max(offd) < 100
cat(sprintf("diagonal all 100%%: %s ; largest off-diagonal: %.1f%%\n",
            all(abs(diag(agree) - 100) < 1e-9), max(offd)))
cat(sprintf("live item means: %s\n\n", paste(sprintf("%.3f", colMeans(L)), collapse = " / ")))

## ---- (B) HTMT matrix (paper Table 7), alpha/AVE/CR (Table 6) ----------------
BLK <- list(PV  = paste0("Pricevalue", 1:3),  PR = paste0("Risk", 1:3),
            PE  = paste0("PerformanceE", 1:3), INN = paste0("innovation", 1:3),
            TTF = TTF,                         U  = paste0("Usage", 1:3))
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
cat("(B) paper Table 7 HTMT vs recomputed from mmc1.xlsx (processing-script block assignment):\n")
for (n in names(PUB)) cat(sprintf("  %-8s published %.3f  observed %.4f  diff %+.4f%s\n", n, PUB[n],
                                  id$obs[n], id$obs[n] - PUB[n], if (grepl("TTF", n)) "   <- TTF cell" else ""))
cat(sprintf("largest residual, identity assignment: %.4f\n", id$resid))

perms <- function(v) if (length(v) == 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(r) c(v[i], r))))
P <- perms(1:6)
res <- sapply(P, function(p) { b <- BLK[p]; names(b) <- names(BLK); score(b)$resid })
ord <- order(res)
ttf_block <- sapply(P, function(p) names(BLK)[p][5])   # which real block gets the TTF label
cat(sprintf("all %d label->block assignments scored; best %.4f (identity=%s), second-best %.4f\n",
            length(P), res[ord[1]], identical(P[[ord[1]]], 1:6), res[ord[2]]))
best_alt <- min(res[ttf_block != "TTF"])
cat(sprintf("best assignment in which the TTF label sits on a non-TTF block: %.4f\n", best_alt))

x <- s[, TTF]
alpha <- 3 / 2 * (1 - sum(apply(x, 2, var)) / var(rowSums(x)))
lam <- abs(eigen(cor(x))$vectors[, 1]) * sqrt(eigen(cor(x))$values[1])
ave <- mean(lam^2); cr <- sum(lam)^2 / (sum(lam)^2 + sum(1 - lam^2))
cat(sprintf("\nTTF Table 6: alpha published 0.983 observed %.4f | AVE published 0.968 observed(PC1) %.4f | CR published 0.985 observed(PC1) %.4f\n",
            alpha, ave, cr))
cat("  (CR is reported, not gated: PC1 rho_c 0.989 exceeds the printed 0.985, which with AVE 0.968\n",
    "   is not a rho_c value; SmartPLS 4 also prints rho_a, which is probably what the paper shows.)\n", sep = "")
others <- sapply(BLK, function(b) { y <- s[, b]; 3 / 2 * (1 - sum(apply(y, 2, var)) / var(rowSums(y))) })
cat("alpha of every block:", paste(sprintf("%s %.4f", names(others), others), collapse = ", "), "\n")

B_ok <- id$resid <= 0.001 && identical(P[[ord[1]]], 1:6) && best_alt > 5 * id$resid &&
        abs(alpha - 0.983) <= 0.0006

cat("\nNOT ESTABLISHED: order within the TTF block. HTMT, alpha, AVE and CR are invariant to\n",
    "permuting TTF1..3, and the paper's only item-level figure (Table 6 bootstrap SDs\n",
    "0.004/0.004/0.003) ties and is resampling-dependent. Status PARTIAL.\n", sep = "")

cat(if (A_ok && B_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
