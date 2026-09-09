# verify_liu_2025_speaking_selfefficacy.R -- Step 5b re-runnable mapping evidence.
#
# CLAIM UNDER TEST: data/liu_2025_classroom_wtc.py assigns this table's item codes
# POSITIONALLY over the S1 Data workbook's 44 item columns
# (item_cols_all[21:26] -> sse_ling_1..5, [26:29] -> sse_selfreg_1..3,
#  [29:31] -> sse_deliv_1..2, [31:35] -> sse_perf_1..4), and the workbook's header
# row IS the sentence we ship as item_text. So the falsifiable prediction is: for
# every respondent, the live resp stored under code X equals the deposit cell in
# the column whose header we shipped as X's item_text.
#
# Decisive rather than circumstantial: no two of the 14 SSE columns are equal as
# vectors, so a cell-for-cell match distinguishes every item from every other item
# -- swapping any pair would break it.
#
# Data: PLOS ONE 10.1371/journal.pone.0328226 S1 Data (.s002, XLSX, 623 x 48).

suppressMessages({library(irw); library(readxl)})

TABLE <- "liu_2025_speaking_selfefficacy"
URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0328226.s002")

# code -> shipped item_text (the deposit header minus its "n. " numbering)
SHIPPED <- c(
  sse_ling_1    = "When speaking English in the classroom, I can speak fluently.",
  sse_ling_2    = "When speaking English in the classroom, I can logically organize my words.",
  sse_ling_3    = "When speaking English in the classroom, I can speak with few pause or filler (i.e., “Um,” “Ah,” or “You Know”).",
  sse_ling_4    = "When speaking English in the classroom, I can speak with grammatical accuracy.",
  sse_ling_5    = "When speaking English in the classroom, I can speak with correct pronunciation, intonation, and liaison.",
  sse_selfreg_1 = "I actively participate in my speaking course to improve my speaking.",
  sse_selfreg_2 = "When speaking English in the classroom, I can think of my goals before speaking.",
  sse_selfreg_3 = "When speaking English in the classroom, I can evaluate whether I achieve my goal in speaking.",
  sse_deliv_1   = "When speaking English in the classroom, I can speak with confidence.",
  sse_deliv_2   = "I am not stressed out when speaking English in the classroom.",
  sse_perf_1    = "I can understand the most difficult material presented in speaking course.",
  sse_perf_2    = "I can do an excellent job on the assignments and tests in the speaking course.",
  sse_perf_3    = "Considering the difficulty of the speaking course, the teacher, and my skill, I think I can do well in this class.",
  sse_perf_4    = "I can receive an excellent grade in speaking course."
)

tmp <- tempfile(fileext = ".xlsx")
utils::download.file(URL, tmp, quiet = TRUE, mode = "wb")
raw <- readxl::read_excel(tmp)
item_cols <- names(raw)[5:ncol(raw)]   # after Number, Gender, Grade, Academic Disciplines
stopifnot(length(item_cols) == 44)
sse_cols <- item_cols[22:35]           # the SSE block, 1-based
stopifnot(length(sse_cols) == 14)

# (A) positional header diff: the header at each mapped position must be the text we shipped
hdr <- trimws(sub("^\\s*\\d+\\.\\s*", "", sse_cols))
cat("-- (A) header vs shipped item_text (positional check) --\n")
ok_hdr <- TRUE
for (i in seq_along(SHIPPED)) {
  same <- identical(hdr[i], unname(SHIPPED[i]))
  ok_hdr <- ok_hdr && same
  cat(sprintf("%-14s col%-3d %-6s %s\n", names(SHIPPED)[i], 4 + 21 + i,
              if (same) "MATCH" else "DIFF", hdr[i]))
}

live <- irw::irw_fetch(TABLE)
dep <- as.data.frame(raw)
names(dep)[1] <- "id"

cat("\n-- (B) cell-for-cell: live resp vs deposit column, joined on id --\n")
cat(sprintf("%-14s %6s %8s %10s %9s\n", "item", "n", "match%", "mean_live", "mean_dep"))
worst <- 1
for (i in seq_along(SHIPPED)) {
  code <- names(SHIPPED)[i]
  l <- live[live$item == code, c("id", "resp")]
  m <- merge(l, data.frame(id = dep$id, dep_resp = dep[[sse_cols[i]]]), by = "id")
  rate <- mean(m$resp == m$dep_resp)
  worst <- min(worst, rate)
  cat(sprintf("%-14s %6d %8.4f %10.4f %9.4f\n", code, nrow(m), rate,
              mean(m$resp), mean(m$dep_resp)))
}

# (C) distinctness -- the check would be vacuous if two SSE columns were identical
agr <- c()
for (a in 1:13) for (b in (a + 1):14)
  agr <- c(agr, mean(dep[[sse_cols[a]]] == dep[[sse_cols[b]]]))
cat(sprintf("\n-- (C) max pairwise cell agreement among the 14 deposit columns: %.3f\n", max(agr)))
cat("So no pair of items is interchangeable under (B): swapping any two codes would\n",
    "drop their match rate to that level or below.\n", sep = "")
cat("NOT established by this route: the ADMINISTERED Chinese wording -- the deposit and\n",
    "S1 Appendix publish English only (text_source=translated_substitute); and the\n",
    "option_text for resp 2-4, which no source labels.\n", sep = "")

cat(if (ok_hdr && worst == 1) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
