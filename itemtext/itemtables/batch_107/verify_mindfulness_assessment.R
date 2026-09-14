# verify_mindfulness_assessment.R
#
# CLAIM UNDER TEST: the IRW bare-integer item code `i` IS source column `Qi` of the
# Open-Source Psychometrics KIMS deposit (data/mindfulness_assessment.R lowercases the
# headers and strips the leading "q"), so item i's shipped item_text is the codebook's
# "Qi." line and the 1-5 option_text are the codebook's own anchors.
#
# Falsifiable: re-derive the table from the deposit's own data.csv (0 -> NA) and demand
# that, for every item, the per-item non-missing n, the per-item mean, and the count of
# EACH of the five response levels reproduce the live table exactly. If item_text for any
# two items were swapped, the swapped pair's response-count vectors would disagree --
# the script prints below that all 39 count-vectors are mutually distinct, which is what
# makes this route separate every item from every other, not merely most of them.
#
# irw_fetch() is used deliberately: this table is 23,439 rows (~0.5 MB), so the export
# cost is negligible and the per-item means it buys are exact.

suppressMessages(library(irw))

TABLE  <- "mindfulness_assessment"
ZIPURL <- "http://openpsychometrics.org/_rawdata/KIMS.zip"
CACHE  <- file.path(".cache", TABLE)
ZIP    <- file.path(CACHE, "KIMS.zip")

dir.create(CACHE, recursive = TRUE, showWarnings = FALSE)
if (!file.exists(ZIP)) download.file(ZIPURL, ZIP, mode = "wb", quiet = TRUE)
if (!file.exists(file.path(CACHE, "kims", "KIMS", "data.csv")))
    unzip(ZIP, exdir = file.path(CACHE, "kims"))
raw <- read.csv(file.path(CACHE, "kims", "KIMS", "data.csv"))

live <- irw::irw_fetch(TABLE)
live$item <- as.integer(as.character(live$item))
live$resp <- as.numeric(live$resp)

cat(sprintf("%-5s %6s %6s %10s %10s %11s  %s\n",
            "item", "n_raw", "n_live", "mean_raw", "mean_live", "max|dcount|", "level counts raw (1..5)"))
ok <- TRUE
vecs <- list()
for (i in 1:39) {
    v  <- raw[[paste0("Q", i)]]; v <- v[!is.na(v) & v != 0]
    lv <- live$resp[live$item == i]; lv <- lv[!is.na(lv)]
    craw  <- vapply(1:5, function(k) sum(v  == k), 0L)
    clive <- vapply(1:5, function(k) sum(lv == k), 0L)
    vecs[[i]] <- craw
    dmax <- max(abs(craw - clive))
    agree <- length(v) == length(lv) && dmax == 0 && abs(mean(v) - mean(lv)) < 1e-10
    ok <- ok && agree
    cat(sprintf("%-5d %6d %6d %10.6f %10.6f %11d  %s%s\n", i, length(v), length(lv),
                mean(v), mean(lv), dmax, paste(craw, collapse = "/"),
                if (agree) "" else "   <-- MISMATCH"))
}

ndup <- sum(duplicated(vapply(vecs, paste, "", collapse = "/")))
cat(sprintf("\nitems whose 5-level count vector duplicates another item's: %d of 39\n", ndup))
cat("A duplicate-free set of count vectors means no permutation of item_text could\n",
    "reproduce these numbers, so this distinguishes every item from every other one.\n", sep = "")
cat("What it does NOT establish: the option_text wording itself (the anchors are taken\n",
    "from the codebook's own sentence and are not testable against counts), nor the\n",
    "instructions, which the deposit does not record.\n")

cat(if (ok && ndup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
