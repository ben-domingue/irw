# verify_lestari_2026_cognitive_flexibility.R -- Step 5b check (batch_707).
#
# Claim: item code CFn carries the text of "Butir n" under "SUB TES 1 (CF)" in the
# deposit's administered Google Form (Instrument Items ... .pdf, Mendeley
# 10.17632/6y7sbzjbny). The codebook defines Item No. as "the sequential item
# number within each respective subtest" and names the raw-data columns CF1-CF24;
# data/lestari_2026_teacher_executive_function.py keeps those column names as the
# IRW item codes unrenamed.
#
# What the data CAN check: that the live IRW codes are the deposit's own CF1..CF24
# numbering (not shuffled by processing), via the per-item means and SDs the
# deposit itself publishes by code ("Fit measure ... .pdf", 80-item table).
# What it CANNOT check: that the deposit's CFn is the form's Butir n. No
# published per-item statistic is keyed to scenario content, option scoring is
# unpublished, and block-structure routes (sub-dimension 3-cycle, teaching-skill
# triplets) are underpowered (8/24 and 6/24 under a general factor). That link
# rests on the label match described above, so this script supports PARTIAL.

suppressMessages(library(irw))
TABLE <- "lestari_2026_cognitive_flexibility"

PUB_MEAN <- c(2.288,1.820,2.239,2.094,1.278,2.451,1.727,2.257,2.256,1.854,1.466,2.527,
              2.279,1.945,2.399,1.968,1.944,2.389,2.367,2.255,2.420,1.724,2.633,1.688)
PUB_SD   <- c(0.661,0.701,1.097,0.974,0.939,0.907,0.645,0.994,1.087,1.076,1.317,0.875,
              1.019,1.125,0.991,1.225,0.959,0.821,1.043,1.116,0.954,1.397,0.818,1.182)
codes <- paste0("CF", 1:24)
TOL <- 0.002

d <- irw::irw_fetch(TABLE)
m <- tapply(d$resp, d$item, mean)[codes]
s <- tapply(d$resp, d$item, sd)[codes]
n <- table(d$item)[codes]

cat(sprintf("%-6s %5s %8s %8s %8s %8s\n", "item", "n", "pubM", "obsM", "pubSD", "obsSD"))
for (i in 1:24) cat(sprintf("%-6s %5d %8.3f %8.3f %8.3f %8.3f\n", codes[i], n[i],
                            PUB_MEAN[i], m[i], PUB_SD[i], s[i]))
dm <- max(abs(m - PUB_MEAN)); ds <- max(abs(s - PUB_SD))
cat(sprintf("\nmax |mean diff| = %.4f, max |sd diff| = %.4f (tol %.3f)\n", dm, ds, TOL))

# Does the match single out each code? Count how many OTHER codes' published
# (mean, sd) pair would also sit within tolerance of each observed pair.
amb <- sapply(1:24, function(i) sum(abs(PUB_MEAN - m[i]) <= TOL & abs(PUB_SD - s[i]) <= TOL))
cat("codes whose observed (mean,sd) matches more than one published pair:",
    sum(amb != 1), "\n")
cat("NOT established here: that deposit code CFn is form item 'Butir n' -- that rests on\n",
    "the codebook/form label match, not on data.\n", sep = "")
cat(if (dm <= TOL && ds <= TOL && all(amb == 1)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
