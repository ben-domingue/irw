# verify_yoshimura_2026_psych_safety.R -- Step 5b check for batch_534.
#
# Claim: ps3m1..ps3m9 are items 1..9 of Section 1 (team leader) of the Japanese
# survey measure of psychological safety (Sasaki et al. 2022, IJERPH 19:9879,
# Supplementary Materials; Japanese version of O'Donovan et al. 2020), and the
# shipped item_text for ps3m<k> is Section 1 item k.
#
# Route (study-internal, published parcel statistics):
#   Yoshimura et al. (2026) S1 File (pone.0346791.s004) path diagram names the PS
#   parcels psafeA125, psafeB367, psafeC489, i.e. items {1,2,5}, {3,6,7}, {4,8,9}.
#   S1 Table (pone.0346791.s001) Table B publishes PS1 4.32 (1.30), PS2 4.16 (1.25),
#   PS3 4.12 (1.21); r(PS1,PS2)=.83, r(PS1,PS3)=.79, r(PS2,PS3)=.83.
#   We test the claimed parcels AND every one of the 1680 assignments of the nine
#   codes to three labelled triplets, and count how many reproduce Table B.
# NOT established: order within each triplet {1,2,5}, {3,6,7}, {4,8,9} -- e.g. a
# swap of ps3m1 and ps3m2 passes. No per-item statistics are published by either
# the study or Sasaki et al. (who publish CFA loadings on a different sample).

suppressMessages(library(irw))
TABLE <- "yoshimura_2026_psych_safety"
d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- as.matrix(w[, paste0("ps3m", 1:9)])
cat("N respondents:", nrow(w), " complete:", sum(complete.cases(w)), "\n\n")

pub_m <- c(4.32, 4.16, 4.12); pub_sd <- c(1.30, 1.25, 1.21); pub_r <- c(.83, .79, .83)
tol <- 0.006
fit <- function(parcels) {
  P <- sapply(parcels, function(ix) rowMeans(w[, ix, drop = FALSE]))
  m <- colMeans(P); s <- apply(P, 2, sd)
  r <- c(cor(P[, 1], P[, 2]), cor(P[, 1], P[, 3]), cor(P[, 2], P[, 3]))
  list(m = m, s = s, r = r,
       pass = all(abs(m - pub_m) <= tol) && all(abs(s - pub_sd) <= tol) && all(abs(r - pub_r) <= tol))
}
ok <- TRUE
claimed <- list(PS1 = c(1, 2, 5), PS2 = c(3, 6, 7), PS3 = c(4, 8, 9))
f <- fit(claimed)
cat("Claimed parcels vs S1 Table B\n")
for (j in 1:3)
  cat(sprintf("  %s items {%s}: M %.3f (pub %.2f)  SD %.3f (pub %.2f)\n", names(claimed)[j],
              paste(claimed[[j]], collapse = ","), f$m[j], pub_m[j], f$s[j], pub_sd[j]))
cat(sprintf("  r(PS1,PS2) %.3f (pub .83)  r(PS1,PS3) %.3f (pub .79)  r(PS2,PS3) %.3f (pub .83)\n",
            f$r[1], f$r[2], f$r[3]))
if (!f$pass) ok <- FALSE

# all labelled partitions of 1..9 into three triplets: choose 3 for PS1, 3 of rest for PS2
n_all <- 0; n_pass <- 0; near <- 0
A <- combn(9, 3)
for (a in seq_len(ncol(A))) {
  rest <- setdiff(1:9, A[, a]); B <- combn(rest, 3)
  for (b in seq_len(ncol(B))) {
    pr <- list(A[, a], B[, b], setdiff(rest, B[, b]))
    n_all <- n_all + 1
    fr <- fit(pr)
    if (fr$pass) { n_pass <- n_pass + 1
      cat("  reproducing assignment:", paste(sapply(pr, paste, collapse = ","), collapse = " | "), "\n") }
    if (all(abs(fr$m - pub_m) <= 0.02)) near <- near + 1
  }
}
cat(sprintf("  %d of %d labelled triplet-assignments reproduce Table B within %.3f\n", n_pass, n_all, tol))
cat(sprintf("  (%d of %d match the three parcel MEANS alone within 0.02 -- means alone are not decisive)\n", near, n_all))
if (n_pass != 1) ok <- FALSE

cat("\nPer-item means (context only; nothing published to compare):\n")
print(round(colMeans(w), 3))
cat("\nNot established: order within the triplets {1,2,5}, {3,6,7}, {4,8,9}\n",
    "(e.g. a swap of ps3m1 and ps3m2 would pass).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
