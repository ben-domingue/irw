# verify_petrowski_2019_sclk9.R
#
# This table is BLOCKED on instrument rights, so no __items.csv was written and
# there is no item-to-text mapping to verify. What IS re-runnable, and what this
# script re-runs, is the RIGHTS FINDING that produced the block -- the same shape
# as batch_124's verify_ozkurt_2026_paces_enjoyment.R.
#
# Claim under test: NCS Pearson, rights holder of the SCL-90-R from which the
# SCL-K-9's nine items are drawn, states terms that RESERVE RIGHTS (no
# reproduction of test items, no display, no redistribution, permission required
# to reproduce/translate) rather than merely disclaiming fitness -- so the
# irw#1945 test blocks the wording, notwithstanding that the PLOS ONE source
# article is CC BY 4.0 and prints all nine items in its Table 1.
#
# PASS = every reserved-right clause below is still present on the live page.
# This establishes NOTHING about any item-to-text correspondence.

URL <- "https://www.pearsonassessments.com/footer/terms-of-sale---use.html"
SHA_AT_EXTRACTION <- "58ed03a1f99624752fbfb372000586b312b7883da5733591d8639fcae8c63be3"

# Substrings quoted in notes_petrowski_2019_sclk9.csv, each one a reserved right.
CLAUSES <- c(
  "reproduction of test items, scales, scoring algorithms, scored directions, or other content, is strictly prohibited",
  "may not be displayed, reproduced, or performed",
  "without the prior written permission of Pearson",
  "must not be resold, re-licensed, transferred, or otherwise redistributed for any purpose",
  "Requests to reproduce, translate, modify, or adapt any Pearson Product must be submitted in writing"
)

ua <- "Mozilla/5.0 (X11; Linux x86_64)"
tmp <- tempfile(fileext = ".html")
ok <- tryCatch({
  utils::download.file(URL, tmp, quiet = TRUE,
                       headers = c("User-Agent" = ua))
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
cat(sprintf("bytes fetched      : %d\n", length(raw)))
cat(sprintf("sha256 at extraction: %s\n", SHA_AT_EXTRACTION))
cat(sprintf("sha256 now          : %s%s\n", ifelse(is.na(sha), "(digest pkg absent)", sha),
            ifelse(!is.na(sha) && identical(sha, SHA_AT_EXTRACTION), "  [byte-identical]",
                   "  [page bytes differ -- dynamic markup; clause grep below is the real test]")))

txt <- rawToChar(raw); Encoding(txt) <- "UTF-8"
# strip tags so a clause split across markup still matches on the text
txt <- gsub("<[^>]+>", " ", txt)
txt <- gsub("&amp;", "&", txt, fixed = TRUE)
txt <- gsub("[[:space:]]+", " ", txt)

hits <- vapply(CLAUSES, function(cl) grepl(cl, txt, fixed = TRUE), logical(1))
cat("\nreserved-right clauses still present on the rights holder's page:\n")
for (i in seq_along(CLAUSES))
  cat(sprintf("  [%s] %s\n", ifelse(hits[i], "FOUND", "GONE "), substr(CLAUSES[i], 1, 78)))
cat(sprintf("\n%d of %d clauses found\n", sum(hits), length(CLAUSES)))

cat("Note: this verifies only that the block still holds. It says nothing about which\n",
    "SCL-K-9 item text belongs to which of scl1..scl9 -- no item text was shipped, and\n",
    "that mapping was never checked against the paper's per-item statistics.\n", sep = "")

cat(if (all(hits)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
