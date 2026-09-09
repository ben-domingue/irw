# verify_kalichman1995_scs.R
#
# CLAIM: live item codes Q1..Q10 are the SAME columns Q1..Q10 of the
# openpsychometrics SCS deposit (SCS.zip -> data.csv), whose codebook.txt prints
# the wording for each of those codes -- and live resp 1..4 carries the same
# level coding as the raw file (1 = Not at all like me .. 4 = Very much like me).
#
# FALSIFIABLE PREDICTION: for each live item, its response-frequency profile over
# resp = 1..4 must match the raw column of the SAME name more closely than any
# other raw column. If any two items' texts were swapped, or the resp levels were
# permuted/reversed, the nearest-neighbour assignment below would break.
#
# The live table (n = 3,215 per item) and the current public deposit
# (n = 3,376 complete) are different snapshots of the same online SCS form, so an
# exact count match is not expected; the profiles are compared as percentages.

suppressMessages(library(irw))

TABLE <- "kalichman1995_scs"

# Raw percentages per item over resp 1..4, computed from
# https://openpsychometrics.org/_rawdata/SCS.zip -> SCS/data.csv (3,376 rows,
# zeros = not answered excluded). Hard-coded so this script needs no network
# access to the deposit.
RAW <- rbind(
  Q1  = c(28.47, 31.00, 20.92, 19.61),
  Q2  = c(31.31, 30.83, 20.83, 17.02),
  Q3  = c(31.57, 31.16, 19.50, 17.77),
  Q4  = c(44.42, 28.53, 14.97, 12.08),
  Q5  = c(33.39, 28.40, 18.58, 19.63),
  Q6  = c( 6.97, 20.95, 26.85, 45.23),
  Q7  = c(33.12, 29.10, 22.00, 15.77),
  Q8  = c(29.90, 28.73, 22.71, 18.66),
  Q9  = c(28.16, 22.51, 23.05, 26.28),
  Q10 = c(28.28, 20.93, 21.11, 29.68))
colnames(RAW) <- 1:4

d <- irw::irw_fetch(TABLE)
d <- d[!is.na(d$resp), ]
tab <- table(d$item, d$resp)
LIVE <- 100 * prop.table(as.matrix(tab), 1)
LIVE <- LIVE[rownames(RAW), colnames(RAW), drop = FALSE]

cat("live response percentages (resp 1..4)\n"); print(round(LIVE, 2))
cat("\nraw deposit percentages (resp 1..4)\n");  print(round(RAW, 2))

# L1 distance, live rows x raw columns
D <- outer(seq_len(nrow(LIVE)), seq_len(nrow(RAW)),
           Vectorize(function(i, j) sum(abs(LIVE[i, ] - RAW[j, ]))))
dimnames(D) <- list(rownames(LIVE), rownames(RAW))

best   <- rownames(RAW)[apply(D, 1, which.min)]
selfd  <- diag(D)
margin <- apply(D, 1, function(r) sort(r)[2] - sort(r)[1])

cat("\n", sprintf("%-6s %-10s %10s %10s\n", "live", "nearest", "self_L1", "margin"), sep = "")
for (i in seq_len(nrow(D)))
  cat(sprintf("%-6s %-10s %10.2f %10.2f\n",
              rownames(D)[i], best[i], selfd[i], margin[i]))

ok_assign <- all(best == rownames(D))
cat(sprintf("\nworst self-distance: %.2f pct pts | smallest margin to the next-best raw column: %.2f pct pts\n",
            max(selfd), min(margin)))

cat("Establishes: a unique bijection live item -> raw column of the same name,\n",
    "so every item is distinguished from every other, AND the resp 1..4 level\n",
    "coding is unpermuted (a reversal would invert every profile).\n",
    "Does NOT establish: that the codebook's own Q-numbering is correct about the\n",
    "published SCS item order -- it establishes only that the wording the codebook\n",
    "attaches to each code is attached to the right live column.\n", sep = "")

cat(if (ok_assign && max(selfd) < min(margin)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
