# verify_liu_2025_foreign_lang_enjoyment.R -- Step 5b re-runnable mapping evidence.
#
# CLAIM UNDER TEST: data/liu_2025_classroom_wtc.py assigns the item codes
# POSITIONALLY over the S1 Data workbook's item columns (item_cols_all[35:38] ->
# fle_personal_1..3, [38:41] -> fle_teacher_1..3, [41:44] -> fle_social_1..3), and
# the workbook's header row IS the item text we ship. So the falsifiable prediction
# is: for every respondent, the live resp under code X equals the deposit cell in
# the column whose header we shipped as X's item_text.
#
# This is decisive rather than circumstantial because no two of the nine FLE columns
# are equal as vectors (max pairwise cell agreement 0.695), so a cell-for-cell match
# distinguishes every item from every other item -- a swap of any pair would break it.
#
# Data: PLOS ONE 10.1371/journal.pone.0328226 S1 Data (.s002, XLSX, 623 x 48).

suppressMessages({library(irw); library(readxl)})

TABLE <- "liu_2025_foreign_lang_enjoyment"
URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0328226.s002")

# code -> the shipped item_text, i.e. the deposit header (minus its "n. " numbering)
SHIPPED <- c(
  fle_personal_1 = "I enjoy it.",
  fle_personal_2 = "I’ve learnt interesting things.",
  fle_personal_3 = "In class, I feel proud of my accomplishments.",
  fle_teacher_1  = "The teacher is encouraging.",
  fle_teacher_2  = "The teacher is friendly.",
  fle_teacher_3  = "The teacher is supportive.",
  fle_social_1   = "We form a tight group.",
  fle_social_2   = "We have common “legends”, such as running jokes.",
  fle_social_3   = "We laugh a lot."
)

tmp <- tempfile(fileext = ".xlsx")
utils::download.file(URL, tmp, quiet = TRUE, mode = "wb")
raw <- readxl::read_excel(tmp)
item_cols <- names(raw)[5:ncol(raw)]      # after Number, Gender, Grade, Academic Disciplines
stopifnot(length(item_cols) == 44)
fle_cols <- item_cols[36:44]              # the FLE block, 1-based

# The header must be the shipped text, numbering and whitespace aside.
hdr <- trimws(sub("^\\s*\\d+\\.\\s*", "", fle_cols))
hdr <- gsub("'", "’", hdr)           # workbook uses a straight apostrophe
cat("-- header vs shipped item_text (positional check) --\n")
ok_hdr <- TRUE
for (i in seq_along(SHIPPED)) {
  same <- identical(hdr[i], unname(SHIPPED[i]))
  ok_hdr <- ok_hdr && same
  cat(sprintf("%-15s col%-3d %-6s %s\n", names(SHIPPED)[i], 4 + 35 + i,
              if (same) "MATCH" else "DIFF", hdr[i]))
}

live <- irw::irw_fetch(TABLE)
dep <- as.data.frame(raw)
names(dep)[1] <- "id"

cat("\n-- cell-for-cell: live resp vs deposit column, joined on id --\n")
cat(sprintf("%-15s %6s %8s %9s %9s\n", "item", "n", "match%", "mean_live", "mean_dep"))
worst <- 1
for (i in seq_along(SHIPPED)) {
  code <- names(SHIPPED)[i]
  l <- live[live$item == code, c("id", "resp")]
  m <- merge(l, data.frame(id = dep$id, dep_resp = dep[[fle_cols[i]]]), by = "id")
  rate <- mean(m$resp == m$dep_resp)
  worst <- min(worst, rate)
  cat(sprintf("%-15s %6d %8.4f %9.4f %9.4f\n", code, nrow(m), rate,
              mean(m$resp), mean(m$dep_resp)))
}

# Distinctness: the check would be vacuous if two FLE columns were equal.
agr <- c()
for (a in 1:8) for (b in (a + 1):9)
  agr <- c(agr, mean(dep[[fle_cols[a]]] == dep[[fle_cols[b]]]))
cat(sprintf("\nmax pairwise cell agreement among the 9 deposit columns: %.3f\n", max(agr)))
cat("So no pair of items is interchangeable under this test: a swap of any two codes\n",
    "would drop their match rate to that level or below.\n", sep = "")
cat("Not established by this route: nothing about the ADMINISTERED Chinese wording --\n",
    "the deposit and S1 Appendix are English only (text_source=translated_substitute).\n", sep = "")

cat(if (ok_hdr && worst == 1) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
