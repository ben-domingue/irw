# verify_nguyen_2026_sdt_academic_motivation.R -- Step 5b mapping check (batch_344).
#
# Claim: item_text for ACM1..ACM7 is right because (a) the study's own
# QUESTIONNAIRE.docx (Mendeley Data 10.17632/n45sjtxmzy, file 47988700-...)
# prints each item beside the very code the data use (PART E, ACM1..ACM7), and
# (b) the IRW item code IS the deposit .xlsx column header of the same name
# (data/nguyen_2026_sdt_online_learning.py melts by name, no positional step).
#
# What would break if item_text for two items were swapped:
#   check 1 -- the shipped item_text for ACMk must equal the questionnaire's
#              text printed against code ACMk, for every k (7/7);
#   check 2 -- the live IRW item ACMk must reproduce the per-level response
#              counts of xlsx column ACMk and of NO other ACM column (7x7
#              match matrix must be the identity).
# Not established: that the depositor filled xlsx column ACMk from questionnaire
# item ACMk -- that tie is the depositor's own code labelling, which is the
# source-level link and cannot be tested statistically here (no per-item
# statistics are published; the 7 items are near-homogeneous, means 3.50-3.67).

suppressMessages({ library(irw); library(xml2); library(readxl) })

TABLE <- "nguyen_2026_sdt_academic_motivation"
here <- tryCatch(dirname(normalizePath(sys.frame(1)$ofile)), error = function(e) "itemtables/batch_344")
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))
if (!file.exists(items_csv)) items_csv <- file.path("itemtables/batch_344", paste0(TABLE, "__items.csv"))

BASE <- "https://data.mendeley.com/public-files/datasets/n45sjtxmzy/files/"
XLSX <- paste0(BASE, "39d2007b-57ea-4369-93c0-47fa82f619c4/file_downloaded")
DOCX <- paste0(BASE, "47988700-6365-4ce6-b61b-d792f37f1184/file_downloaded")
tx <- tempfile(fileext = ".xlsx"); td <- tempfile(fileext = ".docx")
download.file(XLSX, tx, mode = "wb", quiet = TRUE)
download.file(DOCX, td, mode = "wb", quiet = TRUE)

codes <- paste0("ACM", 1:7)
ok <- TRUE

# ---- check 1: questionnaire code -> text vs shipped item_text -------------
ud <- tempfile(); unzip(td, "word/document.xml", exdir = ud)
doc <- read_xml(file.path(ud, "word/document.xml"))
ns <- xml_ns(doc)
rows <- xml_find_all(doc, "//w:tr", ns)
cells <- lapply(rows, function(r) trimws(sapply(xml_find_all(r, "./w:tc", ns),
                  function(c) paste(xml_text(xml_find_all(c, ".//w:t", ns)), collapse = ""))))
q <- setNames(sapply(cells, `[`, 2), sapply(cells, `[`, 1))
shipped <- read.csv(items_csv, stringsAsFactors = FALSE)
sh <- tapply(shipped$item_text, shipped$item, function(x) unique(x)[1])
cat("check 1: questionnaire text printed against each code vs shipped item_text\n")
n1 <- 0
for (k in codes) {
  m <- identical(unname(q[k]), unname(sh[k]))
  n1 <- n1 + m
  cat(sprintf("  %-5s %-5s %s\n", k, if (m) "MATCH" else "DIFF", q[k]))
}
cat(sprintf("  %d/7 verbatim\n\n", n1))
ok <- ok && n1 == 7

# ---- check 2: live item vs xlsx column, per-level counts, 7x7 ------------
x <- as.data.frame(read_excel(tx))
d <- irw::irw_fetch(TABLE)
cnt <- function(v) as.numeric(table(factor(v, levels = 1:5)))
M <- matrix(FALSE, 7, 7, dimnames = list(live = codes, xlsx = codes))
for (a in codes) for (b in codes) M[a, b] <- all(cnt(d$resp[d$item == a]) == cnt(x[[b]]))
cat("check 2: per-level counts (resp 1..5), live item vs its own xlsx column\n")
for (k in codes) cat(sprintf("  %-5s live %-28s xlsx %s\n", k,
                             paste(cnt(d$resp[d$item == k]), collapse = "/"),
                             paste(cnt(x[[k]]), collapse = "/")))
cat("\n  7x7 match matrix (rows live item, cols xlsx column; TRUE = identical counts):\n")
print(M)
diag_ok <- all(diag(M)); off_ok <- !any(M[row(M) != col(M)])
cat(sprintf("  diagonal %d/7 match; off-diagonal matches %d\n", sum(diag(M)), sum(M[row(M) != col(M)])))
ok <- ok && diag_ok && off_ok

cat("\nNot established: that the depositor's xlsx column ACMk holds answers to questionnaire\n",
    "item ACMk -- that is the source's own code labelling, taken as authoritative.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
