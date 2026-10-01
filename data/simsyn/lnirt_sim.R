## lnirt_sim: joint response accuracy and response time, with full truth (#2725)
##
## IRW's own seeded draw from LNIRT::simLNIRT (Fox & Klotzke; CRAN, GPL-3), the
## hierarchical speed-accuracy framework of van der Linden (2007, Psychometrika 72,
## 287-308). The draw is IRW's, so the table carries IRW's licence, as for tirt and
## mudfold.
##
## Model (simLNIRT defaults, td = FALSE, WL = FALSE; read from the function source):
##   accuracy   P(Y_ik = 1) = Phi(a_k * theta_i - b_k)          (normal ogive)
##   log time   log T_ik = lambda_k - phi_k * zeta_i + e_ik,    e_ik ~ N(0, sigma2_k)
##   (theta_i, zeta_i) ~ N(0, [1 rho; rho 1]), rho = 0.3 below (zeta = speed:
##   higher means faster). a and phi are scaled to geometric mean 1, b and lambda
##   centred at 0, sigma2 ~ lognormal(0, 0.3).
##
## Columns
##   resp                 Y (0/1)
##   rt                   exp(log T), in seconds by convention
##   cov_true_theta       ability theta_i
##   cov_true_speed       speed zeta_i
##   itemcov_true_a, itemcov_true_b             accuracy parameters
##   itemcov_true_phi, itemcov_true_lambda      time discrimination and intensity
##   itemcov_true_sigma2                        residual log-time variance
library(LNIRT)
set.seed(20261001)
N <- 1000; K <- 20; rho <- 0.3
s <- simLNIRT(N = N, K = K, rho = rho)

items <- sprintf("item%02d", 1:K)
df <- data.frame(id = rep(1:N, times = K),
                 item = rep(items, each = N),
                 resp = as.vector(s$Y),
                 rt = exp(as.vector(s$RT)),
                 cov_true_theta = rep(s$theta[, 1], times = K),
                 cov_true_speed = rep(s$theta[, 2], times = K))
ip <- data.frame(item = items, itemcov_true_a = s$ab[, 1], itemcov_true_b = s$ab[, 2],
                 itemcov_true_phi = s$ab[, 3], itemcov_true_lambda = s$ab[, 4],
                 itemcov_true_sigma2 = s$sigma2)
df <- merge(df, ip, by = "item", sort = FALSE)
df <- df[order(df$id, df$item), c("id", "item", setdiff(names(df), c("id", "item")))]
stopifnot(nrow(df) == N * K, all(df$resp %in% 0:1), all(df$rt > 0),
          abs(cor(s$theta[, 1], s$theta[, 2]) - rho) < 1e-8)
out <- path.expand("~/.cache/irw-simsyn")
dir.create(out, showWarnings = FALSE, recursive = TRUE)
write.csv(df, file.path(out, "lnirt_sim.csv"), quote = FALSE, row.names = FALSE)
