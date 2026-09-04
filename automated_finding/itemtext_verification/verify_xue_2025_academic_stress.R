# verify_xue_2025_academic_stress.R  --  Step 5b mapping check (backfill, 2026-09-03)
#
# CLAIM UNDER TEST: the 20 stems S3 File of Xue et al. (2025, PLOS ONE,
# 10.1371/journal.pone.0338956) labels (AS1)..(AS20) are attached to the right
# item codes in the live IRW table.
#
# WHY THE CLAIM IS NOT FREE. data/xue_2025_academic_procrastination.py builds all
# three xue_2025_* tables from S1 Data, whose item columns are Q8_1-19, Q9_1-20,
# Q10_1-20. The script renames Q9_i -> AS_i positionally. S3 File does label its
# items AS1..AS20, but the DATA columns carry no text, so the tie between column
# and code is an ORDER inference. Step 5b's "explicit code labels in the paper"
# exemption does NOT apply, and the provenance note's "explicit rather than
# order-inferred" is overstated.
#
# QUOTA. The live table is 11,580 rows (579 x 20), the smallest possible whole
# object; the correlation matrix that routes 5-8 need cannot be got from a
# server-side aggregate, so one irw_fetch is unavoidable and is negligible
# against the 200GB/30-day export cap. The source-side numbers are recomputed
# from the public S1 Data XLSX, not from Redivis.
#
# WHAT IS CHECKED
#   A. Block boundary. Live AS_i must equal source Q9_i (the columns the
#      spreadsheet's own banner labels "Academic Stress"), not the AP or CSS
#      block, and not a shifted window. Cross-checked against the paper's
#      published scale-level alpha and KMO.
#   B. Within-block alignment. Cyclic realignment test: the shipped identity
#      alignment must uniquely maximise a-priori semantic-twin correlations and
#      be the only one putting the sole non-academic stem (AS20, romance) on the
#      least-endorsed column.
#
# NOT CHECKED, and PARTIAL is the status because of it: local transpositions of
# semantically similar neighbours (AS4/AS5, AS13/AS16, AS3/AS19, AS2/AS6).

suppressMessages(library(irw))

TABLE <- "xue_2025_academic_stress"

# Published in the paper's Results for the academic-pressure scale.
PUB_ALPHA <- 0.917
PUB_KMO   <- 0.932

# ---------------------------------------------------------------- live data
d <- as.data.frame(irw::irw_fetch(TABLE))[, c("id", "item", "resp")]
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp[.]", "", names(w))
m <- as.matrix(w[, paste0("AS", 1:20)])
storage.mode(m) <- "numeric"
cat(sprintf("live: %d respondents x %d items\n", nrow(m), ncol(m)))

alpha <- function(x) {
    k <- ncol(x)
    k / (k - 1) * (1 - sum(apply(x, 2, var)) / var(rowSums(x)))
}
kmo <- function(x) {
    R <- cor(x); P <- -cov2cor(solve(R)); lt <- lower.tri(R)
    sum(R[lt]^2) / (sum(R[lt]^2) + sum(P[lt]^2))
}

a_live <- alpha(m); k_live <- kmo(m)
cat(sprintf("A. scale-level: alpha %.4f vs published %.3f | KMO %.4f vs published %.3f\n",
            a_live, PUB_ALPHA, k_live, PUB_KMO))
okA <- abs(round(a_live, 3) - PUB_ALPHA) < 1e-9 && abs(round(k_live, 3) - PUB_KMO) < 1e-9

# ------------------------------------------------- source-side block boundary
# Optional: needs the public S1 Data XLSX + readxl. Skipped offline.
okB <- NA
src <- tryCatch({
    f <- file.path(tempdir(), "pone.0338956.s001.xlsx")
    if (!file.exists(f))
        utils::download.file(paste0("https://journals.plos.org/plosone/article/file",
                                    "?type=supplementary&id=10.1371/journal.pone.0338956.s001"),
                             f, quiet = TRUE, mode = "wb")
    raw <- suppressMessages(as.data.frame(readxl::read_excel(f, col_names = FALSE, .name_repair = "minimal")))
    hdr <- as.character(unlist(raw[2, ]))
    body <- raw[-(1:2), ]; names(body) <- hdr
    body <- body[!is.na(body$index), ]
    body[] <- lapply(body, function(x) suppressWarnings(as.numeric(x)))
    list(hdr = hdr, d = body,
         banner = as.character(unlist(raw[1, ])))
}, error = function(e) NULL)

