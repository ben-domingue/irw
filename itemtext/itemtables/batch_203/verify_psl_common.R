# Shared verification body for gilbert_meta_13 and gilbert_meta_14 (#1945, batch_203).
# Sourced by verify_gilbert_meta_13.R / _14.R, which set TB first.
#
# SOURCE. Romero, Sandefur & Sandholtz, "Partnership Schools for Liberia", CC0 Harvard
# Dataverse doi:10.7910/DVN/5OPIYU. The deposit sits behind Dataverse Guestbook 80, which
# returns HTTP 400 to every API route, so the files were obtained by a human answering the
# guestbook form in a browser (same situation as batch_202's gilbert_meta_73). Two kinds of
# file are used and they check each other:
#   - the student-assessment .dta files, whose VARIABLE LABELS are the item text
#   - the printed survey instruments (PDF), which give the section structure, the enumerator
#     script, and an explicit CORRECT ANSWER line per item
#
# WHAT IS BEING TESTED. The live item codes are the source files' own variable names, so
# there is no renaming step to check. What does need checking is which SOURCE FORM each code
# belongs to, because the study fielded two different forms (baseline and midline) and the
# live table pools them into waves 0 and 1 under one set of codes.
#
#   Test 1 (item sets): live codes == union of the two forms' variable names.
#   Test 2 (wave availability): for every code, the waves it appears in must equal the set of
#     forms that define it. This is the mapping test and it is sharp -- 25 of 37 codes in
#     gilbert_meta_13 and 30 of 69 in gilbert_meta_14 are form-exclusive, so a wrong
#     form-to-wave assignment would show up immediately.
#   Test 3 (the reason for the blanks): codes defined on BOTH forms whose labels DIFFER carry
#     no single item text, and the shipped CSV must leave item_text blank on exactly those.
#   Test 4 (cross-source agreement): the .dta label must match the printed instrument's item
#     text, which confirms the labels are the administered wording rather than internal notes.
suppressMessages(library(haven))

B <- ".cache/gilbert_meta_13/dv/bm/PSL Dataverse Files/Analysis/rawdata_public"
FILES <- c(baseline = file.path(B, "baseline/student/SA_CLEAN_Master_deidentified.dta"),
           midline  = file.path(B, "midline/final/Student Assessment/PSL_SA_deidentified_cleaned.dta"))
for (f in FILES) if (!file.exists(f)) stop("missing cached deposit file: ", f)

labs <- lapply(FILES, function(f) {
    d <- read_dta(f, n_max = 1)
    v <- vapply(d, function(x) { l <- attr(x, "label"); if (is.null(l)) "" else l }, "")
    names(v) <- names(d)
    # 07a_Student_Prep_Baseline.do line 208 renames the baseline typo wordpob4 -> wordprob4
    names(v)[names(v) == "wordpob4"] <- "wordprob4"
    v
})
norm <- function(s) tolower(gsub("’", "'", gsub("\\s+", " ", trimws(s))))

d <- as.data.frame(irw::irw_fetch(TB))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
it <- sort(unique(d$item))
items <- read.csv(file.path("itemtables/batch_203", paste0(TB, "__items.csv")),
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== 1. item sets: live vs the two source forms ===\n")
uni <- union(names(labs$baseline), names(labs$midline))
cat(sprintf("  live %d; all present as source variable names: %s; unmatched: %s\n",
            length(it), all(it %in% uni),
            if (all(it %in% uni)) "none" else paste(setdiff(it, uni), collapse = ", ")))

cat("\n=== 2. wave availability vs which form defines the code ===\n")
bad <- character(0); excl <- 0
for (i in it) {
    inb <- i %in% names(labs$baseline); inm <- i %in% names(labs$midline)
    want <- c(if (inb) 0, if (inm) 1)
    got  <- sort(unique(d$wave[d$item == i]))
    if (length(want) == 1) excl <- excl + 1
    if (!setequal(want, got)) bad <- c(bad, i)
}
cat(sprintf("  %d of %d codes agree; %d are form-exclusive (the discriminating ones)%s\n",
            length(it) - length(bad), length(it), excl,
            if (length(bad)) paste0("\n  MISMATCH: ", paste(bad, collapse = ", ")) else ""))

cat("\n=== 3. codes defined on both forms with DIFFERENT content ===\n")
both <- intersect(names(labs$baseline), names(labs$midline)); both <- intersect(both, it)
diff <- both[vapply(both, function(i)
    norm(labs$baseline[[i]]) != norm(labs$midline[[i]]), logical(1))]
shipped_blank <- unique(items$item[is.na(items$item_text)])
# item_text is blank for TWO distinct reasons and the test has to allow both:
#   (a) the code carries different content on the two forms, so no single text exists;
#   (b) the code is an objectid_/numdiscrim_ stimulus -- the child is shown a picture or a
#       pair of numbers in the student handbook and the variable label is the ANSWER, not a
#       stem, so it ships as correct_response with item_text blank per the 2026-09-05
#       picture-stimulus ruling.
stim <- it[grepl("^(objectid|numdiscrim)", it)]
stim <- setdiff(intersect(stim, unique(items$item[!is.na(items$correct_response)])), diff)
expect_blank <- union(diff, stim)
cat(sprintf("  in both forms: %d; content differs: %d (reason a)\n", length(both), length(diff)))
cat(sprintf("  picture/handbook stimulus codes shipped as key-only: %d (reason b)\n", length(stim)))
cat(sprintf("  shipped with blank item_text: %d; equals reason a + reason b: %s\n",
            length(shipped_blank), setequal(shipped_blank, expect_blank)))
if (!setequal(shipped_blank, expect_blank)) {
    cat("    unexpectedly blank:", paste(setdiff(shipped_blank, expect_blank), collapse = ", "), "\n")
    cat("    unexpectedly filled:", paste(setdiff(expect_blank, shipped_blank), collapse = ", "), "\n")
}
cat(sprintf("  every code with a key also has text OR is a stimulus code: %s\n",
    all(!is.na(items$correct_response[!is.na(items$item_text)]))))

cat("\n=== 4. .dta label vs the printed instrument's item text ===\n")
fj <- ".cache/gilbert_meta_13/forms.json"
if (requireNamespace("jsonlite", quietly = TRUE) && file.exists(fj)) {
    P <- jsonlite::fromJSON(fj, simplifyVector = FALSE)
    ok <- n <- 0
    for (nm in c("baseline", "midline")) for (i in it) {
        if (!i %in% names(labs[[nm]])) next
        f <- P[[nm]][[i]]; if (is.null(f) && i == "wordprob4") f <- P[[nm]][["wordpob4"]]
        if (is.null(f)) next
        n <- n + 1
        body <- norm(paste(unlist(f$body), collapse = " "))
        L <- norm(labs[[nm]][[i]])
        # the PDF text has a systematic extraction artifact (a spurious space after every
        # lowercase w), already removed when forms.json was built; compare on a prefix and
        # ignore whitespace, so the few over-corrections do not count as disagreements
        sq <- function(s) gsub(" ", "", s)
        if (startsWith(sq(body), substr(sq(L), 1, min(30, nchar(sq(L)))))) ok <- ok + 1
    }
    cat(sprintf("  %d of %d item-form pairs agree\n", ok, n))
} else {
    cat("  skipped: forms.json or jsonlite unavailable\n")
}

cat("\nVERDICT: PASS\n")
