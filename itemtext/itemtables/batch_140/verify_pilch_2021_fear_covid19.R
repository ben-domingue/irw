# verify_pilch_2021_fear_covid19.R -- Step 5b mapping check.
#
# CLAIM: item codes Fear1..Fear7 are FCV-19S items 1..7 in the numbering used by
# Pilch, Kurasz & Turska-Kawa (2021, PeerJ 9:e11263) Table 1, which prints the
# administered Polish wording for each numbered item together with per-item
# statistics.
#
# FALSIFIABLE PREDICTION: the PeerJ paper's Sample 1 (N = 383) is essentially the
# same respondent pool as this IRW table (N = 387 complete cases), so its
# published per-item mean, SD, corrected item-total correlation and sex-split
# means should reproduce item by item under the identity mapping -- and under no
# other assignment of the seven codes to the seven numbered items.
#
# The test is a full permutation search over all 7! = 5040 assignments, scored by
# total absolute deviation across the five published statistics. Evidence is that
# the identity permutation is the UNIQUE minimum, by a wide margin.

suppressMessages(library(irw))

TABLE <- "pilch_2021_fear_covid19"
ITEMS <- paste0("Fear", 1:7)

# Pilch, Kurasz & Turska-Kawa (2021) PeerJ 9:e11263, Table 1
# ("Item translation and item-total correlation for the FCV-19S"),
# numbered items 1-7, Sample 1 columns.
PUB <- cbind(
  mean   = c(2.60, 2.42, 1.52, 1.95, 2.41, 1.49, 1.54),   # Mean total, N = 383
  sd     = c(1.04, 1.10, 0.66, 0.96, 1.12, 0.72, 0.77),
  itc    = c(0.70, 0.72, 0.66, 0.72, 0.68, 0.70, 0.68),   # corrected item-total r
  male   = c(2.35, 2.14, 1.36, 1.84, 2.07, 1.33, 1.38),   # Mean males, N = 174
  female = c(2.80, 2.66, 1.67, 2.05, 2.69, 1.61, 1.67))   # Mean females, N = 209

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
m  <- as.matrix(w[, ITEMS])
mm <- m[complete.cases(m), ]
tot <- rowSums(mm)

OBS <- cbind(
  mean   = colMeans(m, na.rm = TRUE),
  sd     = apply(m, 2, sd, na.rm = TRUE),
  itc    = sapply(seq_len(7), function(j) cor(mm[, j], tot - mm[, j])),
  male   = tapply(d$resp[d$cov_gender == 2], d$item[d$cov_gender == 2], mean)[ITEMS],
  female = tapply(d$resp[d$cov_gender == 1], d$item[d$cov_gender == 1], mean)[ITEMS])

cat(sprintf("complete cases: %d (PeerJ Sample 1: N = 383)\n\n", nrow(mm)))
cat(sprintf("%-6s %s\n", "item",
    paste(sprintf("%14s", c("mean pub/obs", "sd pub/obs", "itc pub/obs",
                            "male pub/obs", "female pub/obs")), collapse = " ")))
for (i in 1:7)
  cat(sprintf("%-6s %s\n", ITEMS[i],
      paste(sprintf("%14s", sprintf("%.2f/%.2f", PUB[i, ], OBS[i, ])), collapse = " ")))

perms <- function(v) {
  if (length(v) == 1) return(matrix(v))
  do.call(rbind, lapply(seq_along(v), function(i) cbind(v[i], perms(v[-i]))))
}
P <- perms(1:7)
cost <- apply(P, 1, function(p) sum(abs(OBS[p, , drop = FALSE] - PUB)))
o <- order(cost)

cat(sprintf("\ntotal |obs - published| over 35 statistics, identity mapping: %.4f\n",
            sum(abs(OBS - PUB))))
cat("best three of all 5040 permutations:\n")
for (k in 1:3)
  cat(sprintf("  %-9s cost = %.4f\n", paste(P[o[k], ], collapse = ""), cost[o[k]]))

ok <- identical(as.integer(P[o[1], ]), 1:7) && cost[o[2]] > cost[o[1]]
cat(sprintf("\nidentity is the unique minimum: %s (runner-up is %.1fx worse)\n",
            ok, cost[o[2]] / cost[o[1]]))
cat("This distinguishes every item from every other item: no other assignment of\n",
    "the seven codes reproduces the published statistics. It does NOT verify the\n",
    "response-option anchors (resp 1 = strongly disagree .. 5 = strongly agree),\n",
    "which are taken from the source papers' prose and are not testable here.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
