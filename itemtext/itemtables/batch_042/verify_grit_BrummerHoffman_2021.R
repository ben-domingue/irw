# verify_grit_BrummerHoffman_2021.R
#
# STATUS: this table is BLOCKED ON RIGHTS -- no grit_BrummerHoffman_2021__items.csv
# was written, because the instrument is the 8-item Short Grit Scale (Grit-S;
# Duckworth & Quinn, 2009) and its rights holder states at angeladuckworth.com/measures
# that the scales "cannot be published or used for commercial purposes or wide public
# distribution". The mapping check below was run anyway, so that the record shows the
# block is a rights verdict and not a data problem, and so a future unblock can ship
# without redoing the work.
#
# THE CLAIM BEING TESTED (the mapping that WOULD have shipped): each live item code
# grit_* is the study's own dplyr::rename() of one raw Google-Forms column header, and
# that header contains the item's Portuguese wording. If any two item texts were
# swapped, the item x resp cell counts would no longer line up with the deposited
# data set column of the same name.
#
# Route: response-frequency (cell-count) identity between the OSF deposit's own
# post-recode data set and the live IRW table, plus permutation discrimination.
#
# Data: OSF p8j2v (CC BY 4.0), Deidentified data set/
#   Question_framing_data_processing.Rmd            https://osf.io/download/9yde5/
#   Depression_and_anxiety_question_framing_data_set.Rds  https://osf.io/download/uqpxa/
# Fetching the live table is a whole-table export, but it is only 14,624 rows.

suppressMessages(library(irw))

TABLE  <- "grit_BrummerHoffman_2021"
CACHE  <- file.path(".cache", TABLE)
dir.create(CACHE, recursive = TRUE, showWarnings = FALSE)

get <- function(url, dest) {
    p <- file.path(CACHE, dest)
    if (!file.exists(p)) download.file(url, p, quiet = TRUE, mode = "wb")
    p
}
rmd_path <- get("https://osf.io/download/9yde5/", "processing.Rmd")
rds_path <- get("https://osf.io/download/uqpxa/", "ds.Rds")

## ---- 1. code <-> wording tie, quoted from the authors' own processing script ----
rmd   <- readLines(rmd_path, warn = FALSE, encoding = "UTF-8")
lines <- grep("rename\\(mydata[^,]*,\\s*grit_", rmd, value = TRUE)
codes <- unique(sub(".*,\\s*(grit_[a-z_]+)=.*", "\\1", lines))
heads <- unique(sub(".*=`([^`]*)`.*", "\\1", lines))
cat("rename() lines tying a grit_ code to a form header:", length(lines), "\n")
cat("distinct codes:", length(codes), " distinct headers:", length(heads), "\n\n")

## ---- 2. cell-count identity, live table vs the deposit column of the same name ----
live <- irw::irw_fetch(TABLE)
tt   <- table(live$item, live$resp)
d    <- readRDS(rds_path)
g    <- rownames(tt)
raw  <- t(sapply(g, function(cn) as.integer(table(factor(d[[cn]], levels = 1:5)))))
colnames(raw) <- colnames(tt)

cat(sprintf("%-18s %-22s %-22s\n", "item", "live (resp 1..5)", "deposit column"))
for (i in seq_along(g))
    cat(sprintf("%-18s %-22s %-22s\n", g[i],
                paste(tt[i, ], collapse = "/"), paste(raw[i, ], collapse = "/")))
cells_ok <- identical(as.integer(tt), as.integer(raw))
cat("\nall 8 x 5 = 40 cell counts identical:", cells_ok, "\n")

## ---- 3. permutation discrimination: could a swap have passed? ----
dups <- sum(duplicated(apply(raw, 1, paste, collapse = "/")))
cat("item rows with a duplicate response distribution:", dups,
    "-- so", if (dups == 0) "no non-identity permutation of the 8 assignments reproduces the live counts"
             else "SOME items are not separable by this route", "\n")

cat("\nWhat this does NOT establish: nothing about the ENGLISH wording (the deposit's\n",
    "Questionnaire_English.pdf numbers its options 1=Very much like me .. 5=Not like me\n",
    "at all, which is the OPPOSITE of the stored coding -- the script's car::recode\n",
    "statements, lines 581-588/1087-1094, are what produced the live integers and they\n",
    "make 5 = grittier on every item, i.e. the four reverse-worded items are stored\n",
    "already reverse-scored). It also establishes nothing about rights, which is the\n",
    "actual reason nothing shipped.\n", sep = "")

cat(if (cells_ok && dups == 0 && length(codes) == 8 && length(heads) == 8)
        "VERDICT: PASS\n" else "VERDICT: FAIL\n")
