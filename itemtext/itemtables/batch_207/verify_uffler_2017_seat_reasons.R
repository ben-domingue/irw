# verify_uffler_2017_seat_reasons.R -- Step 5b mapping verification.
#
# CLAIM UNDER TEST: the French category label shipped in `item_text` for each of the
# seven item codes is the right one. The English glosses come from the deposit's own
# `codes` tab (S2 Data, sheet "codes"), which ties column name -> text with no
# inference; the FRENCH wording comes from a different artifact -- the bar chart in
# S1 File, which is an image and carries no column names at all. So the thing that
# could be silently wrong is the French-label <-> item-code assignment, and that is
# what this script tests.
#
# ROUTE: response-frequency matching (Step 5b route 9 / route 1 on a binary item).
# The S1 chart prints, per French label, the % of students who gave that reason.
# Those percentages are computed on the 477 nursing students (the paper's largest
# subgroup); brute-forcing the denominator that makes all seven percentages land on
# integers picks 477 with residual 0.15, and the live table holds exactly 477 unique
# ids with cov_program == "NURS". Each label therefore predicts a specific
# endorsement COUNT for a specific item code. Seven distinct predicted counts,
# including the adjacent pair 37 vs 36, so a correct match pins every item against
# every other -- a swap of any two labels moves at least one count.

suppressMessages(library(irw))

TABLE <- "uffler_2017_seat_reasons"

# S1 File (10.1371/journal.pone.0174947.s001), Graph 1: French label -> published %.
# Transcribed from the chart image; counts are pct * 477 / 100, rounded.
LABEL <- c(practical   = "pour des raisons pratiques",
           habit       = "par habitude",
           affinity    = "par affinité",
           remain      = "place restante",
           concentrate = "pour rester concentré",
           noise       = "pour éviter le bruit",
           `else`      = "pour pouvoir faire autre chose")
PCT   <- c(practical = 33.12, habit = 23.48, affinity = 18.44, remain = 16.14,
           concentrate = 7.75, noise = 7.54, `else` = 4.40)
PRED  <- round(PCT * 477 / 100)
TOL   <- 1   # counts may differ by 1 from rounding / a one-case data revision

d <- irw::irw_fetch(TABLE)
d <- d[d$cov_program == "NURS", ]
cat(sprintf("nursing subsample: %d unique ids (paper: 477 nursing students)\n\n",
            length(unique(d$id))))

obs <- tapply(d$resp, d$item, sum)[names(PCT)]

cat(sprintf("%-12s %-32s %6s %6s %6s\n",
            "item", "shipped item_text (S1 chart)", "pred", "obs", "diff"))
for (i in seq_along(obs))
    cat(sprintf("%-12s %-32s %6d %6d %6d\n",
                names(obs)[i], LABEL[[names(obs)[i]]], PRED[[i]], obs[[i]],
                obs[[i]] - PRED[[i]]))

worst <- max(abs(obs - PRED))
cat(sprintf("\nlargest deviation: %d count(s) (tolerance %d)\n", worst, TOL))

# Rank order is the second, denominator-free half of the same check.
ok_rank <- identical(names(sort(obs, decreasing = TRUE)),
                     names(sort(PRED, decreasing = TRUE)))
cat(sprintf("rank order identical to the chart's printed descending order: %s\n",
            ok_rank))

# What this does NOT establish: it says nothing about the ENGLISH glosses in
# item_text_translated (those come from the deposit's codes tab, which needs no
# check), and nothing about option_text/resp -- there is no printed option wording,
# the 0/1 is the deposit's blank/"O" mark recoded by data/uffler_2017_lecture_seating.py.
cat("Note: pins the French label on each item code only; the English glosses are\n",
    "deposit-labelled and the 0/1 coding carries no source option wording.\n", sep = "")

cat(if (worst <= TOL && ok_rank) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
