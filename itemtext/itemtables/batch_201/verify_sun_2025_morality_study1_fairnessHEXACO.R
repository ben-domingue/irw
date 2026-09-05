## verify_sun_2025_morality_study1_fairnessHEXACO.R  --  batch_201, issue #1945
##
## CORROBORATION ONLY. The mapping_verification row for this table reads
## NOT_NEEDED, because the study's own Codebook.xlsx sheet "Study 1" states the
## pairing outright: one row per it.* variable carrying its item text, subscale
## and response scale, and the live code is that variable name with dots stripped
## and lowercased. There is no inference left to verify.
##
## This script is kept because the check below is still a useful sanity read on
## the SHIPPED WORDING rather than on the mapping: the reverse-worded item(s)
## must show the opposite sign from the rest, and they do. If a future edit ever
## put the wording on the wrong codes, this would catch it.
##
## Superseded framing, recorded so the change is legible: an earlier version of
## this table drew wording from the deposit's normdat-labels.csv (`mv.` prefix)
## and treated mv.X.Fn -> it.X.Fn as "the one inference in this table", which
## this script then tested. That substitution was wrong -- `mv.` is the
## trait-norming study's stem-less label set, not Study 1's administered wording
## -- and it is no longer being made.
##
## Run from itemtext/:  Rscript itemtables/batch_201/verify_sun_2025_morality_study1_fairnessHEXACO.R
suppressMessages({options(irw.itemtext_disclaimer = FALSE); library(irw)})
TBL <- "sun_2025_morality_study1_fairnessHEXACO"
REV <- "ithhf3"
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
