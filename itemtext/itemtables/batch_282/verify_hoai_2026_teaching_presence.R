# verify_hoai_2026_teaching_presence.R
#
# CLAIM UNDER TEST: each live item code TPk carries (a) the English statement the
# deposit's codebook.docx prints beside VARIABLE "TPk", and (b) the Vietnamese
# statement standing at the same position in the Teaching Presence block of the
# administered questionnaire.
#
# Three falsifiable links, all printed below:
#
#  LINK 1 (live code -> source column of "Blended learning_data set.xlsx").
#    data/hoai_2026_blended_learning.py selects the columns matching ^TP[0-9]+$
#    and melts them with var_name="item", so the live code should reproduce the
#    named column exactly. This is falsifiable because the five TP columns have
#    PAIRWISE-DISTINCT response-count vectors over the deposit's 580 rows: any
#    permutation of the block would leave at least one live item unable to
#    reproduce the column it is named after. Counts hard-coded from the deposited
#    workbook (Mendeley doi:10.17632/tdsspksw83 V1, sha256
#    cf8567e12b3c86a5b83398eb37409afa19209315f9bb52945a33433434ad39ae, 580 rows),
#    per the template's rule 4.
#
#  LINK 2 (source column -> English wording). codebook.docx, Table
#    "2. MEASUREMENT VARIABLES", rows VARIABLE=TP1..TP5, LABEL column, hard-coded
#    verbatim below and compared against the shipped item_text_translated.
#
#  LINK 3 (English wording -> administered Vietnamese). The VN and EN
#    questionnaires print the same seven blocks in the same order (5-4-4-5-4-4-4)
#    and TP is block 1. Beyond position, a distinctive-phrase crosswalk pins each
#    Vietnamese stem to exactly one English statement: each phrase pair must
#    select the SAME single item on both sides, so no permutation survives.

suppressMessages(library(irw))
TABLE <- "hoai_2026_teaching_presence"
ok <- TRUE

## ---- LINK 1 -----------------------------------------------------------------
SRC <- rbind(
  TP1 = c(0, 62, 189, 258, 71),
  TP2 = c(1, 57, 206, 250, 66),
  TP3 = c(1, 54, 208, 259, 58),
  TP4 = c(0, 50, 218, 259, 53),
  TP5 = c(1, 50, 208, 270, 51)
)
colnames(SRC) <- as.character(1:5)
codes <- rownames(SRC)
n <- length(codes)

pairs_same <- 0
for (a in 1:(n - 1)) for (b in (a + 1):n)
  if (identical(unname(SRC[a, ]), unname(SRC[b, ]))) pairs_same <- pairs_same + 1
cat("deposit TP columns, counts of resp 1..5 (n=580 each):\n"); print(SRC)
cat(sprintf("identical pairs among the five source columns: %d (need 0)\n\n", pairs_same))
if (pairs_same != 0) ok <- FALSE

d <- irw::irw_fetch(TABLE)
obs <- table(factor(d$item, levels = codes), factor(d$resp, levels = 1:5))
obs <- matrix(as.integer(obs), nrow = n, dimnames = dimnames(SRC))
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
  TP1 = "The instructor clearly communicates course objectives and expectations at the beginning of the course.",
  TP2 = "The instructor provides clear guidance on how to learn both in class and online.",
  TP3 = "The instructor encourages students to exchange ideas during learning activities.",
  TP4 = "The instructor provides feedback that helps me adjust my learning when I encounter difficulties.",
  TP5 = "The instructor organizes the course progress appropriately for the blended learning format."
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
  TP1 = "Ngay từ đầu môn học, giảng viên nêu rõ mục tiêu và yêu cầu cần đạt.",
  TP2 = "Hướng dẫn của giảng viên giúp tôi biết rõ cách học trên lớp và trực tuyến.",
  TP3 = "Giảng viên khuyến khích sinh viên trao đổi ý kiến trong các buổi học.",
  TP4 = "Phản hồi của giảng viên giúp tôi điều chỉnh việc học khi gặp khó khăn.",
  TP5 = "Tiến độ giảng dạy được giảng viên tổ chức phù hợp với cách học kết hợp."
)
cat("\nshipped item_text vs Questionaire_VN.docx Teaching Presence block, rows 1-5:\n")
for (it in codes) {
  got <- unique(csv$item_text[csv$item == it])
  same <- length(got) == 1 && identical(trimws(got), VN[[it]])
  if (!same) ok <- FALSE
  cat(sprintf("%-5s %s\n", it, if (same) "match" else "MISMATCH"))
}

# distinctive phrase pairs: each must select exactly one item on BOTH sides,
# and the same one. (Each also occurs exactly once among all 31/32 distinct
# statements printed in the whole questionnaire, checked at extraction time.)
PAIRS <- list(
  c("mục tiêu và yêu cầu cần đạt", "course objectives and expectations"),
  c("cách học trên lớp và trực tuyến", "how to learn both in class and online"),
  c("khuyến khích sinh viên trao đổi ý kiến", "encourages students to exchange ideas"),
  c("Phản hồi của giảng viên", "provides feedback"),
  c("Tiến độ giảng dạy", "organizes the course progress")
)
cat("\nVN/EN content crosswalk (each phrase pair must select the same single item):\n")
for (p in PAIRS) {
  hv <- codes[grepl(p[1], VN, fixed = TRUE)]
  he <- codes[grepl(p[2], CODEBOOK, fixed = TRUE)]
  good <- length(hv) == 1 && length(he) == 1 && identical(hv, he)
  if (!good) ok <- FALSE
  cat(sprintf("  %-40s -> %-6s | %-38s -> %-6s  %s\n",
              p[1], paste(hv, collapse = ","), p[2], paste(he, collapse = ","),
              if (good) "unique, agree" else "AMBIGUOUS/DISAGREE"))
}

cat("\nWhat this does NOT establish: the resp<->option_text direction. The five\n",
    "anchors come from the questionnaire's own printed scale line and the\n",
    "codebook's VALID CODING column (1 = Hoàn toàn không đồng ý ... 5 = Hoàn\n",
    "toàn đồng ý), which agree with each other but cannot be tested against the\n",
    "data: the deposit stores integers only and publishes no label counts. Nor\n",
    "can any link detect an error inside the deposit's own codebook -- a\n",
    "mislabelled VARIABLE row would satisfy links 1, 2 and 3 alike.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
