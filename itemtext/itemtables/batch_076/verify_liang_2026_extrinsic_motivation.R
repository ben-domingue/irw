# Step 5b re-runnable evidence for liang_2026_extrinsic_motivation.
#
# THE CLAIM UNDER TEST. The IRW item codes EM1..EM5 are the source CSV's own
# column names (data/liang_2026_exercise_motivation.py renames EM1_num..EM5_num
# to EM1..EM5 by name), but the source file carries NO item wording -- its
# headers are bare codes. The wording comes from the paper's Table 1, which
# numbers the ten items 1-10 and groups 6-10 under "Extrinsic Motivation"
# WITHOUT printing the EM codes. So the shipped mapping is an ORDER inference:
#   EM1=item6, EM2=item7, EM3=item8, EM4=item9, EM5=item10.
# What is testable is the paper's own statement of where each item came from:
#   items 6-8  adapted from Asad et al. [16]  -- app engagement / task motivation
#   item  9    from Eom & Ashill [17]         -- grade-oriented motivation
#   item  10   from Tsai et al. [18]          -- social-recognition motivation
# That predicts a 3+1+1 structure in the live correlations: EM1-EM3 a tight
# block, EM4 attached but looser (still app-referential), EM5 the most
# peripheral (no app reference at all, ego/social recognition).
#
# This does NOT establish the order WITHIN {EM1,EM2,EM3} -- see the note at the
# end. Status recorded as PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "liang_2026_extrinsic_motivation"

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id","item","resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
items <- paste0("EM", 1:5)
w <- w[, items]
cat("N respondents:", nrow(w), "\n\n")

R <- cor(w)
cat("EM inter-item correlation matrix (live data):\n")
print(round(R, 3))

rest <- sapply(items, function(v)
    cor(w[[v]], rowMeans(w[, setdiff(items, v), drop = FALSE])))
cat("\nitem-rest correlations:\n")
print(round(rest, 3))

# Prediction 1: the Asad block {EM1,EM2,EM3} is internally tighter than any
# correlation either of the two single-source items has with that block.
block <- c(R["EM1","EM2"], R["EM1","EM3"], R["EM2","EM3"])
em4_block <- c(R["EM4","EM1"], R["EM4","EM2"], R["EM4","EM3"])
em5_block <- c(R["EM5","EM1"], R["EM5","EM2"], R["EM5","EM3"])
cat(sprintf("\nwithin {EM1,EM2,EM3}: min %.3f  (r = %s)\n",
            min(block), paste(sprintf("%.2f", block), collapse = ", ")))
cat(sprintf("EM4 (item 9, Eom & Ashill) to that block: max %.3f\n", max(em4_block)))
cat(sprintf("EM5 (item 10, Tsai)        to that block: max %.3f\n", max(em5_block)))

p1 <- min(block) > max(em4_block) && min(block) > max(em5_block)
# Prediction 2: EM5, the only item with no reference to the app, is the most
# peripheral item of the five.
p2 <- which.min(rest) == 5
# Prediction 3: EM4 sits between the block and EM5 in centrality.
p3 <- mean(em4_block) > mean(em5_block)

cat(sprintf("\nP1 Asad block tighter than either outside item: %s\n", p1))
cat(sprintf("P2 EM5 lowest item-rest (%.3f, next lowest %.3f): %s\n",
            min(rest), sort(rest)[2], p2))
cat(sprintf("P3 EM4 closer to block than EM5 (%.3f vs %.3f): %s\n",
            mean(em4_block), mean(em5_block), p3))

cat("\nNOTE -- what this does NOT establish: it separates the three Asad-sourced\n",
    "items from item 9 and item 10 and distinguishes those two from each other,\n",
    "but it cannot order EM1/EM2/EM3 among themselves, because all three come\n",
    "from one source scale and their pairwise r (0.77-0.83) are within noise of\n",
    "each other at N=45. A permutation inside that triple would not be detected.\n",
    "The paper's published EFA (S1 Table) is NOT usable as a stronger route: a\n",
    "2-factor varimax PA solution on the deposited data does not reproduce the\n",
    "published IM/EM split at all (EM loadings 0.90/0.82/0.73/0.47/0.37 on the\n",
    "first factor against a published 0.71/0.75/0.69/0.77/0.74).\n", sep = "")

cat(if (p1 && p2 && p3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
