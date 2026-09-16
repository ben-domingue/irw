# verify_wu2026_liking.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST. Two things, neither of which validate_items.R can see:
#   (a) the live codes Liking_1..Liking_10 are the LIKING ("This vase is pleasing
#       to see.") ratings of ceramic vase stimuli 1..10 as numbered in Fig 1 of the
#       source paper -- i.e. Liking_n is vase n, not some other vase and not a
#       typicality/novelty rating;
#   (b) resp is stored in the administered direction, 1 = "Strongly Disagree" ..
#       7 = "Strongly Agree", not reverse-coded.
#
# ROUTE 1 (per-item published descriptive statistics). Wu, Yahaya, Tai & Ren (2026),
# "Practical research on the boundaries of MAYA design principles with ceramic
# products as the carrier", PLOS ONE 21(4):e0342855, doi:10.1371/journal.pone.0342855
# (CC BY 4.0). Fig 2 prints the mean Liking rating for each of the ten vases in its
# data table row labelled "Liking" (figure image .g002). Those ten numbers are the
# falsifiable prediction: they are all distinct (smallest gap 0.10, vase7 3.71 vs
# vase10 3.81), so a permutation of the code->vase assignment breaks the match, and
# a reversed 1-7 coding would move every mean to 8 - m.

suppressMessages(library(irw))
TABLE <- "wu2026_liking"

# Wu et al. (2026) Fig 2, row "Liking", vases 1..10 (2 d.p. as printed).
PUBLISHED <- c(4.84, 5.35, 5.18, 3.99, 4.93, 4.35, 3.71, 4.47, 4.15, 3.81)
TOL <- 0.02

d <- as.data.frame(irw::irw_fetch(TABLE))
its <- paste0("Liking_", 1:10)
obs <- tapply(d$resp, d$item, mean)[its]
n   <- tapply(d$resp, d$item, length)[its]

cat(sprintf("%-10s %5s %12s %10s %8s %12s\n",
            "item", "n", "published", "observed", "diff", "if reversed"))
for (i in seq_along(its))
    cat(sprintf("%-10s %5d %12.2f %10.2f %8.3f %12.2f\n",
                its[i], n[i], PUBLISHED[i], obs[i], obs[i] - PUBLISHED[i],
                8 - obs[i]))

worst <- max(abs(obs - PUBLISHED))
cat(sprintf("\nlargest |observed - published| = %.3f (tolerance %.2f)\n", worst, TOL))

# Direction check: how badly does the reversed reading fit?
worst_rev <- max(abs((8 - obs) - PUBLISHED))
cat(sprintf("largest |reversed - published| = %.3f -- the reversed coding is refuted\n",
            worst_rev))

# Is the match item-specific, or would any permutation do?
perm_ok <- sum(replicate(20000, max(abs(sample(obs) - PUBLISHED)) <= TOL))
cat(sprintf("random permutations of the observed means matching within %.2f: %d / 20000\n",
            TOL, perm_ok))

cat("\nWhat this does NOT establish:\n")
cat(" - The item_text shipped is IDENTICAL for all ten items ('This vase is pleasing\n")
cat("   to see.'), because the items differ only in which vase image was shown. So no\n")
cat("   permutation of item_text is even possible; what Route 1 pins is the stimulus\n")
cat("   identity behind each code (Liking_n = Fig 1 vase n), which is not itself\n")
cat("   reproducible as text -- Fig 1 is images only.\n")
cat(" - The administered wording. The study was run face-to-face with 200 native\n")
cat("   Chinese speakers; the shipped English is the paper's own rendering and no\n")
cat("   Chinese wording exists in the deposit or supplements.\n")
cat(" - The labels of resp 2..6, which the paper never prints (left blank, not padded).\n\n")

cat(if (worst <= TOL && worst_rev > TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
