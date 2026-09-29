# verify_lestari_2026_inhibitory_control.R -- Step 5b check (batch_707).
#
# Claim: item code ICn carries the text of "Butir n" under "SUB TES 2 (IC)" in the
# deposit's administered Google Form (Instrument Items ... .pdf, Mendeley
# 10.17632/6y7sbzjbny, pages 20-41). The codebook defines Item No. as "the sequential
# item number within each respective subtest" and names the raw-data columns
# IC1-IC40; data/lestari_2026_teacher_executive_function.py keeps those column names
# as the IRW item codes unrenamed.
#
# What the data CAN check: that the live IRW codes are the deposit's own IC1..IC40
# numbering (not shuffled by processing), via the per-item means and SDs the deposit
# itself publishes by code ("Fit measure ... .pdf", 80-item reliability table).
# What it CANNOT check: that the deposit's ICn is the form's Butir n. No published
# per-item statistic is keyed to scenario content and option scoring is unpublished;
# that link rests on the form/codebook label match, so this supports PARTIAL only.

suppressMessages(library(irw))
TABLE <- "lestari_2026_inhibitory_control"

PUB_MEAN <- c(2.446,2.259,2.557,2.492,2.310,2.227,2.110,1.522,1.464,1.992,
              2.420,2.256,2.122,2.027,1.637,1.898,2.315,1.850,2.378,2.251,
              2.166,2.488,2.288,2.372,2.192,2.019,2.427,2.061,1.944,1.906,
              2.334,2.455,2.290,2.078,2.566,2.419,2.308,2.178,2.218,2.401)
PUB_SD   <- c(1.044,0.756,0.876,0.841,1.010,0.879,1.005,1.287,0.829,0.999,
              1.022,1.095,1.251,1.074,1.269,1.064,0.765,1.012,0.894,0.906,
              0.991,0.919,1.150,0.822,1.108,0.885,1.079,1.091,0.852,1.167,
              0.849,1.063,1.122,1.057,0.922,0.980,0.816,1.215,0.984,1.057)
codes <- paste0("IC", 1:40)
TOL <- 0.002

d <- irw::irw_fetch(TABLE)
m <- tapply(d$resp, d$item, mean)[codes]
s <- tapply(d$resp, d$item, sd)[codes]
n <- table(d$item)[codes]

cat(sprintf("%-6s %5s %8s %8s %8s %8s\n", "item", "n", "pubM", "obsM", "pubSD", "obsSD"))
for (i in 1:40) cat(sprintf("%-6s %5d %8.3f %8.3f %8.3f %8.3f\n", codes[i], n[i],
                            PUB_MEAN[i], m[i], PUB_SD[i], s[i]))
dm <- max(abs(m - PUB_MEAN)); ds <- max(abs(s - PUB_SD))
cat(sprintf("\nmax |mean diff| = %.4f, max |sd diff| = %.4f (tol %.3f)\n", dm, ds, TOL))

# Does the match single out each code? Count published (mean, sd) pairs within
# tolerance of each observed pair; each code must match exactly one (its own).
amb <- sapply(1:40, function(i) sum(abs(PUB_MEAN - m[i]) <= TOL & abs(PUB_SD - s[i]) <= TOL))
own <- sapply(1:40, function(i) abs(PUB_MEAN[i] - m[i]) <= TOL & abs(PUB_SD[i] - s[i]) <= TOL)
cat("codes whose observed (mean,sd) matches more than one published pair:", sum(amb != 1), "\n")
cat("codes matching their OWN published pair:", sum(own), "of 40\n")
cat("NOT established here: that deposit code ICn is form item 'Butir n' -- that rests on\n",
    "the codebook/form label match, not on data. Option<->resp is not verified (no key).\n", sep = "")
cat(if (dm <= TOL && ds <= TOL && all(amb == 1) && all(own)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
