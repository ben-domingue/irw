# verify_nguyen_2026_autonomy_academic_motivation.R -- Step 5b mapping check (batch_351).
#
# Claim: item_text for AM1..AM3 is right because (a) the study's own
# Questionnaire.docx (Mendeley Data 10.17632/whsbpyxy6w, file 5e9f5e33-...)
# prints each item beside the very code the data use (table row "B ACADEMIC
# MOTIVATION", AM1..AM3), and (b) the IRW item code IS the deposit .xlsx column
# header of the same name (data/nguyen_2026_learner_autonomy.py melts AM1..AM3
# by name; id = 1-based row index), so no positional step exists.
#
# What would break if item_text for two items were swapped:
#   check 1 -- shipped item_text for AMk must equal the questionnaire text
#              printed against code AMk, for every k (3/3);
#   check 2 -- the live IRW item AMk must agree cell-for-cell with xlsx column
#              AMk (row = id) and clearly less with any other AM column (3x3).
# Not established: that the depositor filled xlsx column AMk from questionnaire
# item AMk -- that tie is the depositor's own code labelling, taken as
# authoritative; no article with per-item statistics exists to corroborate it.

suppressMessages({ library(irw); library(xml2); library(readxl) })

TABLE <- "nguyen_2026_autonomy_academic_motivation"
here <- tryCatch(dirname(normalizePath(sys.frame(1)$ofile)), error = function(e) "itemtables/batch_351")
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))
if (!file.exists(items_csv)) items_csv <- file.path("itemtables/batch_351", paste0(TABLE, "__items.csv"))

BASE <- "https://data.mendeley.com/public-files/datasets/whsbpyxy6w/files/"
XLSX <- paste0(BASE, "a794ff25-bbfb-41a1-8aa9-de9fc114b6cc/file_downloaded")
DOCX <- paste0(BASE, "5e9f5e33-9c99-4e02-8f84-67c9688a534b/file_downloaded")
tx <- tempfile(fileext = ".xlsx"); td <- tempfile(fileext = ".docx")
download.file(XLSX, tx, mode = "wb", quiet = TRUE)
download.file(DOCX, td, mode = "wb", quiet = TRUE)

codes <- paste0("AM", 1:3)
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
cat(sprintf("  %d/3 verbatim\n\n", n1))
ok <- ok && n1 == 3

# ---- check 2: live (id, AMk) vs xlsx row id, column AMj -------------------
x <- as.data.frame(read_excel(tx))
d <- irw::irw_fetch(TABLE)
cat(sprintf("live rows %d, ids %d; xlsx rows %d\n", nrow(d), length(unique(d$id)), nrow(x)))
A <- matrix(NA_real_, 3, 3, dimnames = list(live = codes, xlsx = codes))
for (a in codes) {
  s <- d[d$item == a, ]
  for (b in codes) A[a, b] <- mean(s$resp == x[[b]][s$id])
}
cat("cell agreement (rows live item, cols xlsx column):\n"); print(round(A, 3))
off <- max(A[row(A) != col(A)])
cat(sprintf("  diagonal min %.3f; best off-diagonal %.3f\n", min(diag(A)), off))
ok <- ok && all(diag(A) == 1) && off < 0.9

cat("\nNot established: that the depositor's xlsx column AMk holds answers to questionnaire\n",
    "item AMk -- that is the source's own code labelling, taken as authoritative. Nor does\n",
    "this check the anchor direction (see notes: the questionnaire states 1=Strongly disagree).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
