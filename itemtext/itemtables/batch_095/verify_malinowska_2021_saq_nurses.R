# Verifies the item_text <-> item mapping for malinowska_2021_saq_nurses.
#
# The claim under test: bezp_N carries SAQ-SF PL questionnaire item N (N = 1..36),
# the five kier_Na columns are the WARD-MANAGER rating of double-rated items 24-28
# while bezp_24..28 are the HOSPITAL-DIRECTOR rating of the same five questions,
# and resp runs 1 = "Zdecydowanie nie zgadzam sie" .. 5 = "Zdecydowanie sie zgadzam"
# with 6 = "Nie dotyczy" (not applicable).
#
# Four falsifiable predictions, none of which is a count check:
#  A  The SAQ-SF's reverse-worded items are exactly {2, 11, 36}. With the shipped
#     anchor direction those three, and only those three, must correlate NEGATIVELY
#     with the mean of the positively-worded climate items.
#  B  resp = 6 is the "not applicable" box, not a sixth agreement level. Item 35 asks
#     about collaboration with PHARMACISTS -- the one collaborator most ward nurses
#     never work with -- so it must carry by far the largest share of resp = 6.
#  C  Ward management is rated above hospital management on every SAQ study,
#     including this group's own paediatric replication (PMC12504464, item 24
#     Unit 66.03 vs Hosp 62.93). So mean(kier_Na) > mean(bezp_N) for all N in 24:28.
#  D  The five discriminating SAQ-SF blocks (JS 15-19, SR 20-23, WC 29-32,
#     hospital-mgt 24-28, unit-mgt kier) must each be internally most coherent.
#
# What this does NOT establish: order WITHIN a subscale block. Teamwork-climate and
# safety-climate items are near-collinear in this sample (the adaptation paper found
# the same, PLOS ONE 10.1371/journal.pone.0246340), so D is deliberately not run over
# them. Status is therefore PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "malinowska_2021_saq_nurses"

d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.numeric(d$resp)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
w <- w[, setdiff(colnames(w), "id"), drop = FALSE]
w[w == 6] <- NA                                   # drop "Nie dotyczy" before scoring

ok <- TRUE

## A -- keying polarity
pos  <- paste0("bezp_", c(1, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13))
tot  <- rowMeans(w[, pos], na.rm = TRUE)
its  <- paste0("bezp_", 1:36)
r    <- sapply(its, function(i) cor(w[[i]], tot, use = "pairwise.complete.obs"))
cat("A. item-total r with positively-worded climate mean\n")
for (i in its) cat(sprintf("   %-8s %+.3f%s\n", i, r[[i]],
                           if (r[[i]] < 0) "   <- negative" else ""))
neg <- sort(names(r)[r < 0])
cat("   negative set:", paste(neg, collapse = ", "),
    "| SAQ-SF reverse-worded items: bezp_11, bezp_2, bezp_36\n")
okA <- identical(neg, sort(c("bezp_2", "bezp_11", "bezp_36"))); ok <- ok && okA
cat("   ->", if (okA) "PASS" else "FAIL", "\n\n")

## B -- resp = 6 is the not-applicable box
d6  <- tapply(d$resp == 6, d$item, mean) * 100
d6  <- sort(d6, decreasing = TRUE)
cat("B. share of resp = 6, top 5 and bottom 3 (%)\n")
for (i in c(names(d6)[1:5], names(d6)[(length(d6) - 2):length(d6)]))
    cat(sprintf("   %-8s %5.2f\n", i, d6[[i]]))
okB <- names(d6)[1] == "bezp_35" && d6[[1]] > 3 * d6[[2]]; ok <- ok && okB
cat(sprintf("   bezp_35 = %.2f%% vs next highest %s = %.2f%% -> %s\n\n",
            d6[[1]], names(d6)[2], d6[[2]], if (okB) "PASS" else "FAIL"))

## C -- ward manager rated above hospital director on all five paired items
cat("C. paired management items, mean (6 excluded)\n")
okC <- TRUE
for (n in 24:28) {
    a <- mean(w[[paste0("kier_", n, "a")]], na.rm = TRUE)
    b <- mean(w[[paste0("bezp_", n)]],      na.rm = TRUE)
    cat(sprintf("   item %d  kier_%da (ward mgr) %.3f   bezp_%d (hosp dir) %.3f   diff %+.3f\n",
                n, n, a, n, b, a - b))
    okC <- okC && a > b
}
ok <- ok && okC
cat("   ->", if (okC) "PASS (ward > hospital on all 5)" else "FAIL", "\n\n")

## D -- block coherence on the five discriminating subscales
blocks <- list(JS = paste0("bezp_", 15:19), SR = paste0("bezp_", 20:23),
               WC = paste0("bezp_", 29:32), PMhosp = paste0("bezp_", 24:28),
               PMunit = paste0("kier_", 24:28, "a"))
cols <- unlist(blocks, use.names = FALSE)
cm   <- abs(cor(w[, cols], use = "pairwise.complete.obs")); diag(cm) <- NA
hits <- 0
cat("D. mean |r| with each block (own block must win)\n")
for (b in names(blocks)) for (i in blocks[[b]]) {
    m <- sapply(names(blocks), function(g) mean(cm[i, setdiff(blocks[[g]], i)], na.rm = TRUE))
    best <- names(which.max(m)); hits <- hits + (best == b)
    cat(sprintf("   %-9s own=%-7s %.3f   best=%-7s %.3f  %s\n",
                i, b, m[[b]], best, max(m), if (best == b) "OK" else "MISS"))
}
okD <- hits == length(cols); ok <- ok && okD
cat(sprintf("   %d/%d -> %s\n\n", hits, length(cols), if (okD) "PASS" else "FAIL"))

cat("Not established by any route above: the order of items WITHIN the teamwork-climate\n",
    "and safety-climate blocks (bezp_1..13), which are near-collinear here.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
