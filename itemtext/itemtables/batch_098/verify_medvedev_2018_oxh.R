# verify_medvedev_2018_oxh.R -- Step 5b evidence, re-runnable.
#
# mapping_basis = reconstructed. The study's supplement (peerj-06-4903-s001.xlsx) labels
# nothing -- its headers are bare OXH1..OXH29 -- and Medvedev (2018) PeerJ reproduces no
# item wording. The shipped item_text is the canonical OHQ (Hills & Argyle 2002), so the
# CLAIM being tested is that IRW's oxh_n is OHQ item n.
#
# Three falsifiable predictions follow from that claim:
#   Route 6  the OHQ's canonical reverse-scored items {1,5,6,10,13,14,19,23,24,27,28,29}
#            -- and only those -- must key negatively in the live data.
#   Route 3  reverse-scoring exactly those twelve and averaging all 29 must reproduce the
#            paper's Table 2 (mean 4.18, SD 0.637, alpha 0.903); the no-reversal rival must not.
#   Route 7  the paper singles out "item 2 in OHQ, which correlates with other items at
#            about 0.12" -- so oxh_2 must be the unique weak item.
#
# What this does NOT establish: order WITHIN a keying class. See the closing note.

suppressMessages(library(irw))

TABLE <- "medvedev_2018_oxh"
REV   <- c(1, 5, 6, 10, 13, 14, 19, 23, 24, 27, 28, 29)   # canonical OHQ reverse-scored set
PUB_MEAN <- 4.18; PUB_SD <- 0.637; PUB_ALPHA <- 0.903     # Medvedev 2018 PeerJ, Table 2
PUB_ITEM2_R <- 0.12                                       # "about 0.12", Results

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w$id <- NULL
w <- w[, paste0("oxh_", 1:29)]

ws <- w; ws[, REV] <- 7 - ws[, REV]                       # reverse-score per the claim
tot <- rowSums(ws)
alpha <- function(m) { m <- na.omit(m); k <- ncol(m)
                       (k / (k - 1)) * (1 - sum(apply(m, 2, var)) / var(rowSums(m))) }

## ---- Route 6: keying polarity -------------------------------------------------------
r_raw <- sapply(1:29, function(i) cor(w[, i], tot - ws[, i], use = "pairwise.complete.obs"))
neg   <- which(r_raw < 0)
cat("Route 6 -- corrected item-total r of the RAW (as-administered) item\n")
cat(sprintf("%-8s %7s %s\n", "item", "r", "keys"))
for (i in 1:29)
    cat(sprintf("oxh_%-4d %7.3f %s\n", i, r_raw[i],
                if (r_raw[i] < 0) "reverse" else "forward"))
cat(sprintf("\n  negative-keying items observed : %s\n", paste(neg, collapse = ",")))
cat(sprintf("  canonical OHQ reverse set      : %s\n", paste(REV, collapse = ",")))
ok6 <- identical(as.integer(neg), as.integer(REV))
cat(sprintf("  match: %s (%d/29 items in the correct polarity class)\n\n",
            ok6, sum((1:29 %in% REV) == (r_raw < 0))))

## ---- Route 3: published scale mean / SD / alpha --------------------------------------
sc <- rowMeans(ws); rawm <- rowMeans(w)
cat("Route 3 -- OHQ scale score against Medvedev (2018) Table 2\n")
cat(sprintf("  %-28s %8s %8s %8s\n", "", "mean", "SD", "alpha"))
cat(sprintf("  %-28s %8.2f %8.3f %8.3f\n", "published (n=180)", PUB_MEAN, PUB_SD, PUB_ALPHA))
cat(sprintf("  %-28s %8.3f %8.3f %8.3f\n", "observed, 12 items reversed",
            mean(sc, na.rm = TRUE), sd(sc, na.rm = TRUE), alpha(ws)))
cat(sprintf("  %-28s %8.3f %8.3f %8.3f  <- rival reading\n", "observed, NO reversal",
            mean(rawm, na.rm = TRUE), sd(rawm, na.rm = TRUE), alpha(w)))
ok3 <- abs(mean(sc, na.rm = TRUE) - PUB_MEAN) < 0.05 &&
       abs(sd(sc, na.rm = TRUE)  - PUB_SD)   < 0.05 &&
       abs(alpha(ws) - PUB_ALPHA)            < 0.02
cat(sprintf("  reproduces published values within tolerance: %s\n\n", ok3))

## ---- Route 7: the marker item --------------------------------------------------------
r_sc <- sapply(1:29, function(i) cor(ws[, i], tot - ws[, i], use = "pairwise.complete.obs"))
o <- order(r_sc)
cat("Route 7 -- corrected item-total r on scored items, four weakest\n")
for (i in o[1:4]) cat(sprintf("  oxh_%-3d %6.3f\n", i, r_sc[i]))
cat(sprintf("  paper: 'item 2 in OHQ ... correlates with other items at about %.2f'\n", PUB_ITEM2_R))
ok7 <- (o[1] == 2) && abs(r_sc[2] - PUB_ITEM2_R) < 0.05
cat(sprintf("  oxh_2 is the unique minimum at %.3f (next: oxh_%d at %.3f): %s\n\n",
            r_sc[2], o[2], r_sc[o[2]], ok7))

cat("NOT ESTABLISHED: order within a keying class. A permutation confined to the 17\n",
    "forward-keyed items (or to the 12 reverse-keyed ones), leaving oxh_2 in place, would\n",
    "pass all three routes unchanged. Step 5b status is therefore PARTIAL, not VERIFIED.\n", sep = "")

cat(if (ok6 && ok3 && ok7) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
