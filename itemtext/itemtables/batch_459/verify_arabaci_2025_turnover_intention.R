# verify_arabaci_2025_turnover_intention.R -- Step 5b, batch_459.
#
# Claim: TurnoverIntention1..3 (the deposit's "Turnover Intention1..3" columns,
# space stripped by data/arabaci_2025_task_diversity.py) correspond, in order, to
# the three items listed under "Turnover Intention" in the deposit's
# "Supplementary Data 2 - Appendix A.docx". mapping_basis = paper_order: the
# appendix lists the items unnumbered, so the tie is presentation order.
#
# The paper (RBGN 27(3), doi:10.7819/rbgn.v27i03.4318) publishes no per-item
# statistics for this scale (Table 2 gives only a loading RANGE, .877-.936), so
# there is no route that separates every item. Two checks, both falsifiable:
#
#  (A) Ordering convention of the deposit. The paper names one item by POSITION:
#      "Item 4 of the burnout scale, 'I have sufficient energy for my family and
#      friends in my leisure time,' was excluded ... since its factor loading was
#      lower than 0.50." Appendix A lists that statement 4th under Burnout. If the
#      deposit's column numbers follow Appendix A order, Burnout4 must be the
#      weakest item of the sibling table arabaci_2025_burnout (lowest corrected
#      item-rest correlation). This tests the premise paper_order rests on.
#  (B) Content structure within this table. Item 1 ("I often think about leaving")
#      is the cognition item; items 2 ("actively looking for jobs") and 3
#      ("probably quit ... soon") are the behavioural-intention pair. Prediction:
#      r(2,3) exceeds both r(1,2) and r(1,3), i.e. item 1 is the odd one out.
#
# NOT established: which of TurnoverIntention2 / TurnoverIntention3 is "looking
# for jobs" vs "quit soon". Nothing published separates them; that pair rests on
# presentation order (supported by check A) alone. Status is therefore PARTIAL.

suppressMessages(library(irw))

wide <- function(tab) {
    d <- as.data.frame(irw::irw_fetch(tab)[, c("id", "item", "resp")])
    w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
    m <- as.matrix(w[, -1]); colnames(m) <- sub("^resp\\.", "", colnames(m))
    m[, order(colnames(m))]
}
item_rest <- function(m) sapply(colnames(m), function(j)
    cor(m[, j], rowSums(m[, colnames(m) != j, drop = FALSE]), use = "complete.obs"))

# (A)
b <- wide("arabaci_2025_burnout")
ir <- item_rest(b)
cat("(A) arabaci_2025_burnout corrected item-rest correlations:\n")
print(round(ir, 3))
okA <- names(which.min(ir)) == "Burnout4"
cat(sprintf("    weakest item: %s (%.3f); next weakest %.3f -> %s\n\n",
            names(which.min(ir)), min(ir), sort(ir)[2],
            if (okA) "matches paper's 'Item 4' exclusion" else "DOES NOT match"))

# (B)
t <- wide("arabaci_2025_turnover_intention")
r <- cor(t, use = "complete.obs")
cat("(B) arabaci_2025_turnover_intention inter-item correlations:\n")
print(round(r, 3))
r12 <- r["TurnoverIntention1", "TurnoverIntention2"]
r13 <- r["TurnoverIntention1", "TurnoverIntention3"]
r23 <- r["TurnoverIntention2", "TurnoverIntention3"]
okB <- r23 > r12 && r23 > r13
cat(sprintf("    r(2,3)=%.3f vs r(1,2)=%.3f, r(1,3)=%.3f -> item 1 %s\n\n",
            r23, r12, r13, if (okB) "is the odd one out, as predicted" else "is NOT the odd one out"))

cat("Not established: the order of TurnoverIntention2 vs TurnoverIntention3 within\n",
    "the behavioural pair (no published per-item statistic separates them).\n", sep = "")
cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
