# verify_ren_2024_phq9.R -- Step 5b check for batch_320.
#
# Claim: live codes P1..P9 (the deposit's own column names, melted unchanged by
# data/ren_2024_rural_elderly.py) are canonical PHQ-9 items 1..9, and resp 1..4
# are the canonical 0..3 anchors shifted by +1 (1 = "Not at all" .. 4 = "Nearly
# every day").
#
# Routes:
#  (A) option axis, route 3: paper Table 2 (Sci Rep 14:14057) reports Depression
#      M = 4.57, SD = 4.71, N = 1587 on the paper's 0-3 coding. sum(resp - 1)
#      must reproduce it; the reversed direction (4 - resp) would give ~22.4.
#  (B) item axis, route 7: PHQ-9 item 9 (thoughts of death/self-harm) must be
#      the least endorsed item in a community sample -- pins P9.
#  (C) item axis, structural signature: items 1-2 (the PHQ-2 core: anhedonia,
#      depressed mood) are the most strongly intercorrelated pair.
# NOT established: the order among P3..P8 (e.g. P5 vs P7 vs P8 are not
# distinguished by any published statistic); those rest on canonical numbering.

suppressMessages(library(irw))
TABLE <- "ren_2024_phq9"
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
P <- paste0("P", 1:9)
w <- w[complete.cases(w[, P]), ]

# (A)
tot <- rowSums(w[, P] - 1); rev <- rowSums(4 - w[, P])
cat(sprintf("(A) N complete = %d (published 1587)\n", nrow(w)))
cat(sprintf("    total, resp-1 : M = %.2f SD = %.2f  (published 4.57 / 4.71)\n", mean(tot), sd(tot)))
cat(sprintf("    total, 4-resp : M = %.2f SD = %.2f  (reversed direction)\n", mean(rev), sd(rev)))
okA <- nrow(w) == 1587 && abs(mean(tot) - 4.57) < 0.01 && abs(sd(tot) - 4.71) < 0.01

# (B)
m <- colMeans(w[, P]); fl <- colMeans(w[, P] == 1) * 100
cat("(B) item means / % at floor:\n")
for (p in P) cat(sprintf("    %s  %.3f  %5.1f%%\n", p, m[p], fl[p]))
okB <- names(which.min(m)) == "P9" && names(which.max(fl)) == "P9"
cat(sprintf("    least endorsed: %s (next lowest mean %.3f, %s)\n",
            names(which.min(m)), sort(m)[2], names(sort(m))[2]))

# (C)
r <- cor(w[, P]); r[lower.tri(r, diag = TRUE)] <- NA
top <- which(r == max(r, na.rm = TRUE), arr.ind = TRUE)
pair <- paste(P[top[1, 1]], P[top[1, 2]])
cat(sprintf("(C) strongest inter-item r = %.3f for %s; next = %.3f\n",
            max(r, na.rm = TRUE), pair, sort(r, decreasing = TRUE)[2]))
okC <- pair == "P1 P2"

cat("Note: P9 and the {P1,P2} pair are pinned; order within P3..P8 is not.\n")
cat(if (okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
