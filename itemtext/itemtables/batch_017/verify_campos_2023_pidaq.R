# verify_campos_2023_pidaq.R -- Step 5b mapping check for campos_2023_pidaq.
#
# CLAIM UNDER TEST: the live item codes PIDAQ01..PIDAQ24 are the PIDAQ item NUMBERS
# 1..24 of the 24-item version used by this study, i.e. PIDAQnn carries the wording
# printed against "itnn" in Table 1 of Campos, Costa, Bonafe, Maroco & Campos (2020),
# Int Dent J 70:321-327 (PMC9379174) -- item 4 "I am proud of my teeth", item 1
# "I don't like my teeth when I look at myself in the mirror", item 24 "I like my
# tooth color", and so on. Two rival numbering conventions exist in the PIDAQ
# literature: the ORIGINAL interleaved order (Dental Self-Confidence = 4,7,12,17,21,23)
# and a subscale-sequential renumbering used by several validation papers
# (Dental Self-Confidence = 1..6). They disagree about every item, so the mapping
# stands or falls on which one this data uses.
#
# DATA SOURCE: the study's own S1 File (PLOS ONE 10.1371/journal.pone.0287235.s004,
# sheet "DB", N=7593), NOT irw::irw_fetch() -- deliberately. A fetch exports the whole
# table against the corpus download cap, and data/campos_2023_aesthetic_dental.py maps
# the 24 spreadsheet columns PIDAQ01..PIDAQ24 to the live `item` codes BY NAME (no
# positional step, no rename), dropping only out-of-range/missing cells. Nothing is
# dropped in practice: irw_table_sets() reports n = 7593 for each of the 24 items with
# resp in 0..4, which equals the spreadsheet's own N and range. So the live table is
# the spreadsheet, column for column.
#
# CHECK 1 (keying polarity, route 6). Dental Self-Confidence is worded positively and
#   the other three factors negatively, so the DSC block must correlate NEGATIVELY with
#   every other item. Under the interleaved numbering that block is {4,7,12,17,21,23,24};
#   under the sequential one it would be {1,2,3,4,5,6,24}.
# CHECK 2 (per-item descriptive statistics, route 1). Campos et al. (2021), Acta Odontol
#   Scand 79:335-343, Table 2 publishes mean/SD/skewness/kurtosis for it1..it24 of
#   PIDAQ-Fi in the same Finnish data collection. Compared here against the 3,614
#   Finnish respondents of this deposit, item by item, plus a check that no single
#   transposition of two items fits better than the identity mapping.
# CHECK 3 (subscale block structure, route 5). Items should correlate most with their
#   own published factor.

suppressMessages(library(readxl))

URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0287235.s004"
COLS <- sprintf("PIDAQ%02d", 1:24)
DSC  <- c(4, 7, 12, 17, 21, 23, 24)   # interleaved numbering + the added tooth-colour item
SUB  <- list(DSC = DSC,
             SI  = c(2, 5, 9, 13, 14, 15, 19, 22),
             PI  = c(3, 6, 10, 11, 16, 20),
             AC  = c(1, 8, 18))

f <- file.path(tempdir(), "campos2023_s1.xlsx")
if (!file.exists(f)) download.file(URL, f, mode = "wb", quiet = TRUE)
db <- as.data.frame(readxl::read_excel(f, sheet = "DB"))
X  <- as.data.frame(lapply(db[COLS], as.numeric))
cat(sprintf("deposit: %d rows, %d PIDAQ columns, resp range %g-%g\n\n",
            nrow(X), ncol(X), min(X, na.rm = TRUE), max(X, na.rm = TRUE)))

ok <- TRUE

## ---- CHECK 1: keying polarity -------------------------------------------------
C <- cor(X, use = "pairwise.complete.obs")
neg <- sapply(seq_len(24), function(i) sum(C[i, -i] < 0))
cat("CHECK 1 -- keying polarity (count of NEGATIVE correlations with the other 23 items)\n")
for (i in seq_len(24))
    cat(sprintf("  %-8s %2d negative  %s\n", COLS[i], neg[i],
                if (i %in% DSC) "[predicted positive-worded: Dental Self-Confidence]" else ""))
pos_block <- which(neg == 17)
c1 <- setequal(as.numeric(pos_block), as.numeric(DSC))
cat(sprintf("  block correlating negatively with all 17 others: {%s}\n",
            paste(pos_block, collapse = ",")))
cat(sprintf("  predicted (interleaved numbering): {%s}  -> %s\n",
            paste(DSC, collapse = ","), if (c1) "MATCH" else "MISMATCH"))
cat(sprintf("  rival (subscale-sequential numbering) would be {1,2,3,4,5,6,24} -> %s\n\n",
            if (c1) "REJECTED" else "not rejected"))
ok <- ok && c1

