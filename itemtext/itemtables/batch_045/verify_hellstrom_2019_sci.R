# verify_hellstrom_2019_sci.R
#
# Claim under test (BOTH mapping axes at once):
#   (a) item_text <-> item : SCI_1..SCI_8 carry the wording of the paper's
#       numbered SCI items 1..8;
#   (b) option_text <-> resp : the IRW integer coding is the REVERSE of the
#       canonical SCI scoring for items 1,2,3,5,6,7,8 and matches it for item 4,
#       because data/hellstrom_2019_sleep_battery.py re-coded the .sav's LABEL
#       strings with its own maps (DURATION5 '0-15 min' -> 0, IMPACT5
#       'not at all' -> 0, ...) instead of keeping the .sav's stored integers
#       (which run '>60 min' = 0 ... '0-15 min' = 4).
#
# Falsifiable prediction: Hellstrom et al. 2019 PLOS ONE Table 2 publishes the
# full item x response-category endorsement frequencies (n = 634). Under the
# claimed mapping every one of the 40 cells must reproduce exactly on the live
# data. Any swapped pair of items, or any flipped/permuted response direction,
# breaks it -- all eight items have distinct count profiles.
#
# Table 2 is printed with the CANONICAL SCI column order 4,3,2,1,0 (best sleep
# first). PUBLISHED below is rewritten into the shipped IRW resp order 0..4,
# i.e. the option_text this table ships against resp = 0,1,2,3,4.

suppressMessages(library(irw))

TABLE <- "hellstrom_2019_sci"

# Table 2 counts, re-ordered to the shipped resp 0..4 with the shipped option_text.
PUBLISHED <- rbind(
  SCI_1 = c(227, 212,  93,  49,  51),  # 0-15 min | 16-30 | 31-45 | 46-60 | >60 min
  SCI_2 = c(370, 128,  48,  47,  40),  # same duration anchors
  SCI_3 = c(330,  92,  73,  55,  81),  # 0-1 nights | 2 | 3 | 4 | 5-7 nights
  SCI_4 = c( 22,  94, 149, 248, 119),  # Very poor | Poor | Average | Good | Very good
  SCI_5 = c(103, 241, 158,  87,  42),  # Not at all | A little | Somewhat | Much | Very much
  SCI_6 = c(101, 230, 162,  98,  38),
  SCI_7 = c(134, 253, 139,  68,  34),
  SCI_8 = c(313,  61,  48,  28, 176)   # no problem/<1 mo | 1-2 | 3-6 | 7-12 mo | >1 yr
)
colnames(PUBLISHED) <- as.character(0:4)

d <- irw::irw_fetch(TABLE)
obs <- table(factor(d$item, levels = rownames(PUBLISHED)),
             factor(d$resp, levels = 0:4))
obs <- matrix(as.integer(obs), nrow = nrow(PUBLISHED),
              dimnames = dimnames(PUBLISHED))

cat("resp:            0     1     2     3     4      (published / observed)\n")
for (i in rownames(PUBLISHED)) {
  cat(sprintf("%-6s pub %5d %5d %5d %5d %5d\n", i, PUBLISHED[i, 1], PUBLISHED[i, 2],
              PUBLISHED[i, 3], PUBLISHED[i, 4], PUBLISHED[i, 5]))
  cat(sprintf("%-6s obs %5d %5d %5d %5d %5d\n", "", obs[i, 1], obs[i, 2],
              obs[i, 3], obs[i, 4], obs[i, 5]))
}

mismatch <- sum(PUBLISHED != obs)
cat(sprintf("\ncells compared: %d   mismatched: %d\n", length(PUBLISHED), mismatch))

# Counter-check: the .sav's own stored coding is the reverse for 7 of 8 items.
# If the table had preserved it, these reversed profiles would match instead.
rev_mismatch <- sum(PUBLISHED[, 5:1] != obs)
cat(sprintf("cells mismatched under the REVERSED (canonical .sav) reading: %d\n",
            rev_mismatch))

cat("Note: this pins every item against every other item (all 8 count profiles\n",
    "are distinct) and pins the full resp->option_text direction per item. It does\n",
    "NOT check the Swedish wording character by character against Table 2, and the\n",
    "shipped option_text is the study's English -- the Swedish anchors were never\n",
    "published.\n", sep = "")

cat(if (mismatch == 0 && rev_mismatch > 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
