# verify_jablonska_2020_swls.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST
#   (a) resp <-> option_text: the live integers 1..7 are the study's 7-point
#       agreement scale running 1 = strongest DISAGREEMENT .. 7 = strongest
#       AGREEMENT, so the Polish anchors shipped at resp=1..7 are
#       "Calkowicie sie nie zgadzam" .. "Calkowicie sie zgadzam" in that order.
#   (b) item <-> the source column it was melted from: data/jablonska_2020_instagram.py
#       melts the S2 Dataset (.xlsx) columns 50..54 with var_name="item", so the IRW
#       item code IS the spreadsheet header string. The per-item response
#       distributions are the falsifiable consequence.
#
# THE TEST (route 9, response-frequency matching)
#   The S2 Dataset stores TEXT labels ("Strongly disagree" .. "Strongly agree");
#   the live IRW table stores integers. Count every item x label cell in the
#   source and every item x resp cell in the live table. A correct mapping
#   matches cell for cell (35 cells); any flipped direction, permuted level or
#   shifted item assignment breaks it immediately. The 5 items' 7-count vectors
#   are pairwise distinct, so this separates every item from every other item.
#
# WHAT IT DOES NOT ESTABLISH
#   Which POLISH SENTENCE belongs to which header. That tie is not statistical:
#   the S3 Appendix (10.1371/journal.pone.0229354.s004) prints the questionnaire
#   twice, English then Polish, in identical item order, and the .xlsx headers are
#   a literal English rendering of the Polish sentences ("Uwazam, ze moje zycie
#   jest bliskie idealu." <-> "50. I think my life is close to ideal."), so it is
#   settled by translation correspondence plus identical ordering, not by numbers.
#   Same for the Polish anchor STRINGS: their order within the questionnaire is
#   what (a) tests, not their wording.

suppressMessages(library(irw))
TABLE <- "jablonska_2020_swls"

# Source counts, read from S2 Dataset (PLOS 10.1371/journal.pone.0229354.s006),
# columns "50."..."54.", label counts in the order
# Strongly disagree, Disagree, Rather disagree, Neither agree or disagree,
# Rather agree, Agree, Strongly agree  -- i.e. ascending agreement.
SRC <- rbind(
  "50" = c(73, 80, 248, 136, 272, 114,  51),
  "51" = c(39, 47, 176, 116, 363, 150,  83),
  "52" = c(34, 34, 136,  88, 393, 183, 106),
  "53" = c(32, 30, 115,  77, 409, 193, 118),
  "54" = c(85,101, 248,  88, 252, 112,  88))
colnames(SRC) <- 1:7

# Optionally re-read the source file rather than trusting the hard-coded matrix.
xl <- tempfile(fileext = ".xlsx")
ok <- tryCatch({
  utils::download.file(paste0("https://journals.plos.org/plosone/article/file",
                              "?type=supplementary&id=10.1371/journal.pone.0229354.s006"),
                       xl, quiet = TRUE, mode = "wb")
  requireNamespace("readxl", quietly = TRUE)
}, error = function(e) FALSE)
if (isTRUE(ok)) {
  raw <- readxl::read_excel(xl)
  lv <- c("Strongly disagree","Disagree","Rather disagree","Neither agree or disagree",
          "Rather agree","Agree","Strongly agree")
  cols <- grep("^5[0-4]\\.", names(raw), value = TRUE)
  M <- t(sapply(cols, function(c) as.integer(table(factor(raw[[c]], levels = lv)))))
  rownames(M) <- substr(cols, 1, 2); colnames(M) <- 1:7
  M <- M[rownames(SRC), , drop = FALSE]
  cat("Source S2 Dataset re-downloaded; hard-coded matrix matches file: ",
      all(M == SRC), "\n\n", sep = "")
  SRC <- M
} else {
  cat("Source S2 Dataset not re-downloaded (offline); using hard-coded counts.\n\n")
}

d <- irw::irw_fetch(TABLE)                 # 4,870 rows / 3 cols -- a trivial export
LIVE <- table(substr(d$item, 1, 2), factor(d$resp, levels = 1:7))
LIVE <- LIVE[rownames(SRC), , drop = FALSE]

cat("item x resp counts -- source label counts (S2 Dataset) vs live IRW integers\n")
cat(sprintf("%-4s %-28s %s\n", "item", "resp=1..7 (source)", "resp=1..7 (live)"))
for (i in rownames(SRC))
  cat(sprintf("%-4s %-28s %s\n", i,
              paste(SRC[i, ], collapse = " "), paste(LIVE[i, ], collapse = " ")))

bad <- sum(SRC != LIVE)
cat(sprintf("\ncells compared: %d   mismatching: %d\n", length(SRC), bad))

# Distinctness: the route only separates items if their count vectors differ.
vecs <- apply(SRC, 1, paste, collapse = "-")
cat(sprintf("distinct per-item count vectors: %d of %d\n", length(unique(vecs)), nrow(SRC)))

# Direction sanity: a flipped scale would invert every item's mean.
cat(sprintf("mean resp per item (agreement should be high in a general sample): %s\n",
            paste(sprintf("%s=%.2f", rownames(SRC),
                          as.vector(SRC %*% 1:7) / rowSums(SRC)), collapse = "  ")))

cat(if (bad == 0 && length(unique(vecs)) == nrow(SRC)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
