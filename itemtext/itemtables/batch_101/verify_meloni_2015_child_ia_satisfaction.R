# Step 5b, routes 8 (semantic coherence of the response distribution) and 2/3b
# (structural signature of the response scale) for meloni_2015_child_ia_satisfaction.
#
# THE CLAIM UNDER TEST. The 20 IRW item codes ARE the S1 workbook's own column
# names (IA1_REL_1 .. IA4_GEN_5) -- data/meloni_2015_disability.py melts them by
# name with no rename and no positional step -- so the four BLOCKS (religious /
# human body / social / general) come straight from the deposit and are not
# inferred. What IS inferred is position 1..5 WITHIN each block: the S2 File
# codebook (journal.pone.0128876.s002) lists the 20 activities as one flat
# roman-numbered list (i)..(xx) tied to no variable code, and the shipped mapping
# assumes that list runs in code order. The S1 workbook carries no variable or
# value labels, so there is no data_labels route to appeal to.
#
# PART A -- instrument identity (Step 3b). This table must be the SATISFACTION /
# preference half of the task, not the frequency half that shipped as
# meloni_2015_child_ia_frequency from the paired IA*_TIME columns. Preference was
# recorded by ordering the five pictures of a block, so the five items of a block
# are constrained against each other and their means must sit near 3; frequency
# carries no such constraint and spreads across the whole scale.
#
# PART B -- within-block order, from preference content (fixed before looking).
#
# PART C -- the same code->activity tie read off the paired IA*_TIME columns,
# whose frequency scale has far more spread and therefore separates items this
# table's compressed preference scale cannot. IA1_REL_4 and IA1_REL_4_TIME are the
# same picture in the same block of the same task, so a check on one is a check on
# the other's code->activity tie. This is why the sibling table is fetched here.
#
# NOT ESTABLISHED, in either part: the order of IA1_REL_2 vs IA1_REL_3 (attend
# worship / go to the catechism), IA2_HBODY_2 / _4 / _5 (watch a TV programme
# about health / play the happy surgeon / play doctor), IA3_SOCIAL_2 vs _5 (give
# seat up / read a newspaper), and IA4_GEN_2 vs _5 (read fairy tales / surf on
# the internet). A swap inside any of those runs would go undetected. Hence
# PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TEXT <- c(
  IA1_REL_1 = "read stories from the Bible",
  IA1_REL_2 = "attend worship in the Church",
  IA1_REL_3 = "go to the catechism",
  IA1_REL_4 = "say prayers",
  IA1_REL_5 = "attend parish youth club",
  IA2_HBODY_1 = "read a book about the human body",
  IA2_HBODY_2 = "watch a TV program about health",
  IA2_HBODY_3 = "search the internet for news about disease",
  IA2_HBODY_4 = "play the happy surgeon",
  IA2_HBODY_5 = "play doctor",
  IA3_SOCIAL_1 = "help a classmate with homework",
  IA3_SOCIAL_2 = "give seat up for an elderly person on a bus",
  IA3_SOCIAL_3 = "help push a wheelchair",
  IA3_SOCIAL_4 = "watch the TV news",
  IA3_SOCIAL_5 = "read a newspaper",
  IA4_GEN_1 = "visit a museum",
  IA4_GEN_2 = "read fairy tales",
  IA4_GEN_3 = "go to the cinema",
  IA4_GEN_4 = "play a sport",
  IA4_GEN_5 = "surf on the internet")

blocks <- list(REL = paste0("IA1_REL_", 1:5), HBODY = paste0("IA2_HBODY_", 1:5),
               SOCIAL = paste0("IA3_SOCIAL_", 1:5), GEN = paste0("IA4_GEN_", 1:5))

d <- irw::irw_fetch("meloni_2015_child_ia_satisfaction")
m  <- tapply(d$resp, d$item, mean)
flo <- tapply(d$resp, d$item, function(x) 100 * mean(x == 1))
cei <- tapply(d$resp, d$item, function(x) 100 * mean(x == 5))

cat("=== per-item preference (1 = liked the least .. 5 = liked the most) ===\n")
cat(sprintf("%-13s %-45s %6s %7s %7s\n", "item", "item_text (shipped)", "mean", "%at 1", "%at 5"))
for (i in names(TEXT))
  cat(sprintf("%-13s %-45s %6.2f %7.1f %7.1f\n", i, TEXT[[i]], m[[i]], flo[[i]], cei[[i]]))

## ---- PART A: the response scale is the block-constrained preference one -------
blk_mean <- vapply(blocks, function(b) mean(m[b]), 0)
cat("\n=== PART A: instrument identity ===\n")
cat(sprintf("block mean of item means: REL %.2f  HBODY %.2f  SOCIAL %.2f  GEN %.2f\n",
            blk_mean[["REL"]], blk_mean[["HBODY"]], blk_mean[["SOCIAL"]], blk_mean[["GEN"]]))
cat(sprintf("spread of the 20 item means: %.2f to %.2f (SD %.2f)\n",
            min(m), max(m), sd(m)))
