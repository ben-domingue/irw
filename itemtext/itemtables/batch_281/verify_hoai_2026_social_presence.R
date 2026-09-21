# verify_hoai_2026_social_presence.R
#
# CLAIM UNDER TEST: each live item code SPk carries (a) the English statement the
# deposit's codebook.docx prints beside VARIABLE "SPk", and (b) the Vietnamese
# statement standing at the same position in the Social Presence block of the
# administered questionnaire.
#
# Three falsifiable links, all printed below:
#
#  LINK 1 (live code -> source column of Blended learning_data set.xlsx).
#    data/hoai_2026_blended_learning.py selects columns matching ^SP[0-9]+$ and
#    melts them with var_name="item", so the live code should reproduce the named
#    column exactly. This is falsifiable because the four SP columns have
#    PAIRWISE-DISTINCT response-count vectors over the deposit's 580 rows: a
#    permutation of the block would leave at least one live item unable to
#    reproduce the column it is named after. Counts hard-coded from the deposited
#    workbook (Mendeley doi:10.17632/tdsspksw83, V1, "Blended learning_data
#    set.xlsx", 580 rows), per the template's rule 4.
#
#  LINK 2 (source column -> English wording). codebook.docx, Table "MEASUREMENT
#    VARIABLES", rows VARIABLE=SP1..SP4, LABEL column, hard-coded verbatim below;
#    compared against the shipped item_text_translated.
#
#  LINK 3 (English wording -> administered Vietnamese). The two questionnaire
#    files print the same seven blocks in the same order (5-4-4-5-4-4-4) and SP is
#    block 2. Beyond position, a content crosswalk pins each Vietnamese stem to
#    exactly one English statement: a distinctive phrase pair must select the SAME
#    single item on both sides, for all four items, so no permutation survives.

suppressMessages(library(irw))
TABLE <- "hoai_2026_social_presence"
ok <- TRUE

## ---- LINK 1 -----------------------------------------------------------------
SRC <- rbind(
  SP1 = c(0, 67, 190, 257, 66),
  SP2 = c(0, 59, 196, 267, 58),
  SP3 = c(0, 59, 197, 270, 54),
  SP4 = c(1, 60, 174, 282, 63)
)
colnames(SRC) <- as.character(1:5)
codes <- rownames(SRC)

pairs_same <- 0
for (a in 1:3) for (b in (a + 1):4)
  if (identical(unname(SRC[a, ]), unname(SRC[b, ]))) pairs_same <- pairs_same + 1
cat("deposit SP columns, counts of resp 1..5 (n=580 each):\n"); print(SRC)
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
  SP1 = "I feel comfortable sharing my ideas during learning activities.",
  SP2 = "The course creates opportunities for me to interact and collaborate with other students.",
  SP3 = "I feel a sense of connection with other students in the course.",
  SP4 = "Learning activities help me feel closer to my classmates."
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
  SP1 = "Tôi cảm thấy thoải mái khi chia sẻ ý kiến trong các buổi học.",
  SP2 = "Việc học tạo điều kiện để tôi trao đổi và làm việc nhóm với các bạn.",
  SP3 = "Tôi có cảm giác gắn kết với các bạn khi cùng tham gia môn học.",
  SP4 = "Các hoạt động học giúp tôi cảm thấy gần gũi hơn với bạn học."
)
cat("\nshipped item_text vs Questionaire_VN.docx Social Presence block, rows 1-4:\n")
for (it in codes) {
  got <- unique(csv$item_text[csv$item == it])
  same <- length(got) == 1 && identical(trimws(got), VN[[it]])
  if (!same) ok <- FALSE
  cat(sprintf("%-5s %s\n", it, if (same) "match" else "MISMATCH"))
}

# distinctive phrase pairs: each must select exactly one item on BOTH sides,
# and the same one.
PAIRS <- list(
  c("chia sẻ ý kiến", "sharing my ideas"),
  c("làm việc nhóm",   "collaborate with other students"),
  c("gắn kết",             "sense of connection"),
  c("gần gũi",             "closer to my classmates")
)
cat("\nVN/EN content crosswalk (each phrase pair must select the same single item):\n")
for (p in PAIRS) {
  hv <- codes[grepl(p[1], VN, fixed = TRUE)]
  he <- codes[grepl(p[2], CODEBOOK, fixed = TRUE)]
  good <- length(hv) == 1 && length(he) == 1 && identical(hv, he)
  if (!good) ok <- FALSE
  cat(sprintf("  %-22s -> %-14s | %-32s -> %-14s  %s\n",
              p[1], paste(hv, collapse = ","), p[2], paste(he, collapse = ","),
              if (good) "unique, agree" else "AMBIGUOUS/DISAGREE"))
}

cat("\nWhat this does NOT establish: the resp<->option_text direction. The five\n",
    "anchors come from the questionnaire's own printed scale line and the\n",
    "codebook's VALID CODING column (1 = Hoàn toàn không đồng ý ... 5 = Hoàn\n",
    "toàn đồng ý), which agree with each other but cannot be tested against the\n",
    "data: the deposit stores integers only and publishes no label counts.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
