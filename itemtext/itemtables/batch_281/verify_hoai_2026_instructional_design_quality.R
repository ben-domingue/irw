# verify_hoai_2026_instructional_design_quality.R
#
# CLAIM UNDER TEST: each live item code IDQk carries the wording the deposit
# assigns to the source column of the same name -- Vietnamese in item_text,
# the authors' own English in item_text_translated.
#
# Three links, all falsified below:
#
#  (A) live item "IDQk"  ->  column "IDQk" of "Blended learning_data set.xlsx".
#      Falsifiable because the five IDQ columns have PAIRWISE-DISTINCT
#      response-count vectors over 580 respondents; if the processing script
#      had permuted the block, at least one live item's counts would fail to
#      reproduce the column it is named after. (Step 5b route 9.)
#  (B) code "IDQk"  ->  English statement. codebook.docx, Table
#      "2. MEASUREMENT VARIABLES", prints VARIABLE=IDQ1..IDQ5 beside the LABEL
#      column. Step 5b exemption 2, "explicit code labels".
#  (C) English statement -> Vietnamese statement. No code is printed beside the
#      Vietnamese, so this is pinned by a distinctive-content crosswalk: each
#      Vietnamese IDQ stem contains a token pair that occurs in exactly ONE of
#      the five statements, and its English counterpart occurs in exactly one
#      too. Checked by counting occurrences, not by reading.
#
# Counts and labels hard-coded from the deposited files (Mendeley
# doi:10.17632/tdsspksw83 V1, CC BY 4.0), per verify_template.R rule 4:
#   Blended learning_data set.xlsx  sha256 cf8567e12b3c86a5b83398eb37409afa19209315f9bb52945a33433434ad39ae
#   codebook.docx                   sha256 812c0dbd4dac32a29077f6882cfc184bdb91595c11664968735affa1fa10db80
#   Questionaire_VN.docx            sha256 27a41b16d9668fe468ae406a0513bff633f2194543304543b79592ae317f39a2
#   Questionaire_EN.docx            sha256 ed9d59c3e55d5b6e41e6a5987b56426291042673f9c00542eb4a63c1eaee68d4

suppressMessages(library(irw))

TABLE <- "hoai_2026_instructional_design_quality"
ok <- TRUE

## ---- (A) response-count vectors ---------------------------------------------
# Counts of responses 1..5 per IDQ column in the deposited workbook (n=580).
SRC <- rbind(
  IDQ1 = c(0,  61, 198, 256, 65),
  IDQ2 = c(1,  60, 204, 242, 73),
  IDQ3 = c(1,  61, 197, 253, 68),
  IDQ4 = c(1,  67, 196, 237, 79),
  IDQ5 = c(2,  65, 188, 267, 58)
)
colnames(SRC) <- as.character(1:5)

pairs_same <- 0
for (a in 1:4) for (b in (a + 1):5)
  if (identical(unname(SRC[a, ]), unname(SRC[b, ]))) pairs_same <- pairs_same + 1
cat("(A) deposit IDQ columns, counts of resp 1..5 (n=580 each):\n")
print(SRC)
cat(sprintf("    identical pairs among the five source columns: %d (need 0)\n\n", pairs_same))
if (pairs_same != 0) ok <- FALSE

d <- irw::irw_fetch(TABLE)
obs <- table(factor(d$item, levels = rownames(SRC)), factor(d$resp, levels = 1:5))
obs <- matrix(as.integer(obs), nrow = 5, dimnames = dimnames(SRC))
cat("    live per-item counts of resp 1..5:\n")
print(obs)
cat("\n    item  matches source column(s)        own column, uniquely?\n")
for (it in rownames(SRC)) {
  hits <- rownames(SRC)[apply(SRC, 1, function(r)
    identical(as.integer(unname(r)), as.integer(unname(obs[it, ]))))]
  good <- identical(hits, it)
  if (!good) ok <- FALSE
  cat(sprintf("    %-5s %-30s %s\n", it, paste(hits, collapse = ","),
              if (good) "yes" else "NO"))
}

## ---- (B) codebook LABEL vs shipped English ----------------------------------
CODEBOOK <- c(
  IDQ1 = "Learning objectives are clearly reflected in course activities and assessments.",
  IDQ2 = "Learning materials are well organized on the learning system.",
  IDQ3 = "Learning activities are designed to encourage active student participation.",
  IDQ4 = "Assessment criteria are clearly explained by the instructor.",
  IDQ5 = "The course structure helps me follow my learning progress effectively."
)
args <- commandArgs(FALSE)
here <- dirname(sub("^--file=", "", grep("^--file=", args, value = TRUE)[1]))
csv <- read.csv(file.path(here, paste0(TABLE, "__items.csv")),
                stringsAsFactors = FALSE, encoding = "UTF-8")
cat("\n(B) shipped item_text_translated vs codebook.docx LABEL for the same VARIABLE:\n")
for (it in names(CODEBOOK)) {
  got <- unique(csv$item_text_translated[csv$item == it])
  same <- length(got) == 1 && identical(trimws(got), CODEBOOK[[it]])
  if (!same) ok <- FALSE
  cat(sprintf("    %-5s %-9s %s\n", it, if (same) "match" else "MISMATCH", got[1]))
}

## ---- (C) VN <-> EN distinctive-content crosswalk ----------------------------
# Per item: a Vietnamese fragment and its English counterpart, each of which
# must occur in exactly one of the five statements on its own side.
VN_KEY <- c(IDQ1 = "Mục tiêu học tập",     # learning objectives
            IDQ2 = "hệ thống học tập",     # learning system
            IDQ3 = "chủ động tham gia",         # active participation
            IDQ4 = "chấm điểm",                 # marking / grading
            IDQ5 = "Cấu trúc môn học")     # course structure
EN_KEY <- c(IDQ1 = "Learning objectives",
            IDQ2 = "learning system",
            IDQ3 = "active student participation",
            IDQ4 = "Assessment criteria",
            IDQ5 = "course structure")
vn_ship <- sapply(names(VN_KEY), function(it) unique(csv$item_text[csv$item == it]))
cat("\n(C) distinctive-content crosswalk (hits among the five statements; need 1 and 1,\n")
cat("    and the single VN hit must be the same item as the single EN hit):\n")
cat(sprintf("    %-5s %-26s %4s  %-30s %4s  %s\n",
            "item", "VN fragment", "hits", "EN fragment", "hits", "same item?"))
for (it in names(VN_KEY)) {
  vh <- names(vn_ship)[grepl(VN_KEY[[it]], vn_ship, fixed = TRUE)]
  eh <- names(CODEBOOK)[grepl(EN_KEY[[it]], CODEBOOK, fixed = TRUE)]
  good <- identical(vh, it) && identical(eh, it)
  if (!good) ok <- FALSE
  cat(sprintf("    %-5s %-26s %4d  %-30s %4d  %s\n",
              it, VN_KEY[[it]], length(vh), EN_KEY[[it]], length(eh),
              if (good) "yes" else "NO"))
}

cat("\nWhat this does NOT establish: the resp <-> option_text direction. The\n",
    "deposit stores integers only and publishes no per-label counts, so the\n",
    "anchor order shipped here rests on the questionnaire's own printed line\n",
    "('1 = Hoàn toàn không đồng ý ... 5 = Hoàn toàn đồng ý') and the codebook's\n",
    "VALID CODING column, which agree, and cannot be tested against the data.\n",
    "It also cannot detect an error inside the deposit's own codebook: a\n",
    "mislabelled VARIABLE row would satisfy (A), (B) and (C) together.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
