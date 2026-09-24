# verify_islam_2022_phq9.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: live item codes PHQ1..PHQ9 carry the official PHQ-9 wording
# in the form's printed numbering (PHQ1 = "Little interest or pleasure in doing
# things", PHQ2 = "Feeling down, depressed, or hopeless", ... PHQ9 = "Thoughts
# that you would be better off dead or of hurting yourself in some way"), and
# resp 0/1/2/3 = Not at all / Several days / More than half the days / Nearly
# every day.
#
# The study's S1 .xlsx (PLOS 10.1371/journal.pone.0279062.s001) has bare headers
# PHQ1..PHQ9 with no labels; data/islam_2022_online_addiction.py melts them by
# name (code IS the column name). What is inferred is what each NAME means --
# the paper prints no PHQ-9 item wording and no per-item PHQ statistics.
#
# Predictions:
#
#   P1  RESPONSE-AXIS DIRECTION (option_text <-> resp). Raw row sums of the live
#       PHQ1..PHQ9 must reproduce the paper's Table 2 depression score, mean 6.29
#       (SD 6.47), N=428, and its Table 4 correlation with the GAD-7 total
#       (r = .659, GAD from the same deposit). If 0 and 3 were the other way
#       round the mean would be 27 - 6.29 = 20.71.
#   P2  PHQ-2 CORE PAIR. Items 1 (anhedonia) and 2 (depressed mood) form the
#       PHQ-2 and are each other's strongest correlate: argmax_j r(PHQ1, j) ==
#       PHQ2 AND argmax_j r(PHQ2, j) == PHQ1. Breaks if either of those two
#       wordings were attached to another code.
#   P3  MARKER ITEM (route 7). Item 9 (suicidal ideation) has the highest share
#       of zero responses of the nine.
#
# Informational only (not a pass criterion): the somatic {3,4,5} vs
# cognitive/affective {2,6,7,8,9} block contrast. It does NOT hold here (the
# printed within/cross means are near-equal), consistent with a PHQ-9 dominated
# by one factor in this sample -- underpowered, not evidence against mapping.
#
# WHAT THIS DOES NOT ESTABLISH: P2 pins {PHQ1, PHQ2} as a pair but not which of
# the two is anhedonia vs depressed mood; P3 pins PHQ9 on floor share only (its
# MEAN is not the lowest, because of the anomalous 21% "nearly every day" --
# see the data-defect print below). Nothing separates PHQ3..PHQ8 from one
# another. Status: PARTIAL.

suppressMessages(library(irw))
TABLE <- "islam_2022_phq9"
XLSX  <- paste0("https://journals.plos.org/plosone/article/file",
                "?type=supplementary&id=10.1371/journal.pone.0279062.s001")
P <- paste0("PHQ", 1:9); G <- paste0("GAD", 1:7)

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
cat(sprintf("live table: %d respondents x %d items\n\n", nrow(w), length(P)))

# --- P1: totals and direction -------------------------------------------------
tf <- tempfile(fileext = ".xlsx")
utils::download.file(XLSX, tf, quiet = TRUE, mode = "wb")
x <- as.data.frame(readxl::read_excel(tf))
x$id <- seq_len(nrow(x))                      # the processing script's row-index id
m <- merge(w[, c("id", P)], x[, c("id", P, G, "Sum_PHQ")], by = "id",
           suffixes = c("", ".src"))
same <- sum(sapply(P, function(p) sum(m[[p]] == m[[paste0(p, ".src")]])))
cat(sprintf("plumbing: live==deposit PHQ cells %d / %d\n", same, 9 * nrow(m)))
tot <- rowSums(m[, P]); gtot <- rowSums(m[, G])
rg <- cor(tot, gtot)
cat(sprintf("P1 live PHQ total: mean %.2f SD %.2f (published 6.29 / 6.47); reversed would be %.2f\n",
            mean(tot), sd(tot), mean(27 - tot)))
cat(sprintf("   live total == deposit Sum_PHQ for %d / %d rows\n", sum(tot == m$Sum_PHQ), nrow(m)))
cat(sprintf("   r(PHQ total, GAD total) = %.3f (published .659)\n\n", rg))
p1 <- abs(mean(tot) - 6.29) < 0.01 && abs(sd(tot) - 6.47) < 0.01 && abs(rg - 0.659) < 0.001

# --- P2: PHQ-2 core pair ------------------------------------------------------
R <- cor(w[, P])
top <- function(i) { r <- R[i, ]; r[i] <- -Inf; names(which.max(r)) }
cat("strongest correlate of each item:\n")
for (i in P) { r <- R[i, ]; r[i] <- -Inf; s <- sort(r, decreasing = TRUE)
  cat(sprintf("  %-5s -> %s (%.2f), next %s (%.2f)\n", i, names(s)[1], s[1], names(s)[2], s[2])) }
p2 <- top("PHQ1") == "PHQ2" && top("PHQ2") == "PHQ1"
cat(sprintf("P2 PHQ1<->PHQ2 mutual strongest: %s\n\n", p2))

# --- P3: marker item ---------------------------------------------------------
pct0 <- sapply(P, function(i) 100 * mean(w[[i]] == 0))
mu   <- sapply(P, function(i) mean(w[[i]]))
cat("per-item mean / %zero:\n")
for (i in P) cat(sprintf("  %-5s %5.3f  %5.1f\n", i, mu[i], pct0[i]))
s0 <- sort(pct0, decreasing = TRUE)
p3 <- names(s0)[1] == "PHQ9"
cat(sprintf("P3 highest %%zero: %s %.1f (next %s %.1f)\n", names(s0)[1], s0[1], names(s0)[2], s0[2]))
cat(sprintf("   (lowest MEAN is %s %.3f, not PHQ9 -- see defect print)\n\n",
            names(which.min(mu)), min(mu)))

# --- informational -----------------------------------------------------------
SOM <- c("PHQ3", "PHQ4", "PHQ5"); COG <- c("PHQ2", "PHQ6", "PHQ7", "PHQ8", "PHQ9")
wi <- function(g) mean(R[g, g][upper.tri(R[g, g])])
cat(sprintf("info: block r within somatic %.3f, within cog/aff %.3f, cross %.3f (does not discriminate)\n",
            wi(SOM), wi(COG), mean(R[SOM, COG])))
cat("defect: PHQ9 response counts 0/1/2/3 =",
    paste(sapply(0:3, function(k) sum(w$PHQ9 == k)), collapse = "/"), "\n\n")

cat("Scope: pins resp direction, the {PHQ1,PHQ2} pair and PHQ9's floor; not order within {1,2} or among 3-8 -> PARTIAL.\n")
ok <- p1 && p2 && p3 && same == 9 * nrow(m)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
