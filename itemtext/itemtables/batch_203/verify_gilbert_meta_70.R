# Verification for gilbert_meta_70 (#1945, batch_203).
#
# The deposit's variable dictionary (RawTestVariables_UTK_BH.xlsx, CC0 Dataverse
# doi:10.7910/DVN/DUBA3J) names every langwrit_std12_* variable with the task it asks,
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
D <- D[startsWith(D$stem, "langwrit_std12"), ]
d <- as.data.frame(irw::irw_fetch("gilbert_meta_70"))
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
    if (!ok) bad <- c(bad, code)
    if (length(want) < 3 || !ok)
        cat(sprintf("  %-32s implied %-12s observed %-12s %s\n", code,
                    paste(want, collapse=","), paste(got, collapse=","),
                    if (ok) "ok" else "VIOLATION"))
}
cat(sprintf("  %d of %d codes are wave-restricted and therefore discriminating\n",
            restricted, nrow(D)))
cat(sprintf("  violations: %d%s\n", length(bad),
            if (length(bad)) paste0(" -- ", paste(bad, collapse=", ")) else ""))


## ---- B. which item positions carry the SAME question on every form ----------
# Added 2026-09-14, for the same reason as gilbert_meta_71's part B. The first
# version shipped the dictionary's task label for all 33 items on the parallel-forms
# argument, without opening the booklets. The deposit publishes all of them -- four
# baseline forms (Hindi_Written_1-2/Hindi1-2_Form1..4.pdf) and four endline samples
# (Written Std1-2/mit1-2 sample 1..4.pdf) -- so which positions are fixed is a fact
# that can be read off rather than assumed.
#
# THE CHECK. b203_hindi12_forms.csv records, per position, how many booklets contain
# a distinctive substring of that position's printed content. The substrings are
# taken from the PDFs' own text layer, which uses a legacy Kruti-Dev encoding and so
# extracts as transliterated noise -- but that noise is DETERMINISTIC, so identical
# content yields identical strings and differing content does not. Unlike the
# arithmetic test in gilbert_meta_71, every position here discriminates, because
# Hindi words are long enough not to collide.
#
# SCOPE per position: codes the dictionary defines at baseline only (let_fill*,
# comp*) are checked against the four baseline forms alone, which is the complete
# set for them; codes defined in all three waves are checked against all eight.
items <- read.csv("itemtables/batch_203/gilbert_meta_70__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")
F <- ".cache/gilbert_meta_73/b203_hindi12_forms.csv"
cat("\n=== B. form-constancy of each question position ===\n")
constB <- TRUE
if (!file.exists(F)) {
    cat("  skipped:", F, "not present (rebuild from the deposit PDFs)\n")
} else {
    fm <- read.csv(F, stringsAsFactors = FALSE)
    ok <- fm$claim == fm$observed
    constB <- all(ok)
    cat(sprintf("  %d of %d positions agree with the shipped reading%s\n", sum(ok), nrow(fm),
                if (all(ok)) "" else paste0(" -- DISAGREE: ", paste(fm$code[!ok], collapse=", "))))
    for (i in seq_len(nrow(fm)))
        cat(sprintf("     %-12s %-9s %d/%d booklets  claim=%s\n",
                    fm$code[i], fm$scope[i], fm$n_booklets[i], fm$n_pool[i], fm$claim[i]))
    dic <- fm[fm$scope == "baseline-dictation", ]
    if (nrow(dic)) {
        cat("  LETTER DICTATION (added 2026-09-14 from 'Dictation for Stds1-2.pdf', the\n")
        cat("  enumerator's sheet, which lists the four letters read out for EACH baseline\n")
        cat("  form). Positions 2 and 4 are the same letter on all four forms; 1 and 3 are\n")
        cat("  not. They still ship BLANK, because let_dic is defined in all three waves\n")
        cat("  and the deposit publishes no endline dictation list -- the endline booklets\n")
        cat("  print only answer blanks. What the sheet does settle is the section's own\n")
        cat("  spoken instruction, which now ships.\n")
    }
    gained <- unique(items$item[!is.na(items$item_text) | !is.na(items$option_text)])
    cat(sprintf("  items carrying literal text or options: %d of %d\n",
                length(gained), length(unique(items$item))))
}

cat("\n=== What this does NOT establish ===\n")
cat("  Codes sharing the same wave profile are not separated from each other, nor\n")
cat("  are members of a task family. Their assignment rests on the dictionary\n")
cat("  naming each variable, which it does. Twenty-one of the thirty-three items\n")
cat("  still carry no text, for two different reasons: their position prints\n")
cat("  different content on each parallel form (let_fill1, matpic1-2, com_sen2,\n")
cat("  make_sen*), or the item IS a picture with no printed words at all\n")
cat("  (writpic*, obj_name*) or is dictated aloud (let_dic*, word_dic*).\n")
cat("  matpic3-4 are pictures whose OPTIONS are words, so they ship options with\n")
cat("  no item_text. PARTIAL for those reasons -- not for lack of a source.\n")
cat("\nVERDICT:", if (!length(bad) && same && constB) "PASS" else "FAIL", "\n")
