# verify_komura_2026_gqs_perceived_safety.R
#
# CLAIM UNDER TEST (mapping_basis = paper_explicit):
#   The S2 File's numbered "Perceived Safety" block --
#     1. Anxious <-> Calm
#     2. Calm <-> Agitated        (reversed item)
#     3. Peaceful <-> Surprised   (reversed item)
#   maps onto the live item codes gqs_perceived_safety_1..3, with resp 1 = the
#   LEFT adjective and resp 5 = the RIGHT adjective (i.e. stored raw, not
#   pre-reversed).
#
# WHAT WOULD BREAK IT: if item_text for item 1 were swapped with item 2 or 3,
# the wrong pair of items would carry S2's "(reversed item)" flag, and
# reverse-scoring them would no longer reproduce the paper's published Table 3
# Perceived Safety means. That is the falsifiable prediction tested below.
#
# Published values hard-coded from Komura & Yamada (2026) PLOS ONE
# 10.1371/journal.pone.0340449, Table 3, "Perceived Safety" row, and Table 1
# condition n's. Only the live IRW data is fetched.

suppressMessages(library(irw))

TABLE <- "komura_2026_gqs_perceived_safety"
ITEMS <- paste0("gqs_perceived_safety_", 1:3)

# Table 3, Perceived Safety row: M (SD) by AI-strategy condition
PUB   <- list(Vertical = c(3.93, 0.73, 52),
              Horizontal = c(3.64, 0.65, 50),
              Random = c(3.61, 0.77, 46))
PUB_F <- 3.06   # F(2,145) = 3.06, p = 0.050
TOL   <- 0.02

d <- irw::irw_fetch(TABLE)
d$item <- as.character(d$item)
w <- data.frame(id = sort(unique(d$id)), stringsAsFactors = FALSE)
for (it in ITEMS) {
    s <- d[d$item == it, c("id", "resp")]
    names(s)[2] <- it
    w <- merge(w, s, by = "id", all.x = TRUE)
}
cov <- unique(d[, c("id", "cov_aitype")])
w <- merge(w, cov, by = "id")

# Paper's Table 1 gives Random n = 46; the file carries 40 'random' + 6 'unknown'
w$cond <- ifelse(w$cov_aitype == "vertical", "Vertical",
          ifelse(w$cov_aitype == "horizontal", "Horizontal", "Random"))

M <- as.matrix(w[, ITEMS])

# ---- ROUTE 3: published subscale means, under the two rival readings ---------
rev_ok  <- cbind(M[, 1], 6 - M[, 2], 6 - M[, 3])   # S2's flags: items 2,3 reversed
raw_all <- M                                        # rival: nothing reversed
score_ok  <- rowMeans(rev_ok)
score_raw <- rowMeans(raw_all)

cat("Route 3 -- paper Table 3 'Perceived Safety' vs live subscale score\n")
cat(sprintf("%-11s %4s | %11s %11s | %11s\n",
            "condition", "n", "published", "obs(2,3 rev)", "obs(all raw)"))
worst <- 0
for (cn in names(PUB)) {
    k <- w$cond == cn
    p <- PUB[[cn]]
    o1 <- mean(score_ok[k]); s1 <- sd(score_ok[k]); o2 <- mean(score_raw[k])
    cat(sprintf("%-11s %4d | %5.2f (%.2f) | %5.3f (%.3f) | %5.3f\n",
                cn, sum(k), p[1], p[2], o1, s1, o2))
    if (sum(k) != p[3]) cat("   WARNING: n mismatch, published n =", p[3], "\n")
    worst <- max(worst, abs(o1 - p[1]), abs(s1 - p[2]))
}
f_obs <- summary(aov(score_ok ~ cond, data = w))[[1]][["F value"]][1]
cat(sprintf("ANOVA F(2,145): published %.2f, observed %.3f\n", PUB_F, f_obs))
cat(sprintf("largest deviation on the reversed reading: %.4f (tolerance %.2f)\n",
            worst, TOL))
cat(sprintf("largest deviation on the all-raw reading:  %.4f\n",
            max(abs(sapply(names(PUB),
                function(cn) mean(score_raw[w$cond == cn]) - PUB[[cn]][1])))))

# ---- Direction check: item 1 must be the UNREVERSED (positive-pole) item -----
mu <- colMeans(M)
cat("\nDirection -- per-item means (raw, as stored)\n")
for (i in 1:3) cat(sprintf("  %-24s %.3f\n", ITEMS[i], mu[i]))
cat("  item 1 is the only item whose high end is the safe pole ('Calm'),\n")
cat("  and it is the only one above the scale midpoint.\n")
dir_ok <- mu[1] > 3 && mu[2] < 3 && mu[3] < 3

# ---- What this does NOT establish -------------------------------------------
cat("\nNOT established -- items 2 and 3 are not separated from each other:\n")
cc <- cor(M)
cat(sprintf("  r(item1,item2) = %+.3f   r(item1,item3) = %+.3f   (difference %.3f)\n",
            cc[1, 2], cc[1, 3], abs(cc[1, 2] - cc[1, 3])))
cat("  Both are reversed, both are negatively keyed against item 1 by a\n")
cat("  near-identical amount, and the paper publishes no per-item statistics.\n")
cat("  Their order rests on S2 File's own 1/2/3 numbering matching the S3\n")
cat("  workbook's column suffixes. Hence PARTIAL, not VERIFIED.\n\n")

cat(if (worst <= TOL && dir_ok && abs(f_obs - PUB_F) < 0.05)
        "VERDICT: PASS\n" else "VERDICT: FAIL\n")
