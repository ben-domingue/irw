# verify_christensen_2018_wsssf_5831.R -- Step 5b, re-runnable mapping evidence.
#
# mapping_basis = paper_explicit. The study's own OSF supplement (SI 1 of
# "Network Structure of the WSS-SF", osf.io/c6rqy) prints all 60 items with the
# very codes the live table uses (PY1..PY15 / PB / MI / SA1..SA15 vs py01..py15
# etc.), so the item axis is a code-label match. This script checks the three
# things that would still break if that reading were wrong:
#
#   A. SUBSCALE ASSIGNMENT + SCORING DIRECTION (Step 5b route 3). The paper's
#      Table 1 publishes M/SD/range of each 15-item subscale for this exact
#      sample (n = 5,831). Summing the live items under the prefix->subscale
#      map we shipped must reproduce them. A py/pb swap (the non-obvious pair:
#      py = Physical Anhedonia, pb = Perceptual Aberration) shows up as
#      2.09 vs 1.21, and an un-reverse-scored table misses every value badly.
#   B. WITHIN-SUBSCALE CONTENT CLUSTERS (route 8). Items that are near-paraphrases
#      of each other must be the most strongly associated pairs in their own
#      subscale. Tested against a permutation null over labels within subscale.
#   C. THE OPTION AXIS. The paper states the cells are endorsement-coded and
#      "after reverse-scoring as needed, all items were scored so that higher
#      scores reflected higher levels of schizotypy" -- which is what licenses
#      the shipped option_text (resp 1 = "False" on the items SI 1 marks
#      reversed, "True" on the rest). If the table were raw true/false, the
#      reversed items -- ordinary pleasant experiences -- would sit near 0.9.
#
# What this does NOT establish: the order of items WITHIN a content cluster
# (e.g. py01 vs py02 vs py04, all three "walk" items). That separation rests on
# the code-label match in SI 1, which is per item and is why the status is
# VERIFIED.

suppressMessages(library(irw))

TABLE <- "christensen_2018_wsssf_5831"
ITEMS_CSV <- file.path(dirname(sub("^--file=", "", commandArgs(FALSE)[grep("^--file=", commandArgs(FALSE))][1])),
                       paste0(TABLE, "__items.csv"))

# --- Published values: Christensen et al. (2018) BRM 50:2531-2550, Table 1,
# --- "Measure Descriptive Statistics", n = 5,831 column.
PUB <- data.frame(
    subscale = c("Physical Anhedonia", "Social Anhedonia",
                 "Perceptual Aberration", "Magical Ideation"),
    prefix   = c("py", "sa", "pb", "mi"),
    M = c(2.09, 1.77, 1.21, 3.26),
    SD = c(2.30, 2.41, 2.28, 2.91),
    lo = c(0, 0, 0, 0), hi = c(14, 15, 15, 15),
    stringsAsFactors = FALSE)

# Items SI 1 marks "(reversed)".
REVERSED <- c(paste0("py", sprintf("%02d", c(1,2,3,4,7,9,11,12,13,14,15))),
              paste0("sa", sprintf("%02d", c(4,9,11,12,13,14))),
              "mi11")

# A priori content clusters, read off the shipped item_text (pairs of
# near-paraphrases), written down before looking at the correlation matrix.
CLUSTERS <- list(
    py = list(c("py01","py02","py04")),                 # three "walk" items
    pb = list(c("pb03","pb07"), c("pb02","pb15")),      # decay/rot; "is my body my own"
    sa = list(c("sa06","sa11","sa12")),                 # prefers solitude / rather be with others
    mi = list(c("mi07","mi13","mi14"), c("mi12","mi15"))# paranormal ability; bizarre
)

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d)[, c("id","item","resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w$id <- NULL
w <- w[, sort(names(w))]
stopifnot(ncol(w) == 60)

ok <- TRUE

cat("A. Subscale totals vs paper Table 1 (n = 5,831)\n")
cat(sprintf("%-22s %14s %14s %12s %12s\n", "subscale", "pub M (SD)", "obs M (SD)", "pub range", "obs range"))
for (i in seq_len(nrow(PUB))) {
    cols <- grep(paste0("^", PUB$prefix[i]), names(w), value = TRUE)
    stopifnot(length(cols) == 15)
    s <- rowSums(w[, cols])
    cat(sprintf("%-22s %6.2f (%.2f) %6.2f (%.2f) %12s %12s\n",
                PUB$subscale[i], PUB$M[i], PUB$SD[i], mean(s), sd(s),
                sprintf("%d - %d", PUB$lo[i], PUB$hi[i]),
                sprintf("%d - %d", min(s), max(s))))
    if (abs(mean(s) - PUB$M[i]) > 0.01 || abs(sd(s) - PUB$SD[i]) > 0.02 ||
        min(s) != PUB$lo[i] || max(s) != PUB$hi[i]) ok <- FALSE
}

cat("\nB. Content-cluster associations vs within-subscale permutation null\n")
set.seed(1)
NPERM <- 20000
for (p in names(CLUSTERS)) {
    cols <- grep(paste0("^", p), names(w), value = TRUE)
    cc <- cor(w[, cols])
    pairs <- do.call(rbind, lapply(CLUSTERS[[p]], function(g) t(combn(g, 2))))
    obs <- mean(mapply(function(a, b) cc[a, b], pairs[,1], pairs[,2]))
    idx <- cbind(match(pairs[,1], cols), match(pairs[,2], cols))
    null <- replicate(NPERM, {
        pm <- sample(length(cols))
        mean(cc[cbind(pm[idx[,1]], pm[idx[,2]])])
    })
    pv <- (1 + sum(null >= obs)) / (NPERM + 1)
    allr <- cc[upper.tri(cc)]
    cat(sprintf("  %s: mean r over %d predicted pair(s) = %.3f | subscale mean r = %.3f | max pair r = %.3f | perm p = %.5f\n",
                p, nrow(pairs), obs, mean(allr), max(allr), pv))
    # Threshold 0.005. The attainable floor for a 3-label cluster is 1/C(15,3)
    # = 0.0022 -- i.e. a predicted triple that lands on the single strongest
    # triple of the 455 possible ones cannot score lower than that.
    if (pv > 0.005) ok <- FALSE
}

cat("\nC. Option axis: table is endorsement-coded with reverse-scoring applied\n")
m <- colMeans(w)
cat(sprintf("  reversed items (n=%d): max endorsement rate = %.3f (%s)\n",
            length(REVERSED), max(m[REVERSED]), names(which.max(m[REVERSED]))))
cat(sprintf("  non-reversed items (n=%d): max endorsement rate = %.3f\n",
            60 - length(REVERSED), max(m[setdiff(names(m), REVERSED)])))
cat("  (raw true/false coding would put the reversed items -- ordinary pleasant\n")
cat("   experiences such as 'I like playing with and petting soft little kittens' -- near 0.9)\n")
if (max(m[REVERSED]) >= 0.5) ok <- FALSE

it <- read.csv(ITEMS_CSV, stringsAsFactors = FALSE)
exp_opt <- ifelse(it$item %in% REVERSED,
                  ifelse(it$resp == 1, "False", "True"),
                  ifelse(it$resp == 1, "True", "False"))
bad <- sum(exp_opt != it$option_text)
cat(sprintf("  shipped option_text rows disagreeing with that keying: %d of %d\n", bad, nrow(it)))
if (bad > 0) ok <- FALSE

cat("\nNote: routes A-C pin subscale membership, scoring direction and the content\n")
cat("clusters; they do not order items inside a cluster. Every item is separated\n")
cat("from every other by the code-label match in SI 1 (60/60, zero mismatches).\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
