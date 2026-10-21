# Step 5b verification for huebner_2021_weightlifting_barriers.
#
# The claim: each item code in the __items.csv carries the wording the
# deposit's own codebook attaches to THAT data column -- not the wording of a
# neighbouring column.
#
# The route is the codebook's name join, re-derived here from the raw files
# rather than from the builder (itemtext_verification/make_itemtext_huebner_2021.py),
# so a bug in the builder cannot pass this. wldat_dictionary.xlsx has one row
# per data column; its `Item` cell IS the column name in wldat_dryad.csv. The
# check is that the join is bijective and that every shipped item_text equals
# the codebook stem for its own code.
#
# Usage: Rscript verify_huebner_2021_weightlifting_barriers.R <wldat_dictionary.xlsx> [items csv]
# Falls back to the live IRW copy of the items table when no path is given.

suppressMessages({library(readxl); library(irw)})

TABLE <- "huebner_2021_weightlifting_barriers"
PROMPT <- list(
  attraction = "The following aspects attract me to Masters weightlifting",
  barriers   = "The following aspects have been barriers / obstacles to my weightlifting.",
  pandemic   = "How much do you agree with the following statements")[["barriers"]]

args <- commandArgs(trailingOnly = TRUE)
cb <- as.data.frame(readxl::read_excel(args[1]))
names(cb)[1:2] <- c("Item", "Question")
cb$Item <- trimws(cb$Item)

items <- if (length(args) >= 2) utils::read.csv(args[2], stringsAsFactors = FALSE) else
  irw::irw_fetch_itemtext(TABLE)
items <- items[!duplicated(items$item), c("item", "item_text")]

norm <- function(x) tolower(gsub("withthe", "with the",
                   gsub("[[:space:]]+", " ", trimws(x))))
stem <- function(q) trimws(sub("^.*? - ", "", gsub("[[:space:]]+", " ", trimws(q))))
head_of <- function(q) trimws(sub(" - .*$", "", gsub("[[:space:]]+", " ", trimws(q))))

cat(sprintf("codebook rows: %d ; shipped items: %d\n", nrow(cb), nrow(items)))
cat(sprintf("%-18s %-62s %s\n", "item", "codebook stem for that item", "match"))
ok <- TRUE
for (i in seq_len(nrow(items))) {
  code <- items$item[i]
  row <- cb[cb$Item == code, , drop = FALSE]
  if (nrow(row) != 1L) { cat(sprintf("%-18s %-62s %s\n", code, "<no unique codebook row>", "FAIL")); ok <- FALSE; next }
  if (norm(head_of(row$Question[1])) != norm(PROMPT)) {
    cat(sprintf("%-18s %-62s %s\n", code, "<belongs to another block>", "FAIL")); ok <- FALSE; next
  }
  want <- stem(row$Question[1]); got <- items$item_text[i]
  hit <- norm(want) == norm(got)
  ok <- ok && hit
  cat(sprintf("%-18s %-62s %s\n", code, substr(want, 1, 62), if (hit) "ok" else paste0("FAIL <- shipped: ", got)))
}

# A reverse check: no codebook stem of this block is attached to the wrong code.
blk <- cb[norm(sapply(cb$Question, head_of)) == norm(PROMPT), ]
cat(sprintf("\ncodebook stems in this block: %d ; shipped items: %d ; bijective: %s\n",
            nrow(blk), nrow(items), identical(sort(blk$Item), sort(items$item))))
ok <- ok && identical(sort(blk$Item), sort(items$item))

cat("Note: this pins every item individually -- the tie is an exact name match\n",
    "given by the depositor, not an ordering or a statistical signal. What it does\n",
    "NOT establish is that the depositor's own codebook is right about her survey;\n",
    "no independent per-item published statistic exists for these blocks.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
