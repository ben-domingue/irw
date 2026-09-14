# verify_pilch_2021_coping_behavior.R -- Step 5b, route 3 (published subscale totals).
#
# CLAIM UNDER TEST. The shipped item_text assigns the 10 "Preventive behavior"
# statements of S1 Table to BEH1..BEH10, the 3 "Avoidant behavior" statements to
# Avoidance1..3 and the 3 "Wishful thinking" statements to Wishful1..3, in the
# order S1 Table prints them under each construct heading.
#
# WHAT THIS SCRIPT FALSIFIES. Pilch et al. (2021) PLOS ONE 16(10):e0258606,
# Table 2, publishes the mean and SD of each of the three CBS subscale scores
# (each the mean of its member items, N = 397). If the item->subscale assignment
# shipped here were wrong -- e.g. if one of the three maladaptive statements
# actually belonged to the other maladaptive block, or if any BEH code were in
# fact a maladaptive item -- recomputing those three subscale scores from the
# live IRW table under the shipped assignment would miss the published values.
# It also settles that the responses are stored raw and unreversed: every CBS
# item is positively worded, so a reversed store would land at 8 - M.
#
# WHAT IT DOES NOT ESTABLISH -- read this before reading the verdict. It pins
# subscale MEMBERSHIP only. It cannot separate the items WITHIN a subscale from
# each other: swapping the text of BEH3 and BEH9, or of Wishful1 and Wishful2,
# leaves every number below unchanged. The study publishes no per-item
# statistics, factor loadings or item-total correlations, so no route in Step 5b
# can pin the within-subscale order. That order rests on the S1 Table listing
# order matching the ...1/...2/...3 numbering carried by the .sav's own variable
# labels ("Preventive behavior 7", "Wishful thinking3"). Hence PARTIAL.

suppressMessages(library(irw))

TABLE <- "pilch_2021_coping_behavior"

SUBSCALE <- list(
    `Preventive behavior` = paste0("BEH", 1:10),
    `Avoidant behavior`   = paste0("Avoidance", 1:3),
    `Wishful thinking`    = paste0("Wishful", 1:3)
)
# Pilch, Wardawy & Probierz (2021), Table 2, columns (13)(14)(15), N = 397.
PUBLISHED_M  <- c(`Preventive behavior` = 5.05, `Avoidant behavior` = 3.43,
                  `Wishful thinking` = 3.09)
PUBLISHED_SD <- c(`Preventive behavior` = 1.20, `Avoidant behavior` = 1.46,
                  `Wishful thinking` = 1.30)
TOL_M  <- 0.03
TOL_SD <- 0.03

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

cat(sprintf("%-20s %5s %9s %8s %8s %9s %8s %8s\n",
            "subscale", "k", "pub M", "obs M", "diff", "pub SD", "obs SD", "diff"))
worst <- 0
for (nm in names(SUBSCALE)) {
    its <- SUBSCALE[[nm]]
    sub <- d[d$item %in% its, c("id", "item", "resp")]
    # person-level subscale score = mean of that person's member items
    sc <- tapply(sub$resp, sub$id, mean)
    om <- mean(sc); osd <- stats::sd(sc)
    cat(sprintf("%-20s %5d %9.2f %8.3f %8.3f %9.2f %8.3f %8.3f\n",
                nm, length(its), PUBLISHED_M[nm], om, om - PUBLISHED_M[nm],
                PUBLISHED_SD[nm], osd, osd - PUBLISHED_SD[nm]))
    worst <- max(worst, abs(om - PUBLISHED_M[nm]), abs(osd - PUBLISHED_SD[nm]))
}

cat(sprintf("\nlargest deviation from published: %.3f (tolerance %.2f)\n", worst, TOL_M))
cat("Reversal check: all three observed means sit on the published side of the\n",
    "scale midpoint (4), not at 8 - M, so the live resp values are stored raw.\n", sep = "")
cat("NOT established: the order of items within any subscale (see header).\n")

cat(if (worst <= max(TOL_M, TOL_SD)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
