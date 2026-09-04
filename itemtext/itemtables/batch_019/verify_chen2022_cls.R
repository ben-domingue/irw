# verify_chen2022_cls.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: the item codes A1..A24 in chen2022_cls are the Children's
# Loneliness Scale's own 24-item numbering (Asher, Hymel & Renshaw 1984), so
# A<k> carries CLS item k's wording; and the six reverse-worded CLS items
# (1, 4, 8, 10, 16, 22) are stored ALREADY reverse-scored, which is why the
# shipped option labels for those six run in descending order.
#
# Three falsifiable predictions, all computed from live data:
#   P1 filler-gap signature -- the 8 numbers absent from A1..A24 must be exactly
#      the CLS's 8 published filler positions {2,5,7,11,13,15,19,23}.
#   P2 published scale statistic -- Chen & Hu (2022) Table 2 reports Loneliness
#      M = 2.04, SD = 0.54 (mean of the 16 items, N = 303). That reproduces from
#      the values AS STORED only if the reverse-worded items are already
#      reversed; re-reversing them gives 2.36 / 0.36.
#   P3 wording-method blocks -- CLS has a well-documented reverse-wording method
#      factor (Maes et al. 2015, Assessment, Model 3). Each item must correlate
#      more strongly with its OWN wording block than with the other block. The
#      block membership is read out of the SHIPPED CSV (which anchor sits at
#      resp = 1), so a file that mislabelled an item's polarity fails here.
#
# WHAT THIS DOES NOT ESTABLISH: order WITHIN a wording block. Nothing here
# separates A9 "I feel alone at school" from A21 "I'm lonely at school"; both
# are non-reverse-worded and behave alike. Hence status PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "chen2022_cls"
ITEMS_CSV <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                       "chen2022_cls__items.csv")
if (!file.exists(ITEMS_CSV)) ITEMS_CSV <- "chen2022_cls__items.csv"

PUB_M  <- 2.04; PUB_SD <- 0.54          # Chen & Hu 2022, Front. Psychol. 13:1014794, Table 2
FILLERS <- c(2, 5, 7, 11, 13, 15, 19, 23)

it <- read.csv(ITEMS_CSV, stringsAsFactors = FALSE)
# "reverse-worded, stored reversed" is declared in the file by the anchor at resp = 1
r1 <- it[it$resp == 1, c("item", "option_text")]
rev_shipped <- sort(r1$item[r1$option_text == "Always true"])
fwd_shipped <- sort(r1$item[r1$option_text == "Not true at all"])
cat("shipped reverse-worded block (resp 1 = 'Always true'):", paste(rev_shipped, collapse = ", "), "\n")
cat("shipped non-reverse block    (resp 1 = 'Not true at all'):", paste(fwd_shipped, collapse = ", "), "\n\n")

d <- irw::irw_fetch(TABLE)
items <- sort(unique(d$item))
nums  <- sort(as.integer(sub("^A", "", items)))

## P1 -------------------------------------------------------------------
gaps <- setdiff(1:24, nums)
cat("P1 numbers absent from A1..A24 :", paste(gaps, collapse = ", "), "\n")
cat("   published CLS filler items  :", paste(FILLERS, collapse = ", "), "\n")
p1 <- identical(as.integer(gaps), as.integer(FILLERS))
cat("   match:", p1, "\n\n")

## P2 -------------------------------------------------------------------
dd <- as.data.frame(d[, c("id", "item", "resp")])
X <- as.data.frame(matrix(NA_real_, nrow = length(unique(dd$id)), ncol = length(items),
                          dimnames = list(sort(unique(dd$id)), items)))
X[cbind(match(dd$id, rownames(X)), match(dd$item, items))] <- as.numeric(dd$resp)
X <- X[complete.cases(X), , drop = FALSE]
scale_mean <- rowMeans(X)
Y <- X; Y[rev_shipped] <- 6 - Y[rev_shipped]     # counterfactual: re-reverse them
cat(sprintf("P2 published (paper Table 2)      M = %.2f  SD = %.2f  (N = 303)\n", PUB_M, PUB_SD))
cat(sprintf("   as stored, no re-reversal      M = %.2f  SD = %.2f  (N = %d)\n",
            mean(scale_mean), sd(scale_mean), nrow(X)))
cat(sprintf("   counterfactual (re-reversed)   M = %.2f  SD = %.2f\n",
            mean(rowMeans(Y)), sd(rowMeans(Y))))
p2 <- abs(mean(scale_mean) - PUB_M) <= 0.02 && abs(sd(scale_mean) - PUB_SD) <= 0.02
cat("   as-stored reproduces the paper:", p2, "\n\n")

## P3 -------------------------------------------------------------------
cc <- cor(X)
cat("P3 per-item mean r with each wording block\n")
cat(sprintf("%-5s %-12s %8s %8s %s\n", "item", "block", "r(rev)", "r(fwd)", "ok"))
ok <- logical(0)
for (i in items) {
    blk <- if (i %in% rev_shipped) "reverse" else "non-reverse"
    rr <- mean(cc[i, setdiff(rev_shipped, i)])
    rf <- mean(cc[i, setdiff(fwd_shipped, i)])
    good <- if (blk == "reverse") rr > rf else rf > rr
    ok <- c(ok, good)
    cat(sprintf("%-5s %-12s %8.3f %8.3f %s\n", i, blk, rr, rf, if (good) "OK" else "MISMATCH"))
}
cat(sprintf("   items classified into their shipped wording block: %d/%d\n\n", sum(ok), length(ok)))
p3 <- all(ok)

cat("Note: P1-P3 pin the numbering scheme, the storage direction, and each item's\n",
    "wording polarity. They do NOT distinguish items within a polarity block, so an\n",
    "item_text swap between e.g. A9 and A21 would survive this check.\n", sep = "")

cat(if (p1 && p2 && p3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
