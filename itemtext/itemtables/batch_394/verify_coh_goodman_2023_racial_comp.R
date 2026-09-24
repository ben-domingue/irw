# verify_coh_goodman_2023_racial_comp.R -- batch_394
#
# Claim: quest_rc1..quest_rc10 follow the order of the PRCM's ten environments
# in the paper (Goodman et al., JMIR Public Health Surveill 2024;10:e55461) and
# its Multimedia Appendix 1 Figures S1-S10: 1 workplace, 2 place of worship,
# 3 HS, 4 HS classroom, 5 junior HS, 6 junior HS classroom, 7 current
# neighborhood, 8 neighborhood growing up, 9 current block, 10 block growing up.
# And resp 1..6 = pictures A..F = all Black .. all White, 7 = not applicable.
#
# The code derivation is "code IS the source column name" (data/coh_goodman_2023.py
# melts the openICPSR xlsx columns as-is), but the column name quest_rcN carries no
# content, and the codebook (openICPSR, Cloudflare-gated) was not reachable. So the
# item->environment tie is an ORDER inference and is checked here structurally.
#
# What this does NOT establish: within each pair it cannot tell the setting from
# its classroom (rc3 vs rc4, rc5 vs rc6) or the neighborhood from the block
# (rc7 vs rc9, rc8 vs rc10); HS vs junior HS (rc3/4 vs rc5/6) is only weakly
# supported; workplace vs worship rests on the N/A count and a race gap.

suppressMessages(library(irw))
TABLE <- "coh_goodman_2023_racial_comp"
d <- as.data.frame(irw::irw_fetch(TABLE))
ok <- TRUE
chk <- function(name, cond) { cat(sprintf("[%s] %s\n", if (cond) "ok" else "FAIL", name)); if (!cond) ok <<- FALSE }
it <- paste0("quest_rc", 1:10)

# 1. resp direction: race code 2 is the majority (Black, 66% in the paper's Table 2).
ids <- unique(d[, c("id", "cov_race_cat")]); print(table(ids$cov_race_cat))
chk("race code 2 is the majority (Black)", which.max(table(ids$cov_race_cat)) == 2)
v <- d[d$resp <= 6, ]
m <- tapply(v$resp, list(v$item, v$cov_race_cat), mean)[it, ]
print(round(m, 2))
chk("every item: Black mean < White mean (code 1 = all Black end)", all(m[, "2"] < m[, "1"]))

# 2. code 8 occurs only on the four school items (rc3-rc6)
tab <- table(d$item, d$resp)[it, ]; print(tab)
has8 <- tab[, "8"] > 0
chk("code 8 used by exactly rc3-rc6 (school block)", identical(unname(which(has8)), 3:6))
chk("rc1 (workplace) has the most not-applicable (code 7)", which.max(tab[, "7"]) == 1)

# 3. pair structure from inter-item correlations (codes 7/8 set missing)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w)); w <- w[, it]; w[w >= 7] <- NA
R <- cor(w, use = "pairwise"); print(round(R, 2))
top <- sapply(it, function(x) { r <- R[x, ]; r[x] <- NA; names(which.max(r)) })
print(top)
pairs <- list(c(3, 4), c(5, 6), c(7, 9), c(8, 10))
for (p in pairs) chk(sprintf("rc%d and rc%d are each other's top correlate", p[1], p[2]),
    top[it[p[1]]] == it[p[2]] && top[it[p[2]]] == it[p[1]])

# 4. childhood residential (rc8, rc10) track the school items; current (rc7, rc9) do not
sch <- it[3:6]
kid <- mean(R[it[c(8, 10)], sch]); now <- mean(R[it[c(7, 9)], sch])
cat(sprintf("mean r with school items: growing-up pair %.2f, current pair %.2f\n", kid, now))
chk("growing-up pair correlates more with schools than current pair", kid > now + 0.15)

cat("Not established: setting vs classroom within rc3/4 and rc5/6; neighborhood vs block\n",
    "within rc7/9 and rc8/10; HS vs junior HS is only weakly supported.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
