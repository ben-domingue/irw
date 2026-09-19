# verify_ozkurt_2026_paces_enjoyment.R -- batch_124, 2026-09-09
#
# THIS TABLE SHIPPED NO ITEM TEXT. It is BLOCKED on instrument rights, so there is
# no item_text <-> item mapping to re-run: mapping_basis=unknown, Step 5b status
# NO_ROUTE. A mapping-verification script would have nothing to verify.
#
# What this script therefore re-runs is the claim the round actually made: that the
# rights holder's own page still carries the non-commercial clause the block rests on.
# That is the falsifiable statement here -- if the FAKO authors relicense, the block
# should be revisited, and this script is what notices.
#
#   VERDICT: PASS  = the clause is still present, the block still stands as recorded.
#   VERDICT: FAIL  = the clause is gone, changed, or could not be re-fetched.
#                    Either way a human should look before this table is re-queued.

TABLE   <- "ozkurt_2026_paces_enjoyment"
PDF_URL <- "https://dergipark.org.tr/tr/download/article-file/1899104"
REFERER <- "https://dergipark.org.tr/tr/pub/anemon/article/976300"
SHA256  <- "768390fd9f577b46e3e301e024b69adae12e258b89190cd0cc8936a091775b0f"

# The clause, as recorded on 2026-09-09 from the Ek-2 appendix of
# Ozkurt, Kucukibis & Eskiler (2022), Anemon 10(1):21-37 -- the Turkish PACES-8
# (FAKO) adaptation that this study administered.
CLAUSE <- "ticari amaç gütmeyen bilimsel çalışmalarda izin alınmaksızın"
# "may be used in NON-COMMERCIAL scientific studies WITHOUT obtaining permission,
#  provided the source is cited"

cat(sprintf("table            : %s\n", TABLE))
cat(sprintf("rights source    : %s\n", PDF_URL))
cat(sprintf("recorded sha256  : %s\n", SHA256))
cat(sprintf("clause sought    : %s\n\n", CLAUSE))

tmp <- tempfile(fileext = ".pdf")
ok <- tryCatch({
    utils::download.file(PDF_URL, tmp, quiet = TRUE, mode = "wb",
                         headers = c("User-Agent" = "Mozilla/5.0 (X11; Linux x86_64)",
                                     "Referer"    = REFERER))
    file.exists(tmp) && file.size(tmp) > 10000
}, error = function(e) { cat("fetch error: ", conditionMessage(e), "\n", sep = ""); FALSE })

if (!ok) {
    cat("could not re-fetch the rights source; clause NOT re-confirmed this run\n")
    cat("VERDICT: FAIL\n"); quit(save = "no")
}

got_sha <- tryCatch(as.character(tools::md5sum(tmp)), error = function(e) NA)  # placeholder
if (requireNamespace("digest", quietly = TRUE))
    got_sha <- digest::digest(file = tmp, algo = "sha256")
cat(sprintf("fetched bytes    : %d\n", file.size(tmp)))
cat(sprintf("fetched sha256   : %s  (%s)\n", got_sha,
            if (identical(got_sha, SHA256)) "byte-identical to the copy read on 2026-09-09"
            else "DIFFERS from the recorded copy -- page may have been revised"))

txt <- tryCatch(system2("pdftotext", c("-layout", shQuote(tmp), "-"), stdout = TRUE),
                error = function(e) character(0))
if (!length(txt)) {
    cat("pdftotext unavailable or produced no text; clause NOT re-confirmed this run\n")
    cat("VERDICT: FAIL\n"); quit(save = "no")
}
txt <- paste(txt, collapse = "\n")

hit <- grepl(CLAUSE, txt, fixed = TRUE)
cat(sprintf("\nclause present   : %s\n", if (hit) "YES" else "NO"))
if (hit) {
    line <- grep(CLAUSE, strsplit(txt, "\n")[[1]], fixed = TRUE, value = TRUE)[1]
    cat(sprintf("quoted line      : %s\n", trimws(line)))
}
# Corroborating fact from the same PDF: the adapters had to ask the originator.
perm <- grepl("Explicit permission was obtained from the author", txt, fixed = TRUE)
cat(sprintf("originator permission sentence present: %s  (bars the English fallback)\n",
            if (perm) "YES" else "NO"))

cat("\nNote: this establishes only that the rights block still holds. It establishes\n",
    "nothing about any item<->text mapping, because none was shipped for this table.\n", sep = "")

cat(if (hit) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
