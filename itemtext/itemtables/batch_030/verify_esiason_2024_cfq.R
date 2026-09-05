# verify_esiason_2024_cfq.R -- Step 5b mapping check, route 6 (keying polarity /
# reverse-item block structure).
#
# CLAIM UNDER TEST: the IRW codes cfq1..cfq13 carry the OFFICIAL CFQ13 item
# numbering, so item_text for cfqN is CFQ13 item N (Gillanders, Bolderston &
# Bond, 2010; wording from Gillanders et al. 2014, Behav Ther 45:83-101).
#
# FALSIFIABLE PREDICTION: the CFQ13's own scoring instructions (ACBS,
# "Cognitive Fusion Questionnaire Scoring Instructions") say the scale is scored
#   sum items 1,2,4,5,7,8,10,11,13 ; reverse score and sum items 3,6,9,12
# i.e. EXACTLY items 3, 6, 9 and 12 are the reverse-worded defusion items. If the
# REDCap form's cfqN numbering did not follow the published CFQ13 numbering, the
# four defusion items would not land on those four positions. Under H0 (a random
# permutation of the 13 texts onto the 13 codes) the chance of the defusion set
# landing exactly on {3,6,9,12} is 1/choose(13,4) = 1/715.
#
# The signal is measured two ways, both from the live data alone:
#   (a) mean correlation of each item with the nine fusion items;
#   (b) item means -- defusion statements are widely endorsed, fusion statements
#       are not, so the two classes separate on level as well as on covariance.
#
# WHAT THIS DOES NOT ESTABLISH: it pins the four-item defusion CLASS and hence the
# instrument's numbering frame. It does NOT distinguish the nine fusion items from
# one another, nor the four defusion items from one another -- a swap of, say,
# cfq1 and cfq5's text would be invisible here. Status is therefore PARTIAL, not
# VERIFIED.

suppressMessages(library(irw))

TABLE  <- "esiason_2024_cfq"
ITEMS  <- paste0("cfq", 1:13)
REV    <- c(3, 6, 9, 12)          # published CFQ13 reverse-scored items
FUS    <- setdiff(1:13, REV)

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, ITEMS]

R <- cor(w, use = "pairwise.complete.obs")

cat(sprintf("%-7s %-5s %11s %10s\n", "item", "class", "mean r w/ 9", "item mean"))
cat(sprintf("%-7s %-5s %11s %10s\n", "", "", "fusion items", ""))
mr <- numeric(13); mm <- numeric(13)
for (i in 1:13) {
    others <- setdiff(FUS, i)
    mr[i] <- mean(R[i, others])
    mm[i] <- mean(w[[i]], na.rm = TRUE)
    cat(sprintf("%-7s %-5s %11.3f %10.2f\n", ITEMS[i],
                if (i %in% REV) "REV" else "fus", mr[i], mm[i]))
}

gap_r <- min(mr[FUS]) - max(mr[REV])
gap_m <- min(mm[REV]) - max(mm[FUS])
cat(sprintf("\nmean r with fusion block:  fusion items %.3f-%.3f | defusion items %.3f-%.3f  (gap %.3f)\n",
            min(mr[FUS]), max(mr[FUS]), min(mr[REV]), max(mr[REV]), gap_r))
cat(sprintf("item means:                fusion items %.2f-%.2f | defusion items %.2f-%.2f  (gap %.2f)\n",
            min(mm[FUS]), max(mm[FUS]), min(mm[REV]), max(mm[REV]), gap_m))

# The recovered reverse set: the four items with the lowest correlation with the
# fusion block. It must equal the published {3,6,9,12} exactly.
recovered <- sort(order(mr)[1:4])
cat(sprintf("\npublished CFQ13 reverse items: %s\n", paste(REV, collapse = ", ")))
cat(sprintf("reverse items recovered from the data: %s\n", paste(recovered, collapse = ", ")))
cat(sprintf("chance of an exact match under a random permutation: 1/%d\n", choose(13, 4)))

cat("\nNote: this pins the defusion class and therefore the CFQ13 numbering frame.\n",
    "It does NOT order the 9 fusion items among themselves, nor the 4 defusion\n",
    "items among themselves. Recorded as PARTIAL in verification_esiason_2024_cfq.csv.\n", sep = "")

ok <- identical(as.integer(recovered), as.integer(REV)) && gap_r > 0.2 && gap_m > 0.5
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
