# verify_lestari_2026_working_memory.R -- Step 5b check (batch_708).
#
# Claim: item code WMn carries the text of "Butir n" under "SUB TES 3 (WM)" in the
# deposit's administered Google Form (Instrument Items ... .pdf, Mendeley
# 10.17632/6y7sbzjbny, pages 41-50). The codebook defines Item No. as the sequential
# item number within each subtest and names the raw-data columns WM1-WM16;
# data/lestari_2026_teacher_executive_function.py keeps those column names as the
# IRW item codes unrenamed (BLOCKS regex 'WM\d+').
#
# What the data CAN check: that the live IRW codes are the deposit's own WM1..WM16
# numbering (not shuffled by processing), via the per-item means and SDs the deposit
# itself publishes by code ("Fit measure ... .pdf", "Reliability Analysis - WM").
# What it CANNOT check: that the deposit's WMn is the form's Butir n. No published
# per-item statistic is keyed to scenario content and option scoring is unpublished;
# that link rests on the form/codebook label match, so this supports PARTIAL only.

suppressMessages(library(irw))
TABLE <- "lestari_2026_working_memory"

PUB_MEAN <- c(2.322,2.340,2.553,2.187,2.168,2.215,2.042,2.037,
              1.763,2.329,1.662,2.163,2.131,2.646,2.346,1.777)
PUB_SD   <- c(0.938,0.860,0.828,1.174,0.943,0.965,1.130,1.056,
              0.966,1.003,0.823,1.071,1.230,0.716,1.119,1.136)
codes <- paste0("WM", 1:16)
TOL <- 0.002

d <- irw::irw_fetch(TABLE)
m <- tapply(d$resp, d$item, mean)[codes]
s <- tapply(d$resp, d$item, sd)[codes]
n <- table(d$item)[codes]

cat(sprintf("%-6s %5s %8s %8s %8s %8s\n", "item", "n", "pubM", "obsM", "pubSD", "obsSD"))
for (i in 1:16) cat(sprintf("%-6s %5d %8.3f %8.3f %8.3f %8.3f\n", codes[i], n[i],
                            PUB_MEAN[i], m[i], PUB_SD[i], s[i]))
dm <- max(abs(m - PUB_MEAN)); ds <- max(abs(s - PUB_SD))
cat(sprintf("\nmax |mean diff| = %.4f, max |sd diff| = %.4f (tol %.3f)\n", dm, ds, TOL))

# Does the match single out each code? Count published (mean, sd) pairs within
# tolerance of each observed pair; each code must match exactly one (its own).
amb <- sapply(1:16, function(i) sum(abs(PUB_MEAN - m[i]) <= TOL & abs(PUB_SD - s[i]) <= TOL))
own <- sapply(1:16, function(i) abs(PUB_MEAN[i] - m[i]) <= TOL & abs(PUB_SD[i] - s[i]) <= TOL)
cat("codes whose observed (mean,sd) matches more than one published pair:", sum(amb != 1), "\n")
cat("codes matching their OWN published pair:", sum(own), "of 16\n")
cat("NOT established here: that deposit code WMn is form item 'Butir n' -- that rests on\n",
    "the codebook/form label match, not on data. Option<->resp is not verified (no key).\n", sep = "")
cat(if (dm <= TOL && ds <= TOL && all(amb == 1) && all(own)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
