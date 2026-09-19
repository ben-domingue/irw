# Verification for cordova2019_clinical_edu_environment (#2228, batch_303).
#
# SOURCE. Harvard Dataverse doi:10.7910/DVN/SHWNK1 (CC0), one file:
# JEEHP-19-043_5_00_4202.xlsx, the study's own Google Forms export. Its
# question headers ARE the administered Spanish item text, each prefixed with
# the item number that data/cordova2019_clinical_edu_environment.py turns into
# item_01..item_40. So this is a reproduction check, not a statistical one.
#
# Route 1: re-melt the deposit and reproduce the full item x resp contingency
#   table of the live IRW table, cell for cell.
# Route 2: the four PHEEM negative items (7, 8, 11, 13) are the four low-mean
#   items in the live data -- an independent confirmation of the numbering.
xl <- ".cache/batch_303/cordova.xlsx"
if (!file.exists(xl)) stop("missing cached deposit file: ", xl)
if (!requireNamespace("readxl", quietly = TRUE)) stop("needs readxl")

d <- as.data.frame(irw::irw_fetch("cordova2019_clinical_edu_environment"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_303/cordova2019_clinical_edu_environment__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA", encoding = "UTF-8")

x <- readxl::read_excel(xl)
hdr <- names(x)
num <- suppressWarnings(as.integer(sub("^([0-9]+)\\..*$", "\\1", hdr)))
keep <- !is.na(num) & grepl("^[0-9]+\\. ", hdr)
cat("=== Route 1: reproduce the table from the deposit ===\n")
cat(sprintf("  numbered question columns in the xlsx: %d (of %d)\n", sum(keep), length(hdr)))
src <- do.call(rbind, lapply(which(keep), function(j) {
    v <- suppressWarnings(as.numeric(x[[j]]))
    v <- v[!is.na(v)]
    data.frame(item = sprintf("item_%02d", num[j]), resp = v, stringsAsFactors = FALSE)
}))
ts <- as.data.frame(table(src$item, src$resp), stringsAsFactors = FALSE)
tl <- as.data.frame(table(d$item, as.numeric(d$resp)), stringsAsFactors = FALSE)
names(ts) <- names(tl) <- c("item", "resp", "n")
m <- merge(ts, tl, by = c("item", "resp"), all = TRUE, suffixes = c("_src", "_live"))
r1 <- nrow(m) == 200 && all(m$n_src == m$n_live)
cat(sprintf("  cells compared: %d   rows src=%d live=%d\n", nrow(m), nrow(src), nrow(d)))
cat(sprintf("  -> every item x resp cell count reproduced exactly: %s\n", r1))

cat("\n=== Route 2: the four PHEEM negative items ===\n")
mu <- tapply(as.numeric(d$resp), d$item, mean)
lo <- sort(names(mu)[mu < 2.5])
cat("  live per-item means below 2.5: ",
    paste(sprintf("%s (%.2f)", lo, mu[lo]), collapse = ", "), "\n")
r2 <- setequal(lo, sprintf("item_%02d", c(7, 8, 11, 13)))
cat(sprintf("  -> exactly items 7, 8, 11 and 13, the PHEEM's four negatives: %s\n", r2))
for (i in lo) cat(sprintf("     %s  %s\n", i, substr(unique(items$item_text[items$item == i]), 1, 72)))

cat("\n=== What this does NOT establish ===\n")
cat("  The anchor labels. The form stored 1-5 and no source publishes the\n")
cat("  Spanish labels; the paper states only that the scale runs 'totally in\n")
cat("  disagreement' to 'totally agree' scored 0-4, i.e. resp - 1. option_text\n")
cat("  is therefore left empty rather than reconstructed. The English in\n")
cat("  item_text_translated is an IRW rendering, not a published translation.\n")
cat("\nVERDICT:", if (r1 && r2) "PASS" else "FAIL", "\n")
