# TEMPLATE for verify_<table>.R -- copy, don't source. One per extracted table.
#
# The job of this file is to make your Step 5b claim RE-RUNNABLE. Whoever triages
# the batch should be able to type one command and watch your evidence reappear,
# instead of rebuilding your analysis from the source paper.
#
# Rules:
#   1. Verify the MAPPING, not the plumbing. "The file has 22 items and they all
#      appear in the live data" is not evidence -- validate_items.R already
#      checked that. Evidence is the thing that would break if item_text for
#      items 3 and 5 were swapped.
#   2. Print the numbers. A bare PASS is not reviewable; the reader wants to see
#      4.80 next to 4.78 and judge for themselves.
#   3. Last line of output must be exactly "VERDICT: PASS" or "VERDICT: FAIL".
#   4. Be self-contained and offline-tolerant where you can: hard-code the
#      published values you are comparing against (they came from a paper, they
#      will not change), and fetch only the live IRW data.
#   5. If your mapping_basis is data_labels there is usually nothing to verify --
#      the source file ties code to text. Write no script and say so in
#      provenance; verify_batch.R will report MISSING(exempt).
#
# Worked example below: the real check for arora2025_blueq_pedagogical, whose
# item codes are assigned POSITIONALLY by the processing script. The claim is
# that ped1..ped10 correspond to spreadsheet columns 3..12; the paper publishes
# per-item means, so those means are the falsifiable prediction.

suppressMessages(library(irw))

TABLE <- "arora2025_blueq_pedagogical"

# Published per-item means, paper Table 1 items 1-10 (jeehp 2025;22:5).
PUBLISHED <- c(4.80, 4.85, 4.78, 4.78, 4.78, 4.60, 4.73, 4.78, 4.78, 4.78)
TOL <- 0.02

d <- irw::irw_fetch(TABLE)
obs <- tapply(d$resp, d$item, mean)
obs <- obs[paste0("ped", 1:10)]

cat(sprintf("%-8s %10s %10s %8s\n", "item", "published", "observed", "diff"))
for (i in seq_along(obs))
    cat(sprintf("%-8s %10.2f %10.2f %8.3f\n",
                names(obs)[i], PUBLISHED[i], obs[i], obs[i] - PUBLISHED[i]))

worst <- max(abs(obs - PUBLISHED))
cat(sprintf("\nlargest deviation: %.3f (tolerance %.2f)\n", worst, TOL))

# State what this does NOT establish -- as important as what it does.
cat("Note: several published means tie at 4.78, so this route alone cannot separate\n",
    "those items from each other; the positional header diff in provenance is what does.\n", sep = "")

cat(if (worst <= TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
