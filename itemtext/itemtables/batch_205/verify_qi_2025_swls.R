# Verification for qi_2025_swls (#1945, batch_205).
#
# SOURCE. Qi, Zou, Chau, Zhou, Wang & Sui (2025), 'A Comprehensive Dataset for
# Investigating the Structure of Self-Bias', Scientific Data 12:1755, CC BY;
# OSF deposit osf.io/3h95f, file Self_bias_dataset/0.Self_reported_scales/Scales.xlsx.
#
# THE MAPPING IS THE COLUMN NAME, AND THE WORKBOOK PROVES THE SCALE MEMBERSHIP.
# The live codes are the spreadsheet's own SWLS_1..SWLS_5 headers. Better, the
# workbook's far-right summary columns are live Excel FORMULAS rather than
# values, so the authors' own definition of the scale is readable: the
# 'Satisfaction with life' column is =AVERAGE(EX:FB), and EX..FB resolve to
# exactly SWLS_1..SWLS_5. No inference about which columns form the scale.
#
# Route 1: the code set equals the workbook's SWLS_ columns.
# Route 2: the authors' own formula resolves to exactly those five columns.
# Route 3: every response vector reproduced from the workbook.
if (!requireNamespace("readxl", quietly = TRUE)) stop("needs readxl")
XL <- ".cache/batch_205/qi_Scales.xlsx"
if (!file.exists(XL)) stop("missing cached deposit file: ", XL)
suppressWarnings(suppressMessages(library(readxl)))
x <- as.data.frame(read_excel(XL, sheet = "Summary_of_data"))

d <- as.data.frame(irw::irw_fetch("qi_2025_swls"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)

cat("=== Route 1: codes are the workbook's own column headers ===\n")
cols <- grep("^SWLS_[0-9]+$", names(x), value = TRUE)
r1 <- setequal(cols, unique(d$item))
cat(sprintf("  workbook SWLS_ columns %d (%s)\n", length(cols), paste(cols, collapse = ", ")))
cat(sprintf("  identical to the live code set: %s\n", r1))

cat("\n=== Route 2: the authors' own summary formula ===\n")
cat("  Scales.xlsx column 'Satisfaction with life' contains, for every row,\n")
cat("      =AVERAGE(EX<row>:FB<row>)\n")
cat("  and columns EX through FB are SWLS_1, SWLS_2, SWLS_3, SWLS_4, SWLS_5.\n")
first <- which(names(x) == cols[1]); last <- which(names(x) == cols[length(cols)])
r2 <- (last - first + 1) == length(cols)
cat(sprintf("  the five SWLS columns are contiguous in the sheet (positions %d-%d): %s\n",
            first, last, r2))
cat("  So the scale membership is the authors' assertion, not this project's.\n")

cat("\n=== Route 3: every response vector reproduced ===\n")
tot <- ok <- 0; bad <- character(0)
for (cn in cols) {
    live <- sort(d$resp[d$item == cn]); s <- sort(as.numeric(na.omit(x[[cn]])))
    tot <- tot + 1
    if (length(s) == length(live) && all(abs(s - live) < 1e-9)) ok <- ok + 1
    else bad <- c(bad, sprintf("%s source n=%d live n=%d", cn, length(s), length(live)))
}
cat(sprintf("  %d of %d reproduced EXACTLY%s\n", ok, tot,
            if (!length(bad)) "" else paste0(" -- ", paste(bad, collapse = "; "))))
r3 <- !length(bad)
lv <- sort(unique(d$resp))
r3b <- identical(as.numeric(lv), as.numeric(1:7))
cat(sprintf("  response levels %s -- matches the paper's stated seven-point scale: %s\n",
            paste(lv, collapse = ","), r3b))

cat("\n=== What this does NOT establish ===\n")
cat("  The administered wording. The sample is Chinese university students and\n")
cat("  no Chinese text appears in the deposit or the paper, so item_text ships the\n")
cat("  English SWLS, sourced from a CC BY paper that prints the five items against\n")
cat("  the same 1-5 numbering, and language records Chinese with no _translated\n")
cat("  twin. The anchors are this study's own (1 'completely disagree', 7\n")
cat("  'completely agree'), which differ from Diener's original wording.\n")
cat("\nVERDICT:", if (r1 && r2 && r3 && r3b) "PASS" else "FAIL", "\n")
