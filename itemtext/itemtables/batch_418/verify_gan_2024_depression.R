# verify_gan_2024_depression.R -- Step 5b mapping check for gan_2024_depression.
#
# Claim: live item codes 抑1..抑17 are HAMD-17 items 1..17 in the instrument's
# canonical numbering, and 抑16 / 抑162 are the two parts (a, b) of item 16
# (loss of weight). Item codes ARE the deposit's column names (no rename), and
# the deposit carries no labels, so the code->text tie is an inference from
# numbering. This script tests it against the paper.
#
# Route 3 (published subscale totals): Gan et al. (2024) Front Endocrinol
# 15:1390564, Table 2, reports M +/- SD for the HAMD total and its five Chinese
# HAMD factors. The canonical factor assignments are
#   somatization of anxiety (SA) = 10,11,12,15,17  (paper's per-item mean 0.40 = 2.02/5,
#                                    i.e. five items; the usual 13 is not in it here)
#   weight (W)                   = 16 (both parts 16a + 16b)
#   cognitive impairment (CI)    = 2,3,9
#   retardation (SU)             = 1,7,8,14
#   sleep disturbance (SD)       = 4,5,6
#   total                        = all 18 columns
# Route 2 (per-item range structure): canonical HAMD-17 rates items
# 1,2,3,7,8,9,10,11,15 on 0-4 and the rest on 0-2; any item observed above 2
# must be in the 0-4 set.
# Route 7 (marker): 抑3 (suicide) should be the least-endorsed item of its factor.
#
# What this does NOT establish: order WITHIN a factor. Sleep {4,5,6} are three
# 0-2 items that no route separates; {2,9}, {1,7,8,14} and {10,11,12,15,17}
# are only partly separated by range structure; 16a vs 16b is not separated.
# Item 13 is pinned by elimination (in the total, in no factor).

suppressMessages(library(irw))
TABLE <- "gan_2024_depression"

# Paper Table 2 (M, SD of raw factor totals).
PUB <- list(
  SA    = c(2.02, 1.475),
  W     = c(1.22, 1.533),
  CI    = c(0.64, 0.788),
  SU    = c(0.82, 1.145),
  SD    = c(2.37, 1.493),
  TOTAL = c(7.17, 3.367)
)
k <- function(v) paste0("抑", v)   # "抑" + number
FAC <- list(
  SA = k(c(10, 11, 12, 15, 17)),
  W  = k(c(16, 162)),
  CI = k(c(2, 3, 9)),
  SU = k(c(1, 7, 8, 14)),
  SD = k(c(4, 5, 6))
)
ALL <- k(c(1:17, 162))
FAC$TOTAL <- ALL

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
stopifnot(all(ALL %in% names(w)))

stat <- function(items) {
  # Two cells are missing (抑1, 抑2 for one patient each); the deposit's own factor
  # columns and the paper count them as 0, so sum with na.rm (n = 318 throughout).
  s <- rowSums(w[, items, drop = FALSE], na.rm = TRUE)
  c(mean(s), sd(s))
}

ok <- TRUE
cat(sprintf("%-6s %-28s %14s %14s\n", "factor", "items", "published M/SD", "live M/SD"))
for (f in names(FAC)) {
  o <- stat(FAC[[f]])
  hit <- abs(o[1] - PUB[[f]][1]) <= 0.006 && abs(o[2] - PUB[[f]][2]) <= 0.002
  ok <- ok && hit
  cat(sprintf("%-6s %-28s %6.2f/%6.3f %7.3f/%6.3f %s\n", f,
              if (f == "TOTAL") "all 18" else paste(sub("抑", "", FAC[[f]]), collapse = ","),
              PUB[[f]][1], PUB[[f]][2], o[1], o[2], if (hit) "ok" else "MISS"))
}

# Discrimination: every single swap of one item between two factors (and
# item 13 in/out) should break at least one published factor statistic.
facs <- c("SA", "W", "CI", "SU", "SD")
item13 <- k(13)
n_swaps <- 0; n_survive <- 0
for (a in facs) for (b in facs) if (a < b) {
  for (x in FAC[[a]]) for (y in FAC[[b]]) {
    A <- c(setdiff(FAC[[a]], x), y); B <- c(setdiff(FAC[[b]], y), x)
    oa <- stat(A); ob <- stat(B)
    n_swaps <- n_swaps + 1
    if (abs(oa[1] - PUB[[a]][1]) <= 0.006 && abs(oa[2] - PUB[[a]][2]) <= 0.002 &&
        abs(ob[1] - PUB[[b]][1]) <= 0.006 && abs(ob[2] - PUB[[b]][2]) <= 0.002)
      n_survive <- n_survive + 1
  }
}
for (a in facs) for (x in FAC[[a]]) {   # swap item 13 into a factor
  A <- c(setdiff(FAC[[a]], x), item13); oa <- stat(A)
  n_swaps <- n_swaps + 1
  if (abs(oa[1] - PUB[[a]][1]) <= 0.006 && abs(oa[2] - PUB[[a]][2]) <= 0.002)
    n_survive <- n_survive + 1
}
cat(sprintf("\ncross-factor single swaps tested: %d; still matching the paper: %d\n",
            n_swaps, n_survive))
ok <- ok && n_survive == 0

# Route 2: range structure.
mx <- tapply(d$resp, d$item, max, na.rm = TRUE)
canon04 <- k(c(1, 2, 3, 7, 8, 9, 10, 11, 15))
above2 <- names(mx)[mx > 2]
cat("items observed above 2:", paste(above2, collapse = " "),
    "| all in canonical 0-4 set:", all(above2 %in% canon04), "\n")
ok <- ok && all(above2 %in% canon04)

# Route 7: suicide marker.
mn <- tapply(d$resp, d$item, mean, na.rm = TRUE)
cat(sprintf("CI factor means: 2=%.3f 3(suicide)=%.3f 9=%.3f\n",
            mn[k(2)], mn[k(3)], mn[k(9)]))
ok <- ok && mn[k(3)] < min(mn[k(c(2, 9))])

cat("Not established: order within a factor (sleep 4/5/6; 16a/16b; partly 2/9,",
    "1/7/8/14, 10/11/12/15/17) -> PARTIAL.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
