# verify_enkavi_2019_stroop.R
#
# CLAIM UNDER TEST: each IRW item code is `<stim_word>_<stim_color>` -- the word
# printed FIRST, the ink colour SECOND -- so e.g. `blue_red` is the word BLUE
# printed in red ink and NOT the word RED printed in blue ink, and the shipped
# item_text / correct_response follow that orientation.
#
# WHY IT IS FALSIFIABLE: the constants below were produced by re-running
# data/enkavi_2019_conflict_tasks.py's item construction over the study's own two
# raw trial files
#   github.com/IanEisenberg/Self_Regulation_Ontology
#     Data/{Complete,Retest}_02-16-2019/Individual_Measures/stroop.csv.gz
# (test-stage rows, resp = the source `correct` column restricted to {0,1}).
# Per-item n alone cannot identify an item (the six incongruent items all have
# n = 5384), so the discriminating statistic is per-item mean accuracy. All nine
# source means are pairwise separated by at least 0.00037 (blue_green vs red_blue) -- far above the 1e-5
# tolerance -- so ANY permutation of the nine item codes, including the
# word/colour transposition, fails this check. A transposition specifically moves
# green_red/red_green by 0.0399, blue_red/red_blue by 0.0241 and
# blue_green/green_blue by 0.0204.
#
# It does NOT re-check item or resp sets -- validate_items.R did that -- and it
# does not test the option_text labels (resp is trial accuracy, 0/1, per the
# processing script).

suppressMessages(library(irw))

TABLE <- "enkavi_2019_stroop"
TOL   <- 1e-5

# item, word shown, ink colour, n, mean accuracy -- all from the raw SRO files.
SRC <- data.frame(
  item = c("blue_blue","blue_green","blue_red","green_blue","green_green",
           "green_red","red_blue","red_green","red_red"),
  word = c("BLUE","BLUE","BLUE","GREEN","GREEN","GREEN","RED","RED","RED"),
  ink  = c("blue","green","red","blue","green","red","blue","green","red"),
  n    = c(10768, 5384, 5384, 5384, 10768, 5384, 5384, 5384, 10768),
  mean = c(0.970840, 0.912704, 0.937221, 0.933135, 0.969354,
           0.942979, 0.913076, 0.903046, 0.977619),
  stringsAsFactors = FALSE
)

d <- irw::irw_fetch(TABLE)
obs_n <- as.vector(table(d$item)[SRC$item])
obs_m <- as.vector(tapply(d$resp, d$item, mean)[SRC$item])

cat(sprintf("%-12s %-6s %-6s %8s %8s %11s %11s %10s\n",
            "item","word","ink","n(src)","n(live)","mean(src)","mean(live)","diff"))
for (i in seq_len(nrow(SRC)))
  cat(sprintf("%-12s %-6s %-6s %8d %8d %11.6f %11.6f %10.2e\n",
              SRC$item[i], SRC$word[i], SRC$ink[i], SRC$n[i], obs_n[i],
              SRC$mean[i], obs_m[i], obs_m[i] - SRC$mean[i]))

worst_m <- max(abs(obs_m - SRC$mean))
n_ok    <- all(obs_n == SRC$n)
gap     <- min(dist(SRC$mean))

cat(sprintf("\nlargest mean deviation: %.2e (tolerance %.0e); n identical: %s\n",
            worst_m, TOL, n_ok))
cat(sprintf("smallest gap between any two source means: %.5f -- any permutation of the\n", gap))
cat("nine codes would move at least one item by more than the tolerance.\n")
cat("Not established here: the option_text accuracy labels (resp is 0/1 accuracy,\n",
    "not a chosen option) and the instructions wording, which come from the task\n",
    "source expfactory-experiments/stroop/experiment.js.\n", sep = "")

cat(if (n_ok && worst_m <= TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
