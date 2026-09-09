# verify_liu_2025_willingness_communicate.R -- Step 5b re-runnable mapping evidence.
#
# CLAIM UNDER TEST: data/liu_2025_classroom_wtc.py assigns this table's item codes
# POSITIONALLY over the S1 Data workbook's 44 item columns (item_cols_all[11:21] ->
# wtc_1..wtc_10, 0-based, i.e. deposit columns 16-25), and the workbook's header row
# IS the English item text we ship. So the falsifiable prediction is: for every
# respondent, the live resp stored under code wtc_i equals the deposit cell in the
# column whose header we shipped as wtc_i's item_text.
#
# Decisive rather than circumstantial: no two of the ten WTC columns are equal as
# vectors, so a cell-for-cell match distinguishes every item from every other item;
# swapping any pair would break it immediately.
#
# Data: PLOS ONE 10.1371/journal.pone.0328226 S1 Data (.s002, XLSX, 623 x 48).

suppressMessages({library(irw); library(readxl)})

TABLE <- "liu_2025_willingness_communicate"
URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0328226.s002")

# code -> the shipped item_text, i.e. the deposit header (minus its "n. " numbering)
SHIPPED <- c(
  wtc_1  = "I am willing to do a role-play standing in front of the class in English (e.g., ordering food in a restaurant).",
  wtc_2  = "I am willing to give a short self-introduction without notes in English to the class.",
  wtc_3  = "I am willing to give a short speech in English to the class about my hometown with notes.",
  wtc_4  = "I am willing to translate a spoken utterance from Chinese into English in my group.",
  wtc_5  = "I am willing to ask the teacher in English to repeat what he/she just said in English because I didn’t understand.",
  wtc_6  = "I am willing to do a role-play in English at my desk, with my peer (e.g., ordering food in a restaurant).",
  wtc_7  = "I am willing to ask my peer sitting next to me in English the meaning of an English word.",
  wtc_8  = "I am willing to ask my group mates in English the meaning of a word I do not know.",
  wtc_9  = "I am willing to ask my group mates in English how to pronounce a word in English.",
  wtc_10 = "I am willing to ask my peer sitting next to me in English how to say an English phrase to express the thoughts in my mind."
)

tmp <- tempfile(fileext = ".xlsx")
utils::download.file(URL, tmp, quiet = TRUE, mode = "wb")
raw <- readxl::read_excel(tmp)
item_cols <- names(raw)[5:ncol(raw)]   # after Number, Gender, Grade, Academic Disciplines
stopifnot(length(item_cols) == 44)
wtc_cols <- item_cols[12:21]           # the WTC block, 1-based (paper's items 12-21)

hdr <- trimws(sub("^\\s*\\d+\\.\\s*", "", wtc_cols))
cat("-- deposit header at the mapped position vs shipped item_text --\n")
ok_hdr <- TRUE
for (i in seq_along(SHIPPED)) {
  same <- identical(hdr[i], unname(SHIPPED[i]))
  ok_hdr <- ok_hdr && same
  cat(sprintf("%-7s col%-3d %-6s %s\n", names(SHIPPED)[i], 4 + 11 + i,
              if (same) "MATCH" else "DIFF", hdr[i]))
}

live <- irw::irw_fetch(TABLE)   # 6,230 rows -- a deliberate, small export
dep <- as.data.frame(raw); names(dep)[1] <- "id"

cat("\n-- cell-for-cell: live resp vs deposit column, joined on id --\n")
cat(sprintf("%-7s %6s %8s %9s %9s\n", "item", "n", "match%", "mean_live", "mean_dep"))
worst <- 1
for (i in seq_along(SHIPPED)) {
  code <- names(SHIPPED)[i]
  l <- live[live$item == code, c("id", "resp")]
  m <- merge(l, data.frame(id = dep$id, dep_resp = dep[[wtc_cols[i]]]), by = "id")
  rate <- mean(m$resp == m$dep_resp)
  worst <- min(worst, rate)
  cat(sprintf("%-7s %6d %8.4f %9.4f %9.4f\n", code, nrow(m), rate,
              mean(m$resp), mean(m$dep_resp)))
}

# Distinctness: the check would be vacuous if two WTC columns were equal vectors.
agr <- c()
for (a in 1:9) for (b in (a + 1):10)
  agr <- c(agr, mean(dep[[wtc_cols[a]]] == dep[[wtc_cols[b]]]))
cat(sprintf("\nmax pairwise cell agreement among the 10 deposit columns: %.3f\n", max(agr)))
cat("No pair of items is interchangeable under this test: swapping any two codes\n",
    "would drop their match rate to that level or below.\n", sep = "")
cat("NOT established by this route: anything about the ADMINISTERED Chinese wording.\n",
    "The deposit and the S1 Appendix are English only, so item_text is the authors'\n",
    "own English rendering (text_source=translated_substitute), not what respondents read.\n",
    "The route also says nothing about the option_text<->resp tie beyond the article's\n",
    "stated 1 = strongly disagree / 5 = strongly agree anchoring.\n", sep = "")

cat(if (ok_hdr && worst == 1) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
