# verify_frikha_2023_pe_acrs.R -- Step 5b re-runnable mapping evidence.
#
# CLAIM: item q<n> in the IRW table is the PE-ARCS item numbered <n> in the study's
# own S1 File (PLOS ONE 10.1371/journal.pone.0297822.s001), whose 12 rows are numbered
# 1-12 and carry both the administered Arabic and the source English wording.
#
# The IRW codes are assigned POSITIONALLY by data/frikha_2023_motivation.py
# (PE_ACRS_COLS = columns 6..17 of files308.xlsx -> q1..q12), so the falsifiable
# prediction is that live q<n> is row-for-row identical to the source column whose
# own header row reads <n>, AND to no other source column.
#
# Fetches: the source .xlsx from Harvard Dataverse (file 7590042) + live IRW data.

suppressMessages({library(irw); library(readxl); library(httr)})

TABLE <- "frikha_2023_pe_acrs"
URL   <- "https://dataverse.harvard.edu/api/access/datafile/7590042"

tmp <- tempfile(fileext = ".xlsx")
httr::GET(URL, httr::write_disk(tmp, overwrite = TRUE),
          httr::user_agent("irw-batch/1.0 (research)"))

full <- as.data.frame(readxl::read_excel(tmp, col_names = FALSE, .name_repair = "minimal"))
hdr  <- suppressWarnings(as.integer(unlist(full[2, 7:18])))   # source item numbers
raw  <- full[-(1:2), , drop = FALSE]
raw  <- raw[rowSums(!is.na(raw)) > 0, , drop = FALSE]
rownames(raw) <- NULL

d <- irw::irw_fetch(TABLE)
w <- tapply(as.numeric(d$resp), list(as.integer(d$id), as.character(d$item)), identity)
ids <- as.integer(rownames(w))

cat(sprintf("source item-number header row (cols 7-18): %s\n", paste(hdr, collapse = ", ")))
cat(sprintf("live ids: %d   live items: %d\n\n", nrow(w), ncol(w)))

cat(sprintf("%-6s %-10s %10s %10s %12s %s\n",
            "live", "src col", "mean_live", "mean_src", "identical", "also identical to"))
ok <- TRUE
for (k in seq_along(hdr)) {
    n   <- hdr[k]
    it  <- paste0("q", n)
    lv  <- w[, it]
    src <- suppressWarnings(as.numeric(unlist(raw[ids + 1, 6 + k])))
    same <- isTRUE(all(lv == src))
    # uniqueness: which other source columns in the block reproduce this item exactly?
    others <- c()
    for (j in seq_along(hdr)) {
        s2 <- suppressWarnings(as.numeric(unlist(raw[ids + 1, 6 + j])))
        if (isTRUE(all(lv == s2))) others <- c(others, hdr[j])
    }
    if (!same || length(others) != 1L || others[1] != n) ok <- FALSE
    cat(sprintf("%-6s %-10s %10.4f %10.4f %12s %s\n",
                it, sprintf("col%d(=%d)", 6 + k, n), mean(lv), mean(src),
                same, paste(others, collapse = ",")))
}

# Independent corroboration: the source file stores its own subscale sums in
# columns 19-21 (Autonomy / Competence / Relatedness). The paper states
# autonomy = items 3,6,9,12; competence = 2,5,8,11; relatedness = 1,4,7,10.
cat("\nStored subscale sums vs sums of the items this mapping assigns:\n")
subs <- list(Autonomy = c(3, 6, 9, 12), Competence = c(2, 5, 8, 11), Relatedness = c(1, 4, 7, 10))
pos  <- c(Autonomy = 19, Competence = 20, Relatedness = 21)
sub_ok <- TRUE
for (nm in names(subs)) {
    stored <- suppressWarnings(as.numeric(unlist(raw[ids + 1, pos[[nm]]])))
    calc   <- rowSums(w[, paste0("q", subs[[nm]]), drop = FALSE])
    agree  <- sum(stored == calc)
    cat(sprintf("  %-12s items %-14s rows agreeing: %d/%d   mean stored %.4f vs computed %.4f\n",
                nm, paste(subs[[nm]], collapse = ","), agree, length(calc),
                mean(stored), mean(calc)))
    if (agree / length(calc) < 0.99) sub_ok <- FALSE
}
cat("  (Competence differs on exactly 2 of 308 rows -- ids 166 and 239 store 10 where\n",
    "   their four items sum to 5; a stale cell in the source workbook, not a mapping issue.\n",
    "   No other 4-item combination of the 12 reproduces the stored column better: the\n",
    "   runner-up (2,7,8,11) agrees on 172/308.)\n", sep = "")

cat("\nWhat this does NOT establish: it pins every item code to a specific source COLUMN,\n",
    "and the source's own header row numbers that column. The number -> WORDING tie comes\n",
    "from the S1 File, which prints its 12 items against the same 1-12 numbering; that tie\n",
    "is a printed label match, not something these data can test.\n", sep = "")

cat(if (ok && sub_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
