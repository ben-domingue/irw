# verify_cdm_timss07.R -- Step 5b mapping verification.
#
# WHAT IS BEING VERIFIED
# The item codes in cdm_timss07 are IEA's own TIMSS item IDs, carried through
# data/cdm.R unchanged (`names(x)[i]` of data.timss07.G4.lee$data). The IEA
# "TIMSS 2007 Released Items: Mathematics Fourth Grade" PDF prints each item's
# ID as the page header above that item's wording, so the item_text <-> item tie
# is an explicit code label, not an order inference.
#
# This script tests the one thing a label match still leaves checkable: the PDF
# also states each item's BLOCK (M04 or M05), and the TIMSS booklet design makes
# that a falsifiable prediction about which students answered which item. If the
# code->wording tie were shifted or permuted across the two blocks, the predicted
# n pattern would break.
#
# Prediction from the released-items PDF's Block column:
#   the 14 items it assigns to block M04 are in booklet 4 only        -> n = 344
#   the 11 items it assigns to block M05 are in booklets 4 and 5      -> n = 698
#
# Data source: the CDM package itself (the IRW table's upstream source), so this
# runs offline and costs no Redivis export quota.

suppressMessages(library(CDM))
data(data.timss07.G4.lee)
d <- data.timss07.G4.lee$data

# Block assignment as printed in the released-items PDF (item -> block).
block <- c(
  M041052="M04", M041056="M04", M041069="M04", M041076="M04", M041281="M04",
  M041164="M04", M041146="M04", M041152="M04", M041258A="M04", M041258B="M04",
  M041131="M04", M041275="M04", M041186="M04", M041336="M04",
  M031303="M05", M031309="M05", M031245="M05", M031242A="M05", M031242B="M05",
  M031242C="M05", M031247="M05", M031219="M05", M031173="M05", M031085="M05",
  M031172="M05"
)

items <- names(block)
stopifnot(all(items %in% names(d)))

n_obs  <- colSums(!is.na(d[, items]))
n_pred <- ifelse(block == "M04", 344L, 698L)

cat("item        block  predicted_n  observed_n  ok\n")
for (i in items)
  cat(sprintf("%-10s  %-5s  %11d  %10d  %s\n",
              i, block[[i]], n_pred[[i]], n_obs[[i]],
              if (n_pred[[i]] == n_obs[[i]]) "yes" else "NO"))

ok_n <- all(n_pred == n_obs)
cat("\nblock-implied n reproduced for", sum(n_pred == n_obs), "of", length(items), "items\n")

# Stronger form of the same test: block membership must be an exact partition by
# booklet, not merely a matching count.
b4 <- d[d$idbook == 4, items]; b5 <- d[d$idbook == 5, items]
ans4 <- items[colSums(!is.na(b4)) > 0]
ans5 <- items[colSums(!is.na(b5)) > 0]
ok_part <- setequal(ans4, items) && setequal(ans5, items[block == "M05"])
cat("booklet 4 answers all 25 items:                     ", setequal(ans4, items), "\n")
cat("booklet 5 answers exactly the 11 block-M05 items:   ",
    setequal(ans5, items[block == "M05"]), "\n")

# The item set itself must be exactly the 25 the PDF documents.
ok_set <- setequal(grep("^M0", names(d), value = TRUE), items)
cat("source item set == the 25 documented released items:", ok_set, "\n\n")

cat("NOTE ON SCOPE: this pins each item to its BLOCK, and the block-to-wording\n")
cat("tie comes from the PDF printing the item ID above the item. It does NOT\n")
cat("independently order items within a block -- nothing in the response data\n")
cat("distinguishes two items in the same block. The within-block tie rests\n")
cat("entirely on the printed ID, which is an explicit label match.\n\n")

if (ok_n && ok_part && ok_set) cat("VERDICT: PASS\n") else cat("VERDICT: FAIL\n")
