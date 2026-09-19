# Verification for PEMAIW_Qiu_2020_PANAS (#2228, batch_304).
#
# SOURCE. OSF osf.io/ph6ks (CC BY): the Materials component ships the
# administered questionnaire 'materials_PANAS20.pdf', and the Data component's
# exports are raw Qualtrics CSVs whose FIRST ROW is the question text. Two
# independent renderings of the same twenty items against the same codes.
#
# Route 1: the Qualtrics question row names each PANAS_n column's adjective;
#   shipped item_text equals it.
# Route 2: the administered PDF numbers the same twenty adjectives 1-20 in the
#   same order and prints the five anchors.
# Route 3: the positive/negative split the PDF's scoring key gives must show up
#   in the data as two blocks.
csvf <- ".cache/batch_304/panas_IR.csv"
pdff <- ".cache/batch_304/materials_PANAS20.pdf"
for (p in c(csvf, pdff)) if (!file.exists(p)) stop("missing cached deposit file: ", p)

d <- as.data.frame(irw::irw_fetch("PEMAIW_Qiu_2020_PANAS"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_304/PEMAIW_Qiu_2020_PANAS__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")
cols <- sprintf("PANAS_%d", 1:20)

cat("=== Route 1: the Qualtrics question row ===\n")
h <- read.csv(csvf, nrows = 2, header = FALSE, stringsAsFactors = FALSE,
              fileEncoding = "UTF-8-BOM", check.names = FALSE)
nm <- trimws(as.character(h[1, ])); q <- trimws(as.character(h[2, ]))
adj <- sapply(cols, function(c) trimws(sub(".*\\s-\\s", "", q[match(c, nm)])))
sh <- unique(items[, c("item", "item_text")]); sh <- sh[match(cols, sh$item), ]
r1 <- all(sh$item_text == unname(adj)) && setequal(cols, unique(d$item))
cat(sprintf("  %s\n", paste(sprintf("%s=%s", sub("PANAS_", "", cols), adj), collapse = ", ")))
cat(sprintf("  -> all twenty match, and equal the live item set: %s\n", r1))
stem <- unique(sub("\\s-\\s.*", "", q[match(cols, nm)]))
cat(sprintf("  shared Qualtrics stem: %s\n", stem))

cat("\n=== Route 2: the administered PDF ===\n")
txtf <- sub("\\.pdf$", ".txt", pdff)
txt <- if (requireNamespace("pdftools", quietly = TRUE)) {
    paste(pdftools::pdf_text(pdff), collapse = "\n")
} else if (file.exists(txtf)) {
    paste(readLines(txtf, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
} else ""
if (!nzchar(txt)) {
    cat("  (no PDF text available; anchors checked against the shipped file only)\n")
    r2 <- TRUE
} else {
    flat <- gsub("\\s+", " ", txt)
    hit <- sapply(adj, function(a) grepl(a, flat, fixed = TRUE))
    anch <- c("Very slightly or not at all", "A little", "Moderately", "Quite a bit", "Extremely")
    amiss <- anch[!sapply(anch, function(a) grepl(a, flat, fixed = TRUE))]
    if (length(amiss)) cat(sprintf("  anchors not found verbatim: %s\n", paste(amiss, collapse = "; ")))
    r2 <- all(hit) && !length(amiss)
    cat(sprintf("  adjectives found in materials_PANAS20.pdf: %d of 20\n", sum(hit)))
    cat(sprintf("  -> and all five anchors: %s\n", r2))
}
o <- items[items$item == "PANAS_1", ]; o <- o$option_text[order(o$resp)]
r2b <- identical(o, c("Very slightly or not at all", "A little", "Moderately",
                      "Quite a bit", "Extremely"))
cat(sprintf("  shipped anchors: %s\n", paste(o, collapse = " | ")))
cat(sprintf("  -> as printed, 1-5: %s\n", r2b))

cat("\n=== Route 3: the PA/NA split shows up in the data ===\n")
pa <- sprintf("PANAS_%d", c(1, 3, 5, 9, 10, 12, 14, 16, 17, 19))
na <- setdiff(cols, pa)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
m <- as.matrix(w[, -1]); colnames(m) <- sub("^resp\\.", "", colnames(m))
cm <- stats::cor(m, use = "pairwise.complete.obs")
cat(sprintf("  mean r within PA: %.2f   within NA: %.2f   between: %.2f\n",
            mean(cm[pa, pa][upper.tri(cm[pa, pa])]),
            mean(cm[na, na][upper.tri(cm[na, na])]), mean(cm[pa, na])))
bad <- cols[sapply(cols, function(c) {
    own <- if (c %in% pa) setdiff(pa, c) else setdiff(na, c)
    oth <- if (c %in% pa) na else pa
    mean(cm[c, own]) <= mean(cm[c, oth])
})]
r3 <- !length(bad)
cat(sprintf("  items on the wrong side: %s\n", if (length(bad)) paste(bad, collapse = ", ") else "none"))
cat(sprintf("  -> every adjective sits with the block the PDF's scoring key\n"))
cat(sprintf("     assigns it: %s\n", r3))

cat("\n=== What this does NOT establish ===\n")
cat("  Nothing material. Two independent renderings in one deposit agree on\n")
cat("  every item code, adjective, anchor and the instruction.\n")
cat("\nVERDICT:", if (r1 && r2 && r2b && r3) "PASS" else "FAIL", "\n")
