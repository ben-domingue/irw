## ising_network_sim: binary symptom data from a known Ising network, with full truth (#2725)
##
## IRW's own seeded draw from IsingSampler::IsingSampler (Epskamp; CRAN, GPL-2; written
## against version 0.5.0). The draw is IRW's, so the table carries IRW's licence, as for
## tirt and mudfold.
##
## Design: one condition of the simulation study of van Borkulo, Borsboom, Epskamp,
## Blanken, Boschloo, Schoevers & Waldorp (2014), A new method for constructing networks
## from binary data, Scientific Reports 4, 5918, doi:10.1038/srep05918: a random network
## of 20 nodes with connection probability 0.2, N = 1,000, positive edge weights drawn as
## squared standard normals, data drawn with the Metropolis-Hastings sampler of
## IsingSampler, responses coded 0/1.
##
## The paper says thresholds were "generated from the normal distribution between zero
## and minus the degree of a node". That sentence does not pin down the normal's mean and
## SD, so this script reads it as: threshold_j ~ N(-s_j / 2, (s_j / 4)^2) truncated to
## [-s_j, 0], where s_j is node j's weighted degree (sum of its edge weights; -s_j / 2 is
## also the threshold in the IsingFit documentation example). The random graph is drawn
## directly (each of the 190 node pairs is an edge with probability 0.2) rather than with
## igraph. nIter = 1000 Metropolis sweeps (the default is 100), for a well-mixed chain.
##
## Each node is an item; id is a simulated respondent. The full weight matrix is in the
## item-level truth: itemcov_true_w_itemKK is the edge weight between this row's item and
## itemKK (0 = no edge, symmetric, zero diagonal).
##
## Columns
##   resp                       node state (0/1)
##   itemcov_true_threshold     node threshold (external field)
##   itemcov_true_degree        node degree (number of edges)
##   itemcov_true_w_item01..20  edge weights
## There is no person-level latent variable in this model, so there are no cov_true_*
## columns.
library(IsingSampler)
set.seed(20261001)
N <- 1000; P <- 20; p_edge <- 0.2
A <- matrix(0, P, P)
A[upper.tri(A)] <- rbinom(P * (P - 1) / 2, 1, p_edge)
W <- A * matrix(rnorm(P * P)^2, P, P)
W <- W + t(W)
s <- rowSums(W)
thr <- numeric(P)
for (j in 1:P) {
  if (s[j] == 0) next
  repeat { v <- rnorm(1, -s[j] / 2, s[j] / 4); if (v >= -s[j] && v <= 0) break }
  thr[j] <- v
}
X <- IsingSampler(N, W, thr, nIter = 1000, responses = c(0L, 1L), method = "MH")

items <- sprintf("item%02d", 1:P)
df <- data.frame(id = rep(1:N, times = P),
                 item = rep(items, each = N),
                 resp = as.vector(X),
                 itemcov_true_threshold = rep(thr, each = N),
                 itemcov_true_degree = rep(rowSums(A + t(A)), each = N))
for (k in 1:P) df[[paste0("itemcov_true_w_", items[k])]] <- rep(W[, k], each = N)
df <- df[order(df$id, df$item), ]
stopifnot(nrow(df) == N * P, all(df$resp %in% 0:1), isSymmetric(W), all(diag(W) == 0),
          all(colMeans(X) > 0.02 & colMeans(X) < 0.98))
out <- path.expand("~/.cache/irw-simsyn")
dir.create(out, showWarnings = FALSE, recursive = TRUE)
write.csv(df, file.path(out, "ising_network_sim.csv"), quote = FALSE, row.names = FALSE)
