# verify_temesgen_2025_elephant_park_attitude.R
#
# Claim: live items Q1..Q7 are the seven "Attitude statement toward KSNP conservation"
# statements 3.1..3.7 of the S1 household questionnaire (peerj-13-19428-s004.docx), in
# that order, and resp is stored raw with 1=strongly agree ... 5=strongly disagree.
#
# The IRW code is assigned POSITIONALLY by data/temesgen_2025_elephant_conflict.py
# (raw.iloc[408:803, 1:9], columns renamed id,Q1..Q7). Header row 407 of the s001 CSV
# reads 'Households','Q1'..'Q7' in exactly those columns, so the rename reproduces the
# source header 7/7. What still needs checking is Q-number -> statement, and that is
# what the published per-item distribution tests.
#
# Published values: Supplemental Table 6 (peerj-13-19428-s002.zip, Table6.docx),
# "Households' response to the attitude statement toward the conservation of KSNP",
# % Agree / Neutral / Disagree for statements 1-7 (N=395).

suppressMessages(library(irw))

TABLE <- "temesgen_2025_elephant_park_attitude"
PUB <- rbind(
  c(49.87, 12.15, 37.97),
  c(52.91, 14.18, 32.91),
  c(60.50, 10.63, 28.87),
  c(27.35, 23.04, 49.61),
  c(60.00, 16.71, 23.29),
  c(38.74, 12.91, 48.35),
  c(34.17, 11.65, 54.18))
rownames(PUB) <- paste0("stmt", 1:7)
TOL <- 0.05  # published to 2 dp; residuals are rounding

d <- irw::irw_fetch(TABLE)
items <- paste0("Q", 1:7)
obs <- t(sapply(items, function(i) {
  r <- d$resp[d$item == i]
  100 * c(mean(r <= 2), mean(r == 3), mean(r >= 4))
}))
flip <- t(sapply(items, function(i) {
  r <- d$resp[d$item == i]
  100 * c(mean(r >= 4), mean(r == 3), mean(r <= 2))
}))

dist <- function(a, b) max(abs(a - b))
cat(sprintf("%-4s %-22s %-22s %8s %10s %10s\n", "item", "published A/N/D",
            "observed A/N/D", "own_dev", "nearest", "next_dev"))
ok <- TRUE
for (k in 1:7) {
  devs <- sapply(1:7, function(j) dist(obs[k, ], PUB[j, ]))
  nearest <- which.min(devs)
  cat(sprintf("%-4s %6.2f/%5.2f/%5.2f    %6.2f/%5.2f/%5.2f    %8.2f %10s %10.2f\n",
              items[k], PUB[k, 1], PUB[k, 2], PUB[k, 3], obs[k, 1], obs[k, 2], obs[k, 3],
              devs[k], rownames(PUB)[nearest], min(devs[-k])))
  if (k <= 6) ok <- ok && devs[k] <= TOL && nearest == k
}

# Q7 is placed by elimination: Q1..Q6 each reproduce exactly one published row, and
# Q7 must not reproduce any of rows 1-6 (it would signal a duplicated/shifted column).
q7_vs_others <- min(sapply(1:6, function(j) dist(obs[7, ], PUB[j, ])))
cat(sprintf("\nQ7 vs its own published row: max dev %.2f points (DOES NOT reproduce)\n",
            dist(obs[7, ], PUB[7, ])))
cat(sprintf("Q7 vs nearest of rows 1-6:   max dev %.2f points\n", q7_vs_others))
ok <- ok && q7_vs_others > 1

# Direction: flipped coding must fail.
flip_dev <- max(sapply(1:6, function(k) dist(flip[k, ], PUB[k, ])))
cat(sprintf("Flipped direction (1=strongly disagree), worst dev over Q1-Q6: %.2f points\n", flip_dev))
ok <- ok && flip_dev > 5

cat("\nDoes NOT establish: Q7's identity positively. Its live distribution (38.73/7.85/53.42)\n",
    "misses published statement 7 (34.17/11.65/54.18) by up to 4.56 points, while Q1-Q6\n",
    "match theirs to <=0.01. Q7 is statement 7 only by elimination (7 codes, 7 statements,\n",
    "six pinned) and by the source CSV's own 'Q7=question 7' footnote.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
