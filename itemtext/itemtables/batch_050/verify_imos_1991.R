# verify_imos_1991.R -- Step 5b evidence for imos_1991 (32nd IMO, Sigtuna, Sweden, 1991).
#
# CLAIM: live item code `problemK` is the official IMO 1991 Problem K, so the
# item_text shipped for `problemK` (transcribed from the official archive PDF
# imo-official.org/assets/documents/problems/1991/1991_eng.pdf, whose problems
# are printed 1-3 under "First Day" and 1-3 again under "Second Day", i.e.
# overall 1..6) is the wording contestants were scored on.
#
# FALSIFIABLE PREDICTION: the official IMO results page publishes every 1991
# contestant's six problem scores in problem order
# (https://www.imo-official.org/results/individual/year/1991/, embedded JSON,
# `scores` = [P1..P6]). If problemK is Problem K, then the full 0-7 score
# distribution of live item problemK must equal the official distribution of
# P_K, cell for cell -- 6 items x 8 levels. A swap of any two problems breaks
# it, because all six distributions are pairwise distinct (checked below).
#
# Hard-coded below: counts of score 0,1,...,7 per problem, tallied from that
# page's embedded JSON, fetched 2026-09-07 (312 contestants, matching the 312
# ids per item in IRW and the 312 contestants imo-official.org lists for the
# 32nd IMO, Sigtuna, Sweden, July 12-23 1991).

suppressMessages(library(irw))

TABLE <- "imos_1991"

OFFICIAL <- rbind(
  problem1 = c( 93, 27, 10,   3, 34,  8,  6, 131),
  problem2 = c( 47, 34, 21,  27, 31,  6, 16, 130),
  problem3 = c( 90, 14, 16, 111, 37, 16,  5,  23),
  problem4 = c(112, 34, 15,  18, 10, 15, 13,  95),
  problem5 = c( 77, 42, 18,  14, 14,  6,  7, 134),
  problem6 = c(172, 29, 27,  16, 10,  5,  3,  50)
)
colnames(OFFICIAL) <- as.character(0:7)

d <- irw::irw_fetch(TABLE)              # 1,872 rows -- small, deliberate fetch
obs <- table(factor(d$item, levels = rownames(OFFICIAL)),
             factor(d$resp, levels = 0:7))
obs <- matrix(as.integer(obs), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("score counts 0..7, official IMO 1991 results vs live IRW table\n\n")
for (i in rownames(OFFICIAL)) {
  cat(sprintf("%-9s official: %s\n", i, paste(sprintf("%4d", OFFICIAL[i, ]), collapse = "")))
  cat(sprintf("%-9s live    : %s   %s\n", "", paste(sprintf("%4d", obs[i, ]), collapse = ""),
              if (all(OFFICIAL[i, ] == obs[i, ])) "MATCH" else "DIFFER"))
}

cat(sprintf("\nmeans  official: %s\n", paste(sprintf("%6.3f", (OFFICIAL %*% 0:7) / rowSums(OFFICIAL)), collapse = "")))
cat(sprintf("means  live    : %s\n",   paste(sprintf("%6.3f", (obs      %*% 0:7) / rowSums(obs)),      collapse = "")))
cat(sprintf("contestants per item, live: %s (official 1991 field: 312)\n",
            paste(unique(rowSums(obs)), collapse = ", ")))

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
