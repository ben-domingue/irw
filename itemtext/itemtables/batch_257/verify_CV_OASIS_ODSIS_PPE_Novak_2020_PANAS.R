# verify_CV_OASIS_ODSIS_PPE_Novak_2020_PANAS.R
#
# CLAIM UNDER TEST -----------------------------------------------------------
# The IRW item codes panas_1 .. panas_20 are the source spreadsheet's own column
# names (data/CV_OASIS_ODSIS_PPE_Novak_2020.R selects starts_with("PANAS") --
# case-insensitive in tidyselect -- out of ex.dataset.csv and melts by name, no
# rename, no positional step). Those columns carry no text, so the adjectives
# are assigned as the canonical Watson, Clark & Tellegen (1988) PANAS in its
# printed order:
#   1 interested(P)  2 distressed(N)  3 excited(P)   4 upset(N)      5 strong(P)
#   6 guilty(N)      7 scared(N)      8 hostile(N)   9 enthusiastic(P) 10 proud(P)
#  11 irritable(N)  12 alert(P)      13 ashamed(N)  14 inspired(P)  15 nervous(N)
#  16 determined(P) 17 attentive(P)  18 jittery(N)  19 active(P)    20 afraid(N)
# and the live table stores raw responses 1 = "very slightly or not at all" ..
# 5 = "extremely" for every item (no reverse keying in the PANAS).
#
# FALSIFIABLE PREDICTIONS --------------------------------------------------
# (1) SUBSCALE BLOCKS (route 5). Canonical P = {1,3,5,9,10,12,14,16,17,19}, the
#     exact set the study's own CZ_short_OASIS_ODSIS.Rmd (osf.io/k5bvs, lines
#     327-334) scores as positive affect -- 1 of C(20,10) = 184,756 splits. Each
#     item should correlate more with the rest of its own block than with the
#     other block. The one permitted exception is panas_12 (alert), which the
#     authors themselves flag (Rmd line 1966) as linked to negative emotionality.
# (2) PUBLISHED TOTALS (route 3). Paper Table 4 (Sandora et al. 2021, IJERPH
#     18:10337) reports PANAS-P 28.83 (SD 9.77), PANAS-N 18.27 (SD 7.58), and a
#     PANAS-P/PANAS-N Spearman r of 0.61. The Rmd computes PANAS_P with
#     starts_with(c("panas_1", ...)), which also captures panas_11, 13, 15, 18
#     (NOTE: an authors' scoring defect -- 14 columns, not 10), and PANAS_N with
#     starts_with("panas_2") capturing panas_20 as intended. Recomputing those
#     exact selections from the live codes must land near the published values.
# (3) AUTHOR-NAMED ITEMS (from the OSF raw file, after proving it equals the
#     live table). The Rmd comment at line 1966 says the positive PANAS_P-OASIS
#     association is driven by "Interested, Attentive and primary: Alert". So
#     among the ten P items, the three highest Spearman correlations with the
#     OASIS total must be panas_1, panas_17, panas_12, with panas_12 the top.
# (4) MARKER ITEMS (route 7). The four lowest-mean items should all be N items
#     and should be the guilt/fear/hostility/shame adjectives {6,7,8,13}.
# (5) DIRECTION. Canonical P total must correlate positively with scored RSES
#     and N total positively with scored BFI-N (sibling tables' verified
#     scoring), i.e. resp ascends with the affect for both blocks.
#
# WHAT THIS DOES NOT ESTABLISH: order within the P block beyond panas_12 and
# the {panas_1, panas_17} pair; order within {6,7,8,13}; order within the other
# six N items {2,4,11,15,18,20}; order within the other seven P items
# {3,5,9,10,14,16,19}. No per-item statistics are published. Hence PARTIAL.

suppressMessages(library(redivis))

TBL <- "`datapages.item_response_warehouse:as2e.cv_oasis_odsis_ppe_novak_2020_panas:3ntv`"
P <- c(1,3,5,9,10,12,14,16,17,19); N <- setdiff(1:20, P)
ADJ <- c("interested","distressed","excited","upset","strong","guilty","scared","hostile",
         "enthusiastic","proud","irritable","alert","ashamed","inspired","nervous",
         "determined","attentive","jittery","active","afraid")

# ---- live aggregates (server-side, no export) ------------------------------
piv <- paste0("WITH w AS (SELECT id, ",
              paste(sprintf('MAX(IF(item="panas_%d", resp, NULL)) AS i%d', 1:20, 1:20), collapse = ", "),
              " FROM ", TBL, " GROUP BY id)")
pairs <- t(combn(20, 2))
sel <- paste(c(sprintf("CORR(i%d,i%d) AS c%d_%d", pairs[,1], pairs[,2], pairs[,1], pairs[,2]),
               sprintf("AVG(i%d) AS m%d", 1:20, 1:20), sprintf("STDDEV(i%d) AS s%d", 1:20, 1:20),
               "COUNT(*) AS n"), collapse = ", ")
r <- as.data.frame(suppressWarnings(redivis::query(paste0(piv, " SELECT ", sel, " FROM w")))$to_data_frame())

R <- diag(20)
for (k in seq_len(nrow(pairs))) {
  v <- as.numeric(r[1, sprintf("c%d_%d", pairs[k,1], pairs[k,2])])
  R[pairs[k,1], pairs[k,2]] <- R[pairs[k,2], pairs[k,1]] <- v
}
m <- as.numeric(r[1, sprintf("m%d", 1:20)])

# Sum-score moments from the live per-item SD and correlations
sum_stats <- function(idx) {
  s <- as.numeric(r[1, sprintf("s%d", idx)])
  c(mean = sum(m[idx]), sd = sqrt(sum(outer(s, s) * R[idx, idx])))
}

