# verify_wang_2016_study3_power.R -- Step 5b, batch_214.
#
# Claim under test: p1..p8 are the eight Generalized Sense of Power Scale items in
# the scale's own canonical numbering (forward 1,3,5,8 / reverse 2,4,6,7), stored
# ALREADY REVERSE-SCORED, so option_text is deliberately flipped on p2/p4/p6/p7.
#
# This checks the MAPPING, not the plumbing:
#   ROUTE 3  published scale total + alpha, and the un-reverse counterfactual
#            -- fixes the stored direction and hence the flipped anchors.
#   ROUTE 5/6 wording-method-factor partition -- fixes WHICH four items are the
#            reverse-worded ones, i.e. the polarity class of every item.
#   ROUTE 7  marker item: "I think I have a great deal of power" must be the
#            least endorsed of the four forward items.
# It does NOT establish the order of items within either polarity class.

suppressMessages(library(irw))

TABLE <- "wang_2016_study3_power"
ITEMS <- paste0("p", 1:8)
REV   <- c("p2", "p4", "p6", "p7")          # canonical reverse-worded set

# Published: Wang YN (2016) PLOS ONE 11(1):e0146050, Table 5 (Study 3, n = 210)
# and the Study 3 Measures section.
PUB_M <- 29.37; PUB_SD <- 5.37; PUB_ALPHA <- 0.88

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- as.data.frame(lapply(ITEMS, function(it) {
  v <- d$resp[d$item == it]; names(v) <- d$id[d$item == it]
  v[as.character(sort(unique(d$id)))]
}))
colnames(w) <- ITEMS
w <- w[complete.cases(w), ]
cat(sprintf("live matrix: %d respondents x %d items\n", nrow(w), ncol(w)))

alpha <- function(m) { k <- ncol(m); k/(k-1) * (1 - sum(apply(m, 2, var))/var(rowSums(m))) }

tot <- rowSums(w)
cat(sprintf("\nROUTE 3 -- published totals (Table 5) and alpha (Measures)\n"))
cat(sprintf("  scale total  observed M %.2f SD %.2f   published M %.2f SD %.2f\n",
            mean(tot), sd(tot), PUB_M, PUB_SD))
cat(sprintf("  Cronbach's alpha observed %.3f          published %.2f\n",
            alpha(w), PUB_ALPHA))
w2 <- w; w2[, REV] <- 6 - w2[, REV]          # counterfactual: un-reverse
cat(sprintf("  counterfactual, un-reversing %s: total M %.2f, alpha %.3f\n",
            paste(REV, collapse = ","), mean(rowSums(w2)), alpha(w2)))
ok3 <- abs(mean(tot) - PUB_M) < 0.05 && abs(sd(tot) - PUB_SD) < 0.05 &&
       abs(alpha(w) - PUB_ALPHA) < 0.02 && alpha(w2) < alpha(w) - 0.3

cat("\nROUTE 5/6 -- wording method factor as a polarity-partition test\n")
R <- cor(w)
contrast <- function(g) {
  h <- setdiff(ITEMS, g)
  win <- mean(c(R[g, g][upper.tri(R[g, g])], R[h, h][upper.tri(R[h, h])]))
  win - mean(R[g, h])
}
combs <- combn(ITEMS, 4, simplify = FALSE)
combs <- combs[sapply(combs, function(g) "p1" %in% g)]   # 35 distinct 4/4 splits
sc <- sapply(combs, contrast)
ord <- order(sc, decreasing = TRUE)
canon <- which(sapply(combs, function(g) setequal(g, c("p1","p3","p5","p8"))))
rk <- which(ord == canon)
cat(sprintf("  canonical split {p1,p3,p5,p8} | {p2,p4,p6,p7}: contrast %+.4f, rank %d of %d\n",
            sc[canon], rk, length(combs)))
for (i in 1:3) cat(sprintf("    #%d %-28s %+.4f\n", i,
      paste(combs[[ord[i]]], collapse = ","), sc[ord[i]]))
cat(sprintf("  within-block r: {p1,p3,p5,p8} %.2f-%.2f ; {p2,p4,p6,p7} %.2f-%.2f ; between %.2f-%.2f\n",
    min(R[c("p1","p3","p5","p8"),c("p1","p3","p5","p8")][upper.tri(diag(4))]),
    max(R[c("p1","p3","p5","p8"),c("p1","p3","p5","p8")][upper.tri(diag(4))]),
    min(R[REV,REV][upper.tri(diag(4))]), max(R[REV,REV][upper.tri(diag(4))]),
    min(R[c("p1","p3","p5","p8"), REV]), max(R[c("p1","p3","p5","p8"), REV])))
ok56 <- rk == 1

cat("\nROUTE 7 -- marker item p5 ('I think I have a great deal of power')\n")
mm <- colMeans(w)
cat(sprintf("  item means: %s\n", paste(sprintf("%s %.2f", ITEMS, mm), collapse = "  ")))
cat(sprintf("  p5 = %.2f, lowest of the four forward items (others %.2f-%.2f)\n",
            mm["p5"], min(mm[c("p1","p3","p8")]), max(mm[c("p1","p3","p8")])))
ok7 <- mm["p5"] == min(mm[c("p1","p3","p5","p8")])

cat("\nNot established by any of the above: the ORDER of items within each polarity\n")
cat("class -- swapping p1 with p3, or p2 with p4, would leave every number here\n")
cat("unchanged. Hence PARTIAL, not VERIFIED.\n")

cat(if (ok3 && ok56 && ok7) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
