# verify_hoai_2026_academic_achievement.R
#
# CLAIM UNDER TEST: each live item code AAk carries the wording the deposit's
# codebook.docx assigns to the source column of the same name.
#
# The chain has two links:
#   (1) codebook.docx: VARIABLE "AAk" -> LABEL (the English item sentence), and
#       Questionaire_VN/EN.docx print the same four AA statements in the same
#       order, so the Vietnamese shipped in item_text is pinned to the English.
#   (2) live item "AAk" -> source column "AAk" of Blended learning_data set.xlsx.
#
# Link (2) is what this script falsifies, and it is falsifiable because the four
# AA columns have DISTINCT response-count vectors over 580 respondents: if the
# processing script had permuted the AA block, at least one live item's counts
# would fail to reproduce the column it is named after. The counts below are
# hard-coded from the deposited workbook (Mendeley doi:10.17632/tdsspksw83,
# "Blended learning_data set.xlsx", 580 rows), per the template's rule 4.

suppressMessages(library(irw))

TABLE <- "hoai_2026_academic_achievement"

# Counts of responses 1..5 per AA column in the deposited .xlsx.
SRC <- rbind(
  AA1 = c(3, 58, 185, 272, 62),
  AA2 = c(1, 63, 187, 268, 61),
  AA3 = c(1, 59, 204, 237, 79),
  AA4 = c(1, 60, 196, 256, 67)
)
colnames(SRC) <- as.character(1:5)

# codebook.docx LABEL column, verbatim, for the AA block.
CODEBOOK <- c(
  AA1 = "I have achieved the learning outcomes required by the course.",
  AA2 = "My academic performance has improved compared to before.",
  AA3 = "I am satisfied with my academic performance.",
  AA4 = "I feel that I have made progress after completing the course."
)

# --- source columns must be mutually distinguishable at all -------------------
pairs_same <- 0
for (a in 1:3) for (b in (a + 1):4)
  if (identical(unname(SRC[a, ]), unname(SRC[b, ]))) pairs_same <- pairs_same + 1
cat("deposit AA columns, counts of resp 1..5 (n=580 each):\n")
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
  hits <- rownames(SRC)[apply(SRC, 1, function(r) identical(as.integer(unname(r)), as.integer(unname(obs[it, ]))))]
  good <- identical(hits, it)
  if (!good) ok <- FALSE
  cat(sprintf("%-5s %-26s %s\n", it, paste(hits, collapse = ","),
              if (good) "yes, uniquely" else "NO"))
}

# --- shipped English must be the codebook label for that same code ------------
csv <- read.csv(file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                          paste0(TABLE, "__items.csv")), stringsAsFactors = FALSE)
cat("\nshipped item_text_translated vs codebook.docx LABEL:\n")
for (it in names(CODEBOOK)) {
  got <- unique(csv$item_text_translated[csv$item == it])
  same <- length(got) == 1 && identical(trimws(got), CODEBOOK[[it]])
  if (!same) ok <- FALSE
  cat(sprintf("%-5s %s | %s\n", it, if (same) "match" else "MISMATCH", got[1]))
}

cat("\nWhat this does NOT establish: the Vietnamese in item_text is tied to the\n",
    "English by the position of each statement inside the AA block of the two\n",
    "questionnaire files, corroborated sentence by sentence (each Vietnamese\n",
    "statement is a one-to-one semantic match for exactly one English one), not\n",
    "by any code printed beside the Vietnamese.\n", sep = "")

cat(if (ok && pairs_same == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
