# verify_znidarsic_2021_coworker_support.R -- Step 5b, batch_407.
#
# Claim: item codes CS01..CS09 are POSITIONAL (data/znidarsic_2021_work_family_balance.py,
# df.iloc[:, 18:27] of PLOS S1 Data 10.1371/journal.pone.0245078.s001, sha256 fd8b260d...),
# and item_text is the trimmed column header at that position. The leader-support block
# (cols 9..17) asks the SAME nine behaviours, so the check must also show the codes do
# not come from that block.
#
# Route (Step 5b route 9 applied to columns / script re-run): the 1..5 response counts of
# every S1 Data column in both blocks are hard-coded below (computed from the xlsx with the
# script's own 1..5 filter). Each live item's count vector must match EXACTLY ONE source
# column, and that column's header must equal the shipped item_text.

suppressMessages(library(irw))
TABLE <- "znidarsic_2021_coworker_support"
here <- tryCatch(dirname(normalizePath(sys.frame(1)$ofile)), error = function(e) "itemtables/batch_407")
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))
if (!file.exists(items_csv)) items_csv <- file.path("itemtables/batch_407", paste0(TABLE, "__items.csv"))

src <- list(   # xlsx 0-based col -> list(header (trimmed), counts at resp 1..5)
  `9`  = list("Switched schedules ( hours, overtime hours, vacation ) to accommodate my family responsibilities", c(13,24,63,89,58)),
  `10` = list("Listened to my problems.", c(16,30,76,72,53)),
  `11` = list("Takes into account my efforts to combine work and family", c(10,32,88,63,54)),
  `12` = list("Juggled tasks or duties to accommodate my family responsibilities.", c(17,43,71,71,45)),
  `13` = list("Shared ideas or advice.", c(23,46,63,74,41)),
  `14` = list("Did not held my family responsibilities against me.", c(63,25,46,50,62)),
  `15` = list("Helped me to figure out how to solve a problem.", c(17,35,54,70,71)),
  `16` = list("Was understanding.", c(6,17,68,82,74)),
  `17` = list("Did not showed resentment of my needs as a working parent.", c(31,22,71,55,68)),
  `18` = list("Helped me to switch schedules ( hours, overtime hours, vacation ) to accommodate my family responsibilities", c(11,18,83,89,46)),
  `19` = list("Listened to my problems.", c(9,19,69,97,53)),
  `20` = list("Takes into account my efforts to combine work and family", c(8,25,77,89,48)),
  `21` = list("Juggled tasks or duties to accommodate my family responsibilities.", c(13,37,78,87,32)),
  `22` = list("Shared ideas or advice.", c(13,29,59,90,56)),
  `23` = list("Did not held my family responsibilities against me.", c(56,32,45,62,52)),
  `24` = list("Helped me to figure out how to solve a problem.", c(11,29,63,90,54)),
  `25` = list("Was understanding.", c(7,13,54,100,73)),
  `26` = list("Did not showed resentment of my needs as a working parent.", c(38,34,48,62,65)))
expected_col <- setNames(as.character(18:26), sprintf("CS%02d", 1:9))

d <- irw::irw_fetch(TABLE)
it <- read.csv(items_csv, stringsAsFactors = FALSE)
txt <- tapply(it$item_text, it$item, `[`, 1)

ok <- TRUE
cat(sprintf("%-5s %-22s %-10s %-8s %s\n", "item", "live counts 1..5", "matches", "expect", "text==header"))
for (i in names(expected_col)) {
  live <- tabulate(d$resp[d$item == i], 5)
  hits <- names(src)[vapply(src, function(s) identical(as.numeric(s[[2]]), as.numeric(live)), TRUE)]
  tmatch <- identical(txt[[i]], src[[expected_col[[i]]]][[1]])
  good <- length(hits) == 1 && hits == expected_col[[i]] && tmatch
  ok <- ok && good
  cat(sprintf("%-5s %-22s %-10s %-8s %s\n", i, paste(live, collapse = "/"),
              if (length(hits)) paste(hits, collapse = ",") else "none", expected_col[[i]], tmatch))
}
cat("\nEach live item's 5-cell count vector matches exactly one of the 18 source columns (both\n",
    "blocks), and it is the co-worker column at the script's position; e.g. CS05 and CS07 share a\n",
    "mean (3.595) but differ in counts (13/29/59/90/56 vs 11/29/63/90/54). This pins every item\n",
    "individually and excludes the identically-worded leader block (cols 9-17).\n",
    "Not established here: the response ANCHORS (1 = never, 5 = very often) come from the paper's\n",
    "Methods, not from this check.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