if (is.null(src)) {
    cat("B. source XLSX unavailable (offline?) -- block-boundary leg skipped\n")
} else {
    b <- src$banner
    cat(sprintf("B. S1 banner: col %d = %s (%s) | col %d = %s (%s) | col %d = %s (%s)\n",
                9,  src$hdr[9],  b[9], 28, src$hdr[28], b[28], 48, src$hdr[48], b[48]))
    cat(sprintf("%-6s %-6s %6s %9s %9s %9s\n", "code", "src", "n", "live_mean", "src_mean", "diff"))
    worst <- 0
    for (i in 1:20) {
        s <- src$d[[paste0("Q9_", i)]]; s <- s[!is.na(s)]
        lm_ <- mean(m[, i]); sm <- mean(s)
        worst <- max(worst, abs(lm_ - sm))
        cat(sprintf("%-6s %-6s %6d %9.4f %9.4f %9.5f\n",
                    paste0("AS", i), paste0("Q9_", i), length(s), lm_, sm, lm_ - sm))
    }
    cat(sprintf("   largest live-vs-Q9 per-item mean deviation: %.6f\n", worst))
    # off-by-one windows must NOT reproduce the published alpha
    i0 <- match("Q9_1", src$hdr)
    for (sh in c(-1, 0, 1)) {
        cols <- src$hdr[(i0 + sh):(i0 + sh + 19)]
        x <- as.matrix(src$d[, cols]); x <- x[complete.cases(x), ]
        cat(sprintf("   window %+d (%s..%s): alpha %.4f%s\n", sh, cols[1], cols[20],
                    alpha(x), if (sh == 0) "  <- shipped" else ""))
    }
    okB <- worst < 1e-9
}

# ---------------------------------------------- within-block cyclic alignment
# A-priori semantic twins, read off the S3 File stems BEFORE looking at the data:
#   AS13/AS16 school environment & adaptation; AS4/AS5 exams & workload;
#   AS2/AS6 employability; AS9/AS10 self-expectation vs future society;
#   AS3/AS11 parental expectation & comparison.
TWINS <- list(c(13, 16), c(4, 5), c(2, 6), c(9, 10), c(3, 11))
R <- cor(m)
lowest <- which.min(colMeans(m))
score <- sapply(0:19, function(s)
    mean(sapply(TWINS, function(p)
        R[((p[1] - 1 + s) %% 20) + 1, ((p[2] - 1 + s) %% 20) + 1])))
romance_col <- sapply(0:19, function(s) ((20 - 1 + s) %% 20) + 1)

cat("\nC. cyclic realignment of text onto columns (shift 0 = as shipped)\n")
ord <- order(-score)
for (j in ord[1:5])
    cat(sprintf("   shift %+3d  twin_r %.3f  romance stem lands on AS%-2d  romance=least-endorsed: %s%s\n",
                j - 1, score[j], romance_col[j],
                romance_col[j] == lowest, if (j - 1 == 0) "   <- shipped" else ""))
cat(sprintf("   least-endorsed column is AS%d (mean %.2f, %.1f%% at floor); AS20 mean inter-item r %.3f\n",
            lowest, min(colMeans(m)), 100 * mean(m[, lowest] == 1),
            mean(R[20, -20])))
okC <- which.max(score) == 1 && romance_col[1] == lowest && score[1] - max(score[-1]) > 0.05

cat("\nDoes NOT establish: local transpositions of semantically similar neighbours\n",
    "(AS4/AS5 r=", sprintf("%.3f", R[4, 5]), ", AS13/AS16 r=", sprintf("%.3f", R[13, 16]),
    ", AS3/AS19, AS2/AS6 r=", sprintf("%.3f", R[2, 6]), ") are invisible to every route\n",
    "available here; the paper publishes no per-item statistics, no item-to-dimension\n",
    "assignment, and the Chinese instrument (Liu 2015) is not recoverable. Status PARTIAL.\n", sep = "")

pass <- okA && okC && (is.na(okB) || okB)
cat(if (isTRUE(pass)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
