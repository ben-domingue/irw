# verify_hoai_2026_student_engagement.R
#
# CLAIM UNDER TEST: each live item code SEk carries (a) the English statement the
# deposit's codebook.docx prints beside VARIABLE "SEk", and (b) the administered
# Vietnamese statement standing at the same position in the Student Engagement
# block ("Su gan ket hoc tap cua sinh vien") of Questionaire_VN.docx.
#
# Three falsifiable links, all printed below.
#
#  LINK 1 (live code -> source column of "Blended learning_data set.xlsx").
#    data/hoai_2026_blended_learning.py selects the columns matching ^SE[0-9]+$
#    and melts them with var_name="item", so the live code should reproduce the
#    named column exactly. Falsifiable because the four SE columns have
#    PAIRWISE-DISTINCT response-count vectors over the deposit's 580 rows: any
#    permutation of the block leaves at least one live item unable to reproduce
#    the column it is named after. Counts hard-coded from the deposited workbook
#    (Mendeley doi:10.17632/tdsspksw83 V1, sha256
#    cf8567e12b3c86a5b83398eb37409afa19209315f9bb52945a33433434ad39ae).
#
#  LINK 2 (source column -> English wording). codebook.docx, Table
#    "MEASUREMENT VARIABLES", rows VARIABLE=SE1..SE4, LABEL column, hard-coded
#    verbatim below and compared against the shipped item_text_translated.
#
#  LINK 3 (English wording -> administered Vietnamese). Both questionnaire files
#    print the same seven blocks in the same order (5-4-4-5-4-4-4); SE is block 6.
#    Beyond position, a distinctive-phrase crosswalk must select the SAME single
#    item on both sides for all four items, so no permutation survives.

suppressMessages(library(irw))
TABLE <- "hoai_2026_student_engagement"
ok <- TRUE

## ---- LINK 1 -----------------------------------------------------------------
SRC <- rbind(
  SE1 = c(2, 69, 181, 249, 79),
  SE2 = c(0, 56, 194, 262, 68),
  SE3 = c(1, 57, 206, 257, 59),
  SE4 = c(1, 52, 187, 272, 68)
)
colnames(SRC) <- as.character(1:5)
codes <- rownames(SRC)

pairs_same <- 0
for (a in 1:3) for (b in (a + 1):4)
  if (identical(unname(SRC[a, ]), unname(SRC[b, ]))) pairs_same <- pairs_same + 1
cat("deposit SE columns, counts of resp 1..5 (n=580 each):\n"); print(SRC)
cat(sprintf("identical pairs among the four source columns: %d (need 0)\n\n", pairs_same))
if (pairs_same != 0) ok <- FALSE

d <- irw::irw_fetch(TABLE)
obs <- table(factor(d$item, levels = codes), factor(d$resp, levels = 1:5))
obs <- matrix(as.integer(obs), nrow = 4, dimnames = dimnames(SRC))
cat("live per-item counts of resp 1..5:\n"); print(obs)

cat("\nitem  matches source column(s)   own column uniquely?\n")
for (it in codes) {
  hits <- codes[apply(SRC, 1, function(r)
    identical(as.integer(unname(r)), as.integer(unname(obs[it, ]))))]
  good <- identical(hits, it)
  if (!good) ok <- FALSE
  cat(sprintf("%-5s %-26s %s\n", it, paste(hits, collapse = ","),
              if (good) "yes" else "NO"))
}

## ---- shipped file -----------------------------------------------------------
here <- dirname(sub("^--file=", "",
                    grep("^--file=", commandArgs(FALSE), value = TRUE)[1]))
csv <- read.csv(file.path(here, paste0(TABLE, "__items.csv")),
                stringsAsFactors = FALSE, encoding = "UTF-8")

## ---- LINK 2 -----------------------------------------------------------------
CODEBOOK <- c(
  SE1 = "I frequently participate in learning activities in the course.",
  SE2 = "I actively allocate time to complete learning tasks.",
  SE3 = "I remain focused during most of the learning process.",
  SE4 = "I demonstrate responsibility and seriousness in my learning."
)
cat("\nshipped item_text_translated vs codebook.docx LABEL for the same VARIABLE:\n")
for (it in codes) {
  got <- unique(csv$item_text_translated[csv$item == it])
  same <- length(got) == 1 && identical(trimws(got), CODEBOOK[[it]])
  if (!same) ok <- FALSE
  cat(sprintf("%-5s %-9s %s\n", it, if (same) "match" else "MISMATCH", got[1]))
}

## ---- LINK 3 -----------------------------------------------------------------
VN <- c(
  SE1 = "Tôi thường xuyên tham gia các hoạt động học tập trong môn học.",
  SE2 = "Tôi chủ động dành thời gian để hoàn thành các nhiệm vụ học tập.",
  SE3 = "Tôi duy trì sự tập trung trong phần lớn thời gian học.",
  SE4 = "Tôi có thái độ nghiêm túc và trách nhiệm đối với việc học."
)
cat("\nshipped item_text vs Questionaire_VN.docx Student Engagement block, rows 1-4:\n")
for (it in codes) {
  got <- unique(csv$item_text[csv$item == it])
  same <- length(got) == 1 && identical(trimws(got), VN[[it]])
  if (!same) ok <- FALSE
  cat(sprintf("%-5s %s\n", it, if (same) "match" else "MISMATCH"))
}

PAIRS <- list(
  c("thường xuyên tham gia",      "frequently participate"),
  c("dành thời gian",                  "allocate time"),
  c("duy trì sự tập trung",       "remain focused"),
  c("nghiêm túc và trách nhiệm", "responsibility and seriousness")
)
cat("\nVN/EN content crosswalk (each phrase pair must select the same single item):\n")
for (p in PAIRS) {
  hv <- codes[grepl(p[1], VN, fixed = TRUE)]
  he <- codes[grepl(p[2], CODEBOOK, fixed = TRUE)]
  good <- length(hv) == 1 && length(he) == 1 && identical(hv, he)
  if (!good) ok <- FALSE
  cat(sprintf("  %-34s -> %-6s | %-32s -> %-6s  %s\n",
              p[1], paste(hv, collapse = ","), p[2], paste(he, collapse = ","),
              if (good) "unique, agree" else "AMBIGUOUS/DISAGREE"))
}

cat("\nWhat this does NOT establish: (i) the resp <-> option_text direction -- the\n",
    "five anchors come from the questionnaire's own printed scale line and the\n",
    "codebook's VALID CODING column, which agree with each other (1 = Hoan toan\n",
    "khong dong y = Strongly disagree ... 5 = Hoan toan dong y = Strongly agree)\n",
    "but cannot be tested against the data, because the deposit stores integers\n",
    "only and publishes no per-label counts; (ii) that the authors' own codebook\n",
    "LABEL assignment is itself correct -- a mislabel there would satisfy links 2\n",
    "and 3 alike.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
