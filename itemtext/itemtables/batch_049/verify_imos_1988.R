# verify_imos_1988.R -- Step 5b evidence for imos_1988 (29th IMO, Canberra 1988).
#
# CLAIM: live item code `problemK` is the official IMO 1988 Problem K, so the
# item_text shipped for `problemK` (transcribed from the official archive PDF
# imo-official.org/assets/documents/problems/1988/1988_eng.pdf, whose problems
# are numbered 1..6) is the wording contestants were scored on.
#
# FALSIFIABLE PREDICTION: the official IMO results page publishes every 1988
# contestant's six problem scores in problem order
# (https://www.imo-official.org/results/individual/year/1988/, embedded JSON,
# `scores` = [P1..P6]). If problemK is Problem K, then the full 0-7 score
# distribution of live item problemK must equal the official distribution of
# P_K, cell for cell -- 6 items x 8 levels. A swap of any two problems breaks
# it, because all six distributions are pairwise distinct (below).
#
# Hard-coded below: counts of score 0,1,...,7 per problem, from that page,
# fetched 2026-09-07 (268 contestants, matching the 268 ids per item in IRW).

suppressMessages(library(irw))

TABLE <- "imos_1988"

OFFICIAL <- rbind(
  problem1 = c(27,  56, 19, 24, 22, 14, 8, 98),
  problem2 = c(92,  16, 13, 19, 25, 24, 7, 72),
  problem3 = c(75, 132, 13,  1,  3,  4, 9, 31),
  problem4 = c(136, 25, 12, 17,  3,  3, 6, 66),
  problem5 = c(76,  35, 23, 10, 20, 11, 7, 86),
  problem6 = c(189, 57,  3,  5,  1,  1, 1, 11)
)
colnames(OFFICIAL) <- as.character(0:7)

d <- irw::irw_fetch(TABLE)              # 1,608 rows -- small, deliberate fetch
obs <- table(factor(d$item, levels = rownames(OFFICIAL)),
             factor(d$resp, levels = 0:7))
obs <- matrix(as.integer(obs), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("score counts 0..7, official IMO 1988 results vs live IRW table\n\n")
for (i in rownames(OFFICIAL)) {
  cat(sprintf("%-9s official: %s\n", i, paste(sprintf("%4d", OFFICIAL[i, ]), collapse = "")))
  cat(sprintf("%-9s live    : %s   %s\n", "", paste(sprintf("%4d", obs[i, ]), collapse = ""),
              if (all(OFFICIAL[i, ] == obs[i, ])) "MATCH" else "DIFFER"))
}

cat(sprintf("\nmeans  official: %s\n", paste(sprintf("%6.3f", (OFFICIAL %*% 0:7) / rowSums(OFFICIAL)), collapse = "")))
cat(sprintf("means  live    : %s\n",   paste(sprintf("%6.3f", (obs      %*% 0:7) / rowSums(obs)),      collapse = "")))

# Are the six official distributions pairwise distinct? If two matched, the
# route could not separate those two items.
dupes <- 0L
for (a in 1:5) for (b in (a + 1):6) if (all(OFFICIAL[a, ] == OFFICIAL[b, ])) dupes <- dupes + 1L
cat(sprintf("\npairs of problems with identical official distributions: %d of 15\n", dupes))

ok <- all(OFFICIAL == obs) && dupes == 0L
cat("Note: this pins every item against every other item (all 15 pairs distinguished),\n",
    "but it verifies only which SCORE COLUMN each code is -- the tie from score column\n",
    "to problem WORDING rests on the official archive numbering both alike (1..6).\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
