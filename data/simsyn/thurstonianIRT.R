##see: https://cran.r-project.org/web/packages/thurstonianIRT/vignettes/TIRT_sim_tests.html

library(thurstonianIRT)
library(dplyr)
library(tidyr)
npersons <- 500
ntraits <- 5
nitems_per_block <- 3
nblocks_per_trait <- 9
nblocks <- ntraits * nblocks_per_trait / nitems_per_block
nitems <- ntraits * nblocks_per_trait
ncomparisons <- (nitems_per_block * (nitems_per_block - 1)) / 2 * nblocks
set.seed(123)
lambda <- runif(nitems, 0.65, 0.96)
signs <- c(rep(1, ceiling(nitems / 2)), rep(-1, floor(nitems / 2)))
lambda <- lambda * signs[sample(seq_len(nitems))]
gamma <- runif(nitems, -1, 1)
Phi <- diag(5)
sdata <- sim_TIRT_data(
  npersons = npersons, 
  ntraits = ntraits, 
  nitems_per_block = nitems_per_block,
  nblocks_per_trait = nblocks_per_trait,
  gamma = gamma,
  lambda = lambda,
  Phi = Phi
)
