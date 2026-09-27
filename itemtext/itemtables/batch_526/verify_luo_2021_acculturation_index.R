# verify_luo_2021_acculturation_index.R
#
# CLAIM UNDER TEST -----------------------------------------------------------
# data/luo_2021_acculturation.py assigns the IRW codes POSITIONALLY:
#     ACCULT_IDX = list(range(49, 59))
#     renamed = {c: f"item_{i+1:02d}" for i, c in enumerate(item_cols)}
# so item_01..item_10 are asserted to be columns 50..59 (1-based) of the study's
# S3 File .sav (doi:10.1371/journal.pone.0260616.s003). Those columns carry their
# item wording IN THE COLUMN NAME (spaces stripped, capped at 64 chars), which is
# where the shipped item_text comes from.
#
# THE FALSIFIABLE PREDICTION -------------------------------------------------
# A. Each item's live 5-cell response distribution equals the .sav column at the
#    claimed position, cell for cell.
# B. The ten .sav distributions are PAIRWISE DISTINCT, so no other assignment of
#    the ten codes to those columns can reproduce A: A + B pins every item.
# C. The shipped item_text contains the .sav column's own words (after stripping
#    the block/number prefix), modulo the two disclosed deviations.
# Hard-coded values below were read with pyreadstat from the S3 File .sav.

suppressMessages(library(irw))
TABLE <- "luo_2021_acculturation_index"

SAV_NAME <- c(
  "50" = "TheAcculturationIndex1.IshouldbehaveinaccordancewithChinesecultu",
  "51" = "@2.IshouldadapttoChineseculture",
  "52" = "@3.IshouldmixwithChinesefriends",
  "53" = "@4.IshouldlearnmoreaboutChineseculture",
  "54" = "@5.IshouldattendChineseactivities",
  "55" = "@6.Ishouldattachedtomyoriginalculture",
  "56" = "@7.Ishouldmaintainmyoriginalculture",
  "57" = "@8.Ishouldmixwithpeoplefrommycountry",
  "58" = "@9.Ishouldkeepintouchwithfriendsfrommycountry",
  "59" = "@10.Ishouldtakepartinactivitieswhichareorganizedbypeopleofmycoun")

SAV_FREQ <- rbind(
  "50" = c(25, 38, 38, 76, 52),
  "51" = c(19, 32, 48, 84, 46),
  "52" = c(11, 32, 44, 85, 57),
  "53" = c(14, 30, 41, 62, 82),
  "54" = c( 9, 36, 42, 75, 67),
  "55" = c( 7, 38, 40, 58, 86),
  "56" = c( 8, 31, 41, 57, 92),
  "57" = c(13, 37, 41, 71, 67),
  "58" = c(12, 25, 40, 49, 103),
  "59" = c(20, 27, 32, 49, 101))
CODES <- sprintf("item_%02d", 1:10)

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = CODES), factor(d$resp, levels = 1:5))

cat("A. Per-item response frequencies: .sav column at claimed position vs live IRW\n\n")
ok <- TRUE
for (i in seq_along(CODES)) {
  s <- SAV_FREQ[i, ]; l <- as.integer(live[i, ])
  m <- all(s == l); ok <- ok && m
  cat(sprintf("%-8s col %s  sav %-20s live %-20s %s\n", CODES[i], rownames(SAV_FREQ)[i],
              paste(s, collapse = "/"), paste(l, collapse = "/"), if (m) "OK" else "MISMATCH"))
}

keys <- apply(SAV_FREQ, 1, paste, collapse = "/")
distinct <- length(unique(keys)) == length(keys)
cat(sprintf("\nB. distinct .sav frequency vectors: %d of %d -> %s\n",
            length(unique(keys)), length(keys),
            if (distinct) "only the claimed assignment fits" else "TIES: some items not separable"))

cat("\nC. Shipped item_text vs .sav column name\n")
csvf <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)[1])),
                  paste0(TABLE, "__items.csv"))
if (!file.exists(csvf)) csvf <- file.path("itemtables", "batch_526", paste0(TABLE, "__items.csv"))
it <- unique(read.csv(csvf, stringsAsFactors = FALSE)[, c("item", "item_text")])
it <- it[match(CODES, it$item), ]
norm <- function(x) gsub("[^a-z]", "", tolower(x))
c_ok <- TRUE
for (i in seq_along(CODES)) {
  sav <- norm(sub("^(TheAcculturationIndex1\\.|@[0-9]+\\.)", "", SAV_NAME[i]))
  sh  <- norm(it$item_text[i])
  if (CODES[i] == "item_06") sh6 <- sub("remain", "", sh)  # disclosed: paper's quote adds 'remain'
  m <- if (CODES[i] == "item_06") sh6 == sav else startsWith(sh, sav)
  c_ok <- c_ok && m
  cat(sprintf("%-8s sav: %-60s shipped: %s %s\n", CODES[i], sav, sh, if (m) "OK" else "MISMATCH"))
}

cat("\nWhat this does NOT establish: items 1 and 10 are cut at SPSS's 64-char name cap;\n")
cat("item 1's tail ('re') is from the paper's own quote, item 10's ('try') is completed\n")
cat("by this project and anything after 'country' is unrecoverable. Item 6 ships the\n")
cat("paper's quoted wording ('remain attached'), not the .sav name ('attached').\n")
cat("Word spacing is restored, not transcribed.\n\n")
cat(if (ok && distinct && c_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
