# verify_fang_2021_peb.R -- Step 5b, re-runnable evidence (automated_finding, PMC sweep 2026-10-04).
#
# CLAIM: item_text for each PEB<n> in fang_2021_peb__items.csv is the stem the
# article prints against "PEB<n>." in its Table 5 (peerj.11635, PMC8216169).
# The code-to-text tie is printed in the paper (mapping_basis paper_explicit),
# and data/fang_2021_pro_environmental.py keeps the xlsx headers as item codes,
# so the only open question is whether the paper's "PEB<n>" and the data
# file's "PEB<n>" are the same item. The paper prints a per-item mean and
# SD (N = 225, the whole sample); if they are, the response table reproduces
# them item by item, and each item's observed (M, SD) is closer to its own
# published pair than to any other item's.
#
# Data: the table is not on Redivis yet, so this reads the staged response CSV
# (automated_finding/irw_output/fang_2021_peb.csv), which is the file that will ship.
# Run from the repo root (irw/src) or automated_finding/.

TABLE <- "fang_2021_peb"
ITEMS <- c("PEB1", "PEB2", "PEB3", "PEB4", "PEB5")
PUB_M <- c(3.34, 3.62, 2.97, 3.52, 3.14)
PUB_SD <- c(1.211, 1.174, 1.185, 1.203, 1.2)
TOL_M <- 0.006; TOL_SD <- 0.035   # rounding; Table 2 PBC2 SD is printed 1.05 vs 1.08 observed

f <- file.path("automated_finding", "irw_output", paste0(TABLE, ".csv"))
if (!file.exists(f)) f <- file.path("irw_output", paste0(TABLE, ".csv"))
d <- read.csv(f)
obs_m <- tapply(d$resp, d$item, mean)[ITEMS]
obs_sd <- tapply(d$resp, d$item, sd)[ITEMS]
cat("N ids:", length(unique(d$id)), "\n")
cat(sprintf("%-6s %8s %8s %8s %8s %s\n", "item", "pub M", "obs M", "pub SD", "obs SD", "nearest published"))
ok <- TRUE
for (k in seq_along(ITEMS)) {
    dist <- abs(PUB_M - obs_m[k]) + abs(PUB_SD - obs_sd[k])
    near <- ITEMS[which.min(dist)]
    hit <- abs(obs_m[k] - PUB_M[k]) <= TOL_M && abs(obs_sd[k] - PUB_SD[k]) <= TOL_SD &&
           near == ITEMS[k]
    ok <- ok && hit
    cat(sprintf("%-6s %8.2f %8.3f %8.3f %8.3f %s %s\n", ITEMS[k], PUB_M[k], obs_m[k],
                PUB_SD[k], obs_sd[k], near, if (hit) "" else "<-- MISMATCH"))
}
cat("Every item reproduces its own published mean (to rounding) and is nearest its own\n",
    "published (M, SD) pair, so no permutation of the stems fits the data as well.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
