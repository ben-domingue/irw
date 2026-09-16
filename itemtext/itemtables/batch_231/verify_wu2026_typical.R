# verify_wu2026_typical.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST. Two things validate_items.R cannot see:
#   (a) the live codes Typical_1..Typical_10 are the TYPICALITY ("This is a typical
#       vase.") ratings of ceramic vase stimuli 1..10 as numbered in Fig 1 of the
#       source paper -- i.e. Typical_n is vase n, and not a liking/novelty rating;
#   (b) resp is stored in the administered direction, 1 = "Strongly Disagree" ..
#       7 = "Strongly Agree", not reverse-coded.
#
# ROUTE 1 (per-item published descriptive statistics). Wu, Yahaya, Tai & Ren (2026),
# "Practical research on the boundaries of MAYA design principles with ceramic
# products as the carrier", PLOS ONE 21(4):e0342855, doi:10.1371/journal.pone.0342855
# (CC BY 4.0). Fig 2 (.g002) prints a mean per vase in its data-table row labelled
# "Typicality". Those ten numbers are the falsifiable prediction: they are all
# distinct, so a permutation of the code->vase assignment breaks the match, and a
# reversed 1-7 coding would move every mean to 8 - m. The paper's own prose
# independently corroborates one cell: "it ranked second in typicality (M = 4.23,
# SD = 1.33)" for Ceramic Vase Stimulus 2.
#
# The published values are printed to 2 d.p., so the exact rounding bound is 0.005
# and that is the tolerance used. The tightest pair is vase6 3.12 vs vase7 3.13
# (gap 0.01), which a 0.005 tolerance still separates -- a 6<->7 transposition
# misses by 0.010.

suppressMessages(library(irw))
TABLE <- "wu2026_typical"

# Wu et al. (2026) Fig 2, row "Typicality", vases 1..10 (2 d.p. as printed).
PUBLISHED <- c(5.70, 4.23, 4.14, 3.29, 4.61, 3.12, 3.13, 2.81, 2.67, 2.16)
TOL <- 0.005   # the rounding bound of a value printed to 2 d.p. (compared with a 1e-9 float slack)

d   <- as.data.frame(irw::irw_fetch(TABLE))
its <- paste0("Typical_", 1:10)
obs <- tapply(d$resp, d$item, mean)[its]
n   <- tapply(d$resp, d$item, length)[its]

cat(sprintf("%-11s %5s %11s %10s %8s %12s\n",
            "item", "n", "published", "observed", "diff", "if reversed"))
for (i in seq_along(its))
    cat(sprintf("%-11s %5d %11.2f %10.4f %8.4f %12.2f\n",
                its[i], n[i], PUBLISHED[i], obs[i], obs[i] - PUBLISHED[i], 8 - obs[i]))

worst <- max(abs(obs - PUBLISHED))
cat(sprintf("\nlargest |observed - published| = %.4f (tolerance %.3f)\n", worst, TOL))

# Direction check: how badly does the reversed reading fit?
worst_rev <- max(abs((8 - obs) - PUBLISHED))
cat(sprintf("largest |reversed - published| = %.3f -- the reversed coding is refuted\n",
            worst_rev))

# The tightest adjacent pair, stated explicitly.
sw <- obs; sw[6:7] <- sw[7:6]
cat(sprintf("Typical_6 <-> Typical_7 transposed: largest |diff| = %.4f (> %.3f, so excluded)\n",
            max(abs(sw - PUBLISHED)), TOL))

# Is the match item-specific, or would any permutation do?
set.seed(1)
perm_ok <- sum(replicate(20000, max(abs(sample(obs) - PUBLISHED)) <= TOL))
cat(sprintf("random permutations of the observed means matching within %.3f: %d / 20000\n",
            TOL, perm_ok))
cat("   (the identity permutation is essentially never drawn, so 0 is the expected pass value)\n")

cat("\nWhat this does NOT establish:\n")
cat(" - The item_text shipped is IDENTICAL for all ten items ('This is a typical\n")
cat("   vase.'), because the items differ only in which vase image was shown. So no\n")
cat("   permutation of item_text is even possible; what Route 1 pins is the stimulus\n")
cat("   identity behind each code (Typical_n = Fig 1 vase n), which is not itself\n")
cat("   reproducible as text -- Fig 1 is photographs with no published descriptions.\n")
cat(" - The administered wording. The study was run face-to-face with 200 native\n")
cat("   Chinese speakers; the shipped English is the paper's own rendering and no\n")
cat("   Chinese wording exists in the deposit or supplements.\n")
cat(" - The labels of resp 2..6, which the paper never prints (left blank, not padded).\n\n")

cat(if (worst <= TOL + 1e-9 && worst_rev > TOL && perm_ok == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
