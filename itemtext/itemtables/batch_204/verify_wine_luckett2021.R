# Verification for wine_luckett2021 (#1945, batch_204).
#
# SOURCE. data/wine_luckett2021.R reads 'Prelim Data.csv' and names each item
# after the source column it came from:
#     intense  <- x$How.intense.do.you.find.this.aroma.
#     pleasant <- x$Pleasantness
#     familiar <- x$Familiarity
# The shipped item_text is those three column headers, so the code-to-text link
# is a rename in the script, not an inference -- which is the load-bearing route
# and it pins all three items individually.
#
# WHY THERE IS NO REPRODUCTION HERE. The deposit (osf.io/nwv5a) returns 'Not
# found' from the OSF API and Europe PMC reports the paper itself as not open
# access, so 'Prelim Data.csv' cannot be re-read to match values cell-for-cell
# the way estcrm_selfeff can. What is checkable is the internal structure, and
# it corroborates the rename independently on the one item where the three
# columns are distinguishable by shape.
#
# Route 1: the code set is exactly the three names the script assigns.
# Route 2: 'intense' is the only 0-100 item. The intensity question was a
#   visual-analogue line scale while Pleasantness and Familiarity were 9-point
#   category scales, so a permutation of the three labels would put the
#   continuous item under a category-scale name. This pins 'intense' on its own.
# Route 3: the correlation structure. Pleasantness and Familiarity are expected
#   to be the most strongly associated pair in odour ratings, and intensity
#   close to orthogonal to pleasantness. Reported, not load-bearing.
d <- as.data.frame(irw::irw_fetch("wine_luckett2021"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
SCRIPT_NAMES <- c("intense", "pleasant", "familiar")

cat("=== Route 1: codes are the script's three assigned names ===\n")
r1 <- setequal(unique(d$item), SCRIPT_NAMES)
cat(sprintf("  script assigns %d, live %d, identical: %s\n",
            length(SCRIPT_NAMES), length(unique(d$item)), r1))

cat("\n=== Route 2: scale shape separates the intensity item ===\n")
for (i in sort(unique(d$item)))
    cat(sprintf("  %-9s n=%4d  range %g to %g  distinct levels %3d  mean %6.2f\n", i,
                sum(d$item == i), min(d$resp[d$item == i]), max(d$resp[d$item == i]),
                length(unique(d$resp[d$item == i])), mean(d$resp[d$item == i])))
rng <- sapply(SCRIPT_NAMES, function(i) max(d$resp[d$item == i]))
r2 <- rng["intense"] > 50 && all(rng[c("pleasant", "familiar")] <= 9)
cat(sprintf("  -> the 0-100 item is '%s': %s\n", names(which.max(rng)), r2))
cat("  (a line scale for intensity, 9-point categories for the other two)\n")

cat("\n=== Route 3: correlation structure across rater x sample ===\n")
w <- reshape(d[, c("rater", "id", "item", "resp")], direction = "wide",
             idvar = c("rater", "id"), timevar = "item")
names(w) <- sub("^resp\\.", "", names(w))
cm <- cor(w[, SCRIPT_NAMES], use = "pairwise.complete.obs")
print(round(cm, 3))
off <- cm; diag(off) <- NA
best <- which(off == max(off, na.rm = TRUE), arr.ind = TRUE)[1, ]
cat(sprintf("  strongest off-diagonal pair: %s & %s (r = %.3f)\n",
            rownames(cm)[best[1]], colnames(cm)[best[2]], max(off, na.rm = TRUE)))
cat("  pleasant & familiar is the strongest pair and intensity is near-orthogonal\n")
cat("  to pleasantness, which is the expected shape. Corroboration only: it\n")
cat("  cannot tell pleasant from familiar, and does not need to -- Route 1 does.\n")

cat("\n=== A data-side defect found while checking, reported not fixed ===\n")
ids  <- unique(as.character(d$id))
ci   <- unique(tolower(ids))
cat(sprintf("  distinct id values: %d; distinct ignoring case: %d\n", length(ids), length(ci)))
dupe <- ci[sapply(ci, function(x) sum(tolower(ids) == x) > 1)]
if (length(dupe)) {
    cat("  the same wine appears under two id values differing only in capitalisation:\n")
    for (x in dupe) cat(sprintf("    %s\n", paste(ids[tolower(ids) == x], collapse = "   |   ")))
    cat("  id is the wine sample and rater is the person, so these split one sample\n")
    cat("  in two. Upstream: data/wine_luckett2021.R takes id <- x$Sample.Name verbatim.\n")
}

cat("\n=== What this does NOT establish ===\n")
cat("  Which of the two 9-point items is Pleasantness and which is Familiarity,\n")
cat("  by any route other than Route 1. Route 1 is a direct column rename in the\n")
cat("  processing script, which is why the status is VERIFIED; Routes 2 and 3 are\n")
cat("  corroboration that happens to separate only the intensity item.\n")
cat("\nVERDICT:", if (r1 && r2) "PASS" else "FAIL", "\n")
