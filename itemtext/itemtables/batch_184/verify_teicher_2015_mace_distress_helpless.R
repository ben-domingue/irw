# verify_teicher_2015_mace_distress_helpless.R -- copied from references/verify_template.R
#
# Claim under test. Each `item` in teicher_2015_mace_distress_helpless is a MACE-X
# event code (S9 File column `<stem>_Helpless`, suffix stripped by
# data/teicher_2015_mace_items.py). item_text for 31 of 35 codes is the S3 File
# (MACE-X) wording at the position where MACEscore's mace_x_names.R lists that stem;
# 4 codes ship blank item_text because S3's wording at their position is not the
# administered item (Attempt_sex_sib, Intercourse_sib, H_Adults_argue, O_Adults_argue).
#
# The helpless table's own responses (0/1 "Helpless" checkbox) carry no per-item
# statistic the paper publishes. The paper DOES publish % Yes for the event
# checklist items that survived into the 52-item MACE (Tables 3,4,5,9,10,11), with
# item descriptions. So this script checks two links:
#   A. code -> wording: % Yes of the same-stem CHECKLIST item in the sibling live
#      tables vs the published % Yes beside the item's description.
#   B. helpless code -> checklist code: for each helpless item, P(helpless=1) must
#      be far higher among respondents who endorsed the same-stem event than among
#      those who did not (ties this table's codes to the checklist codes in A).
# What this does NOT establish: A pins 23 of 35 stems; the remaining 12 (eliminated
# items) are tied only by position + self-describing stem names. Also Table 9 labels
# MACE item 19 "Other adults touched or fondled you" while its % Yes matches the
# o_touch_them column (S2/S3 wording "Had you touch their body"), a label conflict
# the numbers cannot resolve on their own.

suppressMessages(library(irw))

TABLE <- "teicher_2015_mace_distress_helpless"
CHECK <- c("teicher_2015_mace_verbal", "teicher_2015_mace_nonverbal",
           "teicher_2015_mace_physical", "teicher_2015_mace_sexual",
           "teicher_2015_mace_witness_parent", "teicher_2015_mace_witness_sib")

# Published % Yes (paper Tables 5,3,4,9,10,11; image tables, transcribed).
PUBLISHED <- c(
  Afraid = 30.0, Leave = 13.9,                                   # Table 5 items 3,4
  Closet = 3.3,                                                  # Table 3 item 5
  Pushed = 30.9, Hit = 15.1, Hit_med = 3.1,                      # Table 4 items 6-8
  Spank_open = 63.7, Spanked_bare = 23.1, Spanked_strap = 24.5,  # Table 4 items 9-11
  Sex_comment = 4.0, Fondled = 2.8, Touch_them = 1.4,            # Table 9 items 12-14
  o_touch_them = 5.6, o_intercourse = 3.7,                       # Table 9 items 19,20
  Adults_push_m = 12.0, Adults_hit_m = 4.7, Adults_hit_med_m = 2.6, # Table 10 21-23
  Adults_push_f = 9.5, Adults_hit_f = 2.38,                      # Table 10 24,25
  Hit_sib = 11.9, Hit_sib_med = 1.9, Sex_comment_sib = 1.7, Fondled_sib = 1.0 # Table 11
)
TOL <- 0.6   # percentage points; Table 9 used a 967-person subset of the 1051

h <- irw::irw_fetch(TABLE)
ck <- do.call(rbind, lapply(CHECK, function(t) {
  d <- irw::irw_fetch(t); d[, c("id", "item", "resp")] }))

cat("== A. published % Yes vs live same-stem checklist item ==\n")
obs <- tapply(ck$resp, ck$item, mean) * 100
cat(sprintf("%-18s %9s %9s %7s\n", "stem", "published", "observed", "diff"))
dev <- numeric(0)
for (s in names(PUBLISHED)) {
  o <- obs[s]; dev[s] <- o - PUBLISHED[s]
  cat(sprintf("%-18s %9.2f %9.2f %7.2f\n", s, PUBLISHED[s], o, dev[s]))
}
worstA <- max(abs(dev))
cat(sprintf("largest deviation: %.2f pp (tolerance %.2f)\n", worstA, TOL))

# Would a one-position shift survive? Compare each stem to its neighbour's figure.
cat("\nNearest rival published value per stem (a swap would need |diff| <= TOL):\n")
for (s in names(PUBLISHED)) {
  others <- PUBLISHED[names(PUBLISHED) != s]
  r <- names(which.min(abs(others - obs[s])))
  cat(sprintf("  %-18s observed %.2f; closest other published %s=%.2f\n", s, obs[s], r, others[r]))
}

cat("\n== B. helpless item vs own-stem event endorsement (joined on id) ==\n")
okB <- TRUE
cat(sprintf("%-18s %8s %8s %8s %8s\n", "item", "n_ev1", "P(H|ev1)", "n_ev0", "P(H|ev0)"))
for (s in sort(unique(h$item))) {
  a <- h[h$item == s, c("id", "resp")]
  b <- ck[ck$item == s, c("id", "resp")]
  m <- merge(a, b, by = "id", suffixes = c("_h", "_ev"))
  p1 <- mean(m$resp_h[m$resp_ev == 1]); p0 <- mean(m$resp_h[m$resp_ev == 0])
  cat(sprintf("%-18s %8d %8.3f %8d %8.3f\n", s, sum(m$resp_ev == 1), p1, sum(m$resp_ev == 0), p0))
  if (is.na(p1) || is.na(p0) || p1 <= p0) okB <- FALSE
}
cat("B holds for every item (P(H|ev1) > P(H|ev0)):", okB, "\n")

cat(if (worstA <= TOL && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
