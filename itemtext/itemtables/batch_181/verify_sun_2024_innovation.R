# verify_sun_2024_innovation.R
#
# CLAIM: the live IRW table sun_2024_innovation (codes innovation1..innovation3)
# carries the three "SME innovativeness" items that Sun, Tohirovich Dedahanov,
# Li & Young Shin (2024, Heliyon, doi:10.1016/j.heliyon.2024.e36620, section 4.2)
# prints as "1. ... 2. ... 3. ..." -- i.e. that this 3-column block of the study's
# mmc1.xlsx deposit IS the construct the paper calls SME innovativeness (INN), and
# that code innovationK carries the paper's item K.
#
# What can be checked, and what cannot:
#
#  (A) live code -> deposited column. The live table is joined to the study's own
#      mmc1.xlsx (Europe PMC supplementaryFiles for PMC11385760) on id == NO, and
#      each live item is compared respondent-by-respondent with the deposit column
#      of the same name and with the other two innovation columns.
#
#  (B) deposited block -> paper construct. The paper's Table 7 prints the full
#      HTMT matrix for its six constructs (15 cells) and Table 6 prints INN's
#      Cronbach's alpha (0.961). HTMT is an exact function of the item correlation
#      matrix, so it is recomputed from the deposit under the processing script's
#      block assignment, and ALL 720 ways of assigning the six construct labels to
#      the six 3-column blocks are scored, so the identity assignment's margin is
#      visible. This pins which block is INN.
#
#  NOT ESTABLISHED: the order of the three items WITHIN the INN block. Every
#  statistic the paper publishes for INN is symmetric in its three items (HTMT,
#  alpha, CR, AVE, Fornell-Larcker, path coefficients) except Table 6's per-item
#  "Standard deviation" column (0.003 / 0.003 / 0.004), which is a bootstrap SD
#  of the SmartPLS outer loading: two of the three values tie at the printed
#  precision and it depends on the resampling, so it cannot separate the items.
#  The tie innovationK <-> printed item K rests on the matching numbers alone.

suppressMessages({ library(irw); library(readxl) })

TABLE <- "sun_2024_innovation"
SUPPL <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11385760/supplementaryFiles"
INN   <- paste0("innovation", 1:3)

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
L <- sapply(INN, function(it) { x <- d[d$item == it, ]; x$resp[match(ids, x$id)] })
S <- as.matrix(s[match(ids, s$NO), INN])
cat(sprintf("(A) joined respondents: %d of %d deposit rows; NA live=%s deposit=%s\n",
            length(ids), nrow(s), anyNA(L), anyNA(S)))
agree <- matrix(NA_real_, 3, 3, dimnames = list(paste0("live:", INN), INN))
for (i in 1:3) for (j in 1:3) agree[i, j] <- 100 * mean(L[, i] == S[, j])
print(round(agree, 1))
A_ok <- all(abs(diag(agree) - 100) < 1e-9) && max(agree[row(agree) != col(agree)]) < 100
cat(sprintf("diagonal all 100%%: %s ; largest off-diagonal: %.1f%%\n\n",
            all(abs(diag(agree) - 100) < 1e-9), max(agree[row(agree) != col(agree)])))

## ---- (B) HTMT matrix (paper Table 7) and alpha (Table 6) ---------------------
BLK <- list(PV  = paste0("Pricevalue", 1:3),  PR = paste0("Risk", 1:3),
            PE  = paste0("PerformanceE", 1:3), INN = INN,
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
cat("(B) paper Table 7 HTMT vs recomputed from mmc1.xlsx (processing-script block assignment):\n")
for (n in names(PUB)) cat(sprintf("  %-8s published %.3f  observed %.4f  diff %+.4f\n", n, PUB[n], id$obs[n], id$obs[n] - PUB[n]))
cat(sprintf("largest residual, identity assignment: %.4f\n", id$resid))

perms <- function(v) if (length(v) == 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(r) c(v[i], r))))
P <- perms(1:6)
res <- sapply(P, function(p) { b <- BLK[p]; names(b) <- names(BLK); score(b)$resid })
ord <- order(res)
cat(sprintf("all %d label->block assignments scored; best %.4f (identity=%s), second-best %.4f (%s)\n",
            length(P), res[ord[1]], identical(P[[ord[1]]], 1:6), res[ord[2]],
            paste(names(BLK)[P[[ord[2]]]], collapse = ",")))
# the second-best tells you which block INN would have to be to rival identity
inn_alt <- sapply(P, function(p) names(BLK)[p][4])
cat(sprintf("best assignment in which INN is NOT the innovation block: %.4f\n",
            min(res[inn_alt != "INN"])))

x <- s[, INN]
alpha <- 3 / 2 * (1 - sum(apply(x, 2, var)) / var(rowSums(x)))
cat(sprintf("\nCronbach alpha INN: published 0.961, observed %.4f\n", alpha))

B_ok <- id$resid <= 0.001 && identical(P[[ord[1]]], 1:6) && res[ord[2]] > 5 * id$resid &&
        abs(alpha - 0.961) <= 0.0005

cat("\nNOT ESTABLISHED: order within the INN block. HTMT and alpha are invariant to\n",
    "permuting innovation1..3, and the paper publishes no item-specific statistic that\n",
    "separates them (Table 6 bootstrap SDs 0.003/0.003/0.004 tie). Status PARTIAL.\n", sep = "")

cat(if (A_ok && B_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
