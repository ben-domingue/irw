# verify_fredrickson_2015_mhcsf.R
#
# CLAIM UNDER TEST: live item code MHCSF_i carries the wording of MHC-SF item i
# (Keyes' canonical numbering), i = 1..14.
#
# FALSIFIABLE PREDICTION: S1 File Table S1 of Fredrickson et al. (2015),
# PLOS ONE 10(3):e0121839, publishes standardized CFA loadings and t-statistics
# for every one of the 14 items, in two models (1-factor total well-being; the
# canonical 3-factor hedonic[1-3] / social[4-8] / psychological[9-14] model),
# fitted to "n = 121 with complete data on 14 MHC-SF items". The live IRW table
# has exactly 121 complete cases. Refitting both models on the live data must
# reproduce each item's published pair, AND each live item's (t_1f, t_3f) pair
# must be nearer to its OWN published pair than to any other item's -- which is
# what would break if any two items' text were swapped.
#
# Note the 3-factor model's item->factor allocation is itself part of the claim:
# it is the canonical Keyes clustering that the shipped item_text assumes.

suppressMessages({library(irw); library(lavaan)})

TABLE <- "fredrickson_2015_mhcsf"
ITEMS <- paste0("MHCSF_", 1:14)

# Fredrickson et al. (2015) S1 File, Table S1, panel B. Standardized loading and
# t-statistic, columns "1-d Total well-being" and "3-d Hedonic Social Psychological".
PUB <- data.frame(
  load1 = c(.71,.73,.79,.83,.69,.57,.62,.57,.79,.78,.78,.66,.77,.73),
  t1    = c(14.47,16.07,21.45,25.59,13.75,8.78,10.54,8.81,21.57,20.19,20.33,11.97,19.21,16.12),
  load3 = c(.84,.85,.82,.86,.72,.60,.65,.59,.82,.79,.79,.66,.79,.74),
  t3    = c(24.02,24.83,21.91,27.00,14.67,9.59,11.06,9.17,23.97,20.78,20.12,12.09,20.57,16.27))
PUB_FIT <- c(chisq1 = 209.99, df1 = 77, chisq3 = 162.41, df3 = 74, n = 121)

d <- as.data.frame(irw::irw_fetch(TABLE))
d$item <- as.character(d$item); d$resp <- as.numeric(d$resp)
w <- reshape(d[, c("id","item","resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
cc <- w[complete.cases(w[, ITEMS]), ITEMS]
cat(sprintf("complete cases: live %d vs published n = %d\n", nrow(cc), PUB_FIT["n"]))

f1 <- lavaan::cfa(paste("F =~", paste(ITEMS, collapse = "+")), data = cc, std.lv = TRUE)
f3 <- lavaan::cfa('H =~ MHCSF_1+MHCSF_2+MHCSF_3
                   S =~ MHCSF_4+MHCSF_5+MHCSF_6+MHCSF_7+MHCSF_8
                   P =~ MHCSF_9+MHCSF_10+MHCSF_11+MHCSF_12+MHCSF_13+MHCSF_14',
                  data = cc, std.lv = TRUE)
grab <- function(f) { s <- lavaan::standardizedSolution(f); s <- s[s$op == "=~", ]; s[match(ITEMS, s$rhs), ] }
s1 <- grab(f1); s3 <- grab(f3)

cat("\nmodel fit (live vs published):\n")
fm1 <- lavaan::fitMeasures(f1, c("chisq","df")); fm3 <- lavaan::fitMeasures(f3, c("chisq","df"))
cat(sprintf("  1-factor  chisq %8.2f vs %8.2f   df %3.0f vs %3.0f\n", fm1[1], PUB_FIT["chisq1"], fm1[2], PUB_FIT["df1"]))
cat(sprintf("  3-factor  chisq %8.2f vs %8.2f   df %3.0f vs %3.0f\n", fm3[1], PUB_FIT["chisq3"], fm3[2], PUB_FIT["df3"]))

cat("\nper-item loadings and t-statistics, live vs published:\n")
cat(sprintf("%-9s %13s %13s | %13s %13s\n", "item", "load1 l/p", "t1 l/p", "load3 l/p", "t3 l/p"))
for (i in 1:14)
  cat(sprintf("%-9s %6.2f/%5.2f %6.2f/%5.2f | %6.2f/%5.2f %6.2f/%5.2f\n",
              ITEMS[i], s1$est.std[i], PUB$load1[i], s1$z[i], PUB$t1[i],
              s3$est.std[i], PUB$load3[i], s3$z[i], PUB$t3[i]))
worst_load <- max(abs(c(s1$est.std - PUB$load1, s3$est.std - PUB$load3)))
cat(sprintf("\nlargest loading deviation: %.4f (published values are rounded to 2 dp)\n", worst_load))

# The discriminating test: nearest-published-neighbour on the (t1, t3) pair.
L <- cbind(s1$z, s3$z); P <- cbind(PUB$t1, PUB$t3)
D <- as.matrix(dist(rbind(L, P)))[1:14, 15:28]
nn <- apply(D, 1, which.min)
self <- diag(D); margin <- sapply(1:14, function(i) { s <- sort(D[i, ]); s[2] - s[1] })
cat("\nnearest published item for each live item (want 1..14 in order):\n  ", paste(nn, collapse = " "), "\n")
cat(sprintf("%-9s %10s %10s\n", "item", "self-dist", "margin"))
for (i in 1:14) cat(sprintf("%-9s %10.3f %10.3f\n", ITEMS[i], self[i], margin[i]))
cat(sprintf("\nworst self-distance %.3f vs smallest margin to a rival item %.3f\n", max(self), min(margin)))

ok <- all(nn == 1:14) && worst_load <= 0.02 && max(self) < min(margin)

cat("\nWhat this does NOT establish: it pins the live item CODES to the paper's item\n",
    "NUMBERS 1-14. Tying those numbers to the wording relies on Table S1 footnote 2\n",
    "(\"Items are ordered as in ... the MHC-SF instrument\") plus the published\n",
    "item-factor allocation matching Keyes' canonical clusters 1-3 / 4-8 / 9-14.\n",
    "It also says nothing about which of the two sanctioned wordings of item 6 was\n",
    "administered -- see this table's provenance note.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
