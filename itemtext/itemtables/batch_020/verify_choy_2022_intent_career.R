# verify_choy_2022_intent_career.R
#
# STATUS: this table is BLOCKED -- no __items.csv was written, because PLOS ONE
# 10.1371/journal.pone.0279411 Table 1 prints only ONE "Sample item" for the Intent
# construct ("I will join the hospitality workforce after graduation") and never
# prints wording for the other two items, nor a number for the one it does print.
#
# What CAN be checked, and is checked here, is the weaker claim recorded in
# provenance: that the live item codes Intent1/Intent2/Intent3 are the paper's own
# item numbering (Table 4 "Item 1/2/3" under the Intent column). The paper publishes
# standardized CFA factor loadings per item number, plus the scale mean and SD.
# A 3-indicator one-factor model is just-identified, so the standardized loadings are
# computable in closed form from the item correlations:
#     l1 = sqrt(r12*r13/r23), l2 = sqrt(r12*r23/r13), l3 = sqrt(r13*r23/r12)
# If Intent1..3 were permuted relative to the paper's numbering, the loading triple
# would come out permuted too -- and .90/.66/.92 is a distinctive, non-flat pattern,
# so item 2 in particular is separated from items 1 and 3 by ~0.25.
#
# This does NOT establish which item text belongs to which code -- no wording exists
# for two of the three items. It only pins the numbering.

suppressMessages(library(irw))

TABLE <- "choy_2022_intent_career"

# PLOS ONE 10.1371/journal.pone.0279411, Table 4 ("CFA solution"), Intent column.
PUB_LOADINGS <- c(Intent1 = 0.90, Intent2 = 0.66, Intent3 = 0.92)
PUB_MEAN <- 3.87
PUB_SD   <- 1.02
TOL_LOAD <- 0.03
TOL_MEAN <- 0.02

d <- as.data.frame(irw::irw_fetch(TABLE))
items <- c("Intent1", "Intent2", "Intent3")
ids <- sort(unique(d$id))
w <- sapply(items, function(it) {
  s <- d[d$item == it, ]
  s$resp[match(ids, s$id)]
})
w <- as.data.frame(w)

r <- cor(w, use = "pairwise.complete.obs")
obs <- c(
  Intent1 = sqrt(r[1, 2] * r[1, 3] / r[2, 3]),
  Intent2 = sqrt(r[1, 2] * r[2, 3] / r[1, 3]),
  Intent3 = sqrt(r[1, 3] * r[2, 3] / r[1, 2])
)

cat(sprintf("%-9s %10s %10s %8s\n", "item", "published", "observed", "diff"))
for (i in seq_along(obs))
  cat(sprintf("%-9s %10.2f %10.3f %8.3f\n", names(obs)[i],
              PUB_LOADINGS[i], obs[i], obs[i] - PUB_LOADINGS[i]))

scale_mean <- mean(rowMeans(w, na.rm = TRUE), na.rm = TRUE)
scale_sd   <- sd(rowMeans(w, na.rm = TRUE), na.rm = TRUE)
cat(sprintf("\nscale mean  published %.2f  observed %.3f  diff %.3f\n",
            PUB_MEAN, scale_mean, scale_mean - PUB_MEAN))
cat(sprintf("scale SD    published %.2f  observed %.3f  diff %.3f\n",
            PUB_SD, scale_sd, scale_sd - PUB_SD))

# Would any permutation of the codes also fit? Report the best rival.
perms <- list(c(1,3,2), c(2,1,3), c(2,3,1), c(3,1,2), c(3,2,1))
worst_id <- max(abs(obs - PUB_LOADINGS))
rival <- min(sapply(perms, function(p) max(abs(obs[p] - PUB_LOADINGS))))
cat(sprintf("\nidentity mapping worst deviation: %.3f\n", worst_id))
cat(sprintf("best rival permutation worst deviation: %.3f\n", rival))

cat("\nNote: this pins the CODE NUMBERING only, and only partly. Published .90/.66/.92\n",
    "separates item 2 from items 1 and 3 decisively (0.25 apart), but items 1 and 3\n",
    "differ by only .02, so an Intent1<->Intent3 swap fits nearly as well (worst\n",
    "deviation .022 vs .012 for the identity) and this route does NOT rule it out.\n",
    "Separately, the paper publishes no wording at all for two of the three items and\n",
    "does not number the single sample item it does print, so no item_text was shipped\n",
    "for this table.\n", sep = "")

ok <- worst_id <= TOL_LOAD &&
      abs(scale_mean - PUB_MEAN) <= TOL_MEAN &&
      rival > worst_id
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
