# verify_salleh_2023_aim_iam_fim.R -- Step 5b mapping check (batch_167).
#
# CLAIM: item_01..item_12 are the 12 columns of PLOS ONE S1 Dataset
# (10.1371/journal.pone.0294238.s001) in file order, and the shipped Malay
# item_text for item_NN is the header of column NN (header row 1, Malay item
# text, 7 of 12 truncated by one trailing character and restored from the
# paper's Table 2).
#
# data/salleh_2023_aim_iam_fim.py assigns codes POSITIONALLY
# (item_map = {c: f"item_{i+1:02d}" for i, c in enumerate(item_cols)}), so the
# SKILL.md exemption does not apply. Three checks:
#   A. re-derive the positional assignment: live item_NN must equal source
#      column NN respondent-by-respondent, and no other column may equal it.
#   B. header diff: source header NN must be a prefix of shipped item_text NN
#      (<= 1 char missing) and of no other shipped item_text.
#   C. independent cross-check against the paper's own statistics: Table 4
#      polychoric correlations for its items 1,3,6,8,9,10,11 (EFA sample,
#      n = 170, the sample this table holds). Informational + a single-swap
#      robustness test; see the NOTE printed at the end for what C does not do.

suppressMessages({ library(irw); library(psych) })

TABLE <- "salleh_2023_aim_iam_fim"
SRC   <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0294238.s001"
here  <- tryCatch(dirname(normalizePath(sys.frame(1)$ofile)), error = function(e) NULL)
if (is.null(here)) {
    a <- grep("^--file=", commandArgs(FALSE), value = TRUE)
    here <- if (length(a)) dirname(normalizePath(sub("^--file=", "", a[1]))) else "."
}
ITEMS_CSV <- file.path(here, paste0(TABLE, "__items.csv"))

ok <- TRUE

# ---- data -------------------------------------------------------------------
d <- as.data.frame(irw::irw_fetch(TABLE))
tmp <- tempfile(fileext = ".csv")
download.file(SRC, tmp, quiet = TRUE, headers = c("User-Agent" = "Mozilla/5.0"))
src <- read.csv(tmp, check.names = FALSE, fileEncoding = "UTF-8-BOM")
names(src)[1] <- "id"
hdr <- names(src)[-1]
cat(sprintf("source: %d respondents x %d item columns; live: %d rows\n",
            nrow(src), length(hdr), nrow(d)))

w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[order(w$id), ]; src <- src[order(src$id), ]
if (!identical(as.numeric(w$id), as.numeric(src$id))) { cat("id sets differ\n"); ok <- FALSE }
codes <- sprintf("item_%02d", 1:12)

# ---- A. positional re-derivation --------------------------------------------
cat("\n== A. agreement (respondents with identical resp) live item_i vs source column j ==\n")
M <- sapply(1:12, function(j) sapply(1:12, function(i) sum(w[[codes[i]]] == src[[j + 1]])))
dimnames(M) <- list(codes, paste0("col", 1:12))
print(M)
diagv <- diag(M); off <- M; diag(off) <- NA
cat(sprintf("diagonal min %d/%d; largest off-diagonal %d/%d\n",
            min(diagv), nrow(src), max(off, na.rm = TRUE), nrow(src)))
if (any(diagv != nrow(src))) { cat("FAIL A: a live item does not equal its own column\n"); ok <- FALSE }
if (any(off == nrow(src), na.rm = TRUE)) { cat("FAIL A: a live item equals another column too\n"); ok <- FALSE }

# ---- B. header diff against shipped item_text --------------------------------
cat("\n== B. source header (col NN) vs shipped item_text (item_NN) ==\n")
it <- read.csv(ITEMS_CSV, stringsAsFactors = FALSE, fileEncoding = "UTF-8")
txt <- tapply(it$item_text, it$item, function(x) unique(x)[1])[codes]
for (i in 1:12) {
    h <- trimws(hdr[i])
    pre_self  <- startsWith(txt[i], h)
    missing   <- nchar(txt[i]) - nchar(h)
    pre_other <- which(startsWith(txt[-i], h))
    cat(sprintf("%s  prefix=%s  chars_restored=%d  also_prefix_of_other=%d  | %s\n",
                codes[i], pre_self, missing, length(pre_other), h))
    if (!pre_self || missing > 1 || length(pre_other) > 0) { cat("FAIL B at", codes[i], "\n"); ok <- FALSE }
}

# ---- C. paper Table 4 polychoric correlations ---------------------------------
cat("\n== C. paper Table 4 (polychoric) vs live polychoric ==\n")
X <- as.matrix(w[, codes])
pc <- suppressWarnings(psych::polychoric(X)$rho)
slots <- c(1, 3, 6, 8, 9, 10, 11)
lt <- c(.697, .900, .766, .698, .715, .808, .690, .676, .944, .751,
        .699, .697, .905, .923, .938, .708, .760, .796, .762, .809, .897)
P <- matrix(NA, 7, 7); k <- 1
for (i in 2:7) for (j in 1:(i - 1)) { P[i, j] <- lt[k]; k <- k + 1 }
diffs <- function(s) { e <- c(); for (i in 2:7) for (j in 1:(i - 1)) e <- c(e, pc[s[i], s[j]] - P[i, j]); e }
e0 <- diffs(slots); k <- 1
for (i in 2:7) for (j in 1:(i - 1)) {
    cat(sprintf("item%-2d-item%-2d published %.3f live %.3f diff %+.3f\n",
                slots[i], slots[j], P[i, j], pc[slots[i], slots[j]], e0[k])); k <- k + 1
}
hits0 <- sum(abs(e0) <= 0.01)
cat(sprintf("identity: %d/21 cells within 0.01 (median |diff| %.3f)\n", hits0, median(abs(e0))))
# single-swap robustness: replace any one published slot by any other column
alt <- c()
for (p in 1:7) for (cc in setdiff(1:12, slots[p])) {
    s <- slots; if (cc %in% s) s[match(cc, s)] <- slots[p]; s[p] <- cc
    alt <- c(alt, sum(abs(diffs(s)) <= 0.01))
}
cat(sprintf("best of %d single-swap alternatives: %d/21 cells within 0.01\n", length(alt), max(alt)))
if (max(alt) >= hits0) { cat("FAIL C: an alternative assignment fits Table 4 as well as the claimed one\n"); ok <- FALSE }

cat("\nNOTE: A and B together pin every code to its own source column and that column's\n",
    "header text, distinguishing all 12 items. What they do NOT establish is that the\n",
    "study's headers are themselves correct -- C is the independent check on that, and it\n",
    "reaches only the 7 items Table 4 reports (1,3,6,8,9,10,11). Five Table 4 cells\n",
    "(1-6, 6-9, 6-10, 9-10, 10-11) sit 0.06-0.15 ABOVE the live polychorics while the other\n",
    "16 agree to <=0.008; the paper's text value r(2,3)=0.973 is also higher than live.\n",
    "No single-swap reassignment explains those five (best alternative fits fewer cells),\n",
    "so they are reported as a discrepancy in the paper's table, not used as evidence.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
