## hrm_rater_sim: rater effects (severity and variability) under the hierarchical rater
## model, with full generating parameters (#2725)
##
## IRW's own seeded draw from immer::immer_hrm_simulate (Robitzsch & Steinfeld; CRAN,
## GPL (>= 2); written against version 1.5.13). The draw is IRW's, so the table carries
## IRW's licence, as for tirt and mudfold.
##
## Model: the hierarchical rater model (HRM) of Patz, Junker, Johnson & Mariano (2002),
## JEBS 27(4), 341-384, doi:10.3102/10769986027004341. Stage 1: each person has an ideal
## rating xi_pi on each item from a partial credit model, P(xi = k) ∝ exp(a k theta_p -
## b_ik), with b_ik the cumulative category intercept (b_i0 = 0). Stage 2: rater r's observed score is drawn from a discretised normal around the
## ideal rating, P(X = k | xi) ∝ exp(-(k - (xi + phi_ir))^2 / (2 psi_ir)), so phi is rater
## bias (positive = lenient, negative = severe) and psi rater variability (unreliability).
##
## Design: Example 1 of immer::immer_hrm (the package's own simulation design): scores
## 0-3, theta ~ N(0, 2^2), a = 1 (passed as a scalar: immer_hrm_simulate multiplies by the
## whole `a` vector, which is only harmless when every slope is equal), b_ik = item location seq(-1.5, 1.5) + step seq(-2, 2),
## three raters with severities c(-.3, -.2, .5) plus N(0, .3^2) item-by-rater noise,
## centred within item, and variabilities psi = c(.1, .4, .8). The example has N = 500 and
## 4 items; here N = 1,000 and 6 items (to meet the >= 5-item floor of #2726). Every rater
## scores every person on every item (fully crossed).
##
## Layout: one row per person x item x rater; the `rater` column (datastandard.md, "Rater
## data") distinguishes the three scores of the same person-item. The item-by-rater
## parameters are stored as item-level columns indexed by rater.
## The generator does not return the stage-1 ideal ratings xi, so they are not in the
## table.
##
## Columns
##   resp                                   observed rating (0-3)
##   cov_true_theta                         person ability
##   itemcov_true_a                         item slope (1)
##   itemcov_true_b1..b3                    cumulative category intercepts b_i1..b_i3
##   itemcov_true_phi_rater1..3             bias of rater r on this item (+ = lenient)
##   itemcov_true_psi_rater1..3             variability of rater r on this item
##   rater                                  1-3
library(immer)
set.seed(20261001)
N <- 1000; I <- 6; R <- 3; K <- 3; sigma <- 2
theta <- stats::rnorm(N, sd = sigma)
b <- outer(seq(-1.5, 1.5, len = I), seq(-2, 2, len = K), "+")
a <- rep(1, I)
phi <- matrix(c(-.3, -.2, .5), nrow = I, ncol = R, byrow = TRUE)
phi <- phi + stats::rnorm(phi, sd = .3)
phi <- phi - rowMeans(phi)
psi <- matrix(c(.1, .4, .8), nrow = I, ncol = R, byrow = TRUE)
sim <- immer::immer_hrm_simulate(theta, 1, b, phi = phi, psi = psi)

items <- sprintf("item%02d", 1:I)
df <- data.frame(id = rep(sim$pid, times = I),
                 item = rep(items, each = nrow(sim)),
                 resp = unlist(sim[, paste0("I", 1:I)], use.names = FALSE),
                 rater = rep(sim$rater, times = I))
ii <- match(df$item, items)
df$cov_true_theta <- theta[df$id]
df$itemcov_true_a <- a[ii]
for (k in 1:K) df[[paste0("itemcov_true_b", k)]] <- b[ii, k]
for (r in 1:R) df[[paste0("itemcov_true_phi_rater", r)]] <- phi[ii, r]
for (r in 1:R) df[[paste0("itemcov_true_psi_rater", r)]] <- psi[ii, r]
df <- df[order(df$id, df$item, df$rater),
         c("id", "item", "resp", setdiff(names(df), c("id", "item", "resp", "rater")), "rater")]
stopifnot(nrow(df) == N * I * R, all(df$resp %in% 0:K),
          !anyDuplicated(df[, c("id", "item", "rater")]))
out <- path.expand("~/.cache/irw-simsyn")
dir.create(out, showWarnings = FALSE, recursive = TRUE)
write.csv(df, file.path(out, "hrm_rater_sim.csv"), quote = FALSE, row.names = FALSE)
