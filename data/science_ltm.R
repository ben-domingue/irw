## science_ltm: Eurobarometer 38.1 (1992) attitudes to science and technology, Great
## Britain, 392 complete cases, as shipped in ltm::Science (7 items, 4 categories).
##
## The table had no processing script; this one reproduces the published table
## (id = row number, resp = factor code 1-4, resp_raw = factor label) with one
## deliberate change (irw#2513, decided 2026-09-28).
##
## Environment, Technology and Industry are the three negatively worded statements.
## ltm labels every item 1 = "strongly disagree" .. 4 = "strongly agree", but for
## these three the data are scored so that a high value favours science: the GB
## ballot-B marginals in the Eurobarometer 38.1 codebook (GESIS ZA2295, doi:10.4232/1.10904)
## match the data only when 4 is read as "strongly disagree" (total variation distance
## 0.02-0.03 that way, 0.37-0.70 the other way; see
## itemtext/itemtables/batch_169/verify_science_ltm.R). So resp is kept as ltm codes it
## and only resp_raw's labels are reversed for those three items, which also makes
## resp_raw agree with the published item text.
library(ltm)

x <- Science
lev <- levels(x[[1]])   # "strongly disagree" "disagree" "agree" "strongly agree"
stopifnot(all(sapply(x, function(v) identical(levels(v), lev))))
reversed <- c("Environment", "Technology", "Industry")

L <- list()
for (nm in names(x)) {
    resp <- as.integer(x[[nm]])
    labels <- if (nm %in% reversed) rev(lev) else lev
    L[[nm]] <- data.frame(id = seq_len(nrow(x)), item = nm, resp = resp,
                          resp_raw = labels[resp], stringsAsFactors = FALSE)
}
df <- do.call(rbind, L)
rownames(df) <- NULL
write.csv(df, "science_ltm.csv", row.names = FALSE)
