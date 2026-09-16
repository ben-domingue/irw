# verify_yin_2022_values_importance.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: each live `item` string carries the option labels
# 5="Very important" ... 1="Not important", i.e. both mapping axes.
#
# FALSIFIABLE PREDICTION: Yin et al. (2022) PLOS ONE 17(9):e0275292 Table 4
# prints, for all 13 items, the full 5-category response distribution in the
# "All (n = 148)" column (the GAD-7-complete subsample). The live table holds
# the full sample (n = 151-153 per item), so every live cell must be >= its
# published counterpart by a small margin, and each published profile must be
# nearest to the live item it is claimed to belong to. A reversed option scale,
# or any permutation of the 13 items, breaks this immediately (e.g. "Becoming
# famous" is the only descending profile in the set).
#
# Published counts are ordered Very important, Somewhat important, Neutral,
# Not very important, Not important -- i.e. resp 5,4,3,2,1.

suppressMessages(library(irw))

TABLE <- "yin_2022_values_importance"

PUBLISHED <- list(
  "How important is having friends/socializing"      = c(78, 38, 21,  9,  1),
  "How important is your friends perception of you"  = c(22, 44, 39, 35,  7),
  "How important is making your parents proud"       = c(61, 49, 25,  8,  3),
  "How important is maintaining family relations"    = c(60, 41, 30, 13,  2),
  "How important is good health (not getting covid)" = c(78, 29, 28,  7,  5),
  "How important is feeling safe"                    = c(66, 34, 27, 15,  3),
  "How important is getting good grades"             = c(91, 37, 12,  7,  0),
  "How important is finishing high school "          = c(120, 14, 11,  2,  0),
  "How important is going to college"                = c(108, 20, 13,  6,  0),
  "How important is fame"                            = c(  5, 11, 26, 45, 60),
  "How important is having adventure"                = c( 29, 43, 39, 32,  3),
  "How important is money/wealth"                    = c( 32, 52, 45, 14,  3),
  "How important is having your own family"          = c( 51, 37, 27, 22,  9)
)

d <- irw::irw_fetch(TABLE)
tb <- table(d$item, d$resp)
live <- t(apply(tb[names(PUBLISHED), c("5","4","3","2","1"), drop = FALSE], 1, identity))

cat(sprintf("%-50s %-22s %-22s %6s\n", "item", "published(VI..NI)", "live(5..1)", "maxdiff"))
ok_cell <- TRUE
for (it in names(PUBLISHED)) {
    p <- PUBLISHED[[it]]; l <- as.integer(live[it, ])
    dif <- l - p
    cat(sprintf("%-50s %-22s %-22s %6d\n", substr(it, 1, 50),
                paste(p, collapse = ","), paste(l, collapse = ","), max(abs(dif))))
    # live is a superset of the published subsample: every cell >= published,
    # and the excess is bounded by the 5 extra respondents per item.
    if (any(dif < 0) || any(dif > 6)) ok_cell <- FALSE
}

# Discrimination: is each published profile NEAREST (in proportion space) to the
# live item it is claimed to be? This is what breaks under any permutation.
prop <- function(v) v / sum(v)
lp <- t(apply(live, 1, prop))
nearest <- sapply(names(PUBLISHED), function(it) {
    d2 <- apply(lp, 1, function(r) sum(abs(r - prop(PUBLISHED[[it]]))))
    names(which.min(d2))
})
n_ok <- sum(nearest == names(PUBLISHED))
cat(sprintf("\nnearest-profile assignment: %d/13 published profiles map back to their claimed live item\n", n_ok))
wrong <- names(PUBLISHED)[nearest != names(PUBLISHED)]
if (length(wrong)) cat("  mismatched:", paste(wrong, collapse = " | "), "\n")

# Orientation: under a reversed option scale the published profiles would have
# to match the live distributions read backwards. Show that they do not.
lp_rev <- t(apply(lp, 1, rev))
n_rev <- sum(sapply(names(PUBLISHED), function(it)
    which.min(apply(lp_rev, 1, function(r) sum(abs(r - prop(PUBLISHED[[it]]))))) == match(it, rownames(lp))))
cat(sprintf("same test with the option scale reversed: %d/13 (must be low if 5=\"Very important\" is right)\n", n_rev))

cat("\nNote: this pins every item's wording AND the option-label direction. It does\n",
    "not test `instrument`/`section_id`, and the published subsample (n=148) is\n",
    "smaller than the live sample, so exact cell equality is not expected.\n", sep = "")

cat(if (ok_cell && n_ok == 13 && n_rev <= 2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
