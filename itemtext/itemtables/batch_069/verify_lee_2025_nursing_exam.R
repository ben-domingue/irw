# verify_lee_2025_nursing_exam.R
#
# Claim under test: live item_01..item_50 are the exam's items 1..50, in that order.
# The IRW processing script renames raw columns "1".."50" to item_01..item_50
# (data/lee_2025_nursing_exam.py: f"item_{int(c):02d}"), so the code IS the source
# column name up to zero-padding, and the deposit's Supplement 1 numbers the printed
# exam items 1..50.
#
# Falsifiable prediction: the deposit's Supplement 5 publishes a Rasch difficulty
# parameter per item.id 1..50, fitted to these same 117 examinees. Under the Rasch
# model, b is a strictly decreasing function of an item's number correct, so
#   (a) rank(b) must be exactly the reverse of rank(number correct), and
#   (b) items sharing a b value must share a raw score, and vice versa (bijection).
# Any permutation of the item order breaks (a) immediately.

suppressMessages(library(irw))

TABLE <- "lee_2025_nursing_exam"

# Supplement 5, "Estimated item difficulty parameters of 50 items"
# (Harvard Dataverse doi:10.7910/DVN/PWV6H2, file 13126445), column difficulty.par.2,
# rows item.id 1..50, in item.id order.
PUBLISHED_B <- c(
 -0.810270837, -1.137259122,  1.963873784,  0.053658619, -0.885665403,
 -2.445480902, -1.443122849, -3.874591113, -0.143710648, -0.810270837,
 -0.738277193, -0.043025264, -0.738277193, -0.092827720,  0.452658484,
 -0.303797105, -0.539193184,  1.963873787, -1.231847124, -0.417873708,
 -0.539193184, -1.231847124, -1.443122849,  0.535546076,  1.317404272,
 -1.048555265,  0.005778638, -1.562900141, -0.885665403,  1.086571942,
 -1.333357021, -0.810270837, -0.143710672,  1.753119809, -1.562900141,
 -3.167174093,  0.192409216, -2.445480903, -0.885665393, -1.048555265,
 -0.092827701, -1.137259122, -0.603035974,  0.535546077, -0.738277199,
 -2.208049891, -1.048555265, -0.738277193, -0.539193184,  0.410583357)

d <- irw::irw_fetch(TABLE)
items <- sprintf("item_%02d", 1:50)
ncorrect <- as.integer(tapply(d$resp, d$item, sum)[items])
n_ex <- length(unique(d$id))

cat(sprintf("examinees: %d   items: %d\n\n", n_ex, length(items)))
cat(sprintf("%-8s %14s %10s\n", "item", "published b", "n correct"))
for (i in 1:50) cat(sprintf("%-8s %14.6f %10d\n", items[i], PUBLISHED_B[i], ncorrect[i]))

b <- round(PUBLISHED_B, 5)   # JML estimates for equally-scored items differ in the 8th decimal
rho <- cor(b, ncorrect, method = "spearman")
tie_ok <- all(ave(ncorrect, b, FUN = function(x) length(unique(x))) == 1) &&
          all(ave(b, ncorrect, FUN = function(x) length(unique(x))) == 1)

cat(sprintf("\nSpearman(published b rounded to 5dp, n correct) = %.4f   (prediction: -1)\n", rho))
cat(sprintf("distinct b values: %d   distinct raw scores: %d   tie groups agree: %s\n",
            length(unique(b)), length(unique(ncorrect)), tie_ok))

cat("Scope: 20 of the 50 items share a raw score with at least one other item, so this\n",
    "route ranks them into 30 groups; separation inside a group comes from the label\n",
    "match -- raw data columns are named \"1\"..\"50\" and Supplement 1 prints items 1..50\n",
    "under those same numbers, corroborated by Dataset 2's per-item-number topic list\n",
    "(item 33 semen analysis / infertility, item 44 syphilis, item 50 cervical cryotherapy).\n",
    sep = "")

cat(if (isTRUE(rho == -1) && tie_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
