# verify_avilatamayo_2022_skills_dev.R -- Step 5b, re-runnable evidence.
#
# CLAIM UNDER TEST (mapping_basis = paper_order)
#   Live item codes Skills_Dev_3.2_1 .. Skills_Dev_3.7_1 carry, in that order, the
#   six rows of the "Desarrollo de habilidades / Skills development" block of the
#   PLOS S1 Appendix (10.1371/journal.pone.0266711.s002), and live resp 1..7 carry
#   the 7-point anchors "totalmente en desacuerdo" .. "totalmente de acuerdo".
#
# TWO LINKS, CHECKED SEPARATELY
#   (A) live code + live resp  <->  S1 Dataset (.sav) column + its numeric value code.
#       Falsifiable: the full item x resp-level contingency table of the live data
#       must reproduce the .sav's own cell counts, all 42 cells. A permuted item
#       code or a flipped/permuted resp coding breaks it immediately.
#       The .sav counts below are hard-coded from the deposit (a fixed file);
#       the live side is fetched. The table is 2,594 rows, so the fetch is ~30KB.
#   (B) .sav column number  <->  S1 Appendix row.
#       Structural, not statistical. Checked here as: the appendix reproduces
#       exactly the 45 retained items in seven blocks whose sizes equal the .sav's
#       per-prefix item-column counts (7/5/6/6/7/6/8), and the block-final
#       "En general / Overall" summary item -- last row of every one of the seven
#       blocks -- lands on the highest code in each block, which for this table is
#       Skills_Dev_3.7_1. Code contiguity 3.2..3.7 identifies the single item the
#       paper says was dropped from skill development as position 3.1.
#
# WHAT THIS DOES NOT ESTABLISH
#   Nothing here separates Skills_Dev_3.2_1 .. 3.6_1 from one another. A permutation
#   of the appendix's first five skills rows relative to administration order would
#   be invisible: the paper publishes no per-item statistics (Table 1 is composite
#   level only), the six item means span only 4.25-4.66 and item-rest correlations
#   only 0.72-0.83, and the .sav's variable labels are bare position placeholders
#   ("Skill development 2" .. "Skill development 7"), not wording. Hence PARTIAL.

suppressMessages(library(irw))

TABLE <- "avilatamayo_2022_skills_dev"
ITEMS <- paste0("Skills_Dev_3.", 2:7, "_1")

# (A) .sav side: counts of value codes 1..7 per item column, S1 Dataset
#     (10.1371/journal.pone.0266711.s001), non-integer imputed cells dropped
#     exactly as data/avilatamayo_2022_csr.py drops them.
SAV <- rbind(
  "Skills_Dev_3.2_1" = c(42, 47, 55, 69,  92,  91, 36),
  "Skills_Dev_3.3_1" = c(26, 44, 48, 71,  84, 117, 42),
  "Skills_Dev_3.4_1" = c(23, 46, 39, 68,  87, 111, 59),
  "Skills_Dev_3.5_1" = c(21, 38, 34, 91, 117,  96, 36),
  "Skills_Dev_3.6_1" = c(35, 49, 38, 79, 110,  85, 36),
  "Skills_Dev_3.7_1" = c(22, 46, 58, 73,  84,  87, 62))
colnames(SAV) <- 1:7

# (B) block sizes, appendix vs .sav item columns, all seven ICSR scales.
APPENDIX_BLOCKS <- c("Employment stability" = 7, "Working environment" = 5,
                     "Skills development" = 6, "Workforce diversity" = 6,
                     "Work-life balance" = 7, "Tangible employee involvement" = 6,
                     "Empowerment" = 8)
SAV_BLOCKS      <- c("Empl_Stab" = 7, "Work_Envir" = 5, "Skills_Dev" = 6,
                     "Workf_Div" = 6, "Work_Life" = 7, "Tang_Emplo" = 6,
                     "Empow" = 8)

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = ITEMS), factor(d$resp, levels = 1:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(SAV))

cat("(A) item x resp cell counts: live IRW vs S1 Dataset .sav\n\n")
cat(sprintf("%-18s %s\n", "item", paste(sprintf("%5s", c(1:7, "n")), collapse = "")))
for (i in ITEMS) {
  cat(sprintf("%-18s %s   live\n", i, paste(sprintf("%5d", live[i, ]), collapse = "")))
  cat(sprintf("%-18s %s   .sav\n", "",  paste(sprintf("%5d", SAV[i, ]),  collapse = "")))
}
bad <- sum(live != SAV)
cat(sprintf("\ncells compared: %d   mismatched: %d\n", length(SAV), bad))

cat("\n(B) block sizes: S1 Appendix rows vs .sav item columns\n\n")
for (k in seq_along(APPENDIX_BLOCKS))
  cat(sprintf("  %-32s appendix %d   .sav %-12s %d\n",
              names(APPENDIX_BLOCKS)[k], APPENDIX_BLOCKS[k],
              names(SAV_BLOCKS)[k], SAV_BLOCKS[k]))
cat(sprintf("\n  appendix items total: %d (paper: 48 administered, 3 dropped -> 45 retained)\n",
            sum(APPENDIX_BLOCKS)))
blocks_ok <- all(APPENDIX_BLOCKS == SAV_BLOCKS) && sum(APPENDIX_BLOCKS) == 45

# anchor: the shipped item_text for the highest code must be the block-final
# "En general" / "Overall" summary item.
f <- file.path(dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1])),
               paste0(TABLE, "__items.csv"))
if (!file.exists(f)) f <- file.path("itemtables", "batch_274", paste0(TABLE, "__items.csv"))
it <- read.csv(f, colClasses = "character")
last_es <- unique(it$item_text[it$item == "Skills_Dev_3.7_1"])
last_en <- unique(it$item_text_translated[it$item == "Skills_Dev_3.7_1"])
cat(sprintf("\n  anchor, highest code Skills_Dev_3.7_1:\n    %s\n    %s\n", last_es, last_en))
anchor_ok <- length(last_es) == 1 && grepl("^En general,", last_es) &&
             length(last_en) == 1 && grepl("^Overall,", last_en)
cat(sprintf("  starts with 'En general,' / 'Overall,': %s\n", anchor_ok))

cat("\nNot established: no evidence here separates Skills_Dev_3.2_1..3.6_1 from one\n",
    "another; their order rests on the appendix listing the retained items in\n",
    "administration order. Status recorded as PARTIAL, not VERIFIED.\n", sep = "")

cat(if (bad == 0 && blocks_ok && anchor_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
