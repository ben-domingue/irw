# Step 5b mapping verification for pilch_2021_ipip20_validation.
#
# mapping_basis = paper_explicit. The deposit's "Materials" sheet heads a block
# "Personality traits (IPIP-IPIP1 - IPIP-IPIP20)" and then lists 20 items; the
# nth listed item is IPIP<n>. Nothing in the data file ties a code to its text,
# so the tie is positional-within-a-named-range and needs checking.
#
# WHAT WOULD BREAK IF THE MAPPING WERE WRONG
# The IPIP-BFM-20 is an interleaved five-factor marker set: reading the shipped
# item_text off, the implied assignment is
#
#   Extraversion        IPIP1  IPIP6- IPIP11 IPIP16-
#   Agreeableness       IPIP2- IPIP7  IPIP12- IPIP17
#   Conscientiousness   IPIP3- IPIP8  IPIP13- IPIP18
#   Emotional stability IPIP4  IPIP9- IPIP14  IPIP19-
#   Intellect           IPIP5  IPIP10- IPIP15 IPIP20-
#
# (a trailing "-" marks an item whose text is negatively worded). That is the
# canonical every-fifth-item layout, and it is a FALSIFIABLE claim about the
# responses: if the text had been slid by one position, or two items swapped
# across blocks, the four items the text assigns to a factor would stop cohering
# better than items the text assigns elsewhere.
#
# So the test is: after reversing the negatively-worded items, does each item's
# RESPONSE profile put it closest to the block its TEXT claims? That is 20
# independent falsifiable calls. Two rivals are ruled out explicitly -- 2000
# random re-assignments of the stems to the codes, and the "items are blocks of
# four consecutive codes" reading. See the note further down for a third test
# that looks reasonable and is worthless.
#
# WHAT THIS DOES *NOT* ESTABLISH
# It pins each item to its FACTOR, not to its individual stem. Swapping IPIP1
# with IPIP11 (both Extraversion, both positively worded) would leave every
# number below unchanged. Hence status=PARTIAL, not VERIFIED.

RESP <- "irw_output/pilch_2021_ipip20_validation.csv"
if (!file.exists(RESP)) RESP <- file.path("automated_finding", RESP)
d <- read.csv(RESP, stringsAsFactors = FALSE)

wide <- reshape(d[, c("id", "item", "resp")], idvar = "id",
                timevar = "item", direction = "wide")
names(wide) <- sub("^resp\\.", "", names(wide))
wide <- wide[, paste0("IPIP", 1:20)]
wide <- wide[complete.cases(wide), ]
cat(sprintf("respondents with a complete IPIP block: %d\n\n", nrow(wide)))

# Negatively-worded items, read off the shipped English item_text_translated.
NEG <- c(6, 16, 2, 12, 3, 13, 9, 19, 10, 20)
scored <- wide
scored[, NEG] <- 6 - scored[, NEG]

BLOCKS <- list(Extraversion = c(1, 6, 11, 16), Agreeableness = c(2, 7, 12, 17),
               Conscientiousness = c(3, 8, 13, 18),
               `Emotional stability` = c(4, 9, 14, 19),
               Intellect = c(5, 10, 15, 20))

cm <- cor(scored, use = "complete.obs")

mean_within <- function(idx) {
    sub <- cm[idx, idx]
    mean(sub[upper.tri(sub)])
}
mean_between <- function(idx) {
    mean(cm[idx, setdiff(1:20, idx)])
}

cat(sprintf("%-20s %8s %8s %8s\n", "block", "within", "between", "gap"))
gaps <- numeric(0)
for (nm in names(BLOCKS)) {
    w <- mean_within(BLOCKS[[nm]]); b <- mean_between(BLOCKS[[nm]])
    gaps <- c(gaps, w - b)
    cat(sprintf("%-20s %8.3f %8.3f %8.3f\n", nm, w, b, w - b))
}
cat(sprintf("\nevery block coheres above its cross-block mean: %s\n",
            all(gaps > 0)))

# RIVAL MAPPINGS -- and one test that does NOT work, recorded so it is not
# re-invented. A cyclic shift of the text by k positions maps the interleaved
# partition {i, i+5, i+10, i+15} onto ITSELF (k=5 is the identity on sets), so
# every shift yields a valid five-block partition and merely relabels which
# block is called Extraversion. It cannot falsify the mapping, and read naively
# its numbers say the shipped mapping "loses" to k=1. The first draft of this
# file did exactly that and reported FAIL on a mapping that is in fact correct.
#
# The test that does work is per-item: for each item, which block do the
# RESPONSES put it closest to, and is that the block its TEXT claims? That is
# 20 independent falsifiable calls, and a slid or swapped text breaks them.
cat("\nper-item block recovery (correlation with each block, reverse-coded)\n")
claimed <- character(20)
for (nm in names(BLOCKS)) claimed[BLOCKS[[nm]]] <- nm
affinity <- sapply(BLOCKS, function(idx)
    sapply(1:20, function(i) mean(cm[i, setdiff(idx, i)])))
recovered <- colnames(affinity)[apply(affinity, 1, which.max)]
cat(sprintf("%-8s %-20s %-20s %8s %8s\n",
            "item", "text says", "responses say", "own", "next"))
for (i in 1:20) {
    a <- sort(affinity[i, ], decreasing = TRUE)
    cat(sprintf("%-8s %-20s %-20s %8.3f %8.3f%s\n",
                paste0("IPIP", i), claimed[i], recovered[i],
                affinity[i, claimed[i]], a[2],
                if (claimed[i] == recovered[i]) "" else "   <- MISMATCH"))
}
n_ok <- sum(claimed == recovered)
cat(sprintf("\nitems whose responses recover the block their text claims: %d of 20\n",
            n_ok))

# Rival: random re-assignments of the 20 stems to the 20 codes. The shipped
# mapping should sit in the extreme tail, not merely above average.
set.seed(1)
perm_scores <- replicate(2000, {
    p <- sample(20)
    sum(claimed[p] == colnames(affinity)[apply(affinity, 1, which.max)])
})
cat(sprintf("random stem-to-code permutations: mean %.2f of 20, max %d of 2000 draws\n",
            mean(perm_scores), max(perm_scores)))
cat(sprintf("shipped mapping beats all %d random permutations: %s\n",
            length(perm_scores), n_ok > max(perm_scores)))

# Rival: consecutive blocks (1-4, 5-8, ...) rather than interleaved.
consec <- lapply(seq(1, 20, 4), function(s) s:(s + 3))
gap_consec <- mean(sapply(consec, function(idx) {
    s <- cm[idx, idx]
    mean(s[upper.tri(s)]) - mean(cm[idx, setdiff(1:20, idx)])
}))
cat(sprintf("interleaved (shipped) mean gap %.3f vs consecutive-blocks %.3f\n",
            mean(gaps), gap_consec))

ok <- all(gaps > 0) && n_ok == 20 && n_ok > max(perm_scores) &&
      mean(gaps) > gap_consec
cat(sprintf("\nVERDICT: %s\n", if (ok) "PASS" else "FAIL"))