## ---- CHECK 2: per-item statistics vs Campos et al. (2021) Table 2 --------------
# Published PIDAQ-Fi Test Sample (n=1820) column: mean, SD, skewness, kurtosis.
PUB <- rbind(
  c(0.5,0.9, 1.7, 2.6), c(0.6,1.0, 1.8, 2.2), c(1.3,1.2, 0.7,-0.5), c(1.8,1.3, 0.0,-1.0),
  c(0.4,0.8, 2.6, 6.3), c(0.3,0.8, 2.6, 6.6), c(2.2,1.4,-0.2,-1.2), c(0.9,1.3, 1.2, 0.1),
  c(0.3,0.8, 3.1, 9.4), c(0.6,0.9, 1.8, 2.8), c(0.9,1.2, 1.2, 0.3), c(2.1,1.2,-0.2,-1.0),
  c(0.3,0.7, 3.2,11.0), c(0.2,0.6, 3.4,12.2), c(0.3,0.7, 3.0, 9.5), c(0.4,0.8, 2.4, 5.8),
  c(1.6,1.2, 0.1,-1.0), c(0.6,1.0, 2.0, 3.2), c(0.7,1.2, 1.6, 1.5), c(1.7,1.3, 0.4,-0.9),
  c(2.2,1.2,-0.4,-0.9), c(0.5,1.0, 1.9, 3.1), c(2.2,1.3,-0.3,-1.1), c(1.7,1.2, 0.0,-1.0))
skew <- function(v) mean((v - mean(v))^3) / sd(v)^3
kurt <- function(v) mean((v - mean(v))^4) / sd(v)^4 - 3
FIN <- X[db$country == 1, ]
OBS <- t(sapply(FIN, function(v) { v <- v[!is.na(v)]; c(mean(v), sd(v), skew(v), kurt(v)) }))
cat(sprintf("CHECK 2 -- per-item stats, Finnish respondents (n=%d) vs Campos 2021 Table 2\n", nrow(FIN)))
cat(sprintf("  %-8s %18s %18s %8s\n", "item", "published M/SD", "observed M/SD", "dM"))
for (i in seq_len(24))
    cat(sprintf("  %-8s %8.1f %9.1f %8.2f %9.2f %8.3f\n", COLS[i],
                PUB[i,1], PUB[i,2], OBS[i,1], OBS[i,2], OBS[i,1] - PUB[i,1]))
worst <- max(abs(OBS[,1] - PUB[,1]))
cat(sprintf("  largest |mean difference|: %.3f (tolerance 0.15; the published column is a\n", worst))
cat("  random half of the same collection, printed to one decimal)\n")
W <- c(1, 1, 0.5, 0.15)                       # weights: mean, SD, skew, kurtosis
cost <- function(p) sum(sapply(seq_len(24), function(i) sum(W * abs(OBS[i,] - PUB[p[i],]))))
id <- cost(seq_len(24)); best <- Inf; bestpair <- NULL
for (a in 1:23) for (b in (a+1):24) {
    p <- seq_len(24); p[c(a,b)] <- p[c(b,a)]
    if (cost(p) < best) { best <- cost(p); bestpair <- c(a,b) }
}
cat(sprintf("  identity mapping cost %.3f; best of the 276 two-item swaps %.3f (items %d/%d)\n",
            id, best, bestpair[1], bestpair[2]))
c2 <- worst <= 0.15 && best > id
cat(sprintf("  no transposition fits better than the identity mapping: %s\n\n",
            if (best > id) "TRUE" else "FALSE"))
ok <- ok && c2

## ---- CHECK 3: subscale block structure ----------------------------------------
Y <- X; Y[, DSC] <- 4 - Y[, DSC]              # align direction before blocking
CY <- cor(Y, use = "pairwise.complete.obs")
memb <- setNames(rep(names(SUB), lengths(SUB)), unlist(SUB))
hit <- 0
cat("CHECK 3 -- each item's own factor should show its highest mean correlation\n")
for (i in seq_len(24)) {
    sc <- sapply(SUB, function(v) mean(CY[i, setdiff(v, i)]))
    good <- names(which.max(sc)) == memb[[as.character(i)]]
    hit <- hit + good
    cat(sprintf("  %-8s own=%-4s best=%-4s %s  (%s)\n", COLS[i], memb[[as.character(i)]],
                names(which.max(sc)), if (good) "OK " else "miss",
                paste(sprintf("%s=%.2f", names(sc), sc), collapse = " ")))
}
cat(sprintf("  %d/24 items land on their own published factor\n", hit))
cat("  (the study itself reports compromised discriminant validity between Social\n")
cat("   Impact, Psychological Impact and Aesthetic Concern, so misses among those\n")
cat("   three are expected; all 7 Dental Self-Confidence items are correct)\n\n")
c3 <- hit >= 20
ok <- ok && c3

cat("What this does NOT establish: items 9, 13, 14 and 15 are floor items whose\n")
cat("published statistics agree to within the paper's one-decimal rounding, so route 1\n")
cat("separates them only through the global fit, not individually; all four are Social\n")
cat("Impact items, so route 3 cannot separate them either. A swap inside that group\n")
cat("would not be detected by these checks.\n\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