a1 <- all(abs(blk_mean - 3) < 0.35)
a2 <- sd(m) < 0.6
cat(sprintf("%-4s every block mean of item means is within 0.35 of 3 (a within-block ordering constraint)\n",
            if (a1) "OK" else "FAIL"))
cat(sprintf("%-4s the 20 item means are compressed (SD < 0.6), unlike a free frequency scale\n",
            if (a2) "OK" else "FAIL"))

## ---- PART B: preference content ---------------------------------------------
hi <- function(b) names(which.max(m[blocks[[b]]]))
lo <- function(b) names(which.min(m[blocks[[b]]]))
cat("\n=== PART B: within-block order from preference content ===\n")
bchecks <- list(
  list("GEN: 'play a sport' is the most-liked general activity",
       hi("GEN") == "IA4_GEN_4"),
  list("GEN: 'visit a museum' is the least-liked general activity",
       lo("GEN") == "IA4_GEN_1"),
  list("SOCIAL: 'help a classmate with homework' is the most-liked social activity",
       hi("SOCIAL") == "IA3_SOCIAL_1"),
  list("SOCIAL: both adult news media ('watch the TV news', 'read a newspaper') sit in the bottom half of their block",
       sum(m[blocks$SOCIAL] < m[["IA3_SOCIAL_4"]]) <= 2 && sum(m[blocks$SOCIAL] < m[["IA3_SOCIAL_5"]]) <= 2),
  list("HBODY: 'watch a TV program about health' is the least-liked human-body activity",
       lo("HBODY") == "IA2_HBODY_2"),
  list("HBODY: both pretend-play items beat 'search the internet for news about disease'",
       m[["IA2_HBODY_4"]] > m[["IA2_HBODY_3"]] && m[["IA2_HBODY_5"]] > m[["IA2_HBODY_3"]]))
okB <- TRUE
for (c_ in bchecks) { cat(sprintf("%-4s %s\n", if (c_[[2]]) "OK" else "FAIL", c_[[1]])); okB <- okB && c_[[2]] }
cat(sprintf("REL block is flat -- means %s, range %.2f at n~75 (SD ~1.3, SE ~0.15):\n",
            paste(sprintf("%.2f", m[blocks$REL]), collapse = "/"),
            max(m[blocks$REL]) - min(m[blocks$REL])))
cat("     no preference prediction can be made inside it. See PART C.\n")

## ---- PART C: the same tie, on the paired frequency half ---------------------
f <- irw::irw_fetch("meloni_2015_child_ia_frequency")
mf <- tapply(f$resp, f$item, mean)
cat("\n=== PART C: same item codes, frequency half (1 never .. 5 once or more a week) ===\n")
for (i in names(TEXT)) cat(sprintf("%-13s %-45s %6.2f\n", i, TEXT[[i]], mf[[i]]))
hif <- function(b) names(which.max(mf[blocks[[b]]]))
lof <- function(b) names(which.min(mf[blocks[[b]]]))
cchecks <- list(
  list("REL: 'say prayers' is the most frequent religious activity",
       hif("REL") == "IA1_REL_4"),
  list("REL: 'read stories from the Bible' is the least frequent religious activity",
       lof("REL") == "IA1_REL_1"),
  list("HBODY: 'search the internet for news about disease' is the least frequent (6-11yo)",
       lof("HBODY") == "IA2_HBODY_3"),
  list("SOCIAL: 'help a classmate with homework' most frequent, 'help push a wheelchair' least",
       hif("SOCIAL") == "IA3_SOCIAL_1" && lof("SOCIAL") == "IA3_SOCIAL_3"),
  list("SOCIAL: 'read a newspaper' < 'watch the TV news'",
       mf[["IA3_SOCIAL_5"]] < mf[["IA3_SOCIAL_4"]]),
  list("GEN: 'play a sport' most frequent, 'visit a museum' least",
       hif("GEN") == "IA4_GEN_4" && lof("GEN") == "IA4_GEN_1"),
  list("GEN: 'go to the cinema' (an outing) is less frequent than 'read fairy tales' and 'surf on the internet'",
       mf[["IA4_GEN_3"]] < mf[["IA4_GEN_2"]] && mf[["IA4_GEN_3"]] < mf[["IA4_GEN_5"]]))
okC <- TRUE
for (c_ in cchecks) { cat(sprintf("%-4s %s\n", if (c_[[2]]) "OK" else "FAIL", c_[[1]])); okC <- okC && c_[[2]] }

cat("\nNOT ESTABLISHED by A, B or C: IA1_REL_2 vs IA1_REL_3 (3.91/3.72 freq),\n")
cat("IA2_HBODY_2/_4/_5 (2.23/2.24/2.23 freq; 2.45/3.09/2.79 pref -- the pref gaps\n")
cat("are ~1 SE and were not predicted a priori), IA3_SOCIAL_2 vs _5 (1.83/2.03 freq)\n")
cat("and IA4_GEN_2 vs _5 (3.67/3.61 freq). Status PARTIAL.\n")

cat(if (a1 && a2 && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
