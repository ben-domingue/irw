# verify_wang_2015_donation_decision.R -- Step 5b, route 1 (published per-subgroup
# per-item statistics) + route 2 (per-item response range).
#
# Claim under test: item "distress" carries "After reading the child's [children's]
# story I felt worried, upset and sad.", item "sympathy" carries "I felt sympathy and
# compassion towards the sick child [children].", and item "wtc_amount" carries the
# 100-dollar/yuan donation question. Wang, Tang & Wang (2015) PLOS ONE 10(9):e0138219
# publishes cell means for distress and sympathy separately and contributor
# percentages for WTC, so a distress/sympathy swap breaks every one of them.

suppressMessages(library(irw))
TABLE <- "wang_2015_donation_decision"
TOL <- 0.03   # paper rounds to 2 dp

d <- irw::irw_fetch(TABLE)
d$cond <- as.integer(d$cov_condition)          # 1 single-unid 2 single-id 3 group-unid 4 group-id
d$group <- d$cond >= 3
m <- function(item, ...) {
  s <- d[d$item == item, ]
  keep <- rep(TRUE, nrow(s)); f <- list(...)
  for (nm in names(f)) keep <- keep & s[[nm]] %in% f[[nm]]
  mean(s$resp[keep])
}
pct <- function(item, ...) {
  s <- d[d$item == item, ]
  keep <- rep(TRUE, nrow(s)); f <- list(...)
  for (nm in names(f)) keep <- keep & s[[nm]] %in% f[[nm]]
  100 * mean(s$resp[keep] > 0)
}

# published value, label, observed
chk <- list(
  list(4.60, "distress, Chinese, group of 8 (Results, Ratings of distress)",
       m("distress", cov_country = "Chinese", group = TRUE)),
  list(3.35, "distress, Chinese, single victim (Results, Ratings of distress)",
       m("distress", cov_country = "Chinese", group = FALSE)),
  list(6.05, "sympathy, American, single identified (Results, Ratings of sympathy)",
       m("sympathy", cov_country = "American", cond = 2)),
  list(4.90, "sympathy, American, single unidentified",
       m("sympathy", cov_country = "American", cond = 1)),
  list(5.86, "sympathy, Chinese, group identified",
       m("sympathy", cov_country = "Chinese", cond = 4)),
  list(5.56, "sympathy, Chinese, group unidentified",
       m("sympathy", cov_country = "Chinese", cond = 3)),
  list(4.07, "sympathy, Chinese, single identified",
       m("sympathy", cov_country = "Chinese", cond = 2)),
  list(4.16, "sympathy, Chinese, single unidentified",
       m("sympathy", cov_country = "Chinese", cond = 1))
)
cat(sprintf("%-58s %9s %9s %8s\n", "statistic", "published", "observed", "diff"))
worst <- 0
for (x in chk) {
  cat(sprintf("%-58s %9.2f %9.2f %8.3f\n", x[[2]], x[[1]], x[[3]], x[[3]] - x[[1]]))
  worst <- max(worst, abs(x[[3]] - x[[1]]))
}

# WTC: contributor percentages (Results, "The percentage of contributors"), 1 dp
pchk <- list(
  list(97.1, "wtc_amount, Chinese group, % donating > 0", pct("wtc_amount", cov_country = "Chinese", group = TRUE)),
  list(93.2, "wtc_amount, Chinese single, % donating > 0", pct("wtc_amount", cov_country = "Chinese", group = FALSE)),
  list(90.4, "wtc_amount, American group, % donating > 0", pct("wtc_amount", cov_country = "American", group = TRUE)),
  list(81.2, "wtc_amount, American single, % donating > 0", pct("wtc_amount", cov_country = "American", group = FALSE)),
  list(90.0, "wtc_amount, American single identified, % donating > 0", pct("wtc_amount", cov_country = "American", cond = 2)),
  list(72.5, "wtc_amount, American single unidentified, % donating > 0", pct("wtc_amount", cov_country = "American", cond = 1))
)
pworst <- 0
for (x in pchk) {
  cat(sprintf("%-58s %9.1f %9.1f %8.2f\n", x[[2]], x[[1]], x[[3]], x[[3]] - x[[1]]))
  pworst <- max(pworst, abs(x[[3]] - x[[1]]))
}

# Route 2: wtc_amount is the only item on the 0-100 by-tens range.
rng <- tapply(d$resp, d$item, function(v) paste0(min(v), "-", max(v), " (", length(unique(v)), " levels)"))
cat("\nper-item observed response ranges:\n")
for (i in names(rng)) cat(sprintf("  %-12s %s\n", i, rng[i]))

cat(sprintf("\nlargest mean deviation: %.3f (tol %.2f); largest %% deviation: %.2f (tol 0.15)\n",
            worst, TOL, pworst))
cat("A distress<->sympathy swap would move every one of the eight cell means by 0.8-1.4\n",
    "points, so this separates those two items; wtc_amount is separated by range as well.\n",
    "Not established by this route: the option_text<->resp mapping (option_text is blank\n",
    "throughout -- the paper publishes only the two anchors of a '7-point' scale that the\n",
    "data store as eight codes 0-7).\n", sep = "")

cat(if (worst <= TOL && pworst <= 0.15) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
