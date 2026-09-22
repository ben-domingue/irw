# verify_kermen_2022_self_efficacy.R -- Step 5b, route 1 (per-item statistics)
# + route 7 (marker item).
#
# CLAIM UNDER TEST: the live item codes b1..b17 carry the item NUMBERS of the
# Turkish General Self-Efficacy Scale (Genel Ozyeterlilik Olcegi; Yildirim &
# Ilhan 2010, Turk Psikiyatri Dergisi 21(4):301-308), whose Table 1 prints all
# 17 items numbered 1-17. The source .sav has no variable labels at all, so
# nothing at the source ties b<i> to item <i>; the mapping is an inference and
# this is the test of it.
#
# FALSIFIABLE PREDICTION: that adaptation paper's Table 3 publishes per-item
# means and corrected item-total correlations for its own (independent) sample
# of 895 Turkish adults. If b<i> really is item <i>, those two profiles should
# line up with the live high-school sample in index order, and not under a
# permutation. If item_text were permuted across items, it would not.

suppressMessages(library(irw))
TABLE <- "kermen_2022_self_efficacy"

# Yildirim & Ilhan (2010) Table 3, items 1..17.
PUB_R    <- c(.33,.33,.44,.43,.47,.53,.46,.16,.27,.50,.42,.46,.23,.31,.40,.52,.40)
PUB_MEAN <- c(3.59,3.41,4.02,3.55,4.17,3.81,3.56,3.49,4.01,3.71,3.44,3.91,3.33,3.38,4.17,4.18,3.59)

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
w <- w[, paste0("b", 1:17)]
w <- w[complete.cases(w), ]
tot <- rowSums(w)

obs_r    <- sapply(1:17, function(i) cor(w[[i]], tot - w[[i]]))
obs_mean <- sapply(1:17, function(i) mean(w[[i]]))

cat(sprintf("n complete cases: %d\n\n", nrow(w)))
cat(sprintf("%-5s %11s %9s   %11s %9s\n",
            "item", "pub item-r", "obs", "pub mean", "obs"))
for (i in 1:17)
    cat(sprintf("b%-4d %11.2f %9.3f   %11.2f %9.2f\n",
                i, PUB_R[i], obs_r[i], PUB_MEAN[i], obs_mean[i]))

r_itemtotal <- cor(obs_r, PUB_R)
r_means     <- cor(obs_mean, PUB_MEAN)

set.seed(1)
null_it <- replicate(20000, cor(sample(obs_r), PUB_R))
null_mn <- replicate(20000, cor(sample(obs_mean), PUB_MEAN))
p_it <- mean(null_it >= r_itemtotal)
p_mn <- mean(null_mn >= r_means)

cat(sprintf("\nitem-total profile: r = %.3f, permutation p = %.4f (20000 draws)\n",
            r_itemtotal, p_it))
cat(sprintf("item-mean profile : r = %.3f, permutation p = %.4f\n", r_means, p_mn))

# Route 7, marker item: item 8 ("Hosuma gitmeyen bir sey yapmak zorunda
# kaldigimda...") has by far the weakest item-total correlation in the
# published table (.16, next lowest .23). It should be weakest here too.
cat(sprintf("weakest observed item-total: b%d (%.3f); published weakest: item %d (%.2f)\n",
            which.min(obs_r), min(obs_r), which.min(PUB_R), min(PUB_R)))

# What this does NOT establish: the route pins the GLOBAL alignment -- the
# identity ordering against a permuted one -- not each item individually. Of the
# 136 single transpositions, 23 nudge the combined fit slightly upward (largest
# +0.09 on a combined-correlation scale of 2.0), because the published statistics
# come from a different sample (895 adults vs 325 high-school students). So a
# swap between two items with near-identical published statistics is not excluded
# by this test, and the verification status is PARTIAL, not VERIFIED.
#
# Also not established by this script: the direction of option_text. That rests
# on the total, sum(b1..b17), reproducing the source paper's reported
# self-efficacy mean/SD of 61.54/9.75 in the scored 17-85 metric, together with
# all 17 corrected item-total correlations being positive -- i.e. the 11 items
# the adaptation paper declares reverse-scored are stored already reversed.
cat(sprintf("\nstored total: mean %.2f, SD %.2f (Kermen & Yuksel Table 1: 61.54 / 9.75)\n",
            mean(tot), sd(tot)))
cat(sprintf("all 17 corrected item-total correlations positive: %s (min %.3f)\n",
            all(obs_r > 0), min(obs_r)))

ok <- r_itemtotal >= 0.6 && p_it <= 0.01 && which.min(obs_r) == 8 &&
      all(obs_r > 0) && abs(mean(tot) - 61.54) < 0.05
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
