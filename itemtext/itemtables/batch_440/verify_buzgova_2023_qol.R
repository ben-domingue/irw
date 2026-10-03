# verify_buzgova_2023_qol.R -- Step 5b mapping check for buzgova_2023_qol (batch_440).
#
# Claim: live item QoL<n> is OPQOL-brief item <n> (Bowling et al. 2013 numbering),
# and resp is stored RAW on the form's own coding (1 = Strongly agree ... 5 = Strongly
# disagree; every OPQOL-brief item is positively worded, so low resp = better QoL).
#
# The source .sav (PLOS 10.1371/journal.pone.0283772.s001) has no labels, so the tie is
# checked against Table 2 of the same group's Czech OPQOL-brief validation (Buzgova,
# Kozakova, Zelenikova, Bobcikova 2022, BMC Geriatrics 22:534, PMC9219227,
# doi 10.1186/s12877-022-03198-x), which prints item wording i1..I13 against per-item
# Mean, SD and corrected item-total r (n = 954, reported on the reversed 5 = best scale).
#
# Tests:
#  (1) direction: reversed live means (6 - mean) track the published means (<= 0.035);
#      the raw direction would put every item near 1.6-2.1 instead of 3.9-4.4.
#  (2) mapping: over mean, SD and corrected item-total r jointly, the identity
#      assignment is the unique optimum over all 13! permutations (Hungarian
#      assignment), and every one of the 78 pairwise swaps is strictly worse.
#  (3) content marker: the two health items (3 "healthy enough to get out and about",
#      7 "healthy enough to have my independence") are the most strongly correlated
#      pair in the matrix.

suppressMessages({library(irw); library(tidyr); library(dplyr); library(clue)})

TABLE <- "buzgova_2023_qol"
items <- paste0("QoL", 1:13)
pub_m  <- c(3.91,4.03,4.22,4.37,4.09,4.24,4.20,4.17,4.19,4.38,4.37,4.08,4.19)
pub_sd <- c(0.78,0.76,0.80,0.68,0.82,0.69,0.77,0.71,0.76,0.67,0.62,0.71,0.76)
pub_it <- c(0.705,0.701,0.640,0.516,0.734,0.671,0.687,0.760,0.571,0.666,0.709,0.719,0.504)

d <- irw::irw_fetch(TABLE)
w <- d |> select(id, item, resp) |> pivot_wider(names_from = item, values_from = resp)
R <- as.matrix(w[, items])
X <- 6 - R                                   # reverse to the published 5 = best scale
cc <- X[complete.cases(X), ]
m  <- colMeans(X, na.rm = TRUE)
s  <- apply(X, 2, sd, na.rm = TRUE)
it <- sapply(1:13, function(j) cor(cc[, j], rowSums(cc[, -j])))

cat(sprintf("%-6s %7s %7s %7s %7s %7s %7s\n", "item", "pub_M", "obs_M", "pub_SD", "obs_SD", "pub_IT", "obs_IT"))
for (i in 1:13) cat(sprintf("%-6s %7.2f %7.3f %7.2f %7.3f %7.3f %7.3f\n",
    items[i], pub_m[i], m[i], pub_sd[i], s[i], pub_it[i], it[i]))
cat(sprintf("raw (unreversed) item means range: %.2f-%.2f\n", min(6 - m), max(6 - m)))
cat(sprintf("total (complete cases n=%d): mean %.2f SD %.2f  | published 54.49 SD 6.83\n",
            nrow(cc), mean(rowSums(cc)), sd(rowSums(cc))))

ok1 <- max(abs(m - pub_m)) <= 0.035
cat(sprintf("\n(1) max |mean diff| after reversal = %.3f -> %s\n", max(abs(m - pub_m)), ok1))

D <- outer(1:13, 1:13, Vectorize(function(i, j)
    ((m[i] - pub_m[j]) / 0.02)^2 + ((s[i] - pub_sd[j]) / 0.02)^2 + ((it[i] - pub_it[j]) / 0.02)^2))
a <- as.integer(solve_LSAP(D))
id_cost <- sum(diag(D))
swap_gain <- c()
for (i in 1:12) for (j in (i + 1):13) {
  perm <- 1:13; perm[c(i, j)] <- perm[c(j, i)]
  swap_gain <- c(swap_gain, setNames(sum(D[cbind(1:13, perm)]) - id_cost, paste0(i, "<->", j)))
}
ok2 <- identical(a, 1:13) && all(swap_gain > 0)
cat(sprintf("(2) optimal assignment: %s\n    identity cost %.1f; smallest swap penalty %.1f (%s) -> %s\n",
    paste(a, collapse = " "), id_cost, min(swap_gain), names(which.min(swap_gain)), ok2))

C <- cor(R, use = "pairwise.complete.obs"); diag(C) <- NA
top <- which(C == max(C, na.rm = TRUE), arr.ind = TRUE)[1, ]
ok3 <- setequal(items[top], c("QoL3", "QoL7"))
cat(sprintf("(3) strongest inter-item r = %.3f between %s and %s (health pair expected) -> %s\n",
    max(C, na.rm = TRUE), items[top[1]], items[top[2]], ok3))

cat("Note: the published sample (n=954, age>=65) and this table (n~980, age>=60) overlap heavily\n",
    "but are not identical, so small residuals (<=0.03) are expected. Several items tie on mean\n",
    "(3/6/7/9/13 at 4.16-4.24); they are separated by SD and item-total r jointly, not by mean alone.\n", sep = "")
cat(if (ok1 && ok2 && ok3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
