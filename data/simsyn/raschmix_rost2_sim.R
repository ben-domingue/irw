## raschmix_rost2_sim: two-class Rasch mixture with known classes (#2725)
##
## IRW's own seeded draw from psychomix::simRaschmix (Frick, Strobl, Leisch & Zeileis
## 2012, JSS 48(7), doi:10.18637/jss.v048.i07; CRAN, GPL-2 | GPL-3), using its built-in
## design "rost2": the second data-generating process of Rost (1990), Rasch models in
## latent classes, Applied Psychological Measurement 14(3), 271-282.
##
## Design: 1,800 persons, 10 items, two latent classes of 900. Item difficulties run
## 2.7 to -2.7 in steps of 0.6 in class 1 and the exact reverse in class 2; abilities
## take the values -2.7, -0.9, 0.9, 2.7 (450 persons each). extremes = TRUE keeps
## persons with all or no items correct, so all 1,800 are present.
##
## Columns
##   cov_true_class         latent class (1 or 2)
##   cov_true_theta         person ability
##   itemcov_true_b_class1, itemcov_true_b_class2   item difficulty in each class
library(psychomix)
set.seed(20261001)
r <- simRaschmix(design = "rost2", extremes = TRUE)
N <- nrow(r); K <- ncol(r)
items <- sprintf("item%02d", 1:K)
cl <- attr(r, "cluster"); th <- attr(r, "ability"); b <- attr(r, "difficulty")
stopifnot(N == 1800, K == 10, identical(as.integer(table(cl)), c(900L, 900L)),
          all(b[, 1] == -b[, 2]))
df <- data.frame(id = rep(1:N, times = K),
                 item = rep(items, each = N),
                 resp = as.vector(r),
                 cov_true_class = rep(cl, times = K),
                 cov_true_theta = rep(th, times = K),
                 itemcov_true_b_class1 = rep(b[, 1], each = N),
                 itemcov_true_b_class2 = rep(b[, 2], each = N))
df <- df[order(df$id, df$item), ]
stopifnot(all(df$resp %in% 0:1))
out <- path.expand("~/.cache/irw-simsyn")
dir.create(out, showWarnings = FALSE, recursive = TRUE)
write.csv(df, file.path(out, "raschmix_rost2_sim.csv"), quote = FALSE, row.names = FALSE)
