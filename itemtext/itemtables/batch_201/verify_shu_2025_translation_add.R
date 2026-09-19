## verify_shu_2025_translation_add.R  --  batch_201, issue #1945
##
## There is no data-side route here: the article publishes no per-item statistics
## and the three questions share no structure a statistic could separate. What IS
## re-runnable is the wording itself, so this checks the shipped item_text against
## the source it came from -- the PLOS S1 File's "Part 4 : Additional questions"
## block -- rather than re-checking item counts, which validate_items.R already did.
##
## Run from itemtext/:  Rscript itemtables/batch_201/verify_shu_2025_translation_add.R
CSV <- "itemtables/batch_201/shu_2025_translation_add__items.csv"
SRC <- ".cache/shu_2025_translation/s002.txt"
fail <- character(0)

it <- read.csv(CSV, stringsAsFactors = FALSE)
if (!file.exists(SRC)) {
    cat("cached S1 File absent (", SRC, ") -- refetch from\n",
        "doi:10.1371/journal.pone.0318101.s002. Nothing checked.\n", sep = "")
    cat("VERDICT: FAIL\n"); quit(status = 0)
}
src <- paste(readLines(SRC, warn = FALSE), collapse = " ")
norm <- function(s) tolower(trimws(gsub("\\s+", " ", gsub("[^A-Za-z0-9 ]", " ", s))))
hay <- norm(src)

cat("=== each shipped item_text must occur verbatim in the S1 File ===\n")
u <- unique(it[, c("item", "item_text")])
for (k in seq_len(nrow(u))) {
    ok <- grepl(norm(u$item_text[k]), hay, fixed = TRUE)
    cat(sprintf("  %-32s %s\n", u$item[k], if (ok) "found" else "NOT FOUND"))
    if (!ok) fail <- c(fail, paste("item_text not in the source:", u$item[k]))
}

cat("\n=== the source's Part 4 block, for a human to read against the above ===\n")
i <- regexpr("Part 4", src, fixed = TRUE)
if (i > 0) cat(" ", substr(src, i, i + 330), "\n")

cat("\n=== what this does NOT establish ===\n")
cat("  Two of the three codes match their question on content:\n")
cat("    addreasontochooserehab        <- 'Why did you choose to study a therapy programme'\n")
cat("    addmyviewondevelopmentinrehab <- 'My personal views on the prospect of ...'\n")
cat("  The third, addcompetitioninreha, is assigned by ELIMINATION. Its code reads\n")
cat("  'competition' while the remaining question is about study pressure and career\n")
cat("  plans, so the content does not corroborate it. It also uses resp levels 1-4\n")
cat("  where the other two use 1-5, and no response options are published for any of\n")
cat("  the three, so that difference is unexplained. Hence PARTIAL, not VERIFIED.\n")

cat("\n", strrep("-", 60), "\n", sep = "")
if (length(fail)) { cat("VERDICT: FAIL\n"); cat(paste0("  - ", fail, collapse = "\n"), "\n")
} else            { cat("VERDICT: PASS\n") }
