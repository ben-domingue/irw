# verify_matarboumosleh_2017_phq2.R
#
# WHAT IS BEING VERIFIED: the option_text <-> resp mapping -- i.e. the DIRECTION
# of the PHQ-2 frequency anchors shipped in this table
# (0 = "Not at all" ... 3 = "Nearly every day", stored unreversed).
#
# WHAT IS NOT VERIFIED HERE, AND WHY IT DOES NOT NEED TO BE: the item_text <->
# item axis is exempt. The two live item codes ARE header row 1 of the study's
# only supplement (S1 Dataset, 10.1371/journal.pone.0182239.s001) --
# "Lttl_IntrstDoingThngs" and "Feel_Deprssd" -- and
# data/matarboumosleh_2017_smartphone_depr_anx.py melts those columns BY NAME
# (PHQ2_ITEMS = ["Lttl_IntrstDoingThngs", "Feel_Deprssd"]), so the code is the
# source column name with no rename and no positional assignment. The codes are
# additionally self-describing and mutually exclusive in content, so a swap
# between "little interest in doing things" and "feel depressed" would be
# self-evident. mapping_basis = data_labels.
#
# THE FALSIFIABLE CLAIM. If the anchors ran the other way (0 = "Nearly every
# day"), then a HIGH stored score would mean FEW symptoms, and the PHQ-2's
# standard >= 3 screen-positive cut-point would have to be read on the low tail.
# The paper states its screening result in prose:
#
#   "A score of 3 or greater, the recommended cut-point for each when used as a
#    screener, was used to screen for depression and anxiety in our study"
#   "... three-fifths were alcohol drinkers, ONE-FIFTH WERE DEPRESSED, and
#    one-fourth were anxious."
#     -- Matar Boumosleh & Jaalouk (2017), PLOS ONE 12(8): e0182239
#
# So the shipped direction predicts ~20% of the sample at total >= 3. The
# flipped direction predicts the complement side (~91%), which no reading of
# "one-fifth were depressed" survives.
#
# Hard-coded from the deposit S1 Dataset (fetched 2026-09-08), because the
# processing script drops the study's own total column and the live table
# therefore cannot supply it:
#   - Depression_score == Lttl_IntrstDoingThngs + Feel_Deprssd exactly, over all
#     408 complete cases (max abs difference 0.0) -> the study's own total is the
#     RAW unreversed sum; nothing was reverse-scored on the way in.
#   - Deposit prevalence at total >= 3 under the shipped anchors: 21.8%.
#     Under flipped anchors: 91.2%.
#
# WHAT THIS ROUTE DOES NOT ESTABLISH: it fixes the DIRECTION of the scale only.
# It cannot separate the two interior anchors from each other -- relabelling
# 1 = "More than half the days" and 2 = "Several days" would leave every number
# below unchanged. Those two rest on the printed 0/1/2/3 order of the PHQ-9
# form itself. It also cannot distinguish item 1 from item 2, since the total is
# symmetric in them; the data_labels exemption above is what does that.

suppressMessages(library(irw))

TABLE            <- "matarboumosleh_2017_phq2"
PAPER_PREVALENCE <- 0.20   # "one-fifth were depressed", cut-point total >= 3
TOL              <- 0.05   # "one-fifth" is prose, not a printed decimal

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[stats::complete.cases(w[, c("Lttl_IntrstDoingThngs", "Feel_Deprssd")]), ]

tot_shipped <- w$Lttl_IntrstDoingThngs + w$Feel_Deprssd
tot_flipped <- (3 - w$Lttl_IntrstDoingThngs) + (3 - w$Feel_Deprssd)

p_shipped <- mean(tot_shipped >= 3)
p_flipped <- mean(tot_flipped >= 3)

cat(sprintf("complete cases in live table: %d\n\n", nrow(w)))
cat(sprintf("%-34s %10s %10s\n", "reading", "mean total", "pct >= 3"))
cat(sprintf("%-34s %10.3f %9.1f%%\n", "SHIPPED (0 = Not at all)",
            mean(tot_shipped), 100 * p_shipped))
cat(sprintf("%-34s %10.3f %9.1f%%\n", "FLIPPED (0 = Nearly every day)",
            mean(tot_flipped), 100 * p_flipped))
cat(sprintf("\npaper: \"one-fifth were depressed\" at cut-point >= 3  -> %.1f%%\n",
            100 * PAPER_PREVALENCE))
cat(sprintf("deposit S1 Dataset (408 complete cases), shipped reading: 21.8%%\n"))
cat(sprintf("|shipped - paper| = %.3f   |flipped - paper| = %.3f   (tol %.2f)\n",
            abs(p_shipped - PAPER_PREVALENCE), abs(p_flipped - PAPER_PREVALENCE), TOL))

cat("\nPer-item means (corroborating only, NOT the verdict): PHQ-2 anhedonia is\n",
    "normally endorsed slightly more than depressed mood in unselected samples.\n", sep = "")
m <- tapply(d$resp, d$item, mean)
for (nm in names(m)) cat(sprintf("  %-24s %.4f\n", nm, m[[nm]]))

ok <- abs(p_shipped - PAPER_PREVALENCE) <= TOL &&
      abs(p_flipped - PAPER_PREVALENCE) >  TOL
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
