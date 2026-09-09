# verify_komura_2026_mdmt_ethical.R
#
# Step 5b evidence, re-runnable.
#
# WHAT IS BEING VERIFIED. The IRW item codes mdmt_ethical_1..4 are the verbatim
# column names of the study's S3 File workbook (data/komura_2026_godspeed.py
# melts by name -- no positional step), so the code<->source-column tie needs no
# inference. The words come from S2 File, which lists, under the heading
# "Ethical:", a numbered list 1. Ethical / 2. Respectable / 3. Has integrity /
# 4. Honest/upright. The claim under test here is the BLOCK claim: that these
# four columns are the MDMT Ethicality subscale and not one of the study's three
# sibling MDMT blocks (Reliability, Capability, Sincerity), each of which is also
# four items on the same 0-7 scale and would be indistinguishable by any set
# check. Table 2 of the paper publishes each subscale's mean (SD) separately for
# the three AI-strategy conditions, so it is a falsifiable prediction: summing
# the four live items per respondent and averaging within cov_aitype must
# reproduce the Ethicality row and NOT the other three rows.
#
# Source: Komura & Yamada (2026) PLOS ONE 10.1371/journal.pone.0340449, Table 2
# (CC BY 4.0); supplements S2 File (.s002) and S3 File (.s003).

suppressMessages(library(irw))

TABLE <- "komura_2026_mdmt_ethical"
TOL   <- 0.02   # paper rounds to 2 dp

# Paper Table 2, "MDMT trust scale results by AI strategy condition".
# rows = trust dimension, cols = Vertical / Horizontal / Random.
PUB_MEAN <- rbind(
  Reliability = c(4.76, 4.08, 4.09),
  Capability  = c(4.81, 4.00, 4.22),
  Ethicality  = c(4.71, 4.21, 4.11),
  Sincerity   = c(4.92, 4.32, 4.31)
)
PUB_SD <- rbind(
  Reliability = c(1.13, 1.37, 1.30),
  Capability  = c(1.26, 1.52, 1.31),
  Ethicality  = c(1.22, 1.35, 1.30),
  Sincerity   = c(1.08, 1.27, 1.05)
)
COND <- c("vertical", "horizontal", "random")
colnames(PUB_MEAN) <- COND; colnames(PUB_SD) <- COND

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

# per-respondent subscale score = mean of the four ethical items
d <- as.data.frame(d)
m <- tapply(d$resp, list(d$id, d$item), function(x) x[1])
cols <- paste0("mdmt_ethical_", 1:4)
stopifnot(all(cols %in% colnames(m)))
w <- data.frame(id = rownames(m), score = rowMeans(m[, cols]),
                stringsAsFactors = FALSE)

cond <- unique(d[, c("id", "cov_aitype")])
w <- merge(w, cond, by = "id")

# Paper Table 1 puts the Random (Control) condition at n = 46, while the S3 File
# labels only 40 rows "random" and 6 rows "unknown" (148 = 50 + 52 + 46). The 6
# unlabelled rows are therefore part of the control arm; pool them, or every
# Random cell misses by ~0.15 for all four subscales at once.
w$cond <- ifelse(w$cov_aitype %in% c("random", "unknown"), "random", w$cov_aitype)

obs_m <- tapply(w$score, w$cond, mean)[COND]
obs_s <- tapply(w$score, w$cond, sd)[COND]
obs_n <- tapply(w$score, w$cond, length)[COND]

cat("Observed subscale score from the four shipped items (mean of 1..4 per respondent):\n")
cat(sprintf("%-12s %6s %8s %8s\n", "condition", "n", "mean", "sd"))
for (c_ in COND)
  cat(sprintf("%-12s %6d %8.2f %8.2f\n", c_, obs_n[[c_]], obs_m[[c_]], obs_s[[c_]]))

cat("\nAgainst every row of paper Table 2 (max |observed - published| over the 3 conditions):\n")
cat(sprintf("%-12s %26s %10s %10s\n", "Table 2 row", "published means (V/H/R)",
            "max|d| M", "max|d| SD"))
dev_m <- dev_s <- setNames(numeric(nrow(PUB_MEAN)), rownames(PUB_MEAN))
for (r in rownames(PUB_MEAN)) {
  dev_m[r] <- max(abs(obs_m - PUB_MEAN[r, ]))
  dev_s[r] <- max(abs(obs_s - PUB_SD[r, ]))
  cat(sprintf("%-12s %26s %10.3f %10.3f\n", r,
              paste(sprintf("%.2f", PUB_MEAN[r, ]), collapse = " / "),
              dev_m[r], dev_s[r]))
}

best <- names(which.min(dev_m))
cat(sprintf("\nclosest Table 2 row: %s (max deviation %.3f, tolerance %.2f)\n",
            best, dev_m[best], TOL))
cat(sprintf("next closest: %s at %.3f\n",
            names(sort(dev_m))[2], sort(dev_m)[2]))

# What this does NOT establish.
cat("\nNOTE: this pins the BLOCK (these four columns are the Ethicality subscale,\n",
    "separated from Reliability/Capability/Sincerity by the Table 2 means and SDs).\n",
    "It does NOT order the four items within the block: 'Ethical', 'Respectable',\n",
    "'Has integrity' and 'Honest/upright' share one 0-7 scale, are near-synonyms, and\n",
    "the paper publishes no per-item statistic, so no data route can separate them.\n",
    "That ordering rests on the S2 File's own numbered list matching the S3 File's\n",
    "column suffixes _1.._4 -- hence status PARTIAL, not VERIFIED.\n", sep = "")

pass <- (dev_m[best] <= TOL) && (best == "Ethicality") && (dev_s[best] <= TOL)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
