# Mapping check for che_mood_2024_pvhs (peerj.17134, PMC10977085).
#
# Usage: Rscript verify_che_mood_2024_pvhs.R [path/to/response.csv]
#
# Claim: IRW item pLk is the deposit column "pL k", and that column is the
# item the paper prints as pLk in Table 2 (whose wording the item text ships).
# The paper's Table 3 prints, for each of the ten codes, the loading and the
# communality from a one-factor exploratory analysis of these 200 respondents.
# If the codes were permuted, the reproduced loadings would land on the wrong
# codes. All ten published loadings are distinct at 3 dp, so every item is
# separated from every other -- including the close pL2/pL3/pL4 (.892/.884/.885)
# and the two near-zero loaders pL5/pL9 (.096/.119).
#
# The paper calls its extraction "principal component axis"; what reproduces
# Table 3 is iterated one-factor principal-axis factoring (SMC starting
# communalities), which is what SPSS's "Principal axis factoring" does. The
# response data are used as stored (pL5/pL9 unreversed): loadings are reported
# unsigned in the paper, so the sign is taken as the direction of the factor.
#
# Content check on top of the numbers: the two items that barely load are the
# two side-effect worries (pL5 "vaccine baru ... lebih banyak kesan sampingan",
# pL9 "bimbang ... kesan sampingan"), the only two items Methods says were
# reverse-keyed. A text swap between one of them and a pro-vaccine item would
# put a near-zero loading on a pro-vaccine stem.

args <- commandArgs(trailingOnly = TRUE)
path <- if (length(args)) args[1] else "irw_output/che_mood_2024_pvhs.csv"
d <- read.csv(path)

codes <- paste0("pL", 1:10)
# Table 3 (10-item EFA): factor loading, communality.
pub_load <- c(0.793, 0.892, 0.884, 0.885, 0.096, 0.753, 0.798, 0.843, 0.119, 0.755)
pub_comm <- c(0.629, 0.796, 0.781, 0.783, 0.009, 0.567, 0.638, 0.711, 0.014, 0.571)
stopifnot(!anyDuplicated(pub_load))

w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- as.matrix(w[, codes])
cat(sprintf("respondents: %d (paper: 200)\n", nrow(X)))

R <- cor(X)
h <- 1 - 1 / diag(solve(R))
for (it in 1:1000) {
  Rr <- R; diag(Rr) <- h
  e <- eigen(Rr, symmetric = TRUE)
  l <- e$vectors[, 1] * sqrt(e$values[1])
  h_new <- l^2
  if (max(abs(h_new - h)) < 1e-10) break
  h <- h_new
}
l <- l * sign(sum(l))

res <- data.frame(item = codes, pub_load = pub_load, obs_load = round(l, 3),
                  pub_comm = pub_comm, obs_comm = round(l^2, 3))
print(res, row.names = FALSE)

# Loadings must reproduce to rounding; communalities are printed by the paper
# to 3 dp from unrounded loadings, so allow one unit in the last place.
ok_load <- abs(res$obs_load - pub_load) <= 0.0015
ok_comm <- abs(res$obs_comm - pub_comm) <= 0.0015
cat(sprintf("loadings reproduced: %d of 10; communalities: %d of 10\n",
            sum(ok_load), sum(ok_comm)))

# Alpha: Table 3 reports 0.859 for 10 items with pL5/pL9 reverse-scored,
# Table 4 reports 0.944 for the 8 retained items.
alpha <- function(M) { k <- ncol(M); k / (k - 1) * (1 - sum(apply(M, 2, var)) / var(rowSums(M))) }
Xr <- X; Xr[, c("pL5", "pL9")] <- 6 - Xr[, c("pL5", "pL9")]
a10 <- alpha(Xr); a8 <- alpha(X[, setdiff(codes, c("pL5", "pL9"))])
cat(sprintf("alpha 10 items, pL5/pL9 reflected: %.3f (paper 0.859)\n", a10))
cat(sprintf("alpha  8 items without pL5/pL9:     %.3f (paper 0.944)\n", a8))

pass <- all(ok_load) && all(ok_comm) &&
  abs(a10 - 0.859) < 0.0015 && abs(a8 - 0.944) < 0.0015
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
