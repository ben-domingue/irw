## verify_kushnir2017_bfi.R -- batch_067
##
## mapping_basis = data_labels: the IRW `item` value IS the source spreadsheet's
## column header, and that header contains the item wording, so the item<->text
## axis is self-evident (checked below by re-deriving item_text from the header).
## The axis that DID carry a decision is option_text<->resp: the source stores
## label strings ("Agree a little"), the live table stores 1-5, and the mapping
## comes from data/kushnir2017_smoking_cessation.py's BFI_LABEL_MAP. This script
## re-runs the response-frequency match that pins it.
##
## Run from itemtext/:  Rscript itemtables/batch_067/verify_kushnir2017_bfi.R
suppressMessages(library(irw))

TBL  <- "kushnir2017_bfi"
CSV  <- "itemtables/batch_067/kushnir2017_bfi__items.csv"
XLSX <- ".cache/kushnir2017_bfi/raw.xlsx"
URL  <- "https://dataverse.harvard.edu/api/access/datafile/3059090"  # doi:10.7910/DVN/8LBLYS, CC0
LAB  <- c("Disagree strongly"=1, "Disagree a little"=2,
          "Neither agree nor disagree"=3, "Agree a little"=4, "Agree strongly"=5)
fail <- character(0)

if (!file.exists(XLSX)) {
  dir.create(dirname(XLSX), recursive = TRUE, showWarnings = FALSE)
  utils::download.file(URL, XLSX, mode = "wb", quiet = TRUE)
}
src <- suppressMessages(readxl::read_excel(XLSX))
src <- as.data.frame(src, check.names = FALSE)
cols <- grep("BFI", names(src), value = TRUE)
it   <- read.csv(CSV, stringsAsFactors = FALSE)

cat("=== 1. item_text re-derived from the source column header ===\n")
bad <- 0
for (c in cols) {
  want <- sub("^\\(+BFI_[0-9]+\\)[[:space:]]*", "", c)
  got  <- unique(it$item_text[it$item == c])
  if (length(got) != 1 || !identical(got, want)) {
    bad <- bad + 1
    cat(sprintf("  MISMATCH header=%s\n    derived : %s\n    shipped : %s\n",
                c, want, paste(got, collapse = "|")))
  }
}
cat(sprintf("  headers compared: %d | mismatches: %d\n", length(cols), bad))
if (bad) fail <- c(fail, "item_text does not reproduce from the source header")

cat("\n=== 2. option_text<->resp by response-frequency matching ===\n")
live <- irw::irw_fetch(TBL)
cells <- 0; cbad <- 0; tied <- 0
for (c in cols) {
  v  <- src[[c]]; v <- v[!is.na(v)]
  sc <- table(factor(LAB[v], levels = 1:5))
  lc <- table(factor(live$resp[live$item == c], levels = 1:5))
  if (anyDuplicated(as.integer(sc))) tied <- tied + 1
  for (r in 1:5) {
    cells <- cells + 1
    if (sc[[r]] != lc[[r]]) {
      cbad <- cbad + 1
      cat(sprintf("  MISMATCH %s resp=%d source=%d live=%d\n", c, r, sc[[r]], lc[[r]]))
    }
  }
  if (c == cols[1])
    cat(sprintf("  example %s: source %s | live %s\n", c,
                paste(as.integer(sc), collapse = "/"), paste(as.integer(lc), collapse = "/")))
}
cat(sprintf("  item x level cells compared: %d | mismatches: %d\n", cells, cbad))
cat(sprintf("  items whose five level counts are all distinct: %d of %d\n",
            length(cols) - tied, length(cols)))
if (cbad) fail <- c(fail, "option_text/resp frequency mismatch")

cat("\nWhat this does NOT establish: nothing about wording the deposit never published\n",
    "(the BFI-44 preamble and the 'I see myself as someone who...' stem are absent from\n",
    "the file and are not shipped). For the one item whose level counts are not all\n",
    "distinct, route 9 cannot separate the tied levels on its own.\n", sep = "")

cat("\n", strrep("-", 60), "\n", sep = "")
if (length(fail)) { cat(paste0("  - ", fail, collapse = "\n"), "\n"); cat("VERDICT: FAIL\n")
} else cat("VERDICT: PASS\n")
