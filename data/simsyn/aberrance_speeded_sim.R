## aberrance_speeded_sim: test speededness / end-of-test rapid guessing, with full truth (#2725)
##
## IRW's own seeded draw from aberrance::sim (Gorney & Deng; CRAN, GPL (>= 3); written
## against version 0.3.0). The draw is IRW's, so the table carries IRW's licence, as for
## tirt and mudfold.
##
## Design: the change-point speededness design of Shao, Li & Cheng (2016), Detection of
## test speededness using change-point analysis, Psychometrika 81(4), 1118-1141, as coded
## in the aberrance documentation (detect_cp example): 10% of examinees are speeded and,
## after a change point at 90% of the test, switch to rapid guessing. On the last 10% of
## items a speeded examinee's score is Bernoulli(0.25) and the log response time is
## U(log 1, log 10), i.e. 1-10 seconds. Here N = 1,000 (the example uses 50) and n = 40,
## so the change point is after item 36 and items 37-40 are the speeded block.
##
## Rapid guessing is represented by this end-of-test block rather than by guesses on
## random items (the aberrance detect_rg example), because random per-response guessing
## needs a response-level truth flag and the IRW format has no column for one. Here the
## truth for every response follows from cov_true_speeded and itemcov_true_speeded_block.
##
## Model before contamination:
##   score       3PL, P(X = 1) = c + (1 - c) / (1 + exp(-a (theta - b)))
##   log time    lognormal model (van der Linden 2006): log T ~ N(beta - tau, 1 / alpha^2)
##   (theta, tau) ~ N(0, [1 .25; .25 .25]); a ~ lognormal(0, .25); c ~ U(.05, .30);
##   alpha ~ U(1.5, 2.5); (b, beta) ~ N((0, 3.5), [1 .2; .2 .15])
##
## Columns
##   resp                          contaminated item score (0/1)
##   rt                            exp(contaminated log time), seconds
##   cov_true_theta, cov_true_tau  ability and speed
##   cov_true_speeded              1 = speeded examinee (rapid guesses after item 36)
##   itemcov_true_a/b/c, itemcov_true_alpha/beta
##   itemcov_true_speeded_block    1 = item after the change point (items 37-40)
library(aberrance)
set.seed(20261001)
N <- 1000; n <- 40
cv <- sample(1:N, size = N * 0.10)
cp <- n * 0.90
ci <- (cp + 1):n
xi <- MASS::mvrnorm(N, mu = c(theta = 0, tau = 0),
                    Sigma = matrix(c(1, 0.25, 0.25, 0.25), ncol = 2))
psi <- cbind(a = rlnorm(n, meanlog = 0, sdlog = 0.25), b = NA,
             c = runif(n, min = 0.05, max = 0.30),
             alpha = runif(n, min = 1.5, max = 2.5), beta = NA)
psi[, c("b", "beta")] <- MASS::mvrnorm(n, mu = c(b = 0, beta = 3.5),
                                       Sigma = matrix(c(1, 0.2, 0.2, 0.15), ncol = 2))
dat <- sim(psi, xi)
x <- dat$x; y <- dat$y
x[cv, ci] <- rbinom(length(cv) * length(ci), size = 1, prob = 0.25)
y[cv, ci] <- runif(length(cv) * length(ci), min = log(1), max = log(10))

items <- sprintf("item%02d", 1:n)
df <- data.frame(id = rep(1:N, times = n),
                 item = rep(items, each = N),
                 resp = as.vector(x),
                 rt = exp(as.vector(y)),
                 cov_true_theta = rep(xi[, "theta"], times = n),
                 cov_true_tau = rep(xi[, "tau"], times = n),
                 cov_true_speeded = rep(as.integer(1:N %in% cv), times = n),
                 itemcov_true_a = rep(psi[, "a"], each = N),
                 itemcov_true_b = rep(psi[, "b"], each = N),
                 itemcov_true_c = rep(psi[, "c"], each = N),
                 itemcov_true_alpha = rep(psi[, "alpha"], each = N),
                 itemcov_true_beta = rep(psi[, "beta"], each = N),
                 itemcov_true_speeded_block = rep(as.integer(1:n %in% ci), each = N))
df <- df[order(df$id, df$item), ]
stopifnot(nrow(df) == N * n, all(df$resp %in% 0:1), all(df$rt > 0),
          all(df$rt[df$cov_true_speeded == 1 & df$itemcov_true_speeded_block == 1] <= 10))
out <- path.expand("~/.cache/irw-simsyn")
dir.create(out, showWarnings = FALSE, recursive = TRUE)
write.csv(df, file.path(out, "aberrance_speeded_sim.csv"), quote = FALSE, row.names = FALSE)
