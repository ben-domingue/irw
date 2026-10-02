## aberrance_pk_sim: item preknowledge (compromised items) with response times, with full truth (#2725)
##
## IRW's own seeded draw from aberrance::sim (Gorney & Deng; CRAN, GPL (>= 3); written
## against version 0.3.0). The draw is IRW's, so the table carries IRW's licence, as for
## tirt and mudfold.
##
## Design: the preknowledge design of Sinharay (2017), Detection of item preknowledge
## using likelihood ratio test and score test, JEBS 42(1), 46-68, and Sinharay & Johnson
## (2020, BJMSP 73(3), 397-419), as coded in the aberrance documentation (detect_pk
## example): 10% of examinees have preknowledge of 40% of the items. Their scores on the
## compromised items are redrawn as Bernoulli(0.90) and their log response times on those
## items are multiplied by 0.75. Here N = 1,000 (the example uses 500) and n = 40.
##
## Model before contamination:
##   score       2PL, P(X = 1) = 1 / (1 + exp(-a (theta - b))), c = 0
##   log time    lognormal model (van der Linden 2006): log T ~ N(beta - tau, 1 / alpha^2)
##   (theta, tau) ~ N(0, [1 .25; .25 .25]); a ~ lognormal(0, .25); alpha ~ U(1.5, 2.5);
##   (b, beta) ~ N((0, 3.5), [1 .2; .2 .15])
##
## Columns
##   resp                       contaminated item score (0/1)
##   rt                         exp(contaminated log time), seconds (median ~ 33 s)
##   cov_true_theta, cov_true_tau    ability and speed
##   cov_true_preknowledge      1 = examinee had preknowledge
##   itemcov_true_a, itemcov_true_b, itemcov_true_alpha, itemcov_true_beta
##   itemcov_true_compromised   1 = item was compromised
## A response is contaminated exactly when cov_true_preknowledge = 1 and
## itemcov_true_compromised = 1.
library(aberrance)
set.seed(20261001)
N <- 1000; n <- 40
cv <- sample(1:N, size = N * 0.10)
ci <- sample(1:n, size = n * 0.40)
xi <- MASS::mvrnorm(N, mu = c(theta = 0, tau = 0),
                    Sigma = matrix(c(1, 0.25, 0.25, 0.25), ncol = 2))
psi <- cbind(a = rlnorm(n, meanlog = 0, sdlog = 0.25), b = NA, c = 0,
             alpha = runif(n, min = 1.5, max = 2.5), beta = NA)
psi[, c("b", "beta")] <- MASS::mvrnorm(n, mu = c(b = 0, beta = 3.5),
                                       Sigma = matrix(c(1, 0.2, 0.2, 0.15), ncol = 2))
dat <- sim(psi, xi)
x <- dat$x; y <- dat$y
x[cv, ci] <- rbinom(length(cv) * length(ci), size = 1, prob = 0.90)
y[cv, ci] <- y[cv, ci] * 0.75

items <- sprintf("item%02d", 1:n)
df <- data.frame(id = rep(1:N, times = n),
                 item = rep(items, each = N),
                 resp = as.vector(x),
                 rt = exp(as.vector(y)),
                 cov_true_theta = rep(xi[, "theta"], times = n),
                 cov_true_tau = rep(xi[, "tau"], times = n),
                 cov_true_preknowledge = rep(as.integer(1:N %in% cv), times = n),
                 itemcov_true_a = rep(psi[, "a"], each = N),
                 itemcov_true_b = rep(psi[, "b"], each = N),
                 itemcov_true_alpha = rep(psi[, "alpha"], each = N),
                 itemcov_true_beta = rep(psi[, "beta"], each = N),
                 itemcov_true_compromised = rep(as.integer(1:n %in% ci), each = N))
df <- df[order(df$id, df$item), ]
stopifnot(nrow(df) == N * n, all(df$resp %in% 0:1), all(df$rt > 0),
          sum(df$cov_true_preknowledge) == 100 * n, sum(df$itemcov_true_compromised) == 16 * N)
out <- path.expand("~/.cache/irw-simsyn")
dir.create(out, showWarnings = FALSE, recursive = TRUE)
write.csv(df, file.path(out, "aberrance_pk_sim.csv"), quote = FALSE, row.names = FALSE)
