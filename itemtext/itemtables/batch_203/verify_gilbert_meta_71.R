# Verification for gilbert_meta_71 (#1945, batch_203).
#
# The deposit's variable dictionary (RawTestVariables_UTK_BH.xlsx, CC0 Dataverse
# doi:10.7910/DVN/DUBA3J) names every mathwrit_std12_* variable with the task it asks,
# and does so once per WAVE via a prefix: b_ baseline, e1_ midline, e2_ endline.
# Live item codes are those names with the prefix stripped, and the live `wave`
# column (0 / 0.5 / 1) carries what the prefix encoded. The renaming happened
# upstream of this repo (data/gilbert_hte/postprocessing.R points at an external
# analysis directory), so it is tested against the data rather than read off a
# script.
#
# THE TEST: for every code, the set of waves it actually appears in must equal
# the set its dictionary prefixes imply. That covers all codes, not just the
# wave-restricted ones -- a code defined b|e2 must be absent from the midline.
MAP <- c(b = 0, e1 = 0.5, e2 = 1)
D <- read.csv(".cache/gilbert_meta_73/std12_dict.csv", stringsAsFactors = FALSE)
D <- D[startsWith(D$stem, "mathwrit_std12"), ]
d <- as.data.frame(irw::irw_fetch("gilbert_meta_71"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)

same <- setequal(D$stem, unique(d$item))
cat("=== dictionary vs live item sets ===\n")
cat(sprintf("  dictionary %d, live %d, identical: %s\n", nrow(D), length(unique(d$item)), same))

cat("\n=== every code's observed waves vs the waves its prefixes imply ===\n")
bad <- character(0); restricted <- 0
for (i in seq_len(nrow(D))) {
    code <- D$stem[i]
    want <- sort(unname(MAP[strsplit(D$prefixes[i], "|", fixed = TRUE)[[1]]]))
    got  <- sort(unique(d$wave[d$item == code]))
    ok   <- isTRUE(all.equal(as.numeric(want), as.numeric(got)))
    if (length(want) < 3) restricted <- restricted + 1
    # KNOWN DICTIONARY TYPO, not a mapping error. The End1 sheet's row 8b lists
    # e1_mathwrit_std12_add2d_a -- a duplicate of row 8a's variable name --
    # instead of add2d_b, so the harvest sees no e1 entry for add2d_b while the
    # sheet's own question label for that row reads "q8_b". The data settles it:
    # add2d_b is present at the midline wave. Both rows carry the identical task
    # description ("Addition-two digit"), so the typo cannot affect item_text.
    typo <- identical(code, "mathwrit_std12_add2d_b")
    if (!ok && !typo) bad <- c(bad, code)
    if (!ok && typo) cat(sprintf("  %-32s implied %-12s observed %-12s known dictionary typo (End1 row 8b)\n",
                                 code, paste(want, collapse=","), paste(got, collapse=",")))
    if ((length(want) < 3 || !ok) && !(!ok && typo))
        cat(sprintf("  %-32s implied %-12s observed %-12s %s\n", code,
                    paste(want, collapse=","), paste(got, collapse=","),
                    if (ok) "ok" else "VIOLATION"))
}
cat(sprintf("  %d of %d codes are wave-restricted and therefore discriminating\n",
            restricted, nrow(D)))
cat(sprintf("  violations: %d%s\n", length(bad),
            if (length(bad)) paste0(" -- ", paste(bad, collapse=", ")) else ""))


## ---- B. which item positions carry the SAME question on every form ----------
# Added 2026-09-14. The first version of this table shipped the dictionary's task
# label ("Addition-one digit") for all 20 items, on the argument that four parallel
# forms mean no literal item belongs to a code. That is right for MOST positions and
# wrong for some: the deposit publishes all eight booklets (four baseline forms, four
# endline samples) and several positions print the identical problem in every one.
# Those now ship the real question.
#
# THE CHECK, AND WHAT IT CANNOT SETTLE. b203_math12_forms.csv is built by reading all
# eight booklet PDFs and recording, per question position, how many contain every
# operand of that position's problem. A fixed problem appears in 8/8; one that varies
# by form does not. The method only discriminates when an operand has two digits --
# single digits appear somewhere on every math page, so 8/8 is uninformative there.
# Those positions are reported separately and were settled by reading rendered pages.
items <- read.csv("itemtables/batch_203/gilbert_meta_71__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")
F <- ".cache/gilbert_meta_73/b203_math12_forms.csv"
cat("\n=== B. form-constancy of each question position (8 booklets) ===\n")
constB <- TRUE
if (!file.exists(F)) {
    cat("  skipped:", F, "not present (rebuild from the deposit PDFs)\n")
} else {
    fm <- read.csv(F, stringsAsFactors = FALSE)
    disc <- fm[fm$discriminating == 1, ]
    ok <- (disc$claim == "constant") == (disc$n_booklets == 8)
    constB <- all(ok)
    cat(sprintf("  %d of %d discriminating positions agree with the shipped reading%s\n",
                sum(ok), nrow(disc),
                if (all(ok)) "" else paste0(" -- DISAGREE: ", paste(disc$qno[!ok], collapse=", "))))
    for (i in seq_len(nrow(disc)))
        cat(sprintf("     %-3s %-12s operands %-9s %d/8 booklets  claim=%s\n",
                    disc$qno[i], disc$code[i], disc$operands[i], disc$n_booklets[i], disc$claim[i]))
    nd <- fm[fm$discriminating == 0, ]
    cat(sprintf("  not discriminable this way (all operands single-digit): %s\n",
                paste(nd$qno, collapse = ", ")))
    cat("     add1d_d (9+9+9) and subt1d_a (8-3) are shipped constant on the rendered\n")
    cat("     pages, not on this check; num (the Hindi word अठारह) likewise.\n")
    shipped <- sub("^mathwrit_std12_", "", unique(items$item[!is.na(items$item_text)]))
    cat(sprintf("  items shipping a literal question: %d of %d; all claimed constant: %s\n",
                length(shipped), length(unique(items$item)),
                all(shipped %in% c(fm$code[fm$claim == "constant"], "num"))))
}

cat("\n=== What this does NOT establish ===\n")
cat("  Codes sharing the same wave profile are not separated from each other, nor\n")
cat("  are members of a task family. Their assignment rests on the dictionary\n")
cat("  naming each variable, which it does. Twelve of the twenty items still carry\n")
cat("  no item_text: their question position prints a DIFFERENT problem on each of\n")
cat("  the four parallel forms and the live table does not record which form a\n")
cat("  child took, so no single wording is correct for them. PARTIAL for that\n")
cat("  reason -- not for lack of a source.\n")
cat("\nVERDICT:", if (!length(bad) && same && constB) "PASS" else "FAIL", "\n")
