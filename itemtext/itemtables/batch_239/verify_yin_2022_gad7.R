# verify_yin_2022_gad7.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: each live item code (a verbatim column header of the study's
# S1 spreadsheet) carries the canonical GAD-7 stem whose content keyword it names.
#
# What is checked, and why it would break under a swap:
#  (1) IDENTITY OF CODE AND SOURCE COLUMN. data/yin_2022_gad7.py melts the S1
#      workbook's GAD-7 columns by name, so the live item code should BE the
#      source header. Proven by reproducing per-item n and mean from the raw
#      file cell for cell. If the live "GAD-7 question: restless" rows had come
#      from any other source column, the n/mean pair would not reproduce.
#  (2) MARKER ITEM (route 7). "Feeling afraid as if something awful might happen"
#      is the least-endorsed GAD-7 item in community samples; the code named
#      "afraid" must therefore carry the lowest mean of the seven.
#  (3) SCALE DIRECTION / option mapping (route 3). The workbook's own "GAD-7
#      Total" must equal the raw unreversed sum of the seven items, and the
#      "GAD-7 Category" labels must partition it at the canonical 0-4/5-9/
#      10-14/15+ bands -- which is only true if 0 = "Not at all" ascending to
#      3 = "Nearly every day".
#
# NOT established here: nothing statistical separates, say, "worry too much"
# from "unable stop worrying" -- that tie is a label match (the code names its
# own content and the study's Methods section lists the same seven symptoms in
# the same column order), not an inference this script could falsify.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "yin_2022_gad7"
SI <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0275292.s001")

d <- irw::irw_fetch(TABLE)

tmp <- tempfile(fileext = ".xlsx")
utils::download.file(SI, tmp, quiet = TRUE, mode = "wb")
raw <- readxl::read_excel(tmp, sheet = "Survey Data")

cols <- grep("^GAD-7 question:", names(raw), value = TRUE)
cat(sprintf("live items: %d   source GAD-7 columns: %d\n\n", length(unique(d$item)), length(cols)))

cat(sprintf("%-38s %5s %5s %8s %8s\n", "item code = source column", "n_liv", "n_raw", "m_live", "m_raw"))
ok1 <- TRUE
for (cl in cols) {
    v  <- suppressWarnings(as.numeric(raw[[cl]])); v <- v[!is.na(v)]
    li <- d$resp[d$item == cl]
    cat(sprintf("%-38s %5d %5d %8.4f %8.4f\n", cl, length(li), length(v), mean(li), mean(v)))
    if (length(li) != length(v) || abs(mean(li) - mean(v)) > 1e-9) ok1 <- FALSE
}
cat(sprintf("\n(1) per-item n and mean reproduce from the raw columns: %s\n\n", ok1))

m <- tapply(d$resp, d$item, mean)
m <- sort(m)
cat("per-item means, live data (ascending):\n")
for (i in seq_along(m)) cat(sprintf("  %-38s %.4f\n", names(m)[i], m[i]))
ok2 <- names(m)[1] == "GAD-7 question: afraid"
cat(sprintf("(2) lowest-mean item is the 'afraid' code: %s (%.4f vs next %.4f)\n\n",
            ok2, m[1], m[2]))

g   <- as.data.frame(lapply(raw[cols], function(x) suppressWarnings(as.numeric(x))))
s   <- rowSums(g)
tot <- suppressWarnings(as.numeric(raw[["GAD-7 Total"]]))
keep <- !is.na(s) & !is.na(tot)
ok3a <- all(s[keep] == tot[keep])
cat(sprintf("(3a) raw unreversed sum == workbook 'GAD-7 Total': %s (%d/%d rows, max |diff| %.3f)\n",
            ok3a, sum(keep), length(keep), max(abs(s[keep] - tot[keep]))))

cate <- as.character(raw[["GAD-7 Category"]])
bands <- list("Minimal anxiety" = c(0, 4), "Mild anxiety" = c(5, 9),
              "Moderate anxiety" = c(10, 14), "Severe anxiety" = c(15, 21))
ok3b <- TRUE
cat("\n(3b) observed total range within each printed severity label:\n")
for (nm in names(bands)) {
    tt <- tot[!is.na(cate) & cate == nm & !is.na(tot)]
    cat(sprintf("  %-17s n=%3d  observed %2d-%2d   canonical %2d-%2d\n",
                nm, length(tt), min(tt), max(tt), bands[[nm]][1], bands[[nm]][2]))
    if (min(tt) != bands[[nm]][1] || max(tt) != bands[[nm]][2]) ok3b <- FALSE
}
cat(sprintf("(3b) categories partition the raw sum at the canonical GAD-7 bands: %s\n", ok3b))

cat("\nNot established: the 'worry too much' / 'unable stop worrying' pair and the\n",
    "other same-scale stems are distinguished by the codes naming their own content\n",
    "(and by the paper's Methods listing the seven symptoms in this column order),\n",
    "not by anything this script could falsify.\n", sep = "")

cat(if (ok1 && ok2 && ok3a && ok3b) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
