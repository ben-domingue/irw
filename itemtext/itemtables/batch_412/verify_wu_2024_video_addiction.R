# verify_wu_2024_video_addiction.R -- Step 5b re-runnable evidence.
#
# CLAIM UNDER TEST. wu_2024_video_addiction's D1..D14 (the "SFV addiction" block of
# Wu et al. 2024 PLOS ONE S1 Data; the workbook carries only bare codes) are the 14
# retained items of Qin et al. (2019)'s Short Video Addiction Scale IN THE ORDER OF
# QIN'S TABLE 1 (items grouped by dimension), NOT in the order of Qin's appendix
# questionnaire. The shipped file asserts:
#   D1..D5  = anxiety/feeling lost   (Qin Q10, Q11, Q8, Q9, Q12)
#   D6..D8  = withdrawal/escape      (Q14, Q15, Q13)
#   D9..D12 = inability to control   (Q5, Q7, Q6, Q4)
#   D13,D14 = productivity loss      (Q17, Q16)
# and resp 1 = 非常不符合 .. 5 = 非常符合 (higher = more addicted).
#
# ROUTE 3 (published subscale statistics): Wu et al. report Cronbach's alpha 0.904
# total and 0.856 / 0.859 / 0.886 / 0.789 for the four dimensions. The Table-1-order
# blocks must reproduce all four; the appendix-order alternative
# (D1-4 craving = Q4-7, D5-9 anxiety = Q8-12, D10-12 escape = Q13-15, D13-14 = Q16-17)
# is computed as the rival.
# ROUTE 3 (published count): Wu et al. classify as addicts respondents answering
# "affirmatively" (resp >= 4) to at least 4 of Qin's 7 diagnostic items (Q10, Q8,
# Q15, Q5, Q7, Q6, Q16), and report 132 of 560. Under the claimed order those are
# D1, D3, D7, D9, D10, D11, D14. Every alternative placement of the diagnostic items
# WITHIN the claimed blocks (C(5,2)*3*4*2 = 240 sets) is enumerated; the claim needs
# the shipped set to give 132 and to be the only one that does. A reversed anchor
# direction (resp <= 2 as "affirmative") is also computed.
#
# WHAT THIS DOES NOT ESTABLISH: order within the diagnostic/non-diagnostic subsets of
# a block: D1 vs D3 (Q10 vs Q8), D2/D4/D5 (Q11/Q9/Q12), D6 vs D8 (Q14 vs Q13), and
# D9/D10/D11 (Q5/Q7/Q6). Those rest on Qin's Table 1 order. Hence PARTIAL.

suppressMessages(library(irw))
TABLE <- "wu_2024_video_addiction"
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
D <- paste0("D", 1:14)
w <- w[stats::complete.cases(w[, D]), D]
cat(sprintf("live complete respondents: %d (paper N = 560)\n\n", nrow(w)))

alpha <- function(X) { k <- ncol(X); k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X))) }
blk <- function(v) paste0("D", v)
claimed  <- list(anxiety = 1:5, escape = 6:8, craving = 9:12, productivity = 13:14)
appendix <- list(anxiety = 5:9, escape = 10:12, craving = 1:4, productivity = 13:14)
pub <- c(anxiety = 0.856, escape = 0.859, craving = 0.886, productivity = 0.789)
cat(sprintf("%-13s %9s %9s %9s\n", "dimension", "published", "claimed", "appendix"))
ac <- sapply(claimed, function(v) alpha(w[, blk(v)]))
aa <- sapply(appendix, function(v) alpha(w[, blk(v)]))
for (n in names(pub)) cat(sprintf("%-13s %9.3f %9.3f %9.3f\n", n, pub[n], ac[n], aa[n]))
tot <- alpha(w[, D]); cat(sprintf("%-13s %9.3f %9.3f\n", "total", 0.904, tot))
ok_alpha <- all(abs(ac[names(pub)] - pub) <= 0.0015) && abs(tot - 0.904) <= 0.0015
cat(sprintf("claimed blocks reproduce all alphas to 3dp: %s; appendix rival max miss %.3f\n\n",
            ok_alpha, max(abs(aa[names(pub)] - pub))))

addicts <- function(S, affirm = function(x) x >= 4) sum(rowSums(affirm(w[, blk(S)])) >= 4)
shipped <- c(1, 3, 7, 9, 10, 11, 14)
n_ship <- addicts(shipped)
n_rev  <- addicts(shipped, function(x) x <= 2)
cat(sprintf("addicts (>=4 of 7 diagnostic items at resp>=4), shipped set D%s: %d (published 132)\n",
            paste(shipped, collapse = ",D"), n_ship))
cat(sprintf("same set with reversed anchors (resp<=2 affirmative): %d\n", n_rev))
res <- c()
for (a in combn(1:5, 2, simplify = FALSE)) for (e in 6:8) for (dr in 9:12) for (p in 13:14) {
  S <- c(a, e, setdiff(9:12, dr), p)
  res[paste(S, collapse = ",")] <- addicts(S)
}
hits <- names(res)[res == 132]
cat(sprintf("within-block alternatives enumerated: %d; giving 132: %d (%s); range %d-%d\n\n",
            length(res), length(hits), paste(hits, collapse = " | "), min(res), max(res)))

lv <- sapply(D, function(i) length(unique(w[[i]])))
cat("levels used per item:", paste(sprintf("%s=%d", D, lv), collapse = " "), "\n")
cat("NOT established: order within D1/D3, D2/D4/D5, D6/D8, D9/D10/D11 -> PARTIAL\n")

pass <- ok_alpha && n_ship == 132 && length(hits) == 1 && hits == paste(shipped, collapse = ",") && n_rev != 132
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
