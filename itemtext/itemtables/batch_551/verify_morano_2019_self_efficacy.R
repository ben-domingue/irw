# verify_morano_2019_self_efficacy.R -- Step 5b check for batch_551.
#
# Claim: item codes Self-efficacy1..4 are the deposit's own column names
# (peerj-07-7402-s001.xlsx, sheet "Raw data"), tied by number to rows 1-4 of
# Scales S1 (peerj-07-7402-s002.pdf); resp 1..4 runs low -> high efficacy
# ("I run very slowly" = 1 ... "I run very fast" = 4), as S1 prints the 1-4
# header over the columns and the paper states ("from 1, indicating low
# efficacy ... to 4, representing high efficacy").
#
# Route (SKILL.md Step 5b route 3, published scale means): Morano et al. 2019
# Table 1 gives the self-efficacy scale M for each gender x age cell, split into
# two random half-samples. Pool the halves (n-weighted) and compare with the
# live data's mean item score per cell. This checks the resp DIRECTION on every
# item (a reversed item would pull the cell mean by ~(5-2m)/4) and that the
# stored values are raw 1-4. It does NOT distinguish the four items from each
# other: the paper publishes no per-item statistics, so the order
# Self-efficacy1..4 = run speed, exercise difficulty, muscle strength,
# tiredness rests on the number match between column names and S1 rows.

suppressMessages(library(irw))
TABLE <- "morano_2019_self_efficacy"

# Table 1: (n, M) per half-sample, self-efficacy scale
pub <- data.frame(
  gender = c("F","F","M","M","F","F","M","M"),
  age    = c(6,6,6,6,7,7,7,7),
  n      = c(1674,1673,1696,1696,1807,1806,1842,1841),
  M      = c(3.39,3.47,3.53,3.58,3.42,3.50,3.53,3.59))
pubcell <- do.call(rbind, lapply(split(pub, paste(pub$gender, pub$age)), function(s)
  data.frame(gender=s$gender[1], age=s$age[1], n=sum(s$n), M=sum(s$n*s$M)/sum(s$n))))

d <- irw::irw_fetch(TABLE)
pm <- aggregate(resp ~ id + cov_gender + cov_age, data=d, FUN=mean)
cat("cov_gender levels:", paste(unique(pm$cov_gender), collapse=","), "\n")
pm$g <- toupper(substr(as.character(pm$cov_gender),1,1))
pm$g[pm$g %in% c("G","W")] <- "F"; pm$g[pm$g %in% c("B")] <- "M"
obs <- aggregate(resp ~ g + cov_age, data=pm, FUN=function(x) c(n=length(x), m=mean(x)))
obs <- data.frame(gender=obs$g, age=obs$cov_age, n_obs=obs$resp[, "n"], M_obs=obs$resp[, "m"])
cmp <- merge(pubcell, obs, by=c("gender","age"))
cmp$diff <- cmp$M_obs - cmp$M
cmp$M_if_reversed <- 5 - cmp$M_obs
print(cmp, digits=4, row.names=FALSE)

ok_n <- nrow(cmp) == 4 && all(cmp$n == cmp$n_obs)
worst <- max(abs(cmp$diff))
cat(sprintf("\ncell n match: %s; largest |mean diff|: %.3f (tolerance 0.02)\n", ok_n, worst))
cat("Not established: which of the four items is which -- no per-item statistics are published.\n")
cat(if (ok_n && worst <= 0.02) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
