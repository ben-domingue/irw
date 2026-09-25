# verify_nguyen_2026_autonomy_student_ownership.R -- Step 5b mapping check (batch_353).
#
# Claim: item_text for O1..O4 is right because (a) the study's own
# Questionnaire.docx (Mendeley Data 10.17632/whsbpyxy6w, file 5e9f5e33-...)
# prints each item beside the very code the data use (table row "G STUDENT
# OWNERSHIP", O1..O4), and (b) the IRW item code IS the deposit .xlsx column
# header of the same name (data/nguyen_2026_learner_autonomy.py melts O1..O4
# by name; id = 1-based row index), so no positional step exists.
#
# What would break if item_text for two items were swapped:
#   check 1 -- shipped item_text for Ok must equal the questionnaire text
#              printed against code Ok, for every k (4/4);
#   check 2 -- the live IRW item Ok must agree cell-for-cell with xlsx column
#              Ok (row = id) and clearly less with any other O column (4x4).
# Not established: that the depositor filled xlsx column Ok from questionnaire
# item Ok -- that tie is the depositor's own code labelling, taken as
# authoritative; no article with per-item statistics exists to corroborate it.
# The deposit's composite column O is NOT used: it does not equal mean(O1..O4)
# (r=-0.96), so only item-level columns are compared.

suppressMessages({ library(irw); library(xml2); library(readxl) })

TABLE <- "nguyen_2026_autonomy_student_ownership"
here <- tryCatch(dirname(normalizePath(sys.frame(1)$ofile)), error = function(e) "itemtables/batch_353")
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))
if (!file.exists(items_csv)) items_csv <- file.path("itemtables/batch_353", paste0(TABLE, "__items.csv"))

BASE <- "https://data.mendeley.com/public-files/datasets/whsbpyxy6w/files/"
XLSX <- paste0(BASE, "a794ff25-bbfb-41a1-8aa9-de9fc114b6cc/file_downloaded")
DOCX <- paste0(BASE, "5e9f5e33-9c99-4e02-8f84-67c9688a534b/file_downloaded")
tx <- tempfile(fileext = ".xlsx"); td <- tempfile(fileext = ".docx")
download.file(XLSX, tx, mode = "wb", quiet = TRUE)
download.file(DOCX, td, mode = "wb", quiet = TRUE)

codes <- paste0("O", 1:4)
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
  cat(sprintf("  %-4s %-5s %s\n", k, if (m) "MATCH" else "DIFF", q[k]))
}
cat(sprintf("  %d/4 verbatim\n\n", n1))
ok <- ok && n1 == 4

# ---- check 2: live (id, Ok) vs xlsx row id, column Oj -------------------
x <- as.data.frame(read_excel(tx))
d <- irw::irw_fetch(TABLE)
cat(sprintf("live rows %d, ids %d; xlsx rows %d\n", nrow(d), length(unique(d$id)), nrow(x)))
A <- matrix(NA_real_, 4, 4, dimnames = list(live = codes, xlsx = codes))
for (a in codes) {
  s <- d[d$item == a, ]
  for (b in codes) A[a, b] <- mean(s$resp == x[[b]][s$id])
}
cat("cell agreement (rows live item, cols xlsx column):\n"); print(round(A, 3))
off <- max(A[row(A) != col(A)])
cat(sprintf("  diagonal min %.3f; best off-diagonal %.3f\n", min(diag(A)), off))
ok <- ok && all(diag(A) == 1) && off < 0.9

cat("\nNot established: that the depositor's xlsx column Ok holds answers to questionnaire\n",
    "item Ok -- that is the source's own code labelling, taken as authoritative. Nor does\n",
    "this check the anchor direction (see notes: the questionnaire states 1=Strongly disagree).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
