## hmcdm_learning_sim: longitudinal (5-wave) skill growth under a higher-order hidden
## Markov cognitive diagnosis model, with full truth (#2725)
##
## IRW's own seeded draw from hmcdm::sim_alphas and hmcdm::sim_hmcdm (Kwon, Zhang, Wang &
## Chen; CRAN, GPL (>= 2); written against version 2.1.3). The draw is IRW's, so the table
## carries IRW's licence, as for tirt and mudfold.
##
## Design: the higher-order hidden Markov DCM with covariates of Wang, Yang, Culpepper &
## Douglas (2018), Tracking skill acquisition with cognitive diagnosis models, JEBS 43(1),
## 57-87, doi:10.3102/1076998617719727, with the generating values of the hmcdm "HO_sep"
## example (lambda = -1, 1.8, .277, .055 for intercept, learning ability, number of other
## mastered skills and amount of practice) and DINA slip/guess ~ U(.1, .2). The test
## design is the package's Spatial Rotation Learning Program: 50 items in five 10-item
## blocks over four skills (hmcdm::Q_matrix), given at five occasions in the five
## counterbalanced block orders of hmcdm::Test_order. Here N = 1,000 (200 per order; the
## real study had 350), and the initial skill profiles are uniform over the 16 classes.
##
## Why this generator for "growth / longitudinal IRT": no CRAN package simulates a
## continuous-theta growth IRT model from a published design; hmcdm does, with full truth,
## for the discrete-skill (diagnostic) version of growth. Each item is seen once, so
## id x item is unique and `wave` marks the occasion.
##
## Columns
##   wave                        occasion 1-5
##   resp                        DINA item response (0/1)
##   cov_true_theta              general learning ability (constant within person)
##   cov_true_alpha1..4          mastery (0/1) of skills 1-4 AT THAT WAVE (varies by wave;
##                               skills are never lost under this model)
##   cov_true_order              which of the five block orders the person received
##   itemcov_true_slip, itemcov_true_guess   DINA item parameters
##   qmatrix1..4                 Q-matrix row of the item
library(hmcdm)
set.seed(20261001)
N <- 1000; J <- nrow(Q_matrix); K <- ncol(Q_matrix); L <- 5
ver <- rep(1:5, each = N / 5)
blk <- split(1:J, rep(1:5, each = J / 5))
Design <- array(NA_real_, c(N, J, L))
for (i in 1:N) for (t in 1:L) Design[i, blk[[Test_order[ver[i], t]]], t] <- 1

class0 <- sample(1:2^K, N, replace = TRUE)
alpha0 <- t(sapply(class0, function(cl) inv_bijectionvector(K, cl - 1)))
thetas <- rnorm(N)
lambdas <- c(-1, 1.8, .277, .055)
Alphas <- sim_alphas(model = "HO_sep", lambdas = lambdas, thetas = thetas,
                     Q_matrix = Q_matrix, Design_array = Design, alpha0 = alpha0)
itempars <- matrix(runif(J * 2, .1, .2), ncol = 2)   # col 1 slip, col 2 guess
Y <- sim_hmcdm(model = "DINA", Alphas, Q_matrix, Design, itempars = itempars)

items <- sprintf("item%02d", 1:J)
rows <- which(!is.na(Design), arr.ind = TRUE)        # (person, item, wave)
df <- data.frame(id = rows[, 1], item = items[rows[, 2]], wave = rows[, 3],
                 resp = Y[rows],
                 cov_true_theta = thetas[rows[, 1]])
for (k in 1:K) df[[paste0("cov_true_alpha", k)]] <- Alphas[cbind(rows[, 1], k, rows[, 3])]
df$cov_true_order <- ver[rows[, 1]]
df$itemcov_true_slip <- itempars[rows[, 2], 1]
df$itemcov_true_guess <- itempars[rows[, 2], 2]
for (k in 1:K) df[[paste0("qmatrix", k)]] <- Q_matrix[rows[, 2], k]
df <- df[order(df$id, df$wave, df$item), c("id", "item", "resp", setdiff(names(df), c("id", "item", "resp")))]
stopifnot(nrow(df) == N * J, all(df$resp %in% 0:1), !anyDuplicated(df[, c("id", "item")]),
          all(table(df$id, df$wave) == 10),
          all(apply(Alphas, c(1, 2), function(a) all(diff(a) >= 0))))   # no forgetting
out <- path.expand("~/.cache/irw-simsyn")
dir.create(out, showWarnings = FALSE, recursive = TRUE)
write.csv(df, file.path(out, "hmcdm_learning_sim.csv"), quote = FALSE, row.names = FALSE)
