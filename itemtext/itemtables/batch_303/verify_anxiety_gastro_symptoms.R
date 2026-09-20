# Verification for anxiety_gastro_symptoms (#2228, batch_303).
#
# MAPPING BASIS IS data_labels, SO THERE IS NO MAPPING STEP TO VERIFY: the live
# item codes aehas1..aehas15 are the .sav's own column names and every column
# carries both a variable label (the item) and a value-label set (the anchors).
#
# Route 1: shipped item_text and option_text are the .sav's labels, verbatim.
# Route 2: the 0-4 value codes in the .sav become 1-5 in IRW because
#   data/anxiety_gastro_symptoms.R converts to factor and match()es the label
#   vector -- so resp = sav value + 1. Reproduce the live cell counts from the
#   deposit under that rule.
# Route 3: the 9/6 subscale split shipped in the instrument string is the
#   deposit's own CFA code, not this project's reading of the items.
sav <- ".cache/batch_303/EHAS_CFA.sav"
if (!file.exists(sav)) stop("missing cached deposit file: ", sav)
if (!requireNamespace("haven", quietly = TRUE)) stop("needs haven")

d <- as.data.frame(irw::irw_fetch("anxiety_gastro_symptoms"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_303/anxiety_gastro_symptoms__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA", encoding = "UTF-8")
s <- haven::read_sav(sav)
cols <- paste0("aehas", 1:15)

cat("=== Route 1: shipped text == .sav labels ===\n")
lab <- sapply(cols, function(c) trimws(attr(s[[c]], "label")))
sh <- unique(items[, c("item", "item_text")]); sh <- sh[match(cols, sh$item), ]
r1a <- all(sh$item_text == unname(lab)) && setequal(cols, unique(d$item))
for (i in seq_along(cols)) cat(sprintf("  %-8s %s\n", cols[i], substr(lab[i], 1, 84)))
vl <- attr(s$aehas1, "labels"); anch <- names(vl)[order(vl)]
allsame <- all(sapply(cols, function(c) identical(names(attr(s[[c]], "labels"))[order(attr(s[[c]], "labels"))], anch)))
o <- items[items$item == "aehas1", ]; o <- o$option_text[order(o$resp)]
r1b <- allsame && identical(unname(o), anch)
cat(sprintf("  anchors identical across all 15 columns: %s\n", allsame))
cat(sprintf("  shipped anchors: %s\n", paste(o, collapse = " | ")))
cat(sprintf("  -> labels and anchors reproduced: %s\n", r1a && r1b))

cat("\n=== Route 2: the 0-4 -> 1-5 shift, reproduced cell by cell ===\n")
src <- do.call(rbind, lapply(cols, function(c) {
    v <- as.numeric(s[[c]]); v <- v[!is.na(v)]
    data.frame(item = c, resp = v + 1, stringsAsFactors = FALSE)
}))
ts <- as.data.frame(table(src$item, src$resp), stringsAsFactors = FALSE)
tl <- as.data.frame(table(d$item, as.numeric(d$resp)), stringsAsFactors = FALSE)
names(ts) <- names(tl) <- c("item", "resp", "n")
m <- merge(ts, tl, by = c("item", "resp"), all = TRUE)
r2 <- nrow(m) == 75 && all(m$n.x == m$n.y) && nrow(src) == nrow(d)
cat(sprintf("  cells compared: %d   rows src=%d live=%d\n", nrow(m), nrow(src), nrow(d)))
cat(sprintf("  -> every cell reproduced under resp = sav value + 1: %s\n", r2))

cat("\n=== Route 3: the subscale split is the deposit's ===\n")
cat("  'Modified EHAS CFA code for R.docx' (osf.io/gh624) fits\n")
cat("    ANX =~ aehas1 .. aehas9 ;  HYP =~ aehas10 .. aehas15\n")
r3 <- grepl("aehas1-aehas9 form the anxiety subscale", items$instrument[1], fixed = TRUE)
cat(sprintf("  -> the instrument string states exactly that split: %s\n", r3))

cat("\n=== What this does NOT establish ===\n")
cat("  The administered stem and instructions. The .sav carries item text and\n")
cat("  anchors but no instruction block, and none is deposited, so\n")
cat("  instructions/section_prompt are left empty rather than reconstructed.\n")
cat("\nVERDICT:", if (r1a && r1b && r2 && r3) "PASS" else "FAIL", "\n")
