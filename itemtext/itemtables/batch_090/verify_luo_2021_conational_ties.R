# verify_luo_2021_conational_ties.R
#
# CLAIM UNDER TEST -----------------------------------------------------------
# data/luo_2021_acculturation.py assigns the IRW codes POSITIONALLY:
#     CONATIONAL_IDX = list(range(31, 35))
#     renamed = {c: f"item_{i+1:02d}" for i, c in enumerate(item_cols)}
# so item_01..item_04 are asserted to be columns 32..35 (1-based) of the study's
# S3 File .sav.  Those four columns carry their own item wording IN THE COLUMN
# NAME (SPSS strips spaces and truncates at 64 characters), which is where the
# shipped item_text comes from.  If the positional range were shifted, or if
# item_02 and item_03 were swapped, the shipped text would be wrong.
#
# THE FALSIFIABLE PREDICTION -------------------------------------------------
# For each item, the live 4-cell response distribution must equal the response
# distribution of the .sav column at that exact position -- cell for cell.  The
# four co-national columns have PAIRWISE DISTINCT distributions, so this
# fingerprint distinguishes every item from every other item; no permutation of
# the four codes reproduces it.  (Note the means alone do NOT: item_01 and
# item_04 both average 2.847162.  The full frequency table is what separates
# them, which is why this script compares cells and not means.)
#
# Hard-coded below are the .sav's own per-column frequencies at positions 32-35
# (1-based), read with pyreadstat from
#   https://doi.org/10.1371/journal.pone.0260616.s003
# together with the truncated 64-character column NAME at each position, which
# is the source string the shipped item_text extends.

suppressMessages(library(irw))

TABLE <- "luo_2021_conational_ties"

# position (1-based) -> exact 64-char SPSS column name in the S3 File .sav
SAV_NAME <- c(
  "32" = "Conationalties1.Howoftendidyourconationalfriendsreallylistentoyo",
  "33" = "@2.Howoftendidyourconationalfriendstrytotakeyourmindoffyourprobl",
  "34" = "@3.Howoftendidyourconationalfriendshelpyouinpracticalwayslikedoi",
  "35" = "@4.Howoftendidyourconationalfriendsansweryouquestionsorgiveyouad")

# counts of resp 1,2,3,4 in each of those .sav columns
SAV_FREQ <- rbind(
  "32" = c(25, 57, 75, 72),
  "33" = c(23, 67, 76, 63),
  "34" = c(24, 71, 61, 73),
  "35" = c(21, 69, 63, 76))
colnames(SAV_FREQ) <- c("1", "2", "3", "4")

CODES <- c("item_01", "item_02", "item_03", "item_04")   # claimed position order

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = CODES), factor(d$resp, levels = 1:4))

cat("A. Per-item response frequencies: .sav column at the claimed position vs live IRW\n\n")
cat(sprintf("%-8s %-6s %-22s %-22s %s\n",
            "item", "savcol", "sav 1/2/3/4", "live 1/2/3/4", "match"))
ok <- TRUE
for (i in seq_along(CODES)) {
  s <- SAV_FREQ[i, ]; l <- as.integer(live[i, ])
  m <- all(s == l); ok <- ok && m
  cat(sprintf("%-8s %-6s %-22s %-22s %s\n",
              CODES[i], rownames(SAV_FREQ)[i],
              paste(s, collapse = "/"), paste(l, collapse = "/"),
              if (m) "OK" else "MISMATCH"))
}

cat("\nB. Uniqueness of the fingerprint -- would any OTHER assignment also fit?\n")
perm_ok <- 0
for (p in list(c(1,2,3,4), c(1,2,4,3), c(1,3,2,4), c(1,3,4,2), c(1,4,2,3), c(1,4,3,2),
               c(2,1,3,4), c(2,1,4,3), c(2,3,1,4), c(2,3,4,1), c(2,4,1,3), c(2,4,3,1),
               c(3,1,2,4), c(3,1,4,2), c(3,2,1,4), c(3,2,4,1), c(3,4,1,2), c(3,4,2,1),
               c(4,1,2,3), c(4,1,3,2), c(4,2,1,3), c(4,2,3,1), c(4,3,1,2), c(4,3,2,1))) {
  if (all(SAV_FREQ[p, ] == matrix(as.integer(live), nrow = 4))) perm_ok <- perm_ok + 1
}
cat(sprintf("permutations of the 4 codes consistent with the live table: %d of 24\n", perm_ok))

cat("\nC. The shipped item_text extends the .sav column name at that position\n")
csvf <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)[1])),
                  paste0(TABLE, "__items.csv"))
if (!file.exists(csvf)) csvf <- file.path("itemtables", "batch_090", paste0(TABLE, "__items.csv"))
it <- unique(read.csv(csvf, stringsAsFactors = FALSE)[, c("item", "item_text")])
it <- it[match(CODES, it$item), ]
prefix_ok <- TRUE
for (i in seq_along(CODES)) {
  # strip the block/number prefix the .sav name carries, then de-space+de-punctuate both
  raw  <- sub("^(Conationalties1\\.|@[0-9]+\\.)", "", SAV_NAME[i])
  norm <- function(x) tolower(gsub("[^a-z]", "", tolower(x)))
  shipped <- norm(it$item_text[i])
  savtxt  <- norm(raw)
  m <- startsWith(shipped, savtxt); prefix_ok <- prefix_ok && m
  cat(sprintf("%-8s sav[%2d chars]: %s\n", CODES[i], nchar(savtxt), savtxt))
  cat(sprintf("%-8s shipped     : %s   -> %s\n", "", shipped,
              if (m) "sav name is a strict prefix" else "PREFIX MISMATCH"))
}

cat("\nWhat this does NOT establish: the 64-character SPSS cap truncates every column\n")
cat("name mid-word, so the TAIL of each shipped sentence (and all punctuation and word\n")
cat("spacing) is not verified here -- it was completed from the MDSS wording printed in\n")
cat("PMC12314320 and is documented in provenance. A and B verify WHICH source column\n")
cat("each item_NN is, and therefore which of the four MDSS questions it is; C verifies\n")
cat("that the shipped sentence begins with that column's own words.\n\n")

cat(if (ok && perm_ok == 1 && prefix_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
