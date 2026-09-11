# verify_smacof_pvq40.R -- batch_176
#
# STATUS: the table is BLOCKED on instrument rights (see notes_smacof_pvq40.csv), so no
# __items.csv ships and this script carries no mapping_verification outcome. It exists to
# BANK the mapping analysis for a later round if the block is lifted, so nobody re-derives it.
#
# Claims under test (both would be needed to ship PVQ40 text against this table):
#   A. resp direction: live resp 1 = "very much like me" ... 6 = "not like me at all",
#      i.e. the REVERSE of the smacof PVQ40.Rd ("1 ... not at all like me, 6 ... very much
#      like me"). Prediction: value means (low = important) track the pan-cultural value
#      hierarchy of Schwartz & Bardi (2001, JCCP 32:268) -- BE, SD, UN, SE, CO, HE, AC, ST,
#      TR, PO -- positively; under the Rd direction they would track it negatively.
#   B. item codes: smacof's column ORDER is the PVQ40 questionnaire order (the ten value
#      prefixes reproduce the PVQ40 value-per-position sequence at all 40 positions), so
#      the code at position k is PVQ40 item k. Within tradition that makes tr3=9, tr4=20
#      (religious belief), tr1=25, tr2=38 -- NOT tr1..tr4 = 9,20,25,38. Predictions:
#        - tr4 is the religion marker: largest SD of all 40 items, largest share at the
#          "not like me at all" end;
#        - the two nature items (19, 40 = un3, un6) are the most correlated UN pair;
#        - the two national-security items (14, 35 = se2, se5) are the most correlated SE pair;
#        - religion (20 = tr4) and traditional customs (25 = tr1) are the most correlated TR pair.
#
# What this does NOT establish: order among items that share no distinctive content signal
# (e.g. ac1..ac4, he1..he3, st1..st3, po1..po3, sd1..sd4, co*, be*) and swaps WITHIN each
# tested pair (un3<->un6, se2<->se5, tr4<->tr1 pass equally). That is PARTIAL, not VERIFIED.
# The gender check (power higher for men, benevolence higher for women under direction A)
# needs smacof's Gender attribute, which the IRW table does not carry; its numbers are in
# notes_smacof_pvq40.csv instead.

suppressMessages(library(irw))
TABLE <- "smacof_pvq40"

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
x <- w[, setdiff(names(w), "id")]
v <- substr(names(x), 1, 2)

# --- A. direction via value hierarchy ------------------------------------------------
vm <- sapply(split(names(x), v), function(cols) mean(rowMeans(x[, cols, drop = FALSE], na.rm = TRUE)))
hier <- c(be = 1, sd = 2, un = 3, se = 4, co = 5, he = 6, ac = 7, st = 8, tr = 9, po = 10)
vm <- vm[names(hier)]
rho <- cor(rank(vm), hier, method = "spearman")
cat("A. value means (live resp), in pan-cultural hierarchy order:\n")
print(round(vm, 2))
cat(sprintf("Spearman(value mean, hierarchy rank) = %+.2f  (expect > +0.7 if 1 = very much like me)\n\n", rho))
okA <- rho > 0.7

# --- B. positional code mapping ------------------------------------------------------
sds <- sapply(x, sd, na.rm = TRUE)
p6 <- sapply(x, function(z) mean(z == 6, na.rm = TRUE))
cat("B1. top-3 item SDs:\n"); print(round(sort(sds, decreasing = TRUE)[1:3], 2))
cat("B1. top-3 share at resp=6:\n"); print(round(sort(p6, decreasing = TRUE)[1:3], 2))
okB1 <- names(which.max(sds)) == "tr4" && names(which.max(p6)) == "tr4"

R <- cor(x, use = "pairwise.complete.obs")
toppair <- function(pref) {
  cols <- names(x)[v == pref]
  S <- R[cols, cols]; S[lower.tri(S, diag = TRUE)] <- NA
  k <- which(S == max(S, na.rm = TRUE), arr.ind = TRUE)[1, ]
  cat(sprintf("B2. %s: most correlated pair %s-%s r=%.2f\n", pref, cols[k[1]], cols[k[2]], S[k[1], k[2]]))
  sort(c(cols[k[1]], cols[k[2]]))
}
okB2 <- identical(toppair("un"), c("un3", "un6")) &&
        identical(toppair("se"), c("se2", "se5")) &&
        identical(toppair("tr"), c("tr1", "tr4"))

cat("\nThis route pins direction, the religion marker and three within-value pairs; it does\n",
    "not separate items without a distinctive signal, nor swaps within the tested pairs (PARTIAL).\n", sep = "")
cat(if (okA && okB1 && okB2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
