# verify_much_tte_2025_matrixreasoning.R
#
# CLAIM UNDER TEST: the `correct_response` shipped for each item MR01..MR20 is
# that item's own OMIB solution key -- i.e. the per-item content we ship is
# attached to the right item code, not permuted across items.
#
# (No `item_text` is shipped: the OMIB stimuli are 3x3 figural matrices published
# only as images in mr_ItemOverview.pdf, so under the 2026-09-05 picture-stimulus
# ruling item_text is blank by design. `correct_response` is therefore the only
# per-item content that CAN be mis-assigned, and it is what this script checks.)
#
# THE TEST: the study's raw file stores, per participant per item, the raw 20-bit
# element-selection string (X_MRnn_ww) AND the authors' own 0/1 scoring
# (Y_MRnn_ww). Scoring X with the shipped key must reproduce Y exactly. A permuted
# key breaks immediately. Uses only the OSF deposit -- no Redivis export.

items  <- sprintf("MR%02d", 1:20)

# Resolve paths relative to THIS script, not the caller's cwd: verify_batch.R
# invokes it from itemtext/, while a hand re-run happens inside the batch dir.
.args <- commandArgs(trailingOnly = FALSE)
.sf   <- sub("^--file=", "", .args[grep("^--file=", .args)])
scriptdir <- if (length(.sf)) dirname(normalizePath(.sf)) else getwd()
cachedir <- file.path(scriptdir, "..", "..", ".cache", "much_tte_2025_matrixreasoning")
get <- function(name, url) {
  p <- file.path(cachedir, name)
  if (!file.exists(p)) { p <- tempfile(fileext = paste0("_", name)); download.file(url, p, quiet = TRUE) }
  p
}
dat <- read.csv(get("tte_data.csv",         "https://osf.io/download/p25gr/"), colClasses = "character")
key <- read.csv(get("mr_itemsolutions.csv", "https://osf.io/download/yvx7k/"), colClasses = "character")

# the key as SHIPPED in the items csv, not re-read from the deposit
shipped <- read.csv(file.path(scriptdir, "much_tte_2025_matrixreasoning__items.csv"), colClasses = "character")
shipped <- unique(shipped[, c("item", "correct_response")])
rownames(shipped) <- shipped$item

strip <- function(x) gsub("'", "", trimws(x))

cat(sprintf("%-6s %6s %14s %10s %26s\n", "item", "n", "agree(own key)", "p(correct)", "best-agreeing OTHER key"))
tot <- 0; agr <- 0; ok <- TRUE; ambiguous <- character()
for (it in items) {
  w  <- if (as.integer(substr(it, 3, 4)) <= 10) "_01" else "_02"
  x  <- strip(dat[[paste0("X_", it, w)]])
  y  <- dat[[paste0("Y_", it, w)]]
  use <- x != "" & !is.na(y) & y != "" & y != "NA"
  x <- x[use]; y <- as.integer(y[use])
  mine <- shipped[it, "correct_response"]
  a <- sum(as.integer(x == mine) == y)
  # strongest rival: the best-agreeing key belonging to some OTHER item
  rival <- sapply(setdiff(items, it), function(o)
             mean(as.integer(x == strip(key$solutionCode[key$item == o])) == y))
  b <- which.max(rival)
  if (rival[b] >= 1) ambiguous <- c(ambiguous, sprintf("%s~%s", it, names(rival)[b]))
  cat(sprintf("%-6s %6d %8d/%-5d %10.3f %20s %.4f\n",
              it, length(x), a, length(x), mean(y), names(rival)[b], rival[b]))
  tot <- tot + length(x); agr <- agr + a
  if (a != length(x)) ok <- FALSE
}
cat(sprintf("\nTOTAL exact agreement with shipped keys: %d/%d\n", agr, tot))

cat("\nWhat this does NOT establish:\n")
cat(" - no item_text is shipped, so nothing about item wording is tested here;\n")
cat(" - MR11 and MR12 carry an IDENTICAL published solution code\n")
cat("   ('01000000000000000000'), so this route cannot tell them apart. Their tie\n")
cat("   to the item code rests on the codebook's number-preserving column names\n")
cat("   (X_MR11_02/Y_MR11_02 -> MR11), and a swap between them would be inert\n")
cat("   because their shipped correct_response is the same string.\n")
if (length(ambiguous)) cat("   mutually indistinguishable pairs found: ",
                           paste(ambiguous, collapse = ", "), "\n", sep = "")

cat(if (ok && tot > 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
