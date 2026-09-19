# Verification for cucchi_2018_pts (#2228, batch_303).
#
# MAPPING BASIS IS data_labels, SO THERE IS NO MAPPING STEP TO VERIFY: the live
# item codes PTS1..PTS7 are the .sav's own column names and each column carries
# a variable label that states its item. This script checks that the shipped
# text IS those labels, and records the one deliberate override.
#
# Route 1: shipped item_text == the .sav variable labels, code for code.
# Route 2: the value labels. Five of seven columns carry an identical anchor
#   set; PTS4 and PTS7 differ in ways that can only be label-entry slips
#   ('Describe me well'; a whole set shifted down one). The shipped anchors are
#   the 5-of-7 set, and this script prints the two exceptions rather than
#   hiding them.
sav <- ".cache/batch_303/cucchi/peerj-06-5756-s003.sav"
if (!file.exists(sav)) stop("missing cached deposit file: ", sav)
if (!requireNamespace("haven", quietly = TRUE)) stop("needs haven")

d <- as.data.frame(irw::irw_fetch("cucchi_2018_pts"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
items <- read.csv("itemtables/batch_303/cucchi_2018_pts__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")
s <- haven::read_sav(sav)
cols <- paste0("PTS", 1:7)

cat("=== Route 1: shipped text == .sav variable labels ===\n")
lab <- sapply(cols, function(c) trimws(sub("^PTS[0-9]+: ", "", attr(s[[c]], "label"))))
sh <- unique(items[, c("item", "item_text")])
sh <- sh[match(cols, sh$item), ]
r1 <- all(sh$item_text == unname(lab)) && setequal(cols, unique(as.character(d$item)))
for (i in seq_along(cols)) cat(sprintf("  %-5s %s\n", cols[i], substr(lab[i], 1, 86)))
cat(sprintf("  -> all seven match, and equal the live item set: %s\n", r1))

cat("\n=== Route 2: the value labels, including the two that disagree ===\n")
vls <- lapply(cols, function(c) { v <- attr(s[[c]], "labels"); names(v)[order(v)] })
names(vls) <- cols
tab <- table(sapply(vls, paste, collapse = " | "))
modal <- names(tab)[which.max(tab)]
cat(sprintf("  distinct anchor sets across the seven columns: %d\n", length(tab)))
for (nm in names(tab)) cat(sprintf("    [%d col] %s\n", tab[[nm]], nm))
odd <- cols[sapply(vls, paste, collapse = " | ") != modal]
cat(sprintf("  columns departing from the 5-of-7 set: %s\n", paste(odd, collapse = ", ")))
shipped <- unique(items$option_text[order(items$resp)])
shipped <- items$option_text[items$item == "PTS1"][order(items$resp[items$item == "PTS1"])]
r2 <- paste(shipped, collapse = " | ") == modal && setequal(odd, c("PTS4", "PTS7"))
cat(sprintf("  shipped (all items): %s\n", paste(shipped, collapse = " | ")))
cat(sprintf("  -> shipped set is the modal one, exceptions are PTS4/PTS7: %s\n", r2))
cat("  The IRI's anchors are fixed across items; a scale does not relabel one\n")
cat("  item's response options, so these are slips in the .sav, not content.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  That the labels reproduce the IRI exactly. Three carry evident\n")
cat("  transcription slips ('ususally'; PTS3 'from my perspective' where the\n")
cat("  published item reads 'from their perspective'); they are shipped as the\n")
cat("  study recorded them, not silently corrected.\n")
cat("\nVERDICT:", if (r1 && r2) "PASS" else "FAIL", "\n")
