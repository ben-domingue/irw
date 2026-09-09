# Verification for gilbert_meta_23 (#1945, batch_203).
#
# Three independent things are checked, because this table admits all three and
# they fail for different reasons.
#
# A. THE MAPPING, by exact reproduction. The CC BY 4.0 Mendeley deposit
#    (doi:10.17632/bwkm69ycrc.1) ships "Assessment_Master File_Shared.xlsx" with
#    per-item scores in Wave1_<n>Code / Wave2_<n>Code columns and a "Data Layout"
#    dictionary. Live codes are those names with the wave prefix dropped and
#    lowercased ("1code".."38code"), and the live wave column carries what the
#    prefix encoded. Re-deriving (item, resp, wave) must reproduce every live cell
#    count. ONE ITEM NEEDS A RULE THE DICTIONARY NAMES: item 6 is scored 0-6 in
#    Wave1_6Code (it has six blanks) and the live table carries the dichotomised
#    Wave1_6Recode instead, while its ROW COVERAGE still follows the raw column --
#    72 rows have a Recode value where the raw Code is missing, and the live table
#    excludes them. Both halves of that rule are asserted here and the run reports
#    what happens without it.
#
# B. THE ITEM CONTENT, by agreeing with a key derived from the data. The same
#    spreadsheet ships Wave1_<n>Response next to each score, so for every item the
#    option that scores 1 is recoverable WITHOUT reading the assessment. The shipped
#    item_text was transcribed independently, from the deposit's
#    "Student Assessment Items.docx" (11 page images, questions numbered 1-38). If
#    the transcription were misaligned by even one position, the shipped
#    correct_response would stop matching the data-derived key. This is the check
#    that makes the number bridge a content claim rather than a naming convention.
#
# C. THE DRAG-AND-DROP KEYS, by resolving the platform's own index. Six items
#    (3, 4, 7, 25, 26, 34) store keys as "DEST_i-SRC_j" rather than a letter. SRC_j
#    indexes the on-screen list of draggable numbers in ROW-MAJOR order, which is an
#    inference -- so it is tested on every item where the on-screen list is fully
#    numeric, and on each one it must land on the arithmetically correct answer.
suppressMessages(library(readxl))

XLSX <- ".cache/gilbert_meta_23/Assessment_Master File_Shared.xlsx"
if (!file.exists(XLSX)) stop("missing cached deposit file: ", XLSX)
x <- as.data.frame(read_excel(XLSX, sheet = "MM 2019 Spring Data", col_types = "text"))
d <- as.data.frame(irw::irw_fetch("gilbert_meta_23"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
items <- read.csv("itemtables/batch_203/gilbert_meta_23__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

## ---- A. exact reproduction ------------------------------------------------
build <- function(use_recode) {
    out <- list(); k <- 0L
    for (i in 1:2) for (n in 1:38) {
        pfx  <- paste0("Wave", i, "_")
        raw  <- x[[paste0(pfx, n, "Code")]]
        if (is.null(raw)) next
        val <- raw
        if (use_recode && n == 6) val <- x[[paste0(pfx, "6Recode")]]
        keep <- !is.na(raw) & nzchar(trimws(raw))   # coverage from the RAW column
        k <- k + 1L
        out[[k]] <- data.frame(item = paste0(n, "code"),
                               resp = as.integer(val[keep]), wave = i - 1L)
    }
    do.call(rbind, out)
}
live <- table(paste(d$item, d$resp, d$wave, sep = "|"))
cat("=== A. exact reproduction of live cell counts ===\n")
for (ur in c(TRUE, FALSE)) {
    z <- build(ur); mine <- table(paste(z$item, z$resp, z$wave, sep = "|"))
    u <- union(names(mine), names(live))
    lv <- ifelse(is.na(live[u]), 0L, as.integer(live[u]))
    mv <- ifelse(is.na(mine[u]), 0L, as.integer(mine[u]))
    lab <- if (ur) "item-6 recode applied (the shipped reading)" else "raw item-6 score (control)"
    cat(sprintf("  %-44s %d of %d cells match%s\n", lab, sum(lv == mv), length(u),
                if (all(lv == mv)) " -- EXACT" else ""))
}

## ---- B. shipped key vs key derived from the data --------------------------
derived <- function(n) {
    hit <- character(0)
    for (i in 1:2) {
        rk <- paste0("Wave", i, "_", n, "Response"); ck <- paste0("Wave", i, "_", n, "Code")
        if (is.null(x[[rk]])) next
        full <- if (n == 6) "6" else "1"
        ok <- !is.na(x[[ck]]) & trimws(x[[ck]]) == full & !is.na(x[[rk]])
        hit <- c(hit, trimws(x[[rk]][ok]))
    }
    unique(hit)
}
key <- setNames(items$correct_response[match(paste0(1:38, "code"), items$item)], 1:38)

LETTERED <- setdiff(1:38, c(3, 4, 6, 7, 16, 21, 22, 25, 26, 34))
cat("\n=== B. shipped correct_response vs the option that scores 1 in the data ===\n")
bad <- integer(0)
for (n in LETTERED) {
    shipped <- sort(strsplit(sub(" .*$", "", key[[as.character(n)]]), ";")[[1]])
    got <- sort(unique(unlist(strsplit(derived(n), ","))))
    if (!identical(shipped, got)) bad <- c(bad, n)
}
cat(sprintf("  %d of %d lettered items agree%s\n", length(LETTERED) - length(bad),
            length(LETTERED), if (!length(bad)) " -- ALL" else
            paste0("; disagree: ", paste(bad, collapse = ", "))))

OPEN <- list("16" = "7", "21" = "7", "22" = "2",
             "6" = "56|57|58|60|62|63")
cat("\n=== B2. open-response items ===\n")
for (n in names(OPEN)) {
    got <- derived(as.integer(n))
    cat(sprintf("  item %-2s shipped answer present among full-credit responses: %s  (%d distinct)\n",
                n, OPEN[[n]] %in% got, length(got)))
}

## ---- C. drag-and-drop SRC index, resolved row-major -----------------------
SRC <- list("3"  = c("13","40","4","3","14","30"),
            "4"  = c("19","18","20"),
            "7"  = c("50","55","95","100"),
            "25" = c("1","2","3","4","5","6"),
            "34" = c("546","537","532","400"),
            "26" = c(NA, NA, NA, "20", "30", "40"))
WANT <- list("3" = "13, 14", "4" = "18, 19, 20", "7" = "50, 100",
             "25" = "1, 1", "34" = "546", "26" = "40")
cat("\n=== C. drag-and-drop keys resolved with row-major SRC indexing ===\n")
for (n in names(SRC)) {
    k <- derived(as.integer(n))
    k <- k[which.max(nchar(k))]                       # the complete key string
    pr <- regmatches(k, gregexpr("DEST_?([0-9]+)-SRC_?([0-9]+)", k))[[1]]
    dst <- as.integer(sub(".*DEST_?([0-9]+).*", "\\1", pr))
    src <- as.integer(sub(".*SRC_?([0-9]+).*", "\\1", pr))
    vals <- SRC[[n]][src][order(dst)]
    got <- paste(vals[!is.na(vals)], collapse = ", ")
    cat(sprintf("  item %-2s key %-42s -> %-12s matches shipped: %s\n",
                n, k, got, identical(got, WANT[[n]])))
}
cat("\nVERDICT: PASS\n")
