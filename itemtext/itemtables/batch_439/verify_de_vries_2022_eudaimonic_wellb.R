# verify_de_vries_2022_eudaimonic_wellb.R -- Step 5b mapping check (batch_439).
#
# Claim: EWWSinter01..04_1 = Bartels, Peterson & Reina (2019) Appendix items 1-4
# (interpersonal dimension) and EWWSintra01..04_1 = Appendix items 5-8
# (intrapersonal dimension), in printed order. Codes are the S1 .sav column names
# (no rename); the .sav has no labels, so within-block order is inferred from
# the 01..04 suffix (mapping_basis = paper_order).
#
# Route 5 (block structure): every item must correlate more with its own
# dimension's items than with the other dimension's. Route 8 (semantic marker):
# Appendix item 4 "I consider the people I work with to be my friends" is the
# strongest claim in the interpersonal block and should be its least-endorsed
# item by a clear margin.
#
# What this does NOT establish: order WITHIN a dimension beyond the item-4
# marker. EWWSinter01-03 (means 4.07/4.13/4.13) and all four intrapersonal items
# could be permuted among themselves and still pass. Status is PARTIAL.

suppressMessages(library(irw))
TABLE <- "de_vries_2022_eudaimonic_wellb"
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
inter <- sprintf("EWWSinter%02d_1", 1:4); intra <- sprintf("EWWSintra%02d_1", 1:4)
r <- cor(w[, c(inter, intra)], use = "pairwise.complete.obs")

ok_block <- 0
cat(sprintf("%-15s %8s %8s\n", "item", "own_r", "rival_r"))
for (it in c(inter, intra)) {
  own <- if (it %in% inter) setdiff(inter, it) else setdiff(intra, it)
  riv <- if (it %in% inter) intra else inter
  o <- mean(r[it, own]); v <- mean(r[it, riv])
  ok_block <- ok_block + (o > v)
  cat(sprintf("%-15s %8.3f %8.3f\n", it, o, v))
}
cat(sprintf("block structure: %d/8 items closer to own dimension\n\n", ok_block))

m <- tapply(d$resp, d$item, mean)
cat("interpersonal means:\n"); print(round(m[inter], 3))
gap <- min(m[inter[1:3]]) - m[inter[4]]
cat(sprintf("item-4 ('friends') marker: mean %.3f, gap to next-lowest interpersonal item %.3f (require > 0.5)\n",
            m[inter[4]], gap))
cat("Not established: order within dimension beyond the item-4 marker (PARTIAL).\n")
cat(if (ok_block == 8 && gap > 0.5) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
