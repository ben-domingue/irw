# Shared verification for the three much_tte_2025_* tables (#2228, batch_300).
# Sourced by the per-table wrappers, which set TB, NITEM and NOT_ESTABLISHED.
#
# SOURCE. Much, Mutak, Pohl & Ranger (2025), 'Data From a Validation Study of
# Two Psychometric Models on Test-taking Behavior', Journal of Open Psychology
# Data 13(1), CC BY; deposit osf.io/9j6hm.
#
# THE DEPOSIT PRINTS THE ITEMS, which is unusual and is what makes these three
# straightforward. '2_Supplemental files' carries efcm_ItemOverview.pdf (the
# Effort and Current Motivation phrasings side by side with the original TTMI
# wording, plus the instruction text at each timepoint) and ct_ItemOverview.pdf
# (every concentration-task grid with its target letter and the number of times
# the target occurs). The response scales come from the paper's Methods.
#
# Route 1: the item set and the scale the paper states.
# Route 2: the shipped text is non-empty and distinct per item.
d <- as.data.frame(irw::irw_fetch(TB))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv(file.path("itemtables/batch_300", paste0(TB, "__items.csv")),
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: item set and response scale ===\n")
r1 <- setequal(unique(items$item), unique(d$item)) && length(unique(d$item)) == NITEM
cat(sprintf("  live items %d (expected %d), item sets identical: %s\n",
            length(unique(d$item)), NITEM, setequal(unique(items$item), unique(d$item))))
lv <- sort(unique(d$resp))
cat(sprintf("  resp levels: %s\n", paste(utils::head(lv, 12), collapse = ","),
            if (length(lv) > 12) " ..." else ""))
cat(sprintf("  %s\n", SCALE_NOTE))

cat("\n=== Route 2: every item carries distinct text ===\n")
tx <- unique(items[, c("item", "item_text")])
r2 <- nrow(tx) == NITEM && !any(is.na(tx$item_text)) && length(unique(tx$item_text)) == NITEM
cat(sprintf("  %d items, %d distinct item_text values, none blank: %s\n",
            nrow(tx), length(unique(tx$item_text)), r2))
for (i in seq_len(min(4, nrow(tx))))
    cat(sprintf("    %-7s %s\n", tx$item[i], substr(tx$item_text[i], 1, 68)))

cat("\n=== What this does NOT establish ===\n")
cat(NOT_ESTABLISHED)
cat("\nVERDICT:", if (r1 && r2) "PASS" else "FAIL", "\n")
