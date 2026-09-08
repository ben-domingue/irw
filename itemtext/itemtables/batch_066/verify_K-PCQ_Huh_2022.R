# verify_K-PCQ_Huh_2022.R -- Step 5b re-runnable mapping check.
#
# CLAIM UNDER TEST: live item CravN carries the text of item N of the deposit's
# Supplement 1 ("The Korean version of the Pornography Craving Questionnaires
# (PCQ)", doi:10.7910/DVN/SHCUI4, file Suppl_1_Korean_translatioin_PCQ), i.e.
# Crav11 = "바로 지금 음란물을 보는 중이라면, 심장이 더 빨리 뛸 것이다"
# ("My heart would beat faster if I were watching porn right now").
#
# THE RIVAL: the source paper's own Table 1 (Kim et al. 2021, Psychiatry
# Investig 18(6):530, doi:10.30773/pi.2020.0401) prints the same 12 items in a
# DIFFERENT order from Supplement 1. Reading Table 1's numbering onto the data
# would put "If I watched porn right now, I would have difficulty stopping" on
# Crav1 and "My heart would beat faster..." on Crav3. This script tests the two
# numberings against the data.
#
# ROUTE A (paper Table 2, 66 published inter-item correlations): establishes
#   which numbering the paper's ANALYSES use, by comparing the observed
#   correlation matrix to the published one under identity vs under the
#   Table 1 -> Supplement 1 permutation.
# ROUTE B (content marker): the one physiological item ("heart would beat
#   faster") should be the psychometric odd-one-out among 11 cognitive /
#   motivational items -- and the paper reports exactly one misfitting item,
#   "the outfit mean square value of item 11 was 2.3367".
#
# Deliberately NOT re-checked here: item and resp SETS (validate_items.R did
# that) and row counts.

suppressMessages(library(irw))

TABLE <- "K-PCQ_Huh_2022"
ITEMS <- paste0("Crav", 1:12)

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
M <- as.matrix(w[, ITEMS])
M <- M[complete.cases(M), , drop = FALSE]
cat(sprintf("live table: %d responses, %d complete-case respondents x 12 items\n\n",
            nrow(d), nrow(M)))

O <- cor(M)

## ---- published Table 2 (Kim et al. 2021), n = 226 -------------------------
P <- matrix(NA_real_, 12, 12)
cells <- list(
  c(2,1,.509),
  c(3,1,.516), c(3,2,.707),
  c(4,1,.558), c(4,2,.694), c(4,3,.761),
  c(5,1,.427), c(5,2,.541), c(5,3,.574), c(5,4,.560),
  c(6,1,.436), c(6,2,.474), c(6,3,.564), c(6,4,.550), c(6,5,.608),
  c(7,1,.471), c(7,2,.569), c(7,3,.629), c(7,4,.677), c(7,5,.547), c(7,6,.696),
  c(8,1,.474), c(8,2,.610), c(8,3,.725), c(8,4,.650), c(8,5,.661), c(8,6,.688), c(8,7,.783),
  c(9,1,.396), c(9,2,.521), c(9,3,.651), c(9,4,.612), c(9,5,.513), c(9,6,.596), c(9,7,.747), c(9,8,.767),
  c(10,1,.449), c(10,2,.586), c(10,3,.530), c(10,4,.666), c(10,5,.553), c(10,6,.588), c(10,7,.679), c(10,8,.652), c(10,9,.597),
  c(11,1,.388), c(11,2,.383), c(11,3,.350), c(11,4,.434), c(11,5,.458), c(11,6,.380), c(11,7,.425), c(11,8,.425), c(11,9,.332), c(11,10,.517),
  c(12,1,.412), c(12,2,.579), c(12,3,.685), c(12,4,.658), c(12,5,.576), c(12,6,.631), c(12,7,.806), c(12,8,.788), c(12,9,.760), c(12,10,.642), c(12,11,.442))
for (c3 in cells) P[c3[1], c3[2]] <- c3[3]

# Table 1 item k  ->  Supplement 1 item PERM[k], matched by content.
PERM <- c(5, 1, 11, 2, 7, 9, 8, 4, 6, 3, 10, 12)

dev_id <- c(); dev_pm <- c()
for (c3 in cells) {
  a <- c3[1]; b <- c3[2]; v <- c3[3]
  dev_id <- c(dev_id, abs(O[a, b] - v))
  dev_pm <- c(dev_pm, abs(O[PERM[a], PERM[b]] - v))
}

cat("ROUTE A -- 66 published inter-item correlations (paper Table 2, n=226)\n")
cat(sprintf("  identity numbering (Crav k = paper item k):  MAD %.4f, max %.4f\n",
            mean(dev_id), max(dev_id)))
cat(sprintf("  Table 1 numbering (rival permutation):       MAD %.4f, max %.4f\n",
            mean(dev_pm), max(dev_pm)))
cat("  sample of cells (published / identity / rival):\n")
for (k in c(3, 20, 45, 55, 66)) {
  c3 <- cells[[k]]; a <- c3[1]; b <- c3[2]
  cat(sprintf("    item %2d x %2d: %.3f / %.3f / %.3f\n",
              a, b, c3[3], O[a, b], O[PERM[a], PERM[b]]))
}
routeA <- mean(dev_id) < 0.5 * mean(dev_pm)
cat(sprintf("  -> paper's item numbering IS the column numbering: %s\n\n", routeA))

## ---- ROUTE B: the physiological marker item -------------------------------
meanr <- sapply(1:12, function(i) mean(O[i, -i]))
mns <- colMeans(M)
cat("ROUTE B -- per-item mean inter-item r and mean response\n")
ord <- order(meanr)
for (i in ord)
  cat(sprintf("  %-7s mean r %.3f   mean %.2f   sd %.2f\n",
              ITEMS[i], meanr[i], mns[i], sd(M[, i])))
odd <- which.min(meanr)
cat(sprintf("\n  weakest-correlating item: %s (%.3f); next weakest %s (%.3f)\n",
            ITEMS[odd], meanr[odd], ITEMS[ord[2]], meanr[ord[2]]))
cat(sprintf("  under the RIVAL reading the heart-rate item would be Crav3, whose mean r is %.3f (rank %d of 12)\n",
            meanr[3], which(ord == 3)))
cat("  the paper reports exactly one misfitting item: 'the outfit mean square value of item 11 was 2.3367'\n")
routeB <- odd == 11
cat(sprintf("  -> the odd-one-out sits at position 11, as Supplement 1's ordering requires: %s\n\n", routeB))

cat("NOT ESTABLISHED by either route: the order of the near-synonymous items\n",
    "WITHIN Supplement 1's list -- nothing here separates Crav3 from Crav8\n",
    "(intention items, mean r .636/.679) or Crav4 from Crav7 (hypothetical-\n",
    "consequence items, .641/.669). Their text rests on Supplement 1's own\n",
    "1-12 numbering matching the Crav1-Crav12 column suffixes. Hence PARTIAL.\n\n", sep = "")

cat(if (routeA && routeB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
