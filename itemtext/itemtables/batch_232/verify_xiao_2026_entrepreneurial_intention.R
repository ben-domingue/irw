# verify_xiao_2026_entrepreneurial_intention.R
#
# CLAIM UNDER TEST: each live `item` code is the same-named column of the study's
# S2 File "Raw Data" sheet, whose wording is given row-by-row in that file's
# "Variable Codebook" sheet (and repeated verbatim in S1 Table). If any two
# items' texts were swapped, the code<->column tie below would break.
#
# ROUTE: response-frequency fingerprinting (Step 5b route 9 applied to the item
# axis). For each item the vector of counts at resp 1..5 is compared between the
# published raw spreadsheet and the live IRW table. All 40 raw fingerprints are
# mutually DISTINCT, so an exact match of all 40 is an identifying assignment,
# not merely a consistent one: any permutation of two item codes would change at
# least two vectors.
#
# WHAT THIS DOES NOT ESTABLISH: the codebook names the four entrepreneurial
# intention items EI1..EI4 while the raw file (and therefore IRW) calls them
# In1..In4 -- the codebook says so explicitly ("not labelled as EI in uploaded
# raw dataset"). This check pins In1..In4 to raw columns In1..In4, but the
# EI1->In1 ... EI4->In4 correspondence rests on the codebook's listing order,
# which no count can test. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "xiao_2026_entrepreneurial_intention"

# Per-item counts at resp = 1,2,3,4,5, read from the "Raw Data" sheet of
# S2 File (https://doi.org/10.1371/journal.pone.0352807.s002), N = 1389.
RAW <- list(
  Inn1 = c(4,3,141,617,624),     Inn2 = c(2,4,56,469,858),
  Inn3 = c(2,8,174,569,636),     Inn4 = c(2,24,298,631,434),
  Pro1 = c(3,41,498,557,290),    Pro2 = c(14,204,655,334,182),
  Pro3 = c(4,70,425,581,309),    Pro4 = c(9,113,552,488,227),
  Pro5 = c(16,145,520,463,245),
  PPS1 = c(10,28,465,549,337),   PPS2 = c(14,46,479,521,329),
  PPS3 = c(9,28,494,521,337),    PPS4 = c(11,12,383,615,368),
  PPS5 = c(6,18,455,564,346),    PPS6 = c(7,20,477,545,340),
  PPS7 = c(7,20,354,621,387),
  PAF1 = c(47,121,450,513,258),  PAF2 = c(47,142,432,545,223),
  PAF3 = c(20,67,562,506,234),   PAF4 = c(33,90,595,434,237),
  PAF5 = c(66,158,666,318,181),  PAF6 = c(26,64,621,462,216),
  PAF7 = c(83,159,739,253,155),  PAF8 = c(63,136,756,283,151),
  PEE1 = c(115,250,306,512,206), PEE2 = c(79,145,525,463,177),
  PEE3 = c(119,321,482,329,138), PEE4 = c(179,422,411,258,119),
  PEE5 = c(52,121,449,567,200),  PEE6 = c(33,60,435,616,245),
  PEE7 = c(43,87,482,545,232),   PEE8 = c(43,82,463,570,231),
  PEE9 = c(85,189,341,568,206),  PEE10 = c(115,288,390,409,187),
  RM1  = c(0,4,202,730,453),     RM2  = c(0,10,300,690,389),
  In1  = c(48,135,417,542,247),  In2  = c(31,69,387,615,287),
  In3  = c(91,222,556,332,188),  In4  = c(57,86,481,507,258)
)

# Identifiability: are the published fingerprints mutually distinct?
keys <- vapply(RAW, function(v) paste(v, collapse = "-"), "")
cat(sprintf("distinct raw fingerprints: %d of %d\n", length(unique(keys)), length(keys)))
identifiable <- length(unique(keys)) == length(keys)

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

cat(sprintf("\n%-7s %-22s %-22s %s\n", "item", "raw (1|2|3|4|5)", "live (1|2|3|4|5)", "ok"))
bad <- character(0)
for (it in names(RAW)) {
  v <- d$resp[d$item == it]
  live <- as.integer(table(factor(v, levels = 1:5)))
  ok <- identical(live, as.integer(RAW[[it]]))
  if (!ok) bad <- c(bad, it)
  cat(sprintf("%-7s %-22s %-22s %s\n", it,
              paste(RAW[[it]], collapse = "|"),
              paste(live,      collapse = "|"),
              if (ok) "yes" else "NO"))
}

cat(sprintf("\nmatched %d of %d items exactly; mismatches: %s\n",
            length(RAW) - length(bad), length(RAW),
            if (length(bad)) paste(bad, collapse = ", ") else "none"))
cat("Note: this pins every live item code to its same-named source column, and\n",
    "through the Variable Codebook to its wording. It does NOT test the\n",
    "codebook's EI1..EI4 -> In1..In4 renaming, which rests on listing order.\n", sep = "")

cat(if (identifiable && length(bad) == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
