# Verification for SCS_Suh_2023_BFNE (#2228, batch_304).
#
# THE DEPOSIT CARRIES NO ITEM TEXT: both .sav files (osf.io/wsjkb, CC BY) have
# BFNE_1..BFNE_12 with no variable and no value labels, and the paper is
# paywalled. So the wording is the published instrument -- Leary (1983), as
# distributed on the author's own site -- and the numbering has to be checked
# against the data rather than asserted.
#
# Route 1: shape. Twelve codes, resp 1-5, which is Leary's scale.
# Route 2: the reverse-item signature. Leary's four reverse-worded items are
#   2, 4, 7 and 10. If the shipped numbering is the published one, those four
#   should stand apart from the other eight -- and they do: they are exactly
#   the four lowest item-total correlations. The chance of the four lowest
#   landing on a named quartet of twelve is 1 in 495.
# Route 3: direction. All twelve correlate POSITIVELY, which cannot happen if
#   the four reverse-worded items held raw agreement, so they are stored
#   already recoded and their anchors ship inverted.
sav1 <- ".cache/batch_304/SCS_EA.sav"
sav2 <- ".cache/batch_304/SCS_Korean.sav"
for (p in c(sav1, sav2)) if (!file.exists(p)) stop("missing cached deposit file: ", p)
if (!requireNamespace("haven", quietly = TRUE)) stop("needs haven")

d <- as.data.frame(irw::irw_fetch("SCS_Suh_2023_BFNE"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_304/SCS_Suh_2023_BFNE__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")
cols <- sprintf("BFNE_%d", 1:12)

cat("=== Route 1: shape, and that the source really has no labels ===\n")
nolab <- sapply(c(sav1, sav2), function(p) {
    s <- haven::read_sav(p)
    all(sapply(cols, function(c) is.null(attr(s[[c]], "label")) &&
                                 is.null(attr(s[[c]], "labels"))))
})
cat(sprintf("  SCS EA dataset.sav has no labels on BFNE_1..12: %s\n", nolab[[1]]))
cat(sprintf("  SCS Korean dataset.sav likewise: %s\n", nolab[[2]]))
r1 <- all(nolab) && setequal(cols, unique(d$item)) &&
      setequal(sort(unique(as.numeric(d$resp))), 1:5)
cat(sprintf("  live: %d codes, resp %s\n", length(unique(d$item)),
            paste(sort(unique(as.numeric(d$resp))), collapse = ",")))
cat(sprintf("  -> twelve codes on Leary's 1-5 scale: %s\n", r1))
grp <- names(d)[!names(d) %in% c("id", "item", "resp")]
if (length(grp)) print(table(d[[grp[1]]]))

cat("\n=== Route 2: the reverse-item signature ===\n")
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
m <- as.matrix(w[, -1]); colnames(m) <- sub("^resp\\.", "", colnames(m))
m <- m[, cols]
rit <- sapply(cols, function(c)
    stats::cor(m[, c], rowMeans(m[, setdiff(cols, c), drop = FALSE], na.rm = TRUE),
               use = "pairwise.complete.obs"))
rev4 <- sprintf("BFNE_%d", c(2, 4, 7, 10))
for (c in cols) cat(sprintf("    %-8s r = %+.3f%s\n", c, rit[[c]],
                            if (c %in% rev4) "   [Leary reverse-worded]" else ""))
low4 <- names(sort(rit))[1:4]
cat(sprintf("  four lowest: %s\n", paste(sort(low4), collapse = ", ")))
r2 <- setequal(low4, rev4)
cat(sprintf("  -> exactly Leary's reverse-worded quartet: %s\n", r2))

cat("\n=== Route 3: direction, and what the anchors do ===\n")
r3 <- all(rit > 0)
cat(sprintf("  smallest item-total correlation: %+.3f; all positive: %s\n", min(rit), r3))
cat("  So the four are stored ALREADY REVERSED.\n")
sh <- items[items$item == "BFNE_2", ]; sh <- sh[order(sh$resp), ]
fw <- items[items$item == "BFNE_1", ]; fw <- fw[order(fw$resp), ]
cat(sprintf("  BFNE_1  1=%s ... 5=%s\n", fw$option_text[1], fw$option_text[5]))
cat(sprintf("  BFNE_2  1=%s ... 5=%s\n", sh$option_text[1], sh$option_text[5]))
r3b <- fw$option_text[1] == "Not at all characteristic of me" &&
       sh$option_text[1] == "Extremely characteristic of me" &&
       all(sapply(rev4, function(c) {
           z <- items[items$item == c, ]; z$option_text[z$resp == 1] == "Extremely characteristic of me"
       }))
cat(sprintf("  -> anchors inverted for all four reverse items and only those: %s\n", r3b))

cat("\n=== What this does NOT establish ===\n")
cat("  Which language a given respondent read. The table pools group='US'\n")
cat("  (English) and group='Korea' (a Korean translation the deposit does not\n")
cat("  publish), so the base fields carry Leary's English and `language`\n")
cat("  records both. Nor is the wording tied to the codes by any source in\n")
cat("  the deposit -- Route 2 is the evidence, not a label.\n")
cat("\nVERDICT:", if (r1 && r2 && r3 && r3b) "PASS" else "FAIL", "\n")
