# verify_mhscdc_fried_2020_ema.R
#
# CLAIM BEING VERIFIED
# --------------------
# Each live item code Q1..Q18 carries the wording that Measures_EMA.pdf and
# Codebook_EMA.xlsx (OSF deposit osf.io/mvdpe, folder "6. Measures") assign to
# the clean_ema.csv column of the same name.
#
# The chain has two links:
#   (a) codebook  : clean_EMA column "Qn"  ->  item wording   [STATED, twice:
#       the codebook's own clean_EMA/Item columns, and its "Ethica Items vs 2"
#       column which cross-references the administered survey PDF's numbering]
#   (b) processing: clean_ema.csv column "Qn" -> live item "Qn"   [TESTED HERE]
#
# Link (b) is what this script falsifies. data/mhscdc_fried_2020.r does
#   select(id, starts_with("Q"), date) |> pivot_longer(names_to = "item")
# so the live code is meant to be the raw column name verbatim. If any pair of
# columns had been permuted anywhere in that pipeline, the per-item x per-level
# response-frequency table would not reproduce -- and the 18 frequency vectors
# below are pairwise distinct, so the match is IDENTIFYING for every item, not
# just consistent with the mapping.
#
# SOURCE COUNTS: computed from clean_ema.csv (https://osf.io/download/t7g4f/),
# the exact file data/mhscdc_fried_2020.r reads. Hard-coded so this runs offline
# against the live table alone.

suppressMessages(library(irw))
TABLE <- "mhscdc_fried_2020_ema"

# rows = items Q1..Q18, cols = resp 1..5, counts of non-missing responses in clean_ema.csv
SRC <- rbind(
  Q1  = c(2280, 1136,  377,  129,   26),
  Q2  = c(2515,  950,  342,  106,   34),
  Q3  = c(1793, 1236,  606,  243,   69),
  Q4  = c(2175, 1101,  442,  179,   49),
  Q5  = c(2680,  743,  382,  119,   23),
  Q6  = c(3068,  598,  202,   59,   19),
  Q7  = c(1363, 1522,  742,  265,   53),
  Q8  = c(1156, 1503, 1002,  260,   24),
  Q9  = c(2655,  750,  384,  131,   25),
  Q10 = c(3051,  545,  214,   93,   42),
  Q11 = c( 698,  895, 1238,  666,  447),
  Q12 = c( 874, 1261, 1267,  385,  157),
  Q13 = c(1889,  654,  909,  321,  170),
  Q14 = c(1945,  693,  641,  307,  357),
  Q15 = c(2361,  600,  602,  239,  125),
  Q16 = c(1186, 1772,  772,  124,   79),
  Q17 = c(1726, 1639,  407,   97,   63),
  Q18 = c( 159,   53,  226,  457, 3036)
)
colnames(SRC) <- as.character(1:5)

TEXT <- c(
  Q1  = "I found it difficult to relax",
  Q2  = "I was very irritable",
  Q3  = "I was worrying too much about different things",
  Q4  = "I felt nervous, anxious or on edge",
  Q5  = "I felt that I had nothing to look forward",
  Q6  = "I couldn't seem to experience any positive feeling at all",
  Q7  = "I felt tired",
  Q8  = "I was hungry",
  Q9  = "I felt like I lack companionship, or that I am not close to people",
  Q10 = "I felt angry",
  Q11 = "I spent __ on meaningful, offline, social interaction",
  Q12 = "I spent __ using social media to kill/pass the time",
  Q13 = "I spent __ listening to music",
  Q14 = "I postponed working on a task for ___",
  Q15 = "I spent __ minutes outdoors",
  Q16 = "I spent __ occupied with the coronavirus (...)",
  Q17 = "I spent __ thinking about my own health, or that of my close friends (...)",
  Q18 = "I spent __ at home (including the home of parents/partner)"
)

d <- irw::irw_fetch(TABLE)
d$resp <- suppressWarnings(as.numeric(d$resp))
d <- d[!is.na(d$resp), ]
LIVE <- as.matrix(table(factor(d$item, levels = rownames(SRC)),
                        factor(d$resp, levels = 1:5)))

cat("Per-item x per-level response counts: clean_ema.csv (src) vs live IRW table\n\n")
cat(sprintf("%-4s %-46s %-28s %-28s %s\n", "item", "shipped item_text (truncated)",
            "src counts 1..5", "live counts 1..5", "ok"))
ok_all <- TRUE
for (it in rownames(SRC)) {
  s <- SRC[it, ]; l <- LIVE[it, ]
  ok <- all(s == l); ok_all <- ok_all && ok
  cat(sprintf("%-4s %-46s %-28s %-28s %s\n", it, substr(TEXT[[it]], 1, 46),
              paste(s, collapse = ","), paste(l, collapse = ","),
              if (ok) "OK" else "MISMATCH"))
}
cat(sprintf("\ncells compared: %d ; cells matching: %d\n",
            length(SRC), sum(SRC == LIVE)))

# The match only identifies items if no two source vectors coincide.
dup <- anyDuplicated(apply(SRC, 1, paste, collapse = ","))
cat(sprintf("distinct source frequency vectors: %d of %d (duplicate at index %d; 0 = none)\n",
            length(unique(apply(SRC, 1, paste, collapse = ","))), nrow(SRC), dup))

# Structural corroboration for the two response ladders: the codebook puts the
# 5-point Not-at-all..Extremely ladder on Q1-Q10 and the 0-min..>2-hours
# duration ladder on Q11-Q18. A one-position shift of that boundary would put a
# distress item on the duration ladder. Distress items floor hard at 1; the
# duration items do not.
floor_pct <- 100 * LIVE[, "1"] / rowSums(LIVE)
cat(sprintf("\nfloor%% at resp=1, ladder A block Q1-Q10 : min %.1f  max %.1f\n",
            min(floor_pct[1:10]), max(floor_pct[1:10])))
cat(sprintf("floor%% at resp=1, ladder B block Q11-Q18: min %.1f  max %.1f\n",
            min(floor_pct[11:18]), max(floor_pct[11:18])))
cat(sprintf("Q18 ('I spent __ at home') at resp=5 ('> 2 hours'): %.1f%% -- highest ceiling in the table (%s)\n",
            100 * LIVE["Q18", "5"] / sum(LIVE["Q18", ]),
            names(which.max(LIVE[, "5"] / rowSums(LIVE)))))

cat("\nWhat this does NOT establish: it verifies that live Qn is clean_ema.csv column\n",
    "Qn, cell for cell. It does not independently re-derive link (a) -- that the\n",
    "codebook's clean_EMA/Item pairing is itself correct -- which rests on the\n",
    "codebook stating it per item and the survey PDF's numbering agreeing with it.\n", sep = "")

cat(if (ok_all && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
