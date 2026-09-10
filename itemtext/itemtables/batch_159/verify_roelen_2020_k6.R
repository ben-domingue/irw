# verify_roelen_2020_k6.R -- Step 5b, route 9 (response-frequency matching).
#
# CLAIM UNDER TEST. The IRW item codes q_401..q_406 are the *source column names*
# of the study's Stata deposit (S1 Dataset, PLOS 10.1371/journal.pone.0243457.s002),
# whose variable labels carry the K6 wording shipped in the __items.csv, and the
# resp coding 0..4 is the Stata value labels remapped by data/roelen_2020_haiti_battery.py
# as None (0 day)=0, A little (1-9 days)=1, Some (10-19 days)=2, Most (20-29 days)=3,
# All (30 days)=4 -- i.e. the DIRECTION IS REVERSED relative to the Stata numeric codes
# (1='All (30 days)' .. 5='None (0 day)').
#
# WHAT WOULD BREAK IT. The full 6 x 5 item-by-level count matrix from the deposit is
# compared cell for cell against the live table. The six count vectors are pairwise
# distinct, so any permutation of item codes across source columns, and any permutation
# or flip of the response levels, changes at least one cell. This is what a set-level
# gate (validate_items.R) cannot see.
#
# WHAT IT DOES NOT ESTABLISH. It ties each live item code to a source COLUMN; the tie
# from that column to its WORDS is the .dta's own variable labels (mapping_basis
# data_labels), not anything computed here. It also says nothing about the two labels
# Stata truncated at its 80-character cap (q_404, q_405), whose tails were completed
# from the paper's Table 3.
#
# Hard-coded counts below were read from the deposit with pyreadstat (N = 1381, no
# missing K6 data -- the paper states "There was no missing data"), so the script needs
# only the live IRW fetch. roelen_2020_k6 is ~8k rows; the export is negligible.

suppressMessages(library(irw))

TABLE <- "roelen_2020_k6"
LEVELS <- 0:4
OPT <- c("None (0 day)", "A little (1-9 days)", "Some (10-19 days)",
         "Most (20-29 days)", "All (30 days)")

# Deposit counts, rows = q_401..q_406, cols = IRW resp 0..4.
DEPOSIT <- matrix(c(
   87, 437, 542, 266,  49,   # q_401 nervous
   27, 316, 623, 318,  97,   # q_402 hopeless
  118, 394, 561, 281,  27,   # q_403 restless or fidgety
   44, 395, 606, 290,  46,   # q_404 so depressed that nothing could cheer you up
  180, 463, 458, 215,  65,   # q_405 everything was an effort
  141, 379, 590, 244,  27),  # q_406 worthless
  nrow = 6, byrow = TRUE,
  dimnames = list(paste0("q_", 401:406), as.character(LEVELS)))

d <- irw::irw_fetch(TABLE)
LIVE <- table(factor(d$item, levels = rownames(DEPOSIT)),
              factor(d$resp, levels = LEVELS))
LIVE <- matrix(as.integer(LIVE), nrow = 6,
               dimnames = dimnames(DEPOSIT))

cat("Deposit (S1 Dataset .dta) vs live IRW, counts per item x resp level\n")
cat(sprintf("%-8s %22s %22s %22s %22s %22s\n", "item",
            paste0("0=", OPT[1]), paste0("1=", OPT[2]), paste0("2=", OPT[3]),
            paste0("3=", OPT[4]), paste0("4=", OPT[5])))
for (i in rownames(DEPOSIT))
    cat(sprintf("%-8s %22s %22s %22s %22s %22s\n", i,
        paste0(DEPOSIT[i, 1], "/", LIVE[i, 1]), paste0(DEPOSIT[i, 2], "/", LIVE[i, 2]),
        paste0(DEPOSIT[i, 3], "/", LIVE[i, 3]), paste0(DEPOSIT[i, 4], "/", LIVE[i, 4]),
        paste0(DEPOSIT[i, 5], "/", LIVE[i, 5])))

mismatch <- sum(DEPOSIT != LIVE)
cat(sprintf("\ncells compared: %d   mismatched: %d\n", length(DEPOSIT), mismatch))

# Are the six deposit count vectors actually distinct? If they were not, a
# permutation could survive this check and the route would prove nothing.
dupes <- sum(duplicated(apply(DEPOSIT, 1, paste, collapse = "|")))
cat(sprintf("duplicate deposit count vectors (0 means every item is separable): %d\n", dupes))

# The reversed reading, as a negative control: had the script kept Stata's own
# numeric direction, level 0 would carry the 'All (30 days)' counts.
flip <- sum(DEPOSIT[, 5:1] != LIVE)
cat(sprintf("mismatched cells under the FLIPPED coding (should be large): %d\n", flip))

cat("\nNote: this pins live item code -> source column and resp level -> value label.\n")
cat("It does not itself tie a source column to its wording; that is the .dta's own\n")
cat("variable labels. The q_404/q_405 label tails come from the paper's Table 3.\n\n")

cat(if (mismatch == 0 && dupes == 0 && flip > 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