cat(sprintf("live respondents: %s\n\n", r$n))
cat(sprintf("%-9s %-13s %5s %7s %8s %8s\n", "item", "adjective", "block", "mean", "r_ownblk", "r_other"))
ok_block <- logical(20)
for (i in 1:20) {
  own <- if (i %in% P) setdiff(P, i) else setdiff(N, i)
  oth <- if (i %in% P) N else P
  a <- mean(R[i, own]); b <- mean(R[i, oth]); ok_block[i] <- a > b
  cat(sprintf("panas_%-3d %-13s %5s %7.3f %8.3f %8.3f %s\n", i, ADJ[i], if (i %in% P) "P" else "N",
              m[i], a, b, if (a > b) "" else "<-- closer to other block"))
}
fails <- which(!ok_block)
ok1 <- all(fails %in% 12)
cat(sprintf("\n(1) items closer to the other block: {%s}; allowed only {12 alert}: %s\n",
            paste(fails, collapse = ","), ok1))

# (2) published totals with the Rmd's actual selections
selP <- c(1, 3, 5, 9, 10:19); selN <- c(2, 20, 4, 6, 7, 8, 11, 13, 15, 18)
sp <- sum_stats(selP); sn <- sum_stats(selN)
sP <- as.numeric(r[1, sprintf("s%d", selP)]); sN <- as.numeric(r[1, sprintf("s%d", selN)])
covPN <- sum(outer(sP, sN) * R[selP, selN]); rPN <- covPN / (sp["sd"] * sn["sd"])
cat(sprintf("\n(2) PANAS_P (Rmd selection, 14 cols): live %.2f (SD %.2f)  published 28.83 (9.77)\n", sp["mean"], sp["sd"]))
cat(sprintf("    PANAS_N (Rmd selection, 10 cols): live %.2f (SD %.2f)  published 18.27 (7.58)\n", sn["mean"], sn["sd"]))
cat(sprintf("    Pearson r(P,N) live %.2f   published Spearman 0.61\n", rPN))
sc <- sum_stats(P)
cat(sprintf("    (canonical 10-item P for reference: %.2f, SD %.2f -- does NOT match 28.83)\n", sc["mean"], sc["sd"]))
ok2 <- abs(sp["mean"] - 28.83) < 0.3 && abs(sn["mean"] - 18.27) < 0.3 &&
       abs(sp["sd"] - 9.77) < 0.3 && abs(sn["sd"] - 7.58) < 0.3 && abs(rPN - 0.61) < 0.05

# (4) marker items
low4 <- order(m)[1:4]
cat(sprintf("\n(4) four lowest-mean items: {%s} (%s); next lowest %.3f\n",
            paste(sort(low4), collapse = ","), paste(ADJ[sort(low4)], collapse = ", "), sort(m)[5]))
ok4 <- setequal(low4, c(6, 7, 8, 13))

# (3) + (5) from the OSF raw file, after proving it IS the live table
tf <- tempfile(fileext = ".csv")
download.file("https://osf.io/download/hvx57/", tf, quiet = TRUE, mode = "wb")
d <- read.csv2(tf)
p <- sapply(d[, paste0("panas_", 1:20)], as.numeric)
keep <- rowSums(is.na(p)) < 20; p <- p[keep, ]; d <- d[keep, ]
raw_m <- colMeans(p, na.rm = TRUE)
same <- nrow(p) == as.numeric(r$n) && max(abs(raw_m - m)) < 1e-9
cat(sprintf("\nOSF ex.dataset.csv: %d rows, max |raw mean - live mean| = %.2e -> same data: %s\n",
            nrow(p), max(abs(raw_m - m)), same))
oasis <- rowSums(sapply(d[, paste0("OASIS_", 1:5)], as.numeric))
ro <- sapply(P, function(i) cor(oasis, p[, i], use = "complete", method = "spearman"))
names(ro) <- paste0("panas_", P)
cat("(3) Spearman r with OASIS total, P items:\n"); print(round(sort(ro, decreasing = TRUE), 3))
top3 <- P[order(ro, decreasing = TRUE)[1:3]]
ok3 <- setequal(top3, c(1, 12, 17)) && top3[1] == 12
cat(sprintf("    top three = {%s}; predicted {1 interested, 12 alert, 17 attentive} with 12 first: %s\n",
            paste(top3, collapse = ","), ok3))

rs <- sapply(d[, paste0("RSES_", 1:10)], as.numeric); for (j in c(1,3,4,7,10)) rs[, j] <- 5 - rs[, j]
bf <- sapply(d[, paste0("BFI_N_", 1:8)], as.numeric); for (j in c(2,5,7)) bf[, j] <- 6 - bf[, j]
rP <- cor(rowSums(p[, P]), rowSums(rs), use = "complete", method = "spearman")
rN <- cor(rowSums(p[, N]), rowMeans(bf), use = "complete", method = "spearman")
cat(sprintf("\n(5) r(P total, scored RSES) = %+.3f ; r(N total, scored BFI-N) = %+.3f\n", rP, rN))
ok5 <- rP > 0 && rN > 0

cat("\nDoes NOT establish: order within {3,5,9,10,14,16,19}, within {1,17}, within {6,7,8,13},\n")
cat("or within {2,4,11,15,18,20}. Subscale membership, panas_12 and response direction only.\n")
cat(sprintf("checks: blocks %s | totals %s | author-named trio %s | markers %s | direction %s | raw==live %s\n",
            ok1, ok2, ok3, ok4, ok5, same))
cat(if (ok1 && ok2 && ok3 && ok4 && ok5 && same) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
