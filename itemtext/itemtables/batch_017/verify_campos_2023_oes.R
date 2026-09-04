# verify_campos_2023_oes.R -- Step 5b mapping check for campos_2023_oes.
#
# CLAIM UNDER TEST: OES01..OES07 carry, in order, the seven component items of the
# Orofacial Esthetic Scale as printed (in English and Portuguese) in Table 1 of
# Campos, Maroco, John, Santos-Pinto & Campos (2020), PeerJ 8:e8814 (OES-Pt), i.e.
#   OES01 face, OES02 facial profile, OES03 mouth, OES04 rows of teeth,
#   OES05 tooth shape/form, OES06 tooth color, OES07 gum.
#
# DATA SOURCE: the study's own S1 File (PLOS ONE 10.1371/journal.pone.0287235.s004,
# sheet "DB", N=7593), NOT irw::irw_fetch() -- deliberately. A fetch exports the whole
# table against the corpus download cap, and data/campos_2023_aesthetic_dental.py maps
# the seven spreadsheet columns OES01..OES07 to the live `item` codes by NAME (no
# positional step, no rename), dropping only out-of-range/missing cells. Nothing is
# dropped in practice: irw_table_sets() reports n = 7593 for each of the 7 items and
# resp in 0..10, which equals the spreadsheet's own N and range. So the live table is
# the spreadsheet, column for column, and the mapping question is entirely about which
# OES wording belongs on which OESnn column.

suppressMessages(library(readxl))

URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0287235.s004"
COLS <- sprintf("OES%02d", 1:7)

f <- file.path(tempdir(), "campos2023_s1.xlsx")
if (!file.exists(f)) download.file(URL, f, mode = "wb", quiet = TRUE)
d  <- as.data.frame(read_excel(f, sheet = "DB"))
fi <- d[d$country == 1, COLS]   # Finland, n = 3614
br <- d[d$country == 2, COLS]   # Brazil,  n = 3979
cat(sprintf("source rows: Finland %d, Brazil %d, total %d\n", nrow(fi), nrow(br), nrow(d)))

ok <- logical(0)

## ---- CHECK 1: block boundary -------------------------------------------------
# The deposit holds three instruments in one sheet (PIDAQ01-24, OES01-07, SWLS01-05).
# S2 Table of the paper publishes the OES score (mean of the 7 component items) as
# 7.01 (SD 1.58) for Finland and 7.13 (SD 1.74) for Brazil. If the seven columns we
# call OES were the wrong seven, this would not reproduce.
PUB <- c(fi_m = 7.01, fi_s = 1.58, br_m = 7.13, br_s = 1.74)
obs <- c(fi_m = mean(rowMeans(fi)), fi_s = sd(rowMeans(fi)),
         br_m = mean(rowMeans(br)), br_s = sd(rowMeans(br)))
cat("\nCHECK 1 -- published OES score (S2 Table) vs computed from OES01..OES07\n")
for (k in names(PUB))
    cat(sprintf("  %-6s published %5.2f   observed %6.3f   diff %+.3f\n",
                k, PUB[k], obs[k], obs[k] - PUB[k]))
ok["boundary"] <- max(abs(obs - PUB)) <= 0.02

## ---- CHECK 2: the correlated-error pair -------------------------------------
# S1 Table of the paper: the OES factor model was refined "adding a correlation
# between errors of items 1 and 2", in BOTH countries. Campos et al. 2020 names those
# two items explicitly -- "items 1 (face) and 2 (facial profile)" -- the only two
# non-dental items on the scale. Prediction: after extracting one factor, the largest
# residual correlation in the 7x7 matrix is OES01-OES02.
R <- cor(d[, COLS], use = "complete.obs")
e <- eigen(R); L <- e$vectors[, 1] * sqrt(e$values[1])
res <- R - tcrossprod(L); diag(res) <- 0
dimnames(res) <- list(COLS, COLS)
iu <- which(upper.tri(res), arr.ind = TRUE)
pr <- data.frame(a = COLS[iu[, 1]], b = COLS[iu[, 2]], r = res[upper.tri(res)])
pr <- pr[order(-pr$r), ]
cat("\nCHECK 2 -- largest 1-factor residual correlations (predicted top pair: OES01-OES02)\n")
for (i in 1:3) cat(sprintf("  %s - %s  %+.3f\n", pr$a[i], pr$b[i], pr$r[i]))
ok["pair12"] <- pr$a[1] == "OES01" && pr$b[1] == "OES02" && pr$r[1] > 2 * pr$r[2]

## ---- CHECK 3: per-item descriptive profile vs OES-Pt Table 3 ------------------
# Campos et al. 2020 Table 3 gives per-item mean and SD for the SAME instrument in the
# SAME language, administered by the same group to an independent Brazilian sample
# (validation subsample, n = 537). Cross-sample, so the test is the profile, not the
# level: rank agreement plus the three items the profile singles out.
PT_M  <- c(7.0, 6.7, 7.0, 6.7, 7.1, 6.1, 7.4)
PT_SD <- c(2.0, 2.2, 2.4, 2.7, 2.6, 2.7, 2.4)
bm <- colMeans(br); bs <- apply(br, 2, sd)
cat("\nCHECK 3 -- Brazilian subsample vs OES-Pt Table 3 (validation sample, n=537)\n")
cat(sprintf("  %-6s %-38s %11s %11s\n", "item", "wording (claim)", "mean pt/obs", "sd pt/obs"))
W <- c("face", "facial profile", "mouth", "rows of teeth", "shape/form of teeth",
       "color of teeth", "gum")
for (i in 1:7)
    cat(sprintf("  %-6s %-38s %5.1f/%5.2f %5.1f/%5.2f\n",
                COLS[i], W[i], PT_M[i], bm[i], PT_SD[i], bs[i]))
rm_ <- cor(PT_M, bm, method = "spearman"); rs_ <- cor(PT_SD, bs, method = "spearman")
cat(sprintf("  Spearman: means %.2f, SDs %.2f\n", rm_, rs_))
cat(sprintf("  lowest mean  = %s (OES-Pt: item 6, color of teeth)\n", COLS[which.min(bm)]))
cat(sprintf("  highest mean = %s (OES-Pt: item 7, gum)\n",            COLS[which.max(bm)]))
cat(sprintf("  lowest SD    = %s (OES-Pt: item 1, face)\n",           COLS[which.min(bs)]))
ok["profile"] <- rm_ >= 0.85 && rs_ >= 0.85 &&
                 COLS[which.min(bm)] == "OES06" && COLS[which.max(bm)] == "OES07" &&
                 COLS[which.min(bs)] == "OES01"

cat("\nresults: ", paste(sprintf("%s=%s", names(ok), ifelse(ok, "PASS", "FAIL")), collapse = "  "), "\n", sep = "")
cat("What this does NOT establish: the order WITHIN the pinned facial pair\n",
    "(OES01 face vs OES02 facial profile) and within the dental block rests on the\n",
    "cross-sample profile of CHECK 3, not on an in-sample published per-item statistic;\n",
    "this study published no per-item table. It says nothing about the 0-10 anchors\n",
    "beyond the paper's own '0 (very dissatisfied) to 10 (very satisfied)', and nothing\n",
    "about the Finnish and Portuguese wording, which is not what this table ships.\n", sep = "")

cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
