# verify_milavic_2019_psisysf.R -- Step 5b, route 1 (per-item descriptive statistics).
#
# CLAIM UNDER TEST: item_text for PSIS-Y-SF_01..18 is the wording printed against
# rows 1..18 of Table 1 of Milavic et al. (2019), PLOS ONE 14(8):e0220930
# (doi:10.1371/journal.pone.0220930.t001).
#
# Table 1 publishes M, SD, %Min (share answering 1) and %Max (share answering 5)
# for each of the 18 items. Those four numbers per item are the falsifiable
# prediction: if the shipped wording were permuted, the live per-item tuple would
# line up with a DIFFERENT paper row. The script therefore does two things:
#   (a) checks each item against its own published tuple, and
#   (b) checks that the published tuple for row k is UNIQUELY closest to
#       PSIS-Y-SF_k among all 18 live items -- which is what makes this VERIFIED
#       rather than merely consistent.

suppressMessages(library(irw))

TABLE <- "milavic_2019_psisysf"
ITEMS <- sprintf("PSIS-Y-SF_%02d", 1:18)

# Milavic et al. 2019, Table 1 (rows 1-18, in printed order).
PUB <- data.frame(
  row  = 1:18,
  M    = c(4.21,3.81,4.27,3.49,2.94,3.75,2.45,3.10,2.59,2.95,2.63,2.77,4.51,3.94,3.73,2.45,2.28,2.12),
  SD   = c(0.917,1.117,0.897,0.978,0.983,0.948,1.159,1.096,1.148,1.182,1.204,1.145,0.856,1.081,1.054,1.052,1.074,0.987),
  pMin = c(2.3,3.9,0.7,2.3,5.9,1.3,22.0,9.5,18.1,14.1,21.7,15.1,1.0,3.0,2.3,16.4,26.0,29.3),
  pMax = c(45.7,34.2,52.3,16.4,5.6,22.7,6.9,11.2,7.2,8.9,7.2,7.9,69.1,38.5,28.6,5.6,3.6,3.0)
)

d <- irw::irw_fetch(TABLE)
obs <- data.frame(
  item = ITEMS,
  M    = as.numeric(tapply(d$resp, d$item, mean)[ITEMS]),
  SD   = as.numeric(tapply(d$resp, d$item, sd)[ITEMS]),
  pMin = as.numeric(tapply(d$resp, d$item, function(x) 100*mean(x == 1))[ITEMS]),
  pMax = as.numeric(tapply(d$resp, d$item, function(x) 100*mean(x == 5))[ITEMS])
)

cat(sprintf("%-14s %14s %14s %14s %14s\n", "item",
            "M pub/obs", "SD pub/obs", "%Min pub/obs", "%Max pub/obs"))
for (i in 1:18)
  cat(sprintf("%-14s %6.2f/%-7.2f %6.3f/%-7.3f %6.1f/%-7.1f %6.1f/%-7.1f\n",
              obs$item[i], PUB$M[i], obs$M[i], PUB$SD[i], obs$SD[i],
              PUB$pMin[i], obs$pMin[i], PUB$pMax[i], obs$pMax[i]))

dev <- pmax(abs(PUB$M - obs$M), abs(PUB$SD - obs$SD)/1,
            abs(PUB$pMin - obs$pMin)/10, abs(PUB$pMax - obs$pMax)/10)
cat(sprintf("\n(a) largest per-item deviation (rounding-scaled): %.4f  (tolerance 0.015)\n",
            max(dev)))

# (b) uniqueness: distance of every published row to every live item.
dist <- function(k, j) sqrt((PUB$M[k]-obs$M[j])^2 + (PUB$SD[k]-obs$SD[j])^2 +
                            ((PUB$pMin[k]-obs$pMin[j])/10)^2 + ((PUB$pMax[k]-obs$pMax[j])/10)^2)
best <- integer(18); margin <- numeric(18)
for (k in 1:18) {
  dd <- vapply(1:18, function(j) dist(k, j), numeric(1))
  o <- order(dd); best[k] <- o[1]; margin[k] <- dd[o[2]] - dd[o[1]]
}
cat("(b) nearest live item for each published row (want k -> k), with margin to runner-up:\n")
cat(sprintf("    row %2d -> %s  margin %.3f\n", 1:18, obs$item[best], margin), sep = "")

ok_a <- max(dev) <= 0.015
ok_b <- all(best == 1:18) && min(margin) > 0.02
cat(sprintf("\n(a) all 18 tuples match their own published row: %s\n", ok_a))
cat(sprintf("(b) all 18 published rows uniquely nearest their own item (min margin %.3f): %s\n",
            min(margin), ok_b))
cat("This distinguishes every item from every other item, including the two\n",
    "near-tied mean pairs (rows 5/10 at 2.94/2.95 and rows 7/16 both at 2.45),\n",
    "which %Min/%Max separate (5.9/5.6 vs 14.1/8.9; 22.0/6.9 vs 16.4/5.6).\n",
    "It does NOT verify the response-option anchors -- see provenance.\n", sep = "")

cat(if (ok_a && ok_b) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
