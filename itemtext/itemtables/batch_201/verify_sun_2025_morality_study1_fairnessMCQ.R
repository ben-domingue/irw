## verify_sun_2025_morality_study1_fairnessMCQ.R  --  batch_201, issue #1945
##
## Route 6, keying polarity. Wording comes from the deposit's own label file keyed
## mv.<INSTRUMENT>.<FACET><n>, while the response columns are it.<INSTRUMENT>.<FACET><n>
## -- same instrument, facet and number, differing only in the rater-frame prefix.
## That substitution is the one inference in this table, and the reverse-worded item
## tests it: if the wording landed on the wrong items, the sign pattern breaks.
##
## Pins the polarity CLASS of all four items and identifies the reverse-worded
## singleton outright. It does NOT separate the three same-signed items from each
## other, which is why the mapping_verification row reads PARTIAL.
##
## Run from itemtext/:  Rscript itemtables/batch_201/verify_sun_2025_morality_study1_fairnessMCQ.R
suppressMessages({options(irw.itemtext_disclaimer = FALSE); library(irw)})
TBL <- "sun_2025_morality_study1_fairnessMCQ"
REV <- "itmcqf3"
fail <- character(0)

d <- tryCatch(as.data.frame(irw_fetch(TBL)), error = function(e) NULL)
if (is.null(d) || !nrow(d)) {
    cat("live data unavailable -- nothing checked\n"); cat("VERDICT: FAIL\n"); quit(status = 0)
}
d$item <- as.character(d$item)
codes <- sort(unique(d$item))
ids <- unique(d$id)
m <- matrix(NA_real_, length(ids), length(codes), dimnames = list(NULL, codes))
for (nm in codes) {
    s <- d[d$item == nm, , drop = FALSE]
    m[match(s$id, ids), nm] <- as.numeric(s$resp)
}
cm  <- cor(m, use = "pairwise.complete.obs")
avg <- (rowSums(cm) - 1) / (ncol(cm) - 1)

cat("=== mean r with the other items ===\n")
for (nm in codes)
    cat(sprintf("  %-9s %+.3f%s\n", nm, avg[nm],
                if (nm == REV) "   <- reverse-worded per the label file" else ""))

it <- read.csv(file.path("itemtables/batch_201", paste0(TBL, "__items.csv")),
               stringsAsFactors = FALSE)
cat("\nshipped wording for the reverse-worded item:\n  ",
    unique(it$item_text[it$item == REV]), "\n\n")

others <- setdiff(codes, REV)
if (!(avg[REV] < 0 && all(avg[others] > 0))) {
    cat("the reverse-worded item is NOT the sole negative -- polarity does not reproduce\n")
    fail <- c(fail, "polarity pattern does not match the label file's wording")
} else {
    cat(sprintf("clean separation: %s is the only negative (%+.3f), the other three run %+.3f to %+.3f\n",
                REV, avg[REV], min(avg[others]), max(avg[others])))
}

si <- identical(sort(unique(it$item)), codes)
sr <- identical(sort(unique(as.numeric(it$resp))),
                sort(unique(as.numeric(d$resp[!is.na(d$resp)]))))
cat("item set identical:", si, "| resp set identical:", sr, "| live rows:", nrow(d), "\n")
if (!si || !sr) fail <- c(fail, "live set mismatch")

cat("\n", strrep("-", 60), "\n", sep = "")
if (length(fail)) { cat("VERDICT: FAIL\n"); cat(paste0("  - ", fail, collapse = "\n"), "\n")
} else            { cat("VERDICT: PASS\n") }
