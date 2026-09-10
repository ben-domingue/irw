# verify_quarter_life_crisis__iuc.R
#
# CLAIM UNDER TEST: item codes iuc_1..iuc_12 correspond, in order, to columns
# 14..25 (1-based) of the "Data Cleaning" sheet of the Figshare deposit's
# "Research Data.xlsx" (10.6084/m9.figshare.26130403.v1), whose header row 2
# carries the literal IUS-12 wording shipped as item_text
# ("1. Unforeseen events upset me greatly." .. "12. I must get away from all
# uncertain situations.").
#
# The processing script data/quarter_life_crisis.py assigns iuc_1..iuc_12 to the
# pandas column labels "INTOLERANCE OF UNCERTAINTY", "Unnamed: 14" .. "Unnamed: 24",
# i.e. POSITIONALLY -- the codes keep no trace of the source wording, so this is a
# positional derivation and needs a header diff, not an assumed exemption.
#
# FALSIFIABLE PREDICTION: the per-item response-frequency table of the live IRW
# table must reproduce, cell for cell, the frequency table of those source columns
# over the 90 complete rows of the "Data Cleaning" sheet. All 12 source columns
# have distinct frequency signatures, so ANY permutation of the 12 item codes --
# including a swap of two adjacent items -- breaks at least two rows of this
# comparison.

suppressMessages(library(irw))

TABLE <- "quarter_life_crisis__iuc"

# Counts of resp values 1..5 in "Data Cleaning" columns 14..25 (1-based), over the
# 90 rows with complete numeric data on all 12 columns. Hard-coded from the
# Figshare deposit so this script needs no network access to the source.
SRC <- matrix(c(
   8, 12, 36, 32,  2,   # col 14  -> iuc_1
   5, 14, 26, 33, 12,   # col 15  -> iuc_2
  10, 22, 35, 19,  4,   # col 16  -> iuc_3
  10, 22, 22, 24, 12,   # col 17  -> iuc_4
   4, 25, 23, 29,  9,   # col 18  -> iuc_5
  17, 26, 30, 15,  2,   # col 19  -> iuc_6
   9, 20, 33, 24,  4,   # col 20  -> iuc_7
   9, 20, 18, 27, 16,   # col 21  -> iuc_8
  19, 28, 31, 10,  2,   # col 22  -> iuc_9
  14, 30, 20, 15, 11,   # col 23  -> iuc_10
   3, 13, 26, 42,  6,   # col 24  -> iuc_11
  15, 20, 34, 16,  5    # col 25  -> iuc_12
), nrow = 12, byrow = TRUE,
   dimnames = list(paste0("iuc_", 1:12), 1:5))

d <- irw::irw_fetch(TABLE)
obs <- table(factor(d$item, levels = paste0("iuc_", 1:12)),
             factor(d$resp, levels = 1:5))
obs <- matrix(as.integer(obs), nrow = 12, dimnames = dimnames(SRC))

cat(sprintf("%-8s %-22s %-22s %s\n", "item", "source cols 14..25", "live IRW", "match"))
ok <- TRUE
for (i in 1:12) {
  same <- all(SRC[i, ] == obs[i, ])
  ok <- ok && same
  cat(sprintf("%-8s %-22s %-22s %s\n",
              rownames(SRC)[i],
              paste(SRC[i, ], collapse = "/"),
              paste(obs[i, ], collapse = "/"),
              if (same) "yes" else "NO"))
}

nsig <- length(unique(apply(SRC, 1, paste, collapse = "/")))
cat(sprintf("\ncells matching: %d of 60\n", sum(SRC == obs)))
cat(sprintf("distinct source signatures: %d of 12 (a permutation of any two would show)\n", nsig))

cat("Note: this pins item_text<->item for all 12 items. It establishes NOTHING about\n",
    "option_text<->resp -- no response-option labels were shipped, because neither the\n",
    "workbook nor the deposit records the anchor wording.\n", sep = "")

cat(if (ok && nsig == 12) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
