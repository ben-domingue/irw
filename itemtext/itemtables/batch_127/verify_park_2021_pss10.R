# verify_park_2021_pss10.R -- batch_127, 2026-09-09
#
# THIS TABLE SHIPPED NO ITEM TEXT. It is BLOCKED on instrument rights
# (itemtext/instrument_rights_register.csv, row "Perceived Stress Scale (PSS-4/10/14)",
# verdict = block), so there is no item_text <-> item mapping to re-run:
# mapping_basis = unknown, Step 5b status = NO_ROUTE.
#
# What this script re-runs is the two claims the round actually made:
#
#   (A) IDENTITY -- that park_2021_pss10 really is a Perceived Stress Scale, established
#       from the deposit itself rather than from the table's name. The paper's Measures
#       section says the K-PSS "comprises five positive and five negative types of
#       questions"; the S1 File's own subscale sums must therefore decompose as
#       stress_nega_sum = items 1,2,3,9,10 and stress_posi_sum = items 4,5,6,7,8, and the
#       item correlation matrix must split along the same two blocks.
#
#   (B) RIGHTS -- that Cohen's own FAQ page still carries the fee / permission clauses the
#       block rests on, byte-identical to the copy hashed into the register.
#
#   VERDICT: PASS  = identity reproduces AND the clauses are still there; block stands.
#   VERDICT: FAIL  = either check did not reproduce; a human should look before this
#                    table is re-queued or the block is relied on again.

TABLE   <- "park_2021_pss10"
SAV_URL <- paste0("https://journals.plos.org/plosone/article/file",
                  "?type=supplementary&id=10.1371/journal.pone.0246887.s001")
SAV_SHA <- "e95da410d50a6b1ace40fa7646ea8a6374fec6f3405523b546c59bb5bba81626"
DOC_URL <- "https://www.cmu.edu/dietrich/psychology/stress-immunity-disease-lab/scales/.doc/pssfaqs.doc"
DOC_MD5 <- "f2eeb376bfab9aa86ae8ae5c7719ec9c"   # as recorded in the register, 2026-09-08
CLAUSE1 <- "Use of the PSS in profit making ventures including corporate clinical trials requires special permission and a nominal charge."
CLAUSE2 <- "Inclusion of the scale within a larger scale that will be copyrighted also requires specific permission."

UA <- "Mozilla/5.0 (X11; Linux x86_64)"
ok_identity <- FALSE
ok_rights   <- FALSE

cat(sprintf("table : %s\n\n", TABLE))

## ---------------------------------------------------------------- (A) identity
cat("== (A) instrument identity, from the study's own deposit ==\n")
sav <- tempfile(fileext = ".sav")
got <- tryCatch({
    utils::download.file(SAV_URL, sav, quiet = TRUE, mode = "wb",
                         headers = c("User-Agent" = UA))
    file.exists(sav) && file.size(sav) > 10000
}, error = function(e) { cat("fetch error: ", conditionMessage(e), "\n", sep = ""); FALSE })

if (!got) {
    cat("could not fetch S1 File; identity NOT re-confirmed this run\n")
} else if (!requireNamespace("haven", quietly = TRUE)) {
    cat("package 'haven' not available; identity NOT re-confirmed this run\n")
} else {
    if (requireNamespace("digest", quietly = TRUE))
        cat(sprintf("S1 sha256        : %s  (%s)\n", digest::digest(file = sav, algo = "sha256"),
                    if (identical(digest::digest(file = sav, algo = "sha256"), SAV_SHA))
                        "byte-identical to the copy read on 2026-09-09"
                    else "DIFFERS from the recorded copy"))
    d  <- as.data.frame(haven::read_sav(sav))
    it <- paste0("stress_", 1:10)
    cat(sprintf("rows             : %d\n", nrow(d)))

    neg <- c(1, 2, 3, 9, 10); pos <- c(4, 5, 6, 7, 8)
    dn <- max(abs(rowSums(d[, paste0("stress_", neg)]) - d$stress_nega_sum))
    dp <- max(abs(rowSums(d[, paste0("stress_", pos)]) - d$stress_posi_sum))
    cat(sprintf("max|sum(items %s) - stress_nega_sum| = %.3g\n",
                paste(neg, collapse = ","), dn))
    cat(sprintf("max|sum(items %s) - stress_posi_sum| = %.3g\n",
                paste(pos, collapse = ","), dp))

    r  <- cor(d[, it], use = "complete.obs")
    wn <- r[paste0("stress_", neg), paste0("stress_", neg)]
    wp <- r[paste0("stress_", pos), paste0("stress_", pos)]
    xb <- r[paste0("stress_", neg), paste0("stress_", pos)]
    cat(sprintf("within-negative r: %.2f .. %.2f\n", min(wn[wn < 1]), max(wn[wn < 1])))
    cat(sprintf("within-positive r: %.2f .. %.2f\n", min(wp[wp < 1]), max(wp[wp < 1])))
    cat(sprintf("cross-block    r : %.2f .. %.2f\n", min(xb), max(xb)))
    cat(sprintf("item means       : %s\n",
                paste(sprintf("%.2f", colMeans(d[, it], na.rm = TRUE)), collapse = " ")))
    cat(sprintf("variable labels present: %s ; value labels present: %s\n",
                if (any(nzchar(vapply(d, function(x) {
                    l <- attr(x, "label"); if (is.null(l)) "" else as.character(l) }, "")))) "YES" else "NO",
                if (any(vapply(d, function(x) !is.null(attr(x, "labels")), TRUE))) "YES" else "NO"))

    sep <- min(min(wn[wn < 1]), min(wp[wp < 1])) > max(xb)
    ok_identity <- dn < 1e-6 && dp < 1e-6 && sep
    cat(sprintf("=> five-positive/five-negative K-PSS structure reproduces: %s\n",
                if (ok_identity) "YES" else "NO"))
}

