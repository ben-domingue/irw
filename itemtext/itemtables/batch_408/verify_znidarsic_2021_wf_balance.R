# verify_znidarsic_2021_wf_balance.R -- Step 5b, batch_408.
#
# Claim 1 (item axis): item codes WFB1..WFB4 are POSITIONAL (data/znidarsic_2021_work_family_balance.py,
# df.iloc[:, 52:56] of PLOS S1 Data 10.1371/journal.pone.0245078.s001, sha256 fd8b260d...), and
# item_text is the whitespace-trimmed column header at that position.
# Route (Step 5b route 9 applied to columns): the 1..5 response counts of EVERY item column in the
# deposit (0-based cols 9..64, all five instruments) are hard-coded below, computed from the xlsx with
# the script's own 1..5 filter. Each live item's count vector must match EXACTLY ONE source column, it
# must be the column at the script's position, and that column's header must equal shipped item_text.
#
# Claim 2 (option axis, WFB2 only): WFB2 is negatively worded ("I have problems with balancing...")
# but is stored already reverse-scored, so its anchors are shipped reversed (1 = completely agree,
# 5 = completely disagree). Test: WFB2 must correlate POSITIVELY with all three positively worded items.

suppressMessages(library(irw))
TABLE <- "znidarsic_2021_wf_balance"
here <- tryCatch(dirname(normalizePath(sys.frame(1)$ofile)), error = function(e) "itemtables/batch_408")
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))
if (!file.exists(items_csv)) items_csv <- file.path("itemtables/batch_408", paste0(TABLE, "__items.csv"))

counts <- list(`9`=c(13,24,63,89,58), `10`=c(16,30,76,72,53), `11`=c(10,32,88,63,54), `12`=c(17,43,71,71,45),
  `13`=c(23,46,63,74,41), `14`=c(63,25,46,50,62), `15`=c(17,35,54,70,71), `16`=c(6,17,68,82,74),
  `17`=c(31,22,71,55,68), `18`=c(11,18,83,89,46), `19`=c(9,19,69,97,53), `20`=c(8,25,77,89,48),
  `21`=c(13,37,78,87,32), `22`=c(13,29,59,90,56), `23`=c(56,32,45,62,52), `24`=c(11,29,63,90,54),
  `25`=c(7,13,54,100,73), `26`=c(38,34,48,62,65), `27`=c(64,35,40,52,56), `28`=c(62,35,36,59,55),
  `29`=c(50,34,51,58,54), `30`=c(31,45,52,61,57), `31`=c(30,32,46,69,70), `32`=c(22,29,48,66,82),
  `33`=c(49,32,50,53,63), `34`=c(133,23,40,26,24), `35`=c(21,35,65,68,57), `36`=c(65,45,80,35,22),
  `37`=c(74,42,83,30,18), `38`=c(30,40,70,60,46), `39`=c(41,45,85,51,25), `40`=c(72,42,70,43,20),
  `41`=c(47,40,88,42,30), `42`=c(36,39,74,59,39), `43`=c(47,43,72,56,29), `44`=c(57,49,77,41,23),
  `45`=c(37,27,61,48,74), `46`=c(51,32,68,41,55), `47`=c(107,33,52,30,25), `48`=c(95,39,59,29,25),
  `49`=c(139,29,41,21,17), `50`=c(137,26,47,22,15), `51`=c(117,36,33,35,26), `52`=c(38,49,57,72,31),
  `53`=c(35,37,70,60,45), `54`=c(37,51,64,67,28), `55`=c(33,41,59,77,37), `56`=c(9,17,73,103,45),
  `57`=c(3,8,66,98,72), `58`=c(31,42,80,73,21), `59`=c(17,22,101,81,26), `60`=c(13,16,83,83,52),
  `61`=c(19,33,95,64,36), `62`=c(16,34,83,81,33), `63`=c(25,31,100,72,19), `64`=c(21,21,63,82,60))
headers <- c(`52` = "The current relationship between the time I spend on the job and the time I have for my non-formal activities seems good to me.",
             `53` = "I have problems with balancing work and non- work activities.",
             `54` = "I think that the balance between my work requirements and non-work activities is just right.",
             `55` = "Generally speaking, I think my work and private life is balanced..")
expected_col <- setNames(as.character(52:55), paste0("WFB", 1:4))

d <- irw::irw_fetch(TABLE)
it <- read.csv(items_csv, stringsAsFactors = FALSE)
txt <- tapply(it$item_text, it$item, `[`, 1)

ok <- TRUE
cat("Claim 1: live count vectors vs all 56 deposit item columns\n")
cat(sprintf("%-5s %-20s %-8s %-7s %s\n", "item", "live counts 1..5", "matches", "expect", "text==header"))
for (i in names(expected_col)) {
  live <- tabulate(d$resp[d$item == i], 5)
  hits <- names(counts)[vapply(counts, function(s) identical(as.numeric(s), as.numeric(live)), TRUE)]
  tmatch <- identical(txt[[i]], headers[[expected_col[[i]]]])
  good <- length(hits) == 1 && hits == expected_col[[i]] && tmatch
  ok <- ok && good
  cat(sprintf("%-5s %-20s %-8s %-7s %s\n", i, paste(live, collapse = "/"),
              if (length(hits)) paste(hits, collapse = ",") else "none", expected_col[[i]], tmatch))
}

cat("\nClaim 2: WFB2 keying (negatively worded, stored reversed?)\n")
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id", timevar = "item", direction = "wide")
r <- cor(w[, paste0("resp.WFB", 1:4)], use = "pairwise")
r2 <- r["resp.WFB2", c("resp.WFB1", "resp.WFB3", "resp.WFB4")]
print(round(r2, 3))
cat(sprintf("min r(WFB2, positive items) = %.3f; expected > 0 if WFB2 is stored reverse-scored\n", min(r2)))
labs <- it[it$item == "WFB2" & it$resp %in% c(1, 5), c("resp", "option_text")]
anch <- identical(labs$option_text[labs$resp == 1], "completely agree") &&
        identical(labs$option_text[labs$resp == 5], "completely disagree")
cat("shipped WFB2 anchors reversed (1=completely agree, 5=completely disagree):", anch, "\n")
ok <- ok && min(r2) > 0.3 && anch

cat("\nEach live WFB item matches exactly one of the 56 item columns in the deposit (all five\n",
    "blocks), and it is the column at the script's position (52..55), so every item is pinned\n",
    "individually. Not established here: the anchor WORDS (completely disagree / completely agree)\n",
    "come from the paper's Methods 2.1, and the reversal of WFB2's anchors rests on the correlation\n",
    "sign, not on any statement by the authors that the item was recoded.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
