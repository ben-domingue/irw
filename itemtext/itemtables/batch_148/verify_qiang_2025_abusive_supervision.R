# verify_qiang_2025_abusive_supervision.R
#
# mapping_basis = data_labels: data/qiang_2025_red_tape.py renames the S1 File
# columns by an exact literal header->code dictionary
#   "38<U+3001>My supervisor does not praise me for the efforts I make at work." -> as1
#   "39<U+3001>My supervisor avoids embarrassment by blaming me."               -> as2
#   "40<U+3001>My supervisor gives me the silent treatment."                    -> as3
#   "41<U+3001>My supervisor takes out their anger on me when upset ..."        -> as4
# so the shipped item_text IS the source column header and no order inference
# was made. This script nonetheless checks the tie against the data (Step 5b
# route 9): the four source columns have DISTINCT response-frequency profiles,
# so a permutation of the four texts would break the cell-by-cell match.
#
# Falsifiable claim: for each code, the live per-resp counts equal the counts of
# the S1 column whose header we shipped as that code's item_text.

suppressMessages(library(irw))

TABLE <- "qiang_2025_abusive_supervision"

# Counts of resp levels 1..5 in the S1 File (.s001 XLSX, N=396, no missing),
# taken from the column carrying the item_text shipped for each code.
SRC <- rbind(
  as1 = c(3, 32, 49, 209, 103),
  as2 = c(19, 91, 68, 147, 71),
  as3 = c(7, 29, 75, 221, 64),
  as4 = c(20, 90, 47, 151, 88)
)
colnames(SRC) <- 1:5

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
LIVE <- table(factor(d$item, levels = rownames(SRC)), factor(d$resp, levels = 1:5))

cat("resp level:            1     2     3     4     5\n")
for (it in rownames(SRC)) {
  cat(sprintf("%-4s source  %6d%6d%6d%6d%6d\n", it, SRC[it, 1], SRC[it, 2], SRC[it, 3], SRC[it, 4], SRC[it, 5]))
  cat(sprintf("%-4s live    %6d%6d%6d%6d%6d\n", it, LIVE[it, 1], LIVE[it, 2], LIVE[it, 3], LIVE[it, 4], LIVE[it, 5]))
}

ok <- all(as.matrix(LIVE) == SRC)
cat(sprintf("\nall 20 item x level cells match: %s\n", ok))

# The four profiles are mutually distinct, so no permutation of the four texts
# reproduces this table -- the check separates every item from every other.
dist <- min(dist(SRC))
cat(sprintf("minimum Euclidean distance between any two source profiles: %.1f (0 would mean two items are indistinguishable)\n", dist))

# What this does NOT establish: nothing about the ANCHOR wording (1 = strongly
# disagree, 5 = strongly agree) -- that comes from the paper's Measures section,
# not from these counts, which are direction-agnostic.

cat(if (ok && dist > 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
