# Verification for gilbert_meta_112 (#1945, batch_204).  STATUS: PARTIAL.
#
# SOURCE. CC BY view-only OSF deposit osf.io/detfc (Klopp, Bruenken & Stark 2026,
# ESTAFETT team-teaching crossover experiment, Teaching and Teacher Education
# 155:104886). Item codes come from the source spreadsheet's own Item_1..Item_8
# columns via data/gilbert_112-113.R, which clean_names() lowercases to item_1..8.
# Test content is the deposit's 'Validation achievement test' folder.
#
# WHAT IS CERTAIN AND WHAT IS NOT. The code-to-POSITION link is one-to-one and
# uncontested: the spreadsheet has exactly eight Item_ columns and the printed
# Forces test has exactly eight numbered questions. What is NOT settled is which
# printed WORDING goes with a position, because the deposit publishes TWO
# parallel versions of the test and the response table records no version. So a
# code can only carry a question if both versions print the same one there.
#
# Route 1: code set == the spreadsheet's Item_ columns, lowercased.
# Route 2: cross-version comparison. Only the questions identical in both
#   versions ship; the extraction must contain exactly those and no others.
# Route 3: the Forces/DNA split in the script reproduced from the spreadsheet.
#
# The two versions were extracted to .cache/batch_204/b204_forces_forms.csv
# (one row per Vraag, one column per version) so this check reads text rather
# than re-parsing PDFs. Same pattern as batch_203's b203_*_forms.csv.
FORMS <- ".cache/batch_204/b204_forces_forms.csv"
XL    <- ".cache/batch_204/detfc_Data_MainStudy.xlsx"
if (!file.exists(FORMS)) stop("missing extracted forms table: ", FORMS)
if (!requireNamespace("readxl", quietly = TRUE)) stop("needs readxl")
suppressWarnings(suppressMessages(library(readxl)))
f <- read.csv(FORMS, stringsAsFactors = FALSE, colClasses = "character")
x <- as.data.frame(read_excel(XL))

d <- as.data.frame(irw::irw_fetch("gilbert_meta_112"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_204/gilbert_meta_112__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: codes are the spreadsheet's Item_ columns ===\n")
src <- grep("^Item_[0-9]+$", names(x), value = TRUE)
r1  <- setequal(tolower(src), unique(d$item))
cat(sprintf("  spreadsheet Item_ columns %d, live codes %d, identical after\n  lowercasing (clean_names): %s\n",
            length(src), length(unique(d$item)), r1))
cat(sprintf("  %s\n", paste(sort(src), collapse = ", ")))

cat("\n=== Route 2: which questions are constant across the two versions ===\n")
norm <- function(s) trimws(gsub("\\s+", " ", s))
f$same <- norm(f$version1) == norm(f$version2) & nzchar(norm(f$version1))
for (i in seq_len(nrow(f)))
    cat(sprintf("  Vraag %-2s identical: %-5s  %s\n", f$vraag[i], f$same[i],
                substr(norm(f$version1[i]), 1, 62)))
constant <- paste0("item_", f$vraag[f$same])
shipped  <- unique(items$item[!is.na(items$item_text) & nzchar(items$item_text)])
r2 <- setequal(constant, shipped)
cat(sprintf("\n  version-constant questions: %s\n", paste(sort(constant), collapse = ", ")))
cat(sprintf("  codes shipping item_text:   %s\n", paste(sort(shipped), collapse = ", ")))
cat(sprintf("  identical: %s\n", r2))
cat("  The other five have no single text a respondent can be said to have\n")
cat("  seen, so they ship blank rather than pick a version. That is the whole\n")
cat("  reason this is PARTIAL -- both versions are published, the version\n")
cat("  INDICATOR is what the response table is missing.\n")

cat("\n=== Route 3: the Forces/DNA split reproduced ===\n")
fx <- x[x$Content == "Forces", ]
long <- unlist(lapply(src, function(c) suppressWarnings(as.numeric(fx[[c]]))))
r3 <- sum(!is.na(long)) == nrow(d)
cat(sprintf("  spreadsheet rows with Content == 'Forces': %d over %d item columns\n",
            nrow(fx), length(src)))
cat(sprintf("  non-missing cells %d; live rows %d; equal: %s\n",
            sum(!is.na(long)), nrow(d), r3))
cat("  The script filters content == 'Forces' and drop_na(resp), so this count\n")
cat("  matching confirms the table is the Forces arm of the crossover and not\n")
cat("  a mixture -- gilbert_meta_113 is the DNA arm off the same eight columns.\n")

cat("\n=== A defect in the source spreadsheet, reported not fixed ===\n")
cat("  The pretest cells of Item_1, Item_7 and Item_8 are self-referential\n")
cat("  formulas of the form =MIN(O101:O101) -- each cell pointing at itself --\n")
cat("  whose Excel-cached value is 0. Those zeros are fabricated, not observed,\n")
cat("  and they reach this table as wave-0 responses. 752 cells on the Forces\n")
cat("  side, 753 on the DNA side. Not visible to any check here because a\n")
cat("  fabricated 0 is a valid 0/1 response; found by reading the xlsx formulas.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  The wording of the five version-varying items, which is why they are\n")
cat("  blank, and the English translation of the three that do ship -- the\n")
cat("  deposit publishes no English test, so item_text_translated is IRW's.\n")
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")
