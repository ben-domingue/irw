# verify_frikha_2023_pe_ms.R -- Step 5b re-runnable mapping evidence.
#
# CLAIM: item q<n> in the IRW table is the PE-MS item numbered <n> in the study's
# own S2 File (PLOS ONE 10.1371/journal.pone.0297822.s002), whose 9 rows are
# numbered 13-21 and carry both the administered Arabic and the source English
# wording.
#
# The IRW codes are assigned POSITIONALLY by data/frikha_2023_motivation.py
# (PE_MS_COLS = 0-based columns 21..29 of files308.xlsx -> q1..q9, then remapped
# q13..q21), so the falsifiable prediction is that live q<n> is row-for-row
# identical to the source column whose own header row reads <n>, AND to no other
# source column in the PE-MS block.
#
# Independent corroboration: the workbook stores its own subscale sums in
# 0-based columns 30-32 (IM / EM / AM). The S2 File's codification key assigns
# intrinsic = 13,16,19; extrinsic = 14,17,20; amotivation = 15,18,21 -- a
# prediction about which live items sum to which stored column.
#
# Fetches: the source .xlsx from Harvard Dataverse (file 7590042) + live IRW data.

suppressMessages({library(irw); library(readxl); library(httr)})

TABLE <- "frikha_2023_pe_ms"
URL   <- "https://dataverse.harvard.edu/api/access/datafile/7590042"

# Harvard Dataverse intermittently 504s on this endpoint (seen repeatedly
# 2026-09-05). Fall back to the cached copy, which is byte-identical
# (md5 7d9836427eaa5be4ca4d184793401228) to the file the API serves.
CACHE <- ".cache/frikha_2023_pe_ms/files308.xlsx"
tmp <- tempfile(fileext = ".xlsx")
ok_dl <- tryCatch({
    r <- httr::GET(URL, httr::write_disk(tmp, overwrite = TRUE),
                   httr::user_agent("irw-batch/1.0 (research)"))
    httr::status_code(r) == 200 &&
        identical(readBin(tmp, "raw", 2L), as.raw(c(0x50, 0x4b)))
}, error = function(e) FALSE)
if (!ok_dl) {
    cand <- c(CACHE, file.path("..", CACHE), file.path("../..", CACHE))
    hit  <- cand[file.exists(cand)]
    if (!length(hit)) stop("Dataverse fetch failed and no cached files308.xlsx found")
    tmp <- hit[1]
    cat(sprintf("Dataverse fetch failed; using cached copy %s (md5 %s)\n",
                tmp, tools::md5sum(tmp)))
} else cat("source workbook fetched live from Harvard Dataverse file 7590042\n")

full <- as.data.frame(readxl::read_excel(tmp, col_names = FALSE, .name_repair = "minimal"))
# R 1-based: python 0-based col 21..29 -> R col 22..30; header row 2 holds item numbers
hdr  <- suppressWarnings(as.integer(unlist(full[2, 22:30])))
raw  <- full[-(1:2), , drop = FALSE]
raw  <- raw[rowSums(!is.na(raw)) > 0, , drop = FALSE]
rownames(raw) <- NULL

d <- irw::irw_fetch(TABLE)
w <- tapply(as.numeric(d$resp), list(as.integer(d$id), as.character(d$item)), identity)
ids <- as.integer(rownames(w))

cat(sprintf("source item-number header row (0-based cols 21-29): %s\n",
            paste(hdr, collapse = ", ")))
cat(sprintf("live ids: %d   live items: %d\n\n", nrow(w), ncol(w)))

cat(sprintf("%-6s %-12s %10s %10s %12s %s\n",
            "live", "src col", "mean_live", "mean_src", "identical", "also identical to"))
ok <- TRUE
for (k in seq_along(hdr)) {
    n  <- hdr[k]
    it <- paste0("q", n)
    lv <- w[, it]
    src <- suppressWarnings(as.numeric(unlist(raw[ids + 1, 21 + k])))
    same <- isTRUE(all(lv == src))
    others <- c()
    for (j in seq_along(hdr)) {
        s2 <- suppressWarnings(as.numeric(unlist(raw[ids + 1, 21 + j])))
        if (isTRUE(all(lv == s2))) others <- c(others, hdr[j])
    }
    if (!same || length(others) != 1L || others[1] != n) ok <- FALSE
    cat(sprintf("%-6s %-12s %10.4f %10.4f %12s %s\n",
                it, sprintf("col%d(=%d)", 21 + k, n), mean(lv), mean(src),
                same, paste(others, collapse = ",")))
}

cat("\nStored subscale sums vs sums of the items this mapping assigns:\n")
subs <- list(IM = c(13, 16, 19), EM = c(14, 17, 20), AM = c(15, 18, 21))
pos  <- c(IM = 31, EM = 32, AM = 33)   # R 1-based = python 30,31,32
sub_ok <- TRUE
for (nm in names(subs)) {
    stored <- suppressWarnings(as.numeric(unlist(raw[ids + 1, pos[[nm]]])))
    calc   <- rowSums(w[, paste0("q", subs[[nm]]), drop = FALSE])
    agree  <- sum(stored == calc)
    cat(sprintf("  %-4s items %-12s rows agreeing: %d/%d   mean stored %.4f vs computed %.4f\n",
                nm, paste(subs[[nm]], collapse = ","), agree, length(calc),
                mean(stored), mean(calc)))
    if (agree / length(calc) < 0.99) sub_ok <- FALSE
}

# Rule out that some OTHER 3-item combination reproduces each stored sum as well.
cat("\n  runner-up 3-item combinations for each stored subscale column:\n")
combs <- combn(hdr, 3, simplify = FALSE)
for (nm in names(subs)) {
    stored <- suppressWarnings(as.numeric(unlist(raw[ids + 1, pos[[nm]]])))
    sc <- sapply(combs, function(cc) sum(rowSums(w[, paste0("q", cc), drop = FALSE]) == stored))
    o  <- order(sc, decreasing = TRUE)
    cat(sprintf("    %-4s best %s = %d/%d ; runner-up %s = %d/%d\n", nm,
                paste(combs[[o[1]]], collapse = ","), sc[o[1]], length(stored),
                paste(combs[[o[2]]], collapse = ","), sc[o[2]], length(stored)))
}

cat("\nWhat this does NOT establish: it pins every item code to a specific source COLUMN,\n",
    "and the source's own header row numbers that column. The number -> WORDING tie comes\n",
    "from the S2 File, which prints its 9 items against the same 13-21 numbering; that tie\n",
    "is a printed label match, not something these data can test.\n", sep = "")

cat(if (ok && sub_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
