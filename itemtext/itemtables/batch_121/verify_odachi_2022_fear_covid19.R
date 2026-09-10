# verify_odachi_2022_fear_covid19.R -- Step 5b mapping check.
#
# CLAIM UNDER TEST: FCV19S_1..FCV19S_7 in the IRW table are items 1..7 of the
# Fear of COVID-19 Scale, in the numbering published by Ahorsu et al. (2020,
# IJMHA, CC BY, Appendix) and reproduced for the Japanese version by Wakashima
# et al. (2020, PLOS ONE 15(11):e0241958, S1 File, items numbered 1.-7.).
#
# The mapping is NOT taken from data labels: the deposit (S1 minidataset.xlsx)
# carries only the bare column names FCV19S_1..FCV19S_7 with no variable
# labels, so the tie is number-to-number and needs checking against the data.
#
# TWO INDEPENDENT, FALSIFIABLE PREDICTIONS, both fixed before looking:
#
# (A) BLOCK STRUCTURE. Wakashima et al. (2021, PLOS ONE 16(2):e0246840,
#     Table 2) report a two-factor solution for the Japanese FCV-19S in which
#     items 7, 6, 3 and 5 load on the symptomatic factor (.86/.81/.69/.80) and
#     items 2, 1, 4 on the emotional-fear factor (.66/.64/.51). Item 5 is the
#     cross-loading bridge item (1-factor loading .58, the middle of the set),
#     so it is EXCLUDED from this test in advance. Prediction: among the ten
#     ways to split items {1,2,3,4,6,7} into two triples, the published split
#     {1,2,4} | {3,6,7} maximises the sum of within-triple correlations.
#     A permutation of item_text across these six codes would generally destroy
#     that (only 1 of 10 partitions can win).
#
# (B) ENDORSEMENT ORDERING. FCV-19S items 3, 6 and 7 describe physiological /
#     somatic symptoms (clammy hands, insomnia, palpitations); items 1, 2 and 4
#     describe cognitive-affective appraisal (afraid, uncomfortable, fear of
#     dying); item 5 is an external-cue item. In any non-clinical sample the
#     somatic items are the least endorsed. Prediction: mean(3), mean(6),
#     mean(7) are the three lowest of the seven, and mean(1), mean(2), mean(4)
#     the three highest.
#
# WHAT THIS DOES NOT ESTABLISH: items 1 and 2 are not separated from each other
# by anything here (their means and corrected item-total correlations coincide,
# and the two Wakashima papers disagree on their loading order), and item 5 is
# assigned by content and by its bridging correlation profile rather than tested
# by (A). Hence the recorded status is PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "odachi_2022_fear_covid19"
ITEMS <- paste0("FCV19S_", 1:7)

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
colnames(w) <- sub("resp.", "", colnames(w), fixed = TRUE)
m <- as.matrix(w[, ITEMS])
cat(sprintf("n respondents = %d\n\n", nrow(m)))

R <- cor(m)

## ---- (A) block structure ------------------------------------------------
six  <- c("FCV19S_1","FCV19S_2","FCV19S_3","FCV19S_4","FCV19S_6","FCV19S_7")
combs <- combn(six, 3, simplify = FALSE)
seen <- list(); rows <- list()
for (a in combs) {
    b <- setdiff(six, a)
    key <- paste(sort(c(paste(sort(a), collapse=","), paste(sort(b), collapse=","))), collapse="|")
    if (key %in% seen) next
    seen <- c(seen, key)
    s <- sum(R[a, a][upper.tri(diag(3))]) + sum(R[b, b][upper.tri(diag(3))])
    rows[[length(rows)+1]] <- data.frame(
        partition = sprintf("{%s} | {%s}",
            paste(sub("FCV19S_", "", a), collapse=","),
            paste(sub("FCV19S_", "", b), collapse=",")),
        within_sum = s, stringsAsFactors = FALSE)
}
tab <- do.call(rbind, rows)
tab <- tab[order(-tab$within_sum), ]
cat("(A) sum of within-triple correlations, all 10 partitions of {1,2,3,4,6,7}:\n")
for (i in seq_len(nrow(tab)))
    cat(sprintf("    %-22s %6.3f%s\n", tab$partition[i], tab$within_sum[i],
                if (i == 1) "   <- best" else ""))
best <- tab$partition[1]
predA <- best %in% c("{1,2,4} | {3,6,7}", "{3,6,7} | {1,2,4}")
cat(sprintf("\n    published split {1,2,4} | {3,6,7} is the best partition: %s",
            if (predA) "YES" else "NO"))
cat(sprintf("  (margin over runner-up: %.3f)\n\n", tab$within_sum[1] - tab$within_sum[2]))

## ---- (B) endorsement ordering -------------------------------------------
mu <- colMeans(m)
cat("(B) per-item means (live data):\n")
for (i in ITEMS) cat(sprintf("    %-10s %5.2f\n", i, mu[i]))
lowest3  <- names(sort(mu))[1:3]
highest3 <- names(sort(mu, decreasing = TRUE))[1:3]
cat(sprintf("\n    three lowest  = %s   (predicted: somatic items 3, 6, 7)\n",
            paste(sub("FCV19S_", "", sort(lowest3)), collapse = ", ")))
cat(sprintf("    three highest = %s   (predicted: appraisal items 1, 2, 4)\n",
            paste(sub("FCV19S_", "", sort(highest3)), collapse = ", ")))
predB <- setequal(lowest3,  paste0("FCV19S_", c(3,6,7))) &&
         setequal(highest3, paste0("FCV19S_", c(1,2,4)))
cat(sprintf("    ordering as predicted: %s\n\n", if (predB) "YES" else "NO"))

## ---- what is not established --------------------------------------------
ct <- sapply(ITEMS, function(i) cor(m[, i], rowSums(m) - m[, i]))
cat("Not established by this script:\n")
cat(sprintf("  items 1 and 2 are indistinguishable here -- means %.2f vs %.2f, corrected\n",
            mu["FCV19S_1"], mu["FCV19S_2"]))
cat(sprintf("  item-total r %.2f vs %.2f; Wakashima 2020 loads 1 at .590 / 2 at .744 while\n",
            ct["FCV19S_1"], ct["FCV19S_2"]))
cat("  Wakashima 2021 loads 1 at .47 / 2 at .46, i.e. the sources disagree on their order.\n")
cat(sprintf("  item 5 is excluded from (A) as the cross-loading item: mean r with {1,2,4} = %.2f,\n",
            mean(R["FCV19S_5", c("FCV19S_1","FCV19S_2","FCV19S_4")])))
cat(sprintf("  with {3,6,7} = %.2f -- it bridges the two blocks and cannot be placed by (A).\n\n",
            mean(R["FCV19S_5", c("FCV19S_3","FCV19S_6","FCV19S_7")])))

cat(if (predA && predB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
