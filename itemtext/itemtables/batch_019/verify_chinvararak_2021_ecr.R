# verify_chinvararak_2021_ecr.R
#
# STATUS: this table is BLOCKED on the item-text rights rule (irw#1891) and ships NO
# __items.csv. There is therefore no shipped mapping to verify. This script exists so
# that the mapping evidence, which WAS fully established, is re-runnable if the rights
# posture is ever revisited -- see notes_chinvararak_2021_ecr.csv.
#
# The claim being checked: the live item codes ecr1..ecr18 correspond, number for
# number, to the 18 items of the Thai ECR-R-18 as numbered in Wongpakaran & Wongpakaran
# (2012) Clin Pract Epidemiol Ment Health 8:36-42, Table 1 -- odd numbers = avoidance,
# even numbers = anxiety.
#
# This is NOT a plumbing check: item counts and resp sets are irrelevant here. What is
# checked is the item->subscale assignment (which would break if the numbering were
# permuted across the two blocks) and the keying polarity of item 1 (which would break
# if item 1 were any of the seven comfort-worded avoidance items).
#
# Data: fetched from the study's own PLOS S1 SPSS file. The IRW processing script
# (data/chinvararak_2021_attachment_depression.py) melts ecr1..ecr18 with NO renaming,
# so the .sav column ecrN IS the live item code ecrN; no irw_fetch export is needed.

suppressMessages({ library(haven) })

SI <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0255995.s001")
tmp <- tempfile(fileext = ".sav")
download.file(SI, tmp, quiet = TRUE, mode = "wb")
d <- haven::read_sav(tmp)

anx <- paste0("ecr", c(2, 4, 6, 8, 10, 12, 14, 16, 18))   # Wongpakaran Table 1: anxiety
avo <- paste0("ecr", c(1, 3, 5, 7, 9, 11, 13, 15, 17))    # Wongpakaran Table 1: avoidance
all18 <- paste0("ecr", 1:18)

stopifnot(all(c(all18, "AnxietyScore", "AvoidanceScore") %in% names(d)))
cat(sprintf("n respondents: %d\n\n", nrow(d)))

# --- Route 3: does the asserted subscale membership reproduce the file's own scores? ---
a <- rowMeans(d[, anx]); v <- rowMeans(d[, avo])
da <- max(abs(a - d$AnxietyScore)); dv <- max(abs(v - d$AvoidanceScore))
cat("Route 3 -- subscale totals reproduced from the asserted item numbering\n")
cat(sprintf("  anxiety   mean of {%s}\n", paste(anx, collapse = ",")))
cat(sprintf("    computed mean %.4f vs stored AnxietyScore mean %.4f | max abs diff %.10f | r %.6f\n",
            mean(a), mean(d$AnxietyScore), da, cor(a, d$AnxietyScore)))
cat(sprintf("  avoidance mean of {%s}\n", paste(avo, collapse = ",")))
cat(sprintf("    computed mean %.4f vs stored AvoidanceScore mean %.4f | max abs diff %.10f | r %.6f\n\n",
            mean(v), mean(d$AvoidanceScore), dv, cor(v, d$AvoidanceScore)))

# Falsification check: the correct split must beat a wrong one. Swap two items across
# the blocks and confirm the reproduction breaks.
anx_bad <- sub("ecr2$", "ecr3", anx); avo_bad <- sub("ecr3$", "ecr2", avo)
da_bad <- max(abs(rowMeans(d[, anx_bad]) - d$AnxietyScore))
cat(sprintf("  falsification: swapping ecr2<->ecr3 across the blocks gives anxiety max abs diff %.4f (must be > 0)\n\n", da_bad))

# --- Route 6: keying polarity of item 1 ---
C <- cor(d[, all18])
r1_comfort <- C["ecr1", paste0("ecr", c(3, 5, 7, 9, 11, 13, 17))]
r1_anx     <- C["ecr1", anx]
cat("Route 6 -- polarity of ecr1 ('I prefer not to show a partner how I feel deep down')\n")
cat(sprintf("  r(ecr1, seven comfort-worded avoidance items): %.2f .. %.2f, mean %.2f  (must be <= 0.05 and mean < 0)\n",
            min(r1_comfort), max(r1_comfort), mean(r1_comfort)))
cat(sprintf("  r(ecr1, nine anxiety items):                   %.2f .. %.2f  (must be >= 0)\n\n",
            min(r1_anx), max(r1_anx)))

# --- Route 8: direction of the 1-7 anchors, on the reverse-free anxiety block ---
cat("Route 8 -- anchor direction (1 = strongly disagree .. 7 = strongly agree)\n")
cat(sprintf("  raw anxiety mean here %.3f; published ECR-R-18 anxiety means: non-clinical 3.01, clinical 3.70\n",
            mean(d$AnxietyScore)))
cat(sprintf("  a flipped coding would imply %.3f, outside both published samples\n\n",
            8 - mean(d$AnxietyScore)))

cat("Does NOT establish: anything about a shipped table (none was shipped, rights block),\n",
    "and does not separate items WITHIN a subscale -- that rests on the .sav's Thai\n",
    "variable labels matching Wongpakaran's numbered items one for one.\n\n", sep = "")

ok <- da < 1e-9 && dv < 1e-9 && da_bad > 0 &&
      max(r1_comfort) <= 0.05 && mean(r1_comfort) < 0 && min(r1_anx) >= 0
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
