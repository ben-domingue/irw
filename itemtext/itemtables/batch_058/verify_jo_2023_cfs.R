# verify_jo_2023_cfs.R -- Step 5b evidence, route 1 (per-item descriptive statistics).
#
# CLAIM UNDER TEST. The live table's item codes are the raw S1/S3 CSV column names
# CFS1, CFS3, CFS4. The paper (Jo & Baek 2023, PLOS ONE 10.1371/journal.pone.0283997)
# renumbers the three retained Cabin Fever Syndrome items consecutively as CFS1, CFS2,
# CFS3 in both its S1 Appendix item table and its Table 2, so the codes do NOT match and
# the text-to-code assignment is an inference. The shipped assignment is
#   live CFS1 -> paper CFS1 "Staying at home makes me restless."
#   live CFS3 -> paper CFS2 "I have problems focusing while I'm at home ..."
#   live CFS4 -> paper CFS3 "While at home ... I experience social isolation."
# Table 2 publishes a mean for each paper-numbered item; those three means are distinct,
# so they are a falsifiable prediction about which live column is which.
#
# NOTE ON SDs: Table 2's St. Dev. column does NOT reproduce from the raw data (paper
# 1.304/1.331/1.318 vs observed 1.873/1.752/1.891) and its ARP1/ARP2 entries are
# identical (1.611), so the SD column looks to be something other than the raw item SD.
# Only the means are used here. This route pins all three items; it does not verify the
# response-option anchors, which the paper never publishes (option_text ships blank).

suppressMessages(library(irw))

TABLE <- "jo_2023_cfs"

# Paper Table 2, Cabin Fever Syndrome block (means, in paper numbering CFS1/CFS2/CFS3).
PUBLISHED <- c(CFS1 = 4.661, CFS3 = 5.191, CFS4 = 4.901)  # keyed by the LIVE code shipped
TOL <- 0.01

d <- irw::irw_fetch(TABLE)
obs <- tapply(as.numeric(d$resp), d$item, mean)
obs <- obs[names(PUBLISHED)]

cat(sprintf("%-6s %-10s %10s %10s %8s\n", "live", "paper#", "published", "observed", "diff"))
paper_no <- c(CFS1 = "CFS1", CFS3 = "CFS2", CFS4 = "CFS3")
for (i in seq_along(obs))
  cat(sprintf("%-6s %-10s %10.3f %10.3f %8.3f\n",
              names(obs)[i], paper_no[names(obs)[i]], PUBLISHED[i], obs[i],
              obs[i] - PUBLISHED[i]))

worst <- max(abs(obs - PUBLISHED))
cat(sprintf("\nlargest deviation: %.3f (tolerance %.2f)\n", worst, TOL))

# Falsification check: the three published means are mutually distinct, so no other
# permutation of the three texts over the three codes fits within tolerance.
gaps <- min(dist(PUBLISHED))
cat(sprintf("smallest gap between published means: %.3f -- any swap misses by at least this\n", gaps))

cat("Does NOT establish: the option/anchor wording (never published; option_text blank),\n",
    "nor the administration language of the questionnaire.\n", sep = "")

cat(if (worst <= TOL && gaps > TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
