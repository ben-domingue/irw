# verify_gerber_2022_eas_temperament.R -- Step 5b re-runnable evidence.
#
# CLAIM UNDER TEST. The IRW item codes come from the raw column names in
# journal.pone.0276665.s001 ("<n>_PRE<SUBSCALE><k>[R]"), so each code carries a
# questionnaire POSITION n (1-20), a subscale, and a reverse-wording flag. The
# extraction assumes those positions are the canonical EAS item numbers, and
# takes each item's wording from the numbered EAS list published in Psicothema
# 2011;23(1):160-166 (Spanish) rendered in English in IJERPH 2022;19(3):1387
# Table 2. Two things that assumption predicts about the live data, and that a
# permuted mapping would break:
#
#   (A) The six items the column names mark reverse-worded (ACT2, ACT5, TIM2,
#       TIM3, TIM5, SOC4) are the six the shipped wording is reverse-worded for.
#       data/gerber_2022_swisscamp.py recodes exactly those as 6 - raw, so if the
#       polarity assignment were wrong, the recoded item would correlate
#       NEGATIVELY with its own subscale.
#   (B) The paper's Table 1 subscale means reproduce from the items assigned to
#       each subscale -- including which sociability item the paper dropped.
#
# NOT ESTABLISHED by this script: the order WITHIN a polarity class. The data
# cannot separate TIM2/TIM3/TIM5 from one another, ACT2 from ACT5, TIM1 from
# TIM4, ACT1/ACT3/ACT4, SOC1/SOC2/SOC3, or any two EMO items. That ordering
# rests on the 20/20 subscale + 6/6 reversal agreement between the raw column
# names and the published numbered EAS list, which is not a data check.

suppressMessages(library(irw))
TABLE <- "gerber_2022_eas_temperament"

# Gerber, Gentaz & Malsert (2022) PLOS ONE 17(10):e0276665, Table 1, pre-test.
PUB <- list(
  emotionality = c(camp = 2.62, camp_sd = 0.91, ctrl = 2.61, ctrl_sd = 0.80),
  activity     = c(camp = 3.39, camp_sd = 0.74, ctrl = 3.64, ctrl_sd = 0.75),
  sociability  = c(camp = 3.88, camp_sd = 0.87, ctrl = 4.15, ctrl_sd = 0.68),
  shyness      = c(camp = 2.55, camp_sd = 0.77, ctrl = 2.61, ctrl_sd = 0.75))
TOL <- 0.03

REV <- c("ACT2", "ACT5", "TIM2", "TIM3", "TIM5", "SOC4")
FAM <- list(activity = paste0("ACT", 1:5), emotionality = paste0("EMO", 1:5),
            sociability = paste0("SOC", 1:5), shyness = paste0("TIM", 1:5))

d <- as.data.frame(irw::irw_fetch(TABLE))
d1 <- d[d$wave == 1, ]

## ---- (A) polarity: every item correlates positively with its own subscale ----
w <- reshape(d1[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("resp.", "", names(w), fixed = TRUE)
items <- unlist(FAM, use.names = FALSE)
C <- cor(as.matrix(w[, items]), use = "pairwise.complete.obs")

cat("(A) mean correlation with own-subscale mates, wave 1\n")
cat(sprintf("%-6s %-13s %-9s %8s\n", "item", "subscale", "worded", "mean r"))
own_r <- setNames(numeric(length(items)), items)
for (f in names(FAM)) for (it in FAM[[f]]) {
  mates <- setdiff(FAM[[f]], it)
  own_r[it] <- mean(C[it, mates], na.rm = TRUE)
  cat(sprintf("%-6s %-13s %-9s %+8.3f\n", it, f,
              if (it %in% REV) "reverse" else "direct", own_r[it]))
}
neg <- names(own_r)[own_r <= 0]
cat(sprintf("items with non-positive own-subscale r: %s\n\n",
            if (length(neg)) paste(neg, collapse = ", ") else "none"))

## ---- (B) published subscale means -------------------------------------------
pmean <- function(its, tr) {
  x <- d1[d1$item %in% its & d1$treat == tr, ]
  pm <- tapply(x$resp, x$id, mean, na.rm = TRUE)
  c(mean(pm, na.rm = TRUE), sd(pm, na.rm = TRUE))
}
cat("(B) wave-1 subscale person-means vs paper Table 1\n")
cat(sprintf("%-13s %-22s %-22s\n", "subscale", "camp obs (pub)", "control obs (pub)"))
dev <- c()
for (f in c("emotionality", "activity", "shyness")) {
  a <- pmean(FAM[[f]], 1); b <- pmean(FAM[[f]], 0); p <- PUB[[f]]
  cat(sprintf("%-13s %.2f (%.2f)  [%.2f (%.2f)]   %.2f (%.2f)  [%.2f (%.2f)]\n",
              f, a[1], a[2], p["camp"], p["camp_sd"], b[1], b[2], p["ctrl"], p["ctrl_sd"]))
  dev <- c(dev, abs(a[1] - p["camp"]), abs(b[1] - p["ctrl"]))
}
# sociability: the paper's alpha-trimmed scale. Test every leave-one-out subset;
# only the correct exclusion should reproduce the published M and SD.
cat("\nsociability, all five leave-one-out subsets (published 3.88 (0.87) / 4.15 (0.68)):\n")
soc_dev <- c()
for (k in 1:5) {
  its <- setdiff(FAM$sociability, paste0("SOC", k))
  a <- pmean(its, 1); b <- pmean(its, 0)
  dd <- max(abs(a[1] - 3.88), abs(b[1] - 4.15), abs(a[2] - 0.87), abs(b[2] - 0.68))
  soc_dev[k] <- dd
  cat(sprintf("  drop SOC%d: camp %.2f (%.2f)  ctrl %.2f (%.2f)   max|dev| %.3f\n",
              k, a[1], a[2], b[1], b[2], dd))
}
cat(sprintf("best-fitting exclusion: SOC%d (%.3f); next best %.3f\n",
            which.min(soc_dev), min(soc_dev), sort(soc_dev)[2]))

## ---- (C) SOC5 content check --------------------------------------------------
r_soc <- mean(C["SOC5", setdiff(FAM$sociability, "SOC5")])
r_emo <- mean(C["SOC5", FAM$emotionality])
cat(sprintf("\n(C) SOC5 (\"When alone, feels isolated\"): mean r with sociability %+.3f, with emotionality %+.3f\n",
            r_soc, r_emo))

ok_polarity <- all(own_r[setdiff(items, "SOC5")] > 0)
ok_means    <- max(dev) <= TOL
ok_soc      <- which.min(soc_dev) == 5 && min(soc_dev) <= TOL && sort(soc_dev)[2] > 0.15
cat(sprintf("\npolarity ok: %s | emo/act/shy means ok (max dev %.3f <= %.2f): %s | sociability exclusion unique: %s\n",
            ok_polarity, max(dev), TOL, ok_means, ok_soc))
cat("PARTIAL by design: order within a polarity class is not testable here.\n")
cat(if (ok_polarity && ok_means && ok_soc) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