## ------------------------------------------------------------------ (B) rights
cat("\n== (B) rights clause still on the holder's own page ==\n")
doc <- tempfile(fileext = ".doc")
got2 <- tryCatch({
    utils::download.file(DOC_URL, doc, quiet = TRUE, mode = "wb",
                         headers = c("User-Agent" = UA))
    file.exists(doc) && file.size(doc) > 10000
}, error = function(e) { cat("fetch error: ", conditionMessage(e), "\n", sep = ""); FALSE })

if (!got2) {
    cat("could not re-fetch pssfaqs.doc; clause NOT re-confirmed this run\n")
} else {
    md5 <- as.character(tools::md5sum(doc))
    cat(sprintf("fetched bytes    : %d\n", file.size(doc)))
    cat(sprintf("fetched md5      : %s  (%s)\n", md5,
                if (identical(md5, DOC_MD5)) "byte-identical to the register's recorded hash"
                else "DIFFERS from the register -- page may have been revised"))
    out <- tempfile(); dir.create(out)
    prof <- tempfile("lo_profile")   # private profile: avoids clashing with any other
    # NB: Rscript exports an LD_LIBRARY_PATH that breaks soffice.bin ("libreglo.so:
    # cannot open shared object file"), so the converter is launched via `env -u`.
    system2("env", c("-u", "LD_LIBRARY_PATH", "soffice",
                     sprintf("-env:UserInstallation=file://%s", prof),
                     "--headless", "--convert-to", "txt", "--outdir",
                     shQuote(out), shQuote(doc)),
            stdout = FALSE, stderr = FALSE)
    tf <- list.files(out, pattern = "\\.txt$", full.names = TRUE)
    txt <- NA_character_
    if (length(tf)) {
        txt <- paste(readLines(tf[1], warn = FALSE), collapse = "\n")
    } else {
        # fallback: .doc stores its body as (mostly) plain bytes; scan them directly
        raw <- readBin(doc, "raw", file.size(doc))
        txt <- rawToChar(raw[raw >= as.raw(9) & raw <= as.raw(126)])
        cat("libreoffice conversion unavailable; fell back to a raw byte scan of the .doc\n")
    }
    if (is.na(txt)) {
        cat("no text recovered; clause NOT re-confirmed this run\n")
    } else {
        h1 <- grepl(CLAUSE1, txt, fixed = TRUE); h2 <- grepl(CLAUSE2, txt, fixed = TRUE)
        cat(sprintf("clause 1 (fee / special permission) present : %s\n", if (h1) "YES" else "NO"))
        cat(sprintf("clause 2 (permission to include)    present : %s\n", if (h2) "YES" else "NO"))
        if (h1) cat(sprintf("  quoted: %s\n", CLAUSE1))
        if (h2) cat(sprintf("  quoted: %s\n", CLAUSE2))
        ok_rights <- h1 && h2
    }
}

cat("\nNote: this establishes (a) that the table's items are a Perceived Stress Scale and\n",
    "(b) that the block still holds. It establishes NOTHING about any item <-> text\n",
    "mapping: no wording was shipped, and the polarity blocks pin a class of five items,\n",
    "never an individual item.\n", sep = "")

cat(if (ok_identity && ok_rights) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
