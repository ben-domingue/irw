# verify_cogcontrol_gyurkovics_2019_mwprobe.R -- Step 5b, batch_263.
# Adapted from references/verify_template.R.
#
# CLAIMS UNDER TEST
#  (A) item axis: probe_NN is the NN-th thought probe a participant met in the SART,
#      counted over (block, trial) order -- a script-generated integer
#      (cumcount over code==3 rows in data/cogcontrol_gyurkovics.py). Re-derived here
#      from the OSF raw file and matched ROW BY ROW against the live table's own
#      trial_block/trial_num, plus per-position resp counts.
#  (B) resp axis: raw key codes 97/98/99/100 = the paper's options in printed order
#      (on-task / mind blank = space out / zone out / tune out), per the deposit's
#      own Gyurkovics_Stafford_Levita_analyses.R; resp = 1 for zone+tune ("overall MW").
#      Checked by reproducing each category's published age-effect Wald chi2 (paper
#      Table 3, "Age" column) and the directional OR early vs late adolescents for
#      overall MW (published .406) -- a swap of any two categories, or a flipped resp,
#      moves these numbers.
suppressMessages({library(irw); library(lme4)})
TABLE <- "cogcontrol_gyurkovics_2019_mwprobe"
ok <- TRUE

live <- irw::irw_fetch(TABLE)
raw  <- read.csv("https://osf.io/download/9x6yz/", strip.white = TRUE)  # sart_merge.csv, sha256 cffa74d8...
raw  <- raw[order(raw$subid, raw$block, raw$trial), ]
pb   <- raw[raw$code == 3, ]
pb$item <- sprintf("probe_%02d", ave(pb$subid, pb$subid, FUN = seq_along))
pb$resp <- as.integer(pb$resp %in% c(99, 100))

## (A) row-level match on (id, item) -> (block, trial, resp)
m <- merge(live[, c("id", "item", "resp", "trial_block", "trial_num")],
           pb[, c("subid", "item", "block", "trial", "resp")],
           by.x = c("id", "item"), by.y = c("subid", "item"), suffixes = c("_live", "_raw"))
cat(sprintf("live rows %d | raw probe rows %d | joined %d\n", nrow(live), nrow(pb), nrow(m)))
nb <- sum(m$trial_block == m$block); nt <- sum(m$trial_num == m$trial); nr <- sum(m$resp_live == m$resp_raw)
cat(sprintf("block agree %d/%d | trial agree %d/%d | resp agree %d/%d\n", nb, nrow(m), nt, nrow(m), nr, nrow(m)))
ok <- ok && nrow(m) == nrow(live) && nrow(m) == nrow(pb) && nb == nrow(m) && nt == nrow(m) && nr == nrow(m)
cat("\nper-position resp=1 count  live vs raw\n")
lv <- tapply(live$resp, live$item, sum); rv <- tapply(pb$resp, pb$item, sum)
print(rbind(live = lv, raw = rv[names(lv)]))
ok <- ok && all(lv == rv[names(lv)])

## (B) published Table 3 age-effect chi2 per category, analytic sample (filter==1, subid!=107)
s <- live[live$cov_analysis_include %in% 1 & live$id != 107, ]
s$g <- relevel(factor(s$cov_agegroup), "adult")
cat(sprintf("\nanalytic sample: %d participants (paper Table 2: 30+24+28+24 = 106)\n", length(unique(s$id))))
wald <- function(y) {
  mm <- glmer(y ~ g + (1 | id), data = s, family = binomial)
  b <- fixef(mm)[-1]; V <- as.matrix(vcov(mm))[-1, -1]
  c(chi2 = as.numeric(t(b) %*% solve(V) %*% b),
    OR_early_vs_late = unname(exp(b["gearly_adolescent"] - b["glate_adolescent"])))
}
PUB <- c(on_task = 6.92, space_out = 6.59, zone_out = 0.58, tune_out = 10.29, overall_MW = 10.21)
obs <- c(sapply(c("on_task", "space_out", "zone_out", "tune_out"),
                function(k) wald(as.integer(s$trial_report == k))["chi2"]),
         wald(s$resp)["chi2"])
names(obs) <- names(PUB)
print(formatC(rbind(published = PUB, observed = obs), format = "f", digits = 3))
ok <- ok && max(abs(obs - PUB)) < 0.02
orr <- wald(s$resp)["OR_early_vs_late"]; orf <- wald(1 - s$resp)["OR_early_vs_late"]
cat(sprintf("OR early vs late, overall MW: observed %.3f (published .406); with resp flipped %.3f\n", orr, orf))
ok <- ok && abs(orr - 0.406) < 0.01
cat("resp=1 by trial_report:\n"); print(table(live$trial_report, live$resp))
ok <- ok && all(live$resp == as.integer(live$trial_report %in% c("zone_out", "tune_out")))

cat("\nNOT established: the on-screen layout of the probe (option order/numbering and which\n",
    "key selected which option are not printed in the paper; the code->category order rests on\n",
    "the authors' analysis script, corroborated by the five chi2 values above). Every item shares\n",
    "one probe wording, so the item axis cannot be mis-assigned in text; (A) pins each row anyway.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
