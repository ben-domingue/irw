# verify_jo_2023_crp.R -- Step 5b evidence, re-runnable.
#
# Claim under test: the two live item codes CRP3 and CRP4 (the S3 data file's own
# column names) correspond, IN ORDER, to the two Cognitive Risk Perception items
# that Jo & Baek (2023) print in S1 Appendix Table A1 as CRP1 and CRP2. The paper
# numbers this scale 1-2 while the deposited CSV numbers it 3-4, so the tie is an
# inference (mapping_basis = paper_order) and needs a falsifiable check.
#
# The falsifiable prediction: Table 2 of the paper (10.1371/journal.pone.0283997.t002,
# image-only) publishes per-item means for CRP1 = 5.539 and CRP2 = 5.174. If the two
# items were swapped, each observed mean would miss its published value by 0.365.

suppressMessages(library(irw))

TABLE <- "jo_2023_crp"

# Published per-item means, paper Table 2 ("Scale reliability and validity").
PUBLISHED <- c(CRP3 = 5.539,   # printed as CRP1
               CRP4 = 5.174)   # printed as CRP2
TOL <- 0.01

d <- irw::irw_fetch(TABLE)
obs <- tapply(d$resp, d$item, mean)[names(PUBLISHED)]

cat(sprintf("%-6s %-14s %10s %10s %8s\n",
            "item", "paper label", "published", "observed", "diff"))
paper_lab <- c(CRP3 = "CRP1", CRP4 = "CRP2")
for (i in seq_along(obs))
    cat(sprintf("%-6s %-14s %10.3f %10.3f %8.3f\n",
                names(obs)[i], paper_lab[names(obs)[i]],
                PUBLISHED[i], obs[i], obs[i] - PUBLISHED[i]))

worst <- max(abs(obs - PUBLISHED))
swapped <- max(abs(rev(as.numeric(obs)) - as.numeric(PUBLISHED)))
cat(sprintf("\nas shipped: largest deviation %.3f (tolerance %.2f)\n", worst, TOL))
cat(sprintf("if swapped: largest deviation %.3f -- the swap is excluded\n", swapped))

cat("Note: this pins BOTH items, because the two published means differ by 0.365,\n",
    "far beyond the observed agreement. It does NOT verify the response anchors:\n",
    "neither the paper nor the appendix publishes labels for the 1-7 points, so\n",
    "option_text ships blank and no option/resp mapping is claimed.\n", sep = "")

cat(if (worst <= TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
