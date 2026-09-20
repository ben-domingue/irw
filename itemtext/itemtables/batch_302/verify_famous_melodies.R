# Verification for famous_melodies (#2228, batch_302).  STATUS: PARTIAL.
#
# SOURCE. Belfi & Kacirek (2021), 'The famous melodies stimulus set', Behavior
# Research Methods 53:34, doi:10.3758/s13428-020-01411-6; deposit osf.io/wrqzm.
#
# THE ITEMS ARE RATING DIMENSIONS AND THE PERSONS ARE SONGS, which inverts the
# usual roles: data/famous_melodies.R sets id <- x$stimulus and item <-
# x$condition, so a row is one listener rating one melody on one dimension, with
# the listener in `rater`. Anyone grouping by id is grouping by melody.
#
# THE ANCHOR LABELS ARE NOT AVAILABLE, which is why this is PARTIAL. The paper
# is not open access -- Europe PMC has no full text and the Springer page
# returns a stub -- and the deposit's supplement is a table of normative means
# with no scale description. So option_text is blank and section_prompt records
# the observed range instead of inventing labels.
#
# Route 1: five dimensions, matching the supplement's columns.
# Route 2: each dimension has its own scale, which is why one shared set of
#   anchors would have been wrong.
d <- as.data.frame(irw::irw_fetch("famous_melodies"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_302/famous_melodies__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: the five rating dimensions ===\n")
EXP <- c("valence","arousal","familiarity","age_of_acquisition","naming")
r1 <- setequal(unique(d$item), EXP)
cat(sprintf("  live items: %s\n", paste(sort(unique(d$item)), collapse = ", ")))
cat(sprintf("  matches the supplement's rating columns (Valence, Arousal, Familiarity,\n  Age, Naming): %s\n", r1))
cat(sprintf("  melodies rated: %d; listeners: %d\n", length(unique(d$id)), length(unique(d$rater))))

cat("\n=== Route 2: each dimension has its own scale ===\n")
for (i in sort(unique(d$item))) {
    lv <- sort(unique(d$resp[d$item == i]))
    cat(sprintf("  %-20s n=%5d  levels %2d  range %g-%g\n", i, sum(d$item == i), length(lv),
                min(lv), max(lv)))
}
rng <- sapply(EXP, function(i) paste(range(d$resp[d$item == i]), collapse = "-"))
r2 <- length(unique(rng)) > 1
cat(sprintf("  -> the dimensions do NOT share one scale: %s\n", r2))
cat("  age_of_acquisition runs 1-8, three dimensions run 0-4, and naming is 0/1.\n")
cat("  Shipping a single anchor set across the table would have been wrong on\n")
cat("  four of five items, which is why section_prompt records each observed\n")
cat("  range and option_text is left empty.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  The anchor wording, and therefore the direction of any dimension. The\n")
cat("  paper is paywalled and the deposit does not describe the scales, so\n")
cat("  item_text is this project's bracketed description of each dimension --\n")
cat("  '[rating of the melody's valence -- how positive or negative it sounds]' --\n")
cat("  and not administered text. A reader cannot tell from this table whether 0\n")
cat("  on valence is negative or positive. That is the gap, and it is stated\n")
cat("  rather than guessed at. naming is the one unambiguous dimension: 0/1 for\n")
cat("  whether the listener named the melody.\n")
cat("\nVERDICT:", if (r1 && r2) "PASS" else "FAIL", "\n")
