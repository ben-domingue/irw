# verify_temesgen_2025_elephant_conserv_attitude.R
#
# Claim: live items Q1..Q7 are the seven "Attitude statement toward elephant conservation"
# statements 3.8..3.14 of the S1 household questionnaire (peerj-13-19428-s004.docx), in
# that order, and resp is stored raw with 1=strongly agree ... 5=strongly disagree.
#
# The IRW code is assigned POSITIONALLY by data/temesgen_2025_elephant_conflict.py
# (raw.iloc[808:1203, 1:9] of the s001 CSV, columns renamed id,Q1..Q7). Header row 807 of
# that CSV reads 'Households','Q1'..'Q7' in exactly those columns (block titled
# "Table3. House hold response about attitude statement toward African elephant
# conservation"), so the rename reproduces the source header 7/7. What still needs
# checking is Q-number -> statement, which the published per-item distribution tests.
#
# Published values: Supplemental Table 6 (peerj-13-19428-s002.zip, Table6.docx), part II
# "Attitude statement toward African bush elephant", % Agree / Neutral / Disagree for
# statements 8-14.

suppressMessages(library(irw))

TABLE <- "temesgen_2025_elephant_conserv_attitude"
PUB <- rbind(
  c(44.81, 16.46, 38.74),
  c(42.85, 10.71, 46.43),
  c(56.77, 27.37, 15.85),
  c(17.04, 23.16, 59.80),
  c(48.72, 14.10, 37.18),
  c(51.91, 19.59, 28.50),
  c(53.31, 10.20, 36.48))
rownames(PUB) <- paste0("stmt", 8:14)
TOL <- 0.05  # published to 2 dp; residuals are rounding

d <- irw::irw_fetch(TABLE)
items <- paste0("Q", 1:7)
pct <- function(r, flip = FALSE) {
  a <- 100 * c(mean(r <= 2), mean(r == 3), mean(r >= 4))
  if (flip) rev(a) else a
}
obs  <- t(sapply(items, function(i) pct(d$resp[d$item == i])))
flip <- t(sapply(items, function(i) pct(d$resp[d$item == i], flip = TRUE)))
dist <- function(a, b) max(abs(a - b))

cat(sprintf("%-4s %-8s %-22s %-22s %8s %9s %9s\n", "item", "n", "published A/N/D",
            "observed A/N/D", "own_dev", "nearest", "next_dev"))
ok <- TRUE
for (k in 1:7) {
  devs <- sapply(1:7, function(j) dist(obs[k, ], PUB[j, ]))
  nearest <- which.min(devs)
  cat(sprintf("%-4s %-8d %6.2f/%5.2f/%5.2f    %6.2f/%5.2f/%5.2f    %8.2f %9s %9.2f\n",
              items[k], sum(d$item == items[k]), PUB[k, 1], PUB[k, 2], PUB[k, 3],
              obs[k, 1], obs[k, 2], obs[k, 3], devs[k], rownames(PUB)[nearest],
              min(devs[-k])))
  ok <- ok && devs[k] <= TOL && nearest == k && min(devs[-k]) > 1
}

# Direction: the flipped coding (1=strongly disagree) must fail.
flip_dev <- max(sapply(1:7, function(k) dist(flip[k, ], PUB[k, ])))
cat(sprintf("\nFlipped direction (1=strongly disagree), worst dev over Q1-Q7: %.2f points\n",
            flip_dev))
ok <- ok && flip_dev > 5

cat("Note: Agree/Neutral/Disagree collapses 1-2 and 4-5, so this pins item identity and\n",
    "scale direction but not the agree-vs-strongly-agree split within each pole.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
