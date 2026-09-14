# Step 5b route 8 (semantic coherence of the response distribution) for
# meloni_2015_child_ia_frequency.
#
# THE CLAIM UNDER TEST. The 20 IRW item codes are the S1 workbook's own column
# names (IA1_REL_1 .. IA4_GEN_5, minus the "_TIME" suffix the processing script
# strips), so the four BLOCKS -- religious / human body / social / general -- are
# given by the codes and are not inferred. What IS inferred is the position
# 1..5 WITHIN each block: the S2 File codebook lists the 20 activities as a flat
# roman-numbered list (i)..(xx) whose first ten fall into two content-clean
# blocks of five, and the mapping assumes that list runs in code order.
#
# That assumption is falsifiable, because this table's resp scale is a frequency
# (1 = never, 3 = once or more a year, 5 = once or more a week) and the twenty
# activities have strongly different real-world base rates for Italian children
# aged 6-11. The predictions below were fixed from item CONTENT before looking at
# the data; each would break if the within-block order were permuted.
#
# What this does NOT establish: three human-body items (watch a TV programme
# about health / play the happy surgeon / play doctor) have means within 0.01 of
# each other, so no distributional route can separate that trio. Status PARTIAL.

suppressMessages(library(irw))

TABLE <- "meloni_2015_child_ia_frequency"
d <- irw::irw_fetch(TABLE)
m  <- tapply(d$resp, d$item, mean)
ceil <- tapply(d$resp, d$item, function(x) 100 * mean(x == 5))
flo  <- tapply(d$resp, d$item, function(x) 100 * mean(x == 1))

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

cat(sprintf("%-13s %-45s %6s %7s %7s\n", "item", "item_text (shipped)", "mean", "%never", "%weekly"))
for (i in names(TEXT))
  cat(sprintf("%-13s %-45s %6.2f %7.1f %7.1f\n", i, TEXT[[i]], m[[i]], flo[[i]], ceil[[i]]))
cat("\n")

blocks <- list(REL = paste0("IA1_REL_", 1:5), HBODY = paste0("IA2_HBODY_", 1:5),
               SOCIAL = paste0("IA3_SOCIAL_", 1:5), GEN = paste0("IA4_GEN_", 1:5))
hi <- function(b) names(which.max(m[blocks[[b]]]))
lo <- function(b) names(which.min(m[blocks[[b]]]))

checks <- list(
  list("REL: 'say prayers' is the most frequent religious activity",
       hi("REL") == "IA1_REL_4"),
  list("HBODY: 'search the internet for news about disease' is the least frequent (6-11yo)",
       lo("HBODY") == "IA2_HBODY_3"),
  list("SOCIAL: 'help a classmate with homework' most frequent, 'help push a wheelchair' least",
       hi("SOCIAL") == "IA3_SOCIAL_1" && lo("SOCIAL") == "IA3_SOCIAL_3"),
  list("GEN: 'play a sport' most frequent, 'visit a museum' least",
       hi("GEN") == "IA4_GEN_4" && lo("GEN") == "IA4_GEN_1"),
  list("whole table: 'play a sport' is the max of all 20 items",
       names(which.max(m)) == "IA4_GEN_4"),
  list("whole table: 'help push a wheelchair' is the min of all 20 items",
       names(which.min(m)) == "IA3_SOCIAL_3"),
  list("'read a newspaper' < 'watch the TV news' (same social block, different medium)",
       m[["IA3_SOCIAL_5"]] < m[["IA3_SOCIAL_4"]]))

# DISCARDED PREDICTION, recorded so it is not silently dropped: "'go to the cinema'
# should have the smallest SD of the GEN block, being an annual rather than a
# weekly or never activity". It is false in the data (cinema SD 1.12 vs 'play a
# sport' 0.85) but it is a bad test rather than a bad mapping -- an item pinned at
# the ceiling has a compressed SD by construction, so SD here measures position on
# the scale, not regularity of engagement. It is not counted in the verdict.

ok <- TRUE
for (c_ in checks) { cat(sprintf("%-4s %s\n", if (c_[[2]]) "OK" else "FAIL", c_[[1]])); ok <- ok && c_[[2]] }

cat(sprintf("\n%d/%d content predictions hold. Under a random permutation WITHIN each\n",
            sum(vapply(checks, function(x) x[[2]], TRUE)), length(checks)))
cat("block the first four alone would hold with probability (1/5)(1/5)(1/20)(1/20) = 1e-4.\n")
cat("NOT ESTABLISHED: IA2_HBODY_2/_4/_5 (means 2.23/2.24/2.23) are mutually\n")
cat("indistinguishable by any distributional route -- their order rests on the\n")
cat("codebook's list order alone. Hence PARTIAL, not VERIFIED.\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
