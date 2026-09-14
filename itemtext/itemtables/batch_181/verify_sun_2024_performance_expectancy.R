# verify_sun_2024_performance_expectancy.R -- batch_181, Step 5b mapping check.
#
# Claim: PerformanceE1..PerformanceE3 carry the paper's "Performance expectation"
# items 1..3 (Sun et al. 2024, Heliyon, doi:10.1016/j.heliyon.2024.e36620,
# section 4.2 Measurement), code suffix n <-> the paper's list number n.
#
# What this script CAN check:
#   (A) code derivation: each live item is the deposit column of the same name
#       (mmc1.xlsx, joined on NO == id), not a neighbouring column;
#   (B) construct membership: the live three items reproduce the paper's Table 6
#       row for Performance expectation (Cronbach's alpha 0.981, AVE 0.963,
#       CR 0.987), and match that row better than any of the other five
#       constructs' published rows.
# What it CANNOT check: the order WITHIN the construct. alpha/AVE/CR are
# invariant to permuting the three items, the paper prints no per-item means or
# loadings, and the live per-item means are 5.11/5.12/5.11. The PE1..PE3 <->
# item 1..3 tie rests on the paper's numbering only. Status is PARTIAL.

suppressMessages({ library(irw); library(readxl) })

TABLE <- "sun_2024_performance_expectancy"
ITEMS <- c("PerformanceE1", "PerformanceE2", "PerformanceE3")

# Paper Table 6 (AVE, CR, alpha), hard-coded.
PUB <- rbind(INN = c(.927, .975, .961), PR = c(.916, .970, .963),
             PE  = c(.963, .987, .981), PV = c(.967, .984, .983),
             TTF = c(.968, .985, .983), U  = c(.952, .978, .975))
colnames(PUB) <- c("AVE", "CR", "alpha")
BLOCKS <- list(INN = c("innovation1","innovation2","innovation3"),
               PR  = c("Risk1","Risk2","Risk3"),
               PE  = ITEMS,
               PV  = c("Pricevalue1","Pricevalue2","Pricevalue3"),
               TTF = c("TTF1","TTF2","TTF3"),
               U   = c("Usage1","Usage2","Usage3"))

# ---- source deposit (Europe PMC supplementary zip; no email/UA sent) ----
get_xlsx <- function() {
  cache <- file.path("itemtext", ".cache", TABLE, "mmc1.xlsx")
  for (p in c(cache, file.path(".cache", TABLE, "mmc1.xlsx"))) if (file.exists(p)) return(p)
  zf <- tempfile(fileext = ".zip"); dir <- tempfile()
  download.file("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11385760/supplementaryFiles",
                zf, mode = "wb", quiet = TRUE)
  unzip(zf, files = "mmc1.xlsx", exdir = dir)
  file.path(dir, "mmc1.xlsx")
}
src <- as.data.frame(read_excel(get_xlsx()))

# ---- live table ----
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
j <- merge(w, src, by.x = "id", by.y = "NO", suffixes = c(".live", ".src"))
cat(sprintf("(A) live ids %d, source rows %d, joined %d\n", nrow(w), nrow(src), nrow(j)))
okA <- nrow(j) == nrow(src)
cat(sprintf("    %-14s %s\n", "live \\ source", paste(sprintf("%14s", ITEMS), collapse = "")))
for (a in ITEMS) {
  agr <- sapply(ITEMS, function(b) mean(j[[paste0(a, ".live")]] == j[[paste0(b, ".src")]]))
  cat(sprintf("    %-14s %s\n", a, paste(sprintf("%13.1f%%", 100 * agr), collapse = "")))
  okA <- okA && agr[a] == 1
}

# ---- (B) construct-level reliability from the LIVE items ----
alpha <- function(m) { k <- ncol(m); k / (k - 1) * (1 - sum(apply(m, 2, var)) / var(rowSums(m))) }
plsA <- function(m) {                   # PLS mode-A outer loadings (SmartPLS default)
  z <- scale(m); wt <- rep(1, ncol(m))
  for (it in 1:200) { s <- scale(z %*% wt); wt <- as.vector(cor(z, s)) }
  as.vector(cor(z, s))
}
live <- as.matrix(w[, ITEMS])
l <- plsA(live)
obs <- c(AVE = mean(l^2), CR = sum(l)^2 / (sum(l)^2 + sum(1 - l^2)), alpha = alpha(live))
cat("\n(B) live PerformanceE block vs paper Table 6 rows\n")
cat(sprintf("    observed          AVE %.3f  CR %.3f  alpha %.3f\n", obs[1], obs[2], obs[3]))
dist <- apply(PUB, 1, function(p) max(abs(p - obs)))
for (r in rownames(PUB))
  cat(sprintf("    published %-4s    AVE %.3f  CR %.3f  alpha %.3f   max|diff| %.4f\n",
              r, PUB[r, 1], PUB[r, 2], PUB[r, 3], dist[r]))
best <- names(which.min(dist))
cat(sprintf("    best-matching published row: %s (max|diff| %.4f); runner-up %s (%.4f)\n",
            best, min(dist), names(sort(dist))[2], sort(dist)[2]))
okB <- best == "PE" && dist["PE"] <= 0.002

cat("\nper-item live means:", paste(sprintf("%s %.3f", ITEMS, colMeans(live)), collapse = ", "), "\n")
cat("NOT ESTABLISHED: order within the construct. alpha/AVE/CR are permutation-invariant,\n",
    "no per-item statistics are published, and the three live means span only 0.018, so\n",
    "PerformanceE1..3 <-> paper items 1..3 rests on the paper's list numbering alone.\n", sep = "")

cat(sprintf("\n(A) code = same-named source column: %s; (B) construct = Performance expectation: %s\n",
            okA, okB))
cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
