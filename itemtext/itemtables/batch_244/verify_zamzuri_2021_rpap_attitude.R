# verify_zamzuri_2021_rpap_attitude.R
#
# Claim being re-run: live item E<n> is the item Zamzuri et al. (2021) PLOS ONE
# 16(8):e0256636 Table 2 prints against code E<n> (rows 13-22, Attitude domain),
# and therefore carries that row's wording.
#
# Route: per-item descriptive statistics (Step 5b route 1). Table 2 prints each
# item's Mean (SD) for the same N = 253 sample the IRW table holds (Sheet1 of S1
# Data; data/zamzuri_2021_rpap.py melts columns E1..E10 by name). A swap of any two
# items' text would pair a row's printed M (SD) with the wrong live column.
#
# What this does NOT establish on its own: E7 and E9 share a printed mean of 7.58;
# they are separated only by SD (0.75 vs 0.74), a 0.01 margin at the paper's
# precision. The printed code E7/E9 beside each row is the primary tie
# (paper_explicit); this route corroborates it rather than replacing it.

suppressMessages(library(irw))

TABLE <- "zamzuri_2021_rpap_attitude"
ITEMS <- paste0("E", 1:10)

# Table 2, Mean (SD), rows 13-22 (codes E1-E10), transcribed from the article XML.
PUB_M  <- c(7.68, 6.13, 7.84, 6.32, 7.31, 7.44, 7.58, 7.21, 7.58, 7.12)
PUB_SD <- c(0.76, 1.74, 0.50, 1.75, 1.30, 1.21, 0.75, 1.18, 0.74, 1.16)
names(PUB_M) <- names(PUB_SD) <- ITEMS

d <- as.data.frame(irw::irw_fetch(TABLE))
obs_m  <- tapply(d$resp, d$item, mean)[ITEMS]
obs_sd <- tapply(d$resp, d$item, sd)[ITEMS]

cat(sprintf("%-4s %8s %8s %8s %8s\n", "item", "pub_M", "obs_M", "pub_SD", "obs_SD"))
for (i in ITEMS)
    cat(sprintf("%-4s %8.2f %8.4f %8.2f %8.4f\n", i, PUB_M[i], obs_m[i], PUB_SD[i], obs_sd[i]))

# Match on the paper's 2-dp precision: both M and SD must round-match (tol 0.006
# allows half-up vs half-even rounding of e.g. 7.5850).
TOL <- 0.006
ok <- abs(obs_m - PUB_M) <= TOL & abs(obs_sd - PUB_SD) <= TOL
cat(sprintf("\n%d/%d items match published M and SD within %.3f\n", sum(ok), length(ok), TOL))

# Uniqueness: for each live item, how many published rows does it match? A
# mapping is pinned only if each live column matches exactly one published row.
cnt <- sapply(ITEMS, function(i) sum(abs(obs_m[i] - PUB_M) <= TOL & abs(obs_sd[i] - PUB_SD) <= TOL))
cat("published rows matched per live item:", paste(ITEMS, cnt, sep = "=", collapse = " "), "\n")
cat("Note: E7 vs E9 are separated by SD alone (0.75 vs 0.74); every other pair differs in mean.\n")

cat(if (all(ok) && all(cnt == 1)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
