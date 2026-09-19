# verify_pierro_2018_hfs_s4.R
#
# This table is BLOCKED on instrument rights, so no __items.csv was written and
# there is no item-to-text mapping to verify. What IS re-runnable, and what this
# script re-runs, is the RIGHTS FINDING that produced the block -- the same shape
# as batch_134's verify_petrowski_2019_sclk9.R and batch_124's
# verify_ozkurt_2026_paces_enjoyment.R.
#
# Claim under test: Laura Y. Thompson, rights holder of the Heartland Forgiveness
# Scale (HFS; items 1-6 are the Forgiveness of Self subscale this table
# administers), grants use only on a NON-COMMERCIAL, purpose-limited condition --
# a clause that RESERVES a right rather than disclaiming fitness -- so the
# irw#1945 test (as restated 2026-09-08) blocks the wording, notwithstanding that
# the PLOS ONE source article (10.1371/journal.pone.0193357) is CC BY 4.0 and
# prints all six items in its own Study 4 Measures section.
#
# PASS = the reserved-right clause is still present on the rights holder's page.
# This establishes NOTHING about any item-to-text correspondence.

URL <- "https://www.heartlandforgiveness.com/download-the-hfs"
SHA_AT_EXTRACTION <- "25062ecded001202f950d79d75626aa02058963d95a97df055951202b9a36a6a"

# Substrings quoted in notes_pierro_2018_hfs_s4.csv. The first is the reserved
# right itself (a non-commercial condition); the second and third are the grant
# and purpose limitation it conditions, kept so a partial rewrite is visible.
CLAUSES <- c(
  "you will not profit directly from use of the HFS",
  "If you want to use the HFS for research or clinical purposes",
  "you may use the HFS"
)

ua  <- "Mozilla/5.0 (X11; Linux x86_64)"
tmp <- tempfile(fileext = ".html")
ok <- tryCatch({
  utils::download.file(URL, tmp, quiet = TRUE, headers = c("User-Agent" = ua))
  TRUE
}, error = function(e) { message("fetch failed: ", conditionMessage(e)); FALSE })

if (!ok || !file.exists(tmp) || file.info(tmp)$size == 0) {
  cat("could not fetch", URL, "-- cannot re-confirm the clause\n")
  cat("VERDICT: FAIL\n")
  quit(status = 0)
}

raw <- readBin(tmp, "raw", file.info(tmp)$size)
sha <- if (requireNamespace("digest", quietly = TRUE))
           digest::digest(raw, algo = "sha256", serialize = FALSE) else NA_character_
cat(sprintf("bytes fetched       : %d\n", length(raw)))
cat(sprintf("sha256 at extraction: %s\n", SHA_AT_EXTRACTION))
cat(sprintf("sha256 now          : %s%s\n",
            ifelse(is.na(sha), "(digest pkg absent)", sha),
            ifelse(!is.na(sha) && identical(sha, SHA_AT_EXTRACTION),
                   "  [byte-identical]",
                   "  [page bytes differ -- Squarespace markup; the clause grep below is the real test]")))

txt <- rawToChar(raw); Encoding(txt) <- "UTF-8"
# strip tags so a clause split across markup still matches on the text
txt <- gsub("<[^>]+>", " ", txt)
txt <- gsub("&amp;", "&", txt, fixed = TRUE)
txt <- gsub("&#8217;", "'", txt, fixed = TRUE)
txt <- gsub("[[:space:]]+", " ", txt)

hits <- vapply(CLAUSES, function(cl) grepl(cl, txt, fixed = TRUE), logical(1))
cat("\nreserved-right clause still present on the rights holder's page:\n")
for (i in seq_along(CLAUSES))
  cat(sprintf("  [%s] %s\n", ifelse(hits[i], "FOUND", "GONE "), CLAUSES[i]))
cat(sprintf("\n%d of %d clause fragments found\n", sum(hits), length(CLAUSES)))

cat("\nNote: this verifies only that the block still holds. It says NOTHING about which\n",
    "HFS item text belongs to which of hfs1/hfsR2/hfs3/hfsR4/hfs5/hfsR6 -- no item text\n",
    "was shipped, the paper publishes no per-item statistics, and all six items share the\n",
    "same 1-7 range, so no statistical route could distinguish them in any case.\n", sep = "")

# The block is only meaningful if the wording is not already leaking through the
# response table's own item codes (irw#2101/#2123). Show that it is not.
codes <- c("hfs1", "hfsR2", "hfs3", "hfsR4", "hfs5", "hfsR6")
cat(sprintf("\nlive item codes carry no wording: %s\n", paste(codes, collapse = ", ")))

cat(if (hits[1]) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
