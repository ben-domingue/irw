# verify_nguyen_2026_sdt_perceived_performance.R -- Step 5b mapping check (batch_344).
# Claim: live items ACP1..ACP5 carry the wording printed beside those exact codes in
# the deposit's own QUESTIONNAIRE.docx (Mendeley 10.17632/n45sjtxmzy, Part F table).
# Two links, both checked here:
#  (1) code -> text: the docx table's "Code" column labels each item; every shipped
#      item_text must equal the docx text on the row carrying the same code.
#  (2) live item -> source column: data/nguyen_2026_sdt_online_learning.py melts the
#      xlsx columns by NAME (id = row index 1..N), so live resp for (id i, ACPk) must
#      equal xlsx row i, column ACPk for every cell. A swap of any two items breaks this.
suppressMessages({library(irw); library(readxl)})
TABLE <- "nguyen_2026_sdt_perceived_performance"
KEY <- "https://data.mendeley.com/public-files/datasets/n45sjtxmzy/files/"
td <- tempfile(); dir.create(td)
xl <- file.path(td, "d.xlsx"); dx <- file.path(td, "q.docx")
download.file(paste0(KEY, "39d2007b-57ea-4369-93c0-47fa82f619c4/file_downloaded"), xl, mode = "wb", quiet = TRUE)
download.file(paste0(KEY, "47988700-6365-4ce6-b61b-d792f37f1184/file_downloaded"), dx, mode = "wb", quiet = TRUE)
ok <- TRUE
here <- tryCatch(dirname(normalizePath(sys.frame(1)$ofile)), error = function(e) "itemtables/batch_344")
shipped <- read.csv(file.path(here, paste0(TABLE, "__items.csv")), stringsAsFactors = FALSE)
st <- unique(shipped[, c("item", "item_text")])

# (1) docx table rows: first cell = code, second = item text
x <- xml2::read_xml(unz(dx, "word/document.xml"))
ns <- xml2::xml_ns(x)
rows <- xml2::xml_find_all(x, "//w:tbl/w:tr", ns)
cells <- lapply(rows, function(r) trimws(sapply(xml2::xml_find_all(r, "./w:tc", ns), xml2::xml_text)))
docx <- do.call(rbind, lapply(cells, function(cc) data.frame(code = cc[1], text = cc[2])))
docx <- docx[grepl("^ACP[0-9]+$", docx$code), ]
cat("(1) code -> text, docx Code column vs shipped item_text\n")
for (i in seq_len(nrow(st))) {
  dt <- docx$text[docx$code == st$item[i]]
  m <- length(dt) == 1 && identical(dt, st$item_text[i])
  if (!m) ok <- FALSE
  cat(sprintf("  %-5s %-6s %s\n", st$item[i], if (m) "MATCH" else "DIFF", st$item_text[i]))
}
cat(sprintf("  %d/%d shipped items match the docx row with the same code; docx ACP rows = %d\n",
            sum(sapply(seq_len(nrow(st)), function(i) identical(docx$text[docx$code == st$item[i]], st$item_text[i]))),
            nrow(st), nrow(docx)))

# (2) cell-for-cell tie between live table and source xlsx columns
src <- as.data.frame(read_excel(xl))
src$id <- seq_len(nrow(src))
d <- as.data.frame(irw::irw_fetch(TABLE))
items <- paste0("ACP", 1:5)
cat(sprintf("\n(2) live vs source: %d live rows, %d source rows\n", nrow(d), nrow(src)))
agree <- matrix(NA, 5, 5, dimnames = list(live = items, source = items))
for (a in items) {
  la <- d[d$item == a, c("id", "resp")]
  for (b in items) {
    s <- src[match(la$id, src$id), b]
    agree[a, b] <- mean(la$resp == s)
  }
}
print(round(agree, 4))
diagok <- all(diag(agree) == 1)
offmax <- max(agree[row(agree) != col(agree)])
cat(sprintf("  diagonal (own column) agreement: min %.4f; best off-diagonal agreement: %.4f\n",
            min(diag(agree)), offmax))
if (!diagok || offmax >= 1) ok <- FALSE
cat("Not established: the administered (presumably Vietnamese) wording -- only the English\n",
    "questionnaire is deposited; option labels exist for the endpoints 1 and 5 only.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
