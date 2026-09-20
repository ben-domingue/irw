# verify_hoai_2026_learning_experience.R
#
# CLAIM UNDER TEST: each live item code LEk carries the wording the deposit's
# codebook.docx assigns to the source column of the same name.
#
# Two links:
#   (1) codebook.docx, Table "MEASUREMENT VARIABLES": VARIABLE "LEk" -> LABEL
#       (the English item sentence). Questionaire_VN.docx and Questionaire_EN.docx
#       print the same four LE statements, in the same order, in their
#       "Trai nghiem hoc tap" / "Learning Experience" block, which is what pins
#       the Vietnamese shipped in item_text to that English.
#   (2) live item "LEk" -> source column "LEk" of "Blended learning_data set.xlsx".
#
# Link (2) is what this script falsifies, and it is falsifiable because the four
# LE columns have DISTINCT response-count vectors over 580 respondents: had the
# processing script permuted the LE block, at least one live item's counts would
# fail to reproduce the column it is named after. Counts hard-coded from the
# deposited workbook (Mendeley doi:10.17632/tdsspksw83, V1, CC BY 4.0,
# "Blended learning_data set.xlsx", sha256
# cf8567e12b3c86a5b83398eb37409afa19209315f9bb52945a33433434ad39ae), per
# template rule 4.

suppressMessages(library(irw))

TABLE <- "hoai_2026_learning_experience"

# Counts of responses 1..5 per LE column in the deposited .xlsx (n=580 each).
SRC <- rbind(
  LE1 = c(4, 54, 205, 260, 57),
  LE2 = c(1, 50, 197, 270, 62),
  LE3 = c(3, 49, 213, 263, 52),
  LE4 = c(2, 56, 197, 270, 55)
)
colnames(SRC) <- as.character(1:5)

# codebook.docx LABEL column, verbatim, for the LE block.
CODEBOOK <- c(
  LE1 = "Overall, I am satisfied with my learning experience in this course.",
  LE2 = "The combination of face-to-face and online learning helps me learn more effectively.",
  LE3 = "I can manage my learning tasks effectively.",
  LE4 = "What I learned in this course is meaningful and valuable to me."
)

# --- source columns must be mutually distinguishable at all -------------------
pairs_same <- 0
for (a in 1:3) for (b in (a + 1):4)
  if (identical(unname(SRC[a, ]), unname(SRC[b, ]))) pairs_same <- pairs_same + 1
cat("deposit LE columns, counts of resp 1..5 (n=580 each):\n")
print(SRC)
cat(sprintf("identical pairs among the four source columns: %d (need 0)\n\n", pairs_same))

# --- live counts --------------------------------------------------------------
d <- irw::irw_fetch(TABLE)
obs <- table(factor(d$item, levels = rownames(SRC)),
             factor(d$resp, levels = 1:5))
obs <- matrix(as.integer(obs), nrow = 4, dimnames = dimnames(SRC))
cat("live per-item counts of resp 1..5:\n")
print(obs)

# --- for each live item, which source column does it match exactly? -----------
cat("\nitem  matches source column(s)  own-column exact?\n")
ok <- TRUE
for (it in rownames(SRC)) {
  hits <- rownames(SRC)[apply(SRC, 1, function(r)
    identical(as.integer(unname(r)), as.integer(unname(obs[it, ]))))]
  good <- identical(hits, it)
  if (!good) ok <- FALSE
  cat(sprintf("%-5s %-26s %s\n", it, paste(hits, collapse = ","),
              if (good) "yes, uniquely" else "NO"))
}

# --- shipped English must be the codebook label for that same code ------------
csv <- read.csv(file.path(dirname(sub("^--file=", "",
                 grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                 paste0(TABLE, "__items.csv")), stringsAsFactors = FALSE)
cat("\nshipped item_text_translated vs codebook.docx LABEL:\n")
for (it in names(CODEBOOK)) {
  got <- unique(csv$item_text_translated[csv$item == it])
  same <- length(got) == 1 && identical(trimws(got), CODEBOOK[[it]])
  if (!same) ok <- FALSE
  cat(sprintf("%-5s %s | %s\n", it, if (same) "match" else "MISMATCH", got[1]))
}

# --- VN <-> EN crosswalk: each pair shares a token unique to the deposit -------
# Each of the four LE statements carries a phrase that occurs EXACTLY ONCE in the
# whole Vietnamese questionnaire table and whose English counterpart occurs
# exactly once in the whole English questionnaire table and once in codebook.docx
# (counted 2026-09-20 over both docx files, all 30 statement rows). So the
# VN->EN pairing is one-to-one and no permutation of the four survives it.
CROSSWALK <- rbind(
  c("LE1", "h\u00e0i l\u00f2ng v\u1edbi tr\u1ea3i nghi\u1ec7m h\u1ecdc t\u1eadp", "satisfied with my learning experience"),
  c("LE2", "S\u1ef1 k\u1ebft h\u1ee3p gi\u1eefa h\u1ecdc tr\u00ean l\u1edbp v\u00e0 tr\u1ef1c tuy\u1ebfn", "combination of face-to-face and online"),
  c("LE3", "t\u1ef1 qu\u1ea3n l\u00fd", "manage my learning tasks"),
  c("LE4", "gi\u00e1 tr\u1ecb thi\u1ebft th\u1ef1c", "meaningful and valuable")
)
cat("\nVN<->EN crosswalk on the shipped file (each token must hit its own row only):\n")
for (k in seq_len(nrow(CROSSWALK))) {
  it <- CROSSWALK[k, 1]; vn <- CROSSWALK[k, 2]; en <- CROSSWALK[k, 3]
  vn_hits <- unique(csv$item[grepl(vn, csv$item_text, fixed = TRUE)])
  en_hits <- unique(csv$item[grepl(en, csv$item_text_translated, fixed = TRUE)])
  good <- identical(vn_hits, it) && identical(en_hits, it)
  if (!good) ok <- FALSE
  cat(sprintf("%-5s VN token -> {%s}   EN token -> {%s}   %s\n", it,
              paste(vn_hits, collapse = ","), paste(en_hits, collapse = ","),
              if (good) "one-to-one" else "NOT one-to-one"))
}

cat("\nWhat this does NOT establish: (a) the resp<->option_text direction. That rests\n",
    "on the codebook's stated VALID CODING (1 = Strongly disagree ... 5 = Strongly\n",
    "agree) and the questionnaire's own anchor line, and cannot be tested against the\n",
    "data, since the deposit stores integers and publishes no per-label counts.\n",
    "(b) Nothing here separates the items on MEANS: LE1 and LE3 tie at 3.5379 exactly\n",
    "and LE2/LE4 sit 0.038 apart, which is why the route above compares the full\n",
    "five-cell count vector rather than a mean.\n", sep = "")

cat(if (ok && pairs_same == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
