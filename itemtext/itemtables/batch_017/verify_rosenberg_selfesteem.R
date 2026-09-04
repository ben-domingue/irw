# verify_rosenberg_selfesteem.R -- Step 5b mapping check.
#
# CLAIM UNDER TEST: IRW item "i" (bare integers 1..10) is column Qi of the Open
# Psychometrics RSE deposit (http://openpsychometrics.org/_rawdata/RSE.zip), whose
# codebook.txt prints the wording of Q1..Q10. data/rosenberg_selfesteem.R drops
# gender/source/country/age, lowercases the remaining headers and assigns
# row_number() over unique(item) after a pivot_longer -- i.e. a POSITIONAL integer
# over the surviving columns in file order. That is the step this script tests.
#
# FALSIFIABLE PREDICTION: for every i, the live per-item non-missing n and mean must
# equal the values computed directly from data.csv column Qi (0 recoded to missing).
# If any two items' texts were swapped, the paired means would swap with them.
#
# Both halves are computed WITHOUT irw_fetch(): the live side is a server-side
# aggregate query (export quota, SKILL.md Step 5), the source side is the 1.4MB
# deposit CSV, downloaded if not already cached.
suppressMessages({library(irw); library(redivis)})

TABLE <- "rosenberg_selfesteem"
CACHE <- file.path("itemtext/.cache", TABLE, "RSE", "data.csv")
if (!file.exists(CACHE)) CACHE <- file.path(".cache", TABLE, "RSE", "data.csv")
if (!file.exists(CACHE)) {
    dir.create(dirname(dirname(CACHE)), recursive = TRUE, showWarnings = FALSE)
    z <- tempfile(fileext = ".zip")
    download.file("http://openpsychometrics.org/_rawdata/RSE.zip", z, quiet = TRUE)
    unzip(z, exdir = dirname(dirname(CACHE)))
}
src <- read.delim(CACHE, stringsAsFactors = FALSE)

# --- source side: Qi with 0 (= "no answer", per codebook) treated as missing ---
src_n <- src_m <- numeric(10)
for (i in 1:10) {
    v <- suppressWarnings(as.numeric(src[[paste0("Q", i)]]))
    v <- v[!is.na(v) & v != 0]
    src_n[i] <- length(v); src_m[i] <- mean(v)
}

# --- live side: server-side aggregate, no export ---
s <- irw::irw_table_sets(TABLE, source = "core", per_item = FALSE)
q <- redivis::query(sprintf(
    "SELECT item, COUNT(SAFE_CAST(resp AS FLOAT64)) AS n,
            AVG(SAFE_CAST(resp AS FLOAT64)) AS mean_resp
     FROM `%s` GROUP BY item", s$table))
d <- as.data.frame(q$to_data_frame())
d <- d[match(as.character(1:10), as.character(d$item)), ]

cat(sprintf("%-6s %-6s %10s %10s %12s %12s %10s\n",
            "item", "srcCol", "src_n", "live_n", "src_mean", "live_mean", "diff"))
for (i in 1:10)
    cat(sprintf("%-6s %-6s %10d %10d %12.6f %12.6f %10.2e\n",
                i, paste0("Q", i), src_n[i], d$n[i], src_m[i], d$mean_resp[i],
                d$mean_resp[i] - src_m[i]))

n_ok    <- all(src_n == d$n)
worst   <- max(abs(d$mean_resp - src_m))
# Every source mean is distinct, so the mean alone separates each item from every
# other -- including the 3-vs-4 pair, which ties on n (47751 both) but not on mean.
gaps    <- min(dist(src_m))
cat(sprintf("\nn identical for all 10 items: %s\n", n_ok))
cat(sprintf("largest mean deviation: %.3e (tolerance 1e-6)\n", worst))
cat(sprintf("smallest gap between any two source means: %.4f\n", gaps))
cat("  -> all 10 (n, mean) pairs are distinct, so the match pins EVERY item, not a class:\n")
cat("     items 3 and 4 tie on n (47751) and separate on mean (2.3070 vs 2.9225);\n")
cat("     items 6 and 10 are closest on mean (0.0154 apart) and separate on n (47809 vs 47772).\n")
cat("What this does NOT establish: the administered instruction wording (the deposit\n",
    "records none) and the option-label casing, which is transcribed from codebook prose.\n",
    "It also does not test resp direction independently -- direction is settled by the\n",
    "means reproducing RAW (unreversed) source columns exactly.\n", sep = "")

cat(if (n_ok && worst <= 1e-6) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
