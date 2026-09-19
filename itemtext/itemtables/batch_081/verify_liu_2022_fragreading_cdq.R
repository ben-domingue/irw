# verify_liu_2022_fragreading_cdq.R -- Step 5b mapping check.
#
# CLAIM UNDER TEST: item codes N9_1..N9_11 carry the wording numbered 9.1..9.11 in
# the study's own questionnaire (PeerJ supplement s002.docx, Table 3), and resp 1..5
# runs 非常不符合/Strongly Disagree -> 非常符合/Strongly Agree.
#
# The supplement marks *9.6-*9.9 as REVERSE items and groups 9.1-9.5 as
# "D, Cognitive Breadth" and 9.6-9.11 as "E, Cognitive Depth" (9.5, 9.10, 9.11
# dropped at CFA, so the paper's breadth = 9.1-9.4 "D1-D4", depth = 9.6-9.9 "E1-E4").
# Those are falsifiable predictions about the live data:
#   (1) {N9_6..N9_9} is a polarity block: they intercorrelate positively with each
#       other and ~zero/negatively with the unstarred items N9_10/N9_11.
#   (2) paper Table 2: breadth vs attentional fragmentation r = +0.46,
#       depth vs attentional fragmentation r = -0.78 (sign, not magnitude, is the test).
#       Depth must be REVERSE-SCORED to get a negative sign -- which also pins the
#       direction of the 1..5 option coding, since scoring the anchors the other way
#       round would flip depth positive and contradict the published sign.
#
# WHAT THIS DOES NOT ESTABLISH: it separates polarity classes and subscale blocks,
# not individual items within a class (nothing here distinguishes N9_1 from N9_2).
# That tie is the questionnaire's own 9.k numbering against the data's N9_k columns.

suppressMessages(library(irw))

wide <- function(tab) {
  d <- as.data.frame(irw::irw_fetch(tab))
  m <- reshape(d[, c("id", "item", "resp")], idvar = "id",
               timevar = "item", direction = "wide")
  names(m) <- sub("^resp\\.", "", names(m))
  m
}

cdq <- wide("liu_2022_fragreading_cdq")
frq <- wide("liu_2022_fragreading_frq")
m   <- merge(cdq, frq, by = "id")
cat(sprintf("merged respondents: %d\n\n", nrow(m)))

rev_items <- paste0("N9_", 6:9)     # * reverse-marked in the supplement
pos_items <- paste0("N9_", c(10, 11))  # unstarred, same subscale (E)

R <- cor(m[, paste0("N9_", 1:11)], use = "pairwise.complete.obs")

cat("(1) polarity block test\n")
within_rev <- mean(R[rev_items, rev_items][upper.tri(diag(4))])
cross      <- mean(R[rev_items, pos_items])
cat(sprintf("  mean r WITHIN the four *-marked reverse items 9.6-9.9 : %+.3f\n", within_rev))
cat(sprintf("  mean r between those and unstarred 9.10/9.11         : %+.3f\n", cross))
for (i in rev_items)
  cat(sprintf("    %-6s vs N9_10 %+.2f  vs N9_11 %+.2f\n", i, R[i, "N9_10"], R[i, "N9_11"]))
ok1 <- within_rev > 0.30 && cross < 0.15

cat("\n(2) published between-scale correlations (paper Table 2)\n")
breadth <- rowMeans(m[, paste0("N9_", 1:4)])            # D1-D4
depth_r <- rowMeans(6 - m[, paste0("N9_", 6:9)])        # E1-E4, reverse scored
depth_raw <- rowMeans(m[, paste0("N9_", 6:9)])
attfrag <- rowMeans(m[, paste0("N8_", 13:22)])          # C, attentional fragmentation
r_b <- cor(breadth, attfrag); r_d <- cor(depth_r, attfrag); r_draw <- cor(depth_raw, attfrag)
cat(sprintf("  breadth(9.1-9.4) vs attentional frag : observed %+.3f   published +0.46\n", r_b))
cat(sprintf("  depth REVERSED(9.6-9.9) vs att frag  : observed %+.3f   published -0.78\n", r_d))
cat(sprintf("  depth RAW (not reversed) vs att frag : observed %+.3f   (wrong sign vs paper)\n", r_draw))
ok2 <- abs(r_b - 0.46) < 0.10 && r_d < 0 && r_draw > 0

cat("\n(3) option direction implied by (2): 1 = Strongly Disagree ... 5 = Strongly Agree\n")
cat(sprintf("  under the shipped coding, depth reversed as (6-x) gives r %+.3f (paper negative): %s\n",
            r_d, if (r_d < 0) "consistent" else "INCONSISTENT"))
cat(sprintf("  under a flipped anchor order the same score would be %+.3f, contradicting the paper\n", -r_d))

cat("\nNOTE: this pins polarity class, subscale block and anchor direction; it does NOT\n")
cat("distinguish items within a class (e.g. N9_1 vs N9_2). Status recorded as PARTIAL.\n")

cat(if (ok1 && ok2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
