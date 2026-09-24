# Verification for germann_2026_immigration (batch_335). Run from itemtext/.
#
# CLAIM. Live item codes imm1/imm2/imm3 are the source column names of LondonBridgeAttack2017.tab
# (Dataverse doi:10.7910/DVN/ALYGQS, file 13400055; data/germann_2026_terrorism.py melts them by
# name). Their wording comes from the paper's SI Appendix (Cambridge S1475676526101017sup001.pdf),
# which labels each statement with the same code ("imm1: The UK should continue to allow free
# movement ... (reversed)", SI p. 36; Table S2.13/S2.15). resp is stored with imm1 and imm3
# reverse-scored (1 = Completely agree) and imm2 forward (1 = Completely disagree).
#
# CHECKS
#  A. live (item, resp) counts == source-column counts, 15 cells: the live codes are those columns.
#  B. SI Figure S2.20 prints, per labelled item, the regression N in the +-1/2/3-day windows
#     (reg <item> postattack $covars_binaries, Study2_Appendix_FigureS2_20.do). Recomputing those
#     9 Ns from the source columns ties the SI's labels (and so its wording) to each column. The
#     three items' N triples are pairwise distinct, so a swap of any two labels breaks it.
#  C. Direction (option_text <-> resp): Leave voters (refvote2016 == 2) should sit higher than
#     Remain voters on every stored item if higher = more restrictive; with the shipped labels
#     that means Leave voters DISagree with "continue free movement" / "welcome more migrants" and
#     AGREE with "quotas". Also checks the shipped rows put those labels at resp 5.
#     Content cue: the EU-free-movement item (imm1) should show the largest Leave-Remain gap.
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")
suppressMessages(library(irw))
TB <- "germann_2026_immigration"
src <- read.delim(cached_source(".cache/germann_2026_immigration/LondonBridgeAttack2017.tab",
                                "https://dataverse.harvard.edu/api/access/datafile/13400055",
                                min_bytes = 1e7), stringsAsFactors = FALSE)
items <- c("imm1", "imm2", "imm3")
ok <- TRUE

## A
live <- as.data.frame(irw::irw_fetch(TB))
if (!nrow(live)) stop("irw_fetch returned no rows -- nothing was checked")
tl <- table(factor(live$item, levels = items), factor(live$resp, levels = 1:5))
cat("A. per-level counts, source column vs live item\n")
nA <- 0
for (it in items) {
  s <- as.integer(table(factor(src[[it]], levels = 1:5))); l <- as.integer(tl[it, ])
  nA <- nA + sum(s == l)
  cat(sprintf("  %-5s source %-32s live %-32s %s\n", it, paste(s, collapse = "/"),
              paste(l, collapse = "/"), if (all(s == l)) "" else "MISMATCH"))
}
cat(sprintf("  %d of 15 cells match\n\n", nA)); ok <- ok && nA == 15

## B
PUB <- list(imm1 = c(6341, 12553, 22299), imm2 = c(6318, 12501, 22210), imm3 = c(6310, 12499, 22211))
cov <- strsplit("gender1 gender2 gender3 agecat1 agecat2 agecat3 agecat4 agecat5 agecat6 edu1 edu2 edu3 edu4 edu5 edu6 pol_interest1 pol_interest2 pol_interest3 pol_interest4 lr0 lr1 lr2 lr3 lr4 lr5 lr6 lr7 lr8 lr9 lr10 vote2015_1 vote2015_2 vote2015_3 vote2015_4 vote2015_5 vote2015_6 vote2015_7 vote2015_8 vote2015_9 vote2015_10 refvote2016_1 refvote2016_2 refvote2016_3 region1 region2 region3", " ")[[1]]
dt <- as.Date(src$statadate)
win <- list(dt %in% as.Date(c("2017-06-02", "2017-06-04")),
            (dt >= as.Date("2017-06-01") & dt <= as.Date("2017-06-02")) | (dt >= as.Date("2017-06-04") & dt <= as.Date("2017-06-05")),
            (dt >= as.Date("2017-05-31") & dt <= as.Date("2017-06-02")) | (dt >= as.Date("2017-06-04") & dt <= as.Date("2017-06-06")))
cat("B. SI Figure S2.20 regression N (+-1/2/3 days), published vs recomputed from source column\n")
nB <- 0
for (it in items) {
  obs <- sapply(win, function(w) sum(w & complete.cases(src[, c(it, "postattack", cov)])))
  nB <- nB + sum(obs == PUB[[it]])
  cat(sprintf("  %-5s published %-20s recomputed %-20s %s\n", it, paste(PUB[[it]], collapse = "/"),
              paste(obs, collapse = "/"), if (all(obs == PUB[[it]])) "" else "MISMATCH"))
}
distinct <- length(unique(vapply(PUB, paste, "", collapse = "/"))) == 3
cat(sprintf("  %d of 9 match; published triples pairwise distinct: %s\n\n", nB, distinct))
ok <- ok && nB == 9 && distinct

## C
sh <- shipped_items(TB, "itemtables/batch_335/germann_2026_immigration__items.csv")
top <- setNames(sh$option_text[sh$resp == 5], sh$item[sh$resp == 5])[items]
EXPECT_TOP <- c(imm1 = "Completely disagree", imm2 = "Completely agree", imm3 = "Completely disagree")
cat("C. Leave - Remain mean on stored resp (must be > 0 if higher = restrictive)\n")
gap <- sapply(items, function(it) mean(src[[it]][src$refvote2016 == 2], na.rm = TRUE) -
                                  mean(src[[it]][src$refvote2016 == 1], na.rm = TRUE))
for (it in items) cat(sprintf("  %-5s gap %+.3f  shipped resp=5 label '%s' (expected '%s')\n",
                              it, gap[it], top[it], EXPECT_TOP[it]))
cat(sprintf("  largest gap on imm1 (EU free movement): %s\n", names(which.max(gap)) == "imm1"))
ok <- ok && all(gap > 0) && all(top == EXPECT_TOP) && names(which.max(gap)) == "imm1"

cat("\nNot established: nothing beyond the SI's own wording -- the VAA screen text itself",
    "(SI Figure S2.6c) is an image and was not transcribed.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
