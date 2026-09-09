# Verification for paampsmartsud_saba_2023_ders (#1945, batch_201).
#
# The deposit ships DERS_1_POST..DERS_37_POST as bare codes with no wording.
# Wording comes from Gratz & Roemer (2004) Table III, which numbers items in the
# ORIGINAL 41-item pool. The shipped mapping assumes the deposit uses the
# published DERS-36 numbering, i.e. the pool with items 2, 11, 13, 18 and 36
# dropped and the survivors renumbered 1..36 in ascending order.
#
# Three routes test that assumption. Read route 3's limit before trusting this
# as more than it is: routes 1-2 pin the reverse/non-reverse CLASS and the
# unscored column exactly, route 3 pins each item to a SUBSCALE, and nothing
# here separates two same-subscale, same-polarity items from each other.
suppressMessages({ library(irw) })
ART <- ".cache/paampsmartsud_saba_2023/gratz_roemer_2004.txt"
DEP <- ".cache/paampsmartsud_saba_2023/amps_eval.csv"
CANON_REV <- c(1, 2, 6, 7, 8, 10, 17, 20, 22, 24, 34)
set.seed(1945)

clean <- function(s) {
    s <- gsub("ﬁ", "fi", s); s <- gsub("ﬂ", "fl", s); s <- gsub("’", "'", s)
    trimws(gsub("\\s+", " ", s))
}

## parse Table III, keeping the factor each item was listed under
ln  <- readLines(ART, warn = FALSE)
i0  <- grep("Table III\\. Items Composing the Six DERS Factors", ln)
i1  <- grep("^Note\\..*reverse-scored", ln); i1 <- i1[i1 > i0][1]
blk <- ln[(i0 + 1):(i1 - 1)]
pool <- integer(0); text <- character(0); rev <- logical(0); fac <- integer(0)
cur <- NA_integer_
for (l in blk) {
    f <- regmatches(l, regexec("^\\s*([1-6]):", l))[[1]]
    if (length(f) == 2) cur <- as.integer(f[2])
    m <- regmatches(l, regexec("([0-9]{1,2})\\)\\s*(.+?)\\s*$", l))[[1]]
    if (length(m) != 3) next
    tx <- clean(m[3]); isrev <- grepl("\\(r\\)$", tx)
    pool <- c(pool, as.integer(m[2])); rev <- c(rev, isrev); fac <- c(fac, cur)
    text <- c(text, clean(sub("\\s*\\(r\\)$", "", tx)))
}
o <- order(pool); pool <- pool[o]; text <- text[o]; rev <- rev[o]; fac <- fac[o]
stopifnot(length(pool) == 36, !any(is.na(fac)))

cat("=== Route 1: the renumbering must reproduce the canonical reverse set ===\n")
cat("  pool numbers dropped:", paste(setdiff(1:41, pool), collapse = ", "), "\n")
cat("  reverse positions after renumbering:", paste(which(rev), collapse = ", "), "\n")
cat("  canonical DERS-36 reverse set:      ", paste(CANON_REV, collapse = ", "), "\n")
r1 <- identical(as.integer(which(rev)), as.integer(CANON_REV))
cat("  ", if (r1) "PASS -- all 11 land exactly" else "FAIL", "\n\n", sep = "")

cat("=== Route 2: the deposit's own DERS_SUM_POST ===\n")
x <- read.csv(DEP, stringsAsFactors = FALSE, check.names = FALSE)
cols <- paste0("DERS_", 1:37, "_POST")
m37 <- apply(as.matrix(x[, cols]), 2, as.numeric)
s   <- as.numeric(x$DERS_SUM_POST)
ok  <- !is.na(s) & rowSums(is.na(m37)) == 0
sc  <- function(mat, drop) { mm <- mat[, -drop, drop = FALSE]
    for (j in CANON_REV) mm[, j] <- 6 - mm[, j]; rowSums(mm) }
hit <- sapply(1:37, function(j) sum(sc(m37[ok, ], j) == s[ok]))
cat(sprintf("  drop col 37 + canonical reverses: %d of %d rows\n", hit[37], sum(ok)))
cat(sprintf("  best of the other 36 drops:       %d of %d rows\n", max(hit[-37]), sum(ok)))
cat(sprintf("  no reverses at all:               %d of %d rows\n",
            sum(rowSums(m37[ok, -37]) == s[ok]), sum(ok)))
r2 <- hit[37] == sum(ok) && max(hit[-37]) < sum(ok)
cat("  ", if (r2) "PASS -- unique and exact" else "FAIL", "\n\n", sep = "")

cat("=== Route 3: do the six subscales cohere as grouped? ===\n")
M <- m37[ok, 1:36]
for (j in CANON_REV) M[, j] <- 6 - M[, j]          # score all in one direction
C <- cor(M)
grp_mean <- function(g) {
    v <- c()
    for (k in unique(g)) { idx <- which(g == k)
        if (length(idx) > 1) v <- c(v, mean(C[idx, idx][upper.tri(diag(length(idx)))])) }
    mean(v)
}
obs <- grp_mean(fac)
null <- replicate(2000, grp_mean(sample(fac)))
cat(sprintf("  mean within-subscale r as grouped by Table III: %.3f\n", obs))
cat(sprintf("  same-sized random groupings (2000 draws):      mean %.3f, max %.3f\n",
            mean(null), max(null)))
cat(sprintf("  permutation p = %.4f\n", (1 + sum(null >= obs)) / (1 + length(null))))
r3 <- obs > max(null)
cat("  ", if (r3) "PASS -- exceeds every random grouping" else "does not exceed the null",
    "\n\n", sep = "")

cat("=== What this does NOT establish ===\n")
cat("  Routes 1-2 fix the 11 reverse positions and the unscored column; route 3\n")
cat("  assigns each item to a subscale. Within one subscale and one polarity the\n")
cat("  items are still interchangeable on the evidence, so the individual\n")
cat("  assignment rests on the monotone renumbering, not on the data. Recorded\n")
cat("  as PARTIAL for that reason.\n")
stopifnot(r1, r2)

cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")
