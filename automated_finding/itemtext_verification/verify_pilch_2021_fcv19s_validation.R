# Mapping check for pilch_2021_fcv19s_validation (peerj.11263, Sample 2).
#
# Usage: Rscript verify_pilch_2021_fcv19s_validation.R [path/to/response.csv]
#
# The paper's Table 1 prints, for each numbered FCV-19S item and for Sample 2
# (N = 325), the item mean and SD overall and the mean by sex. That is 4
# published numbers per item. If fear<n> really is item n, all 28 must be
# reproduced from the response data; any swap between two items must break
# at least one of them, because no two items share all four numbers.
#
# cov_sex: 2 = male, 1 = female -- the split that reproduces Table 1's
# "males (N = 127)" / "females (N = 198)" counts.

args <- commandArgs(trailingOnly = TRUE)
path <- if (length(args)) args[1] else "irw_output/pilch_2021_fcv19s_validation.csv"
d <- read.csv(path)

# Table 1, Sample 2 columns: total mean, total SD, male mean, female mean.
pub <- data.frame(
  item = paste0("fear", 1:7),
  m    = c(2.72, 2.72, 1.35, 1.97, 2.46, 1.36, 1.35),
  sd   = c(1.15, 1.27, 0.72, 1.11, 1.21, 0.70, 0.70),
  male = c(2.46, 2.31, 1.26, 1.70, 2.13, 1.23, 1.20),
  fem  = c(2.89, 2.98, 1.41, 2.14, 2.67, 1.45, 1.45)
)
stopifnot(!anyDuplicated(pub[, -1]))  # the four numbers separate every item

obs <- do.call(rbind, lapply(pub$item, function(i) {
  x <- d[d$item == i, ]
  data.frame(item = i,
             m    = round(mean(x$resp), 2),
             sd   = round(sd(x$resp), 2),
             male = round(mean(x$resp[x$cov_sex == 2]), 2),
             fem  = round(mean(x$resp[x$cov_sex == 1]), 2))
}))

cat(sprintf("n by sex: male %d, female %d (Table 1: 127, 198)\n",
            length(unique(d$id[d$cov_sex == 2])),
            length(unique(d$id[d$cov_sex == 1]))))
hits <- sum(abs(as.matrix(obs[, -1]) - as.matrix(pub[, -1])) < 0.006)
print(merge(pub, obs, by = "item", suffixes = c("_pub", "_obs")))
cat(sprintf("%d of %d published values reproduced\n", hits, 4 * nrow(pub)))
cat(if (hits == 4 * nrow(pub)) "VERIFIED\n" else "FAIL\n")
