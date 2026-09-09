# verify_luo_2021_ecr.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST. data/luo_2021_acculturation.py assigns the IRW item codes
# POSITIONALLY: ECR_IDX = [9,10,11,12,13,14,16,17,19,21,23,25] over the columns
# of the study's SPSS file (PLOS S3 File, 10.1371/journal.pone.0260616.s003),
# renamed f"item_{i+1:02d}". The shipped item_text is the text carried in the
# SPSS *variable name* at each of those positions. So the falsifiable claim is:
#
#   live luo_2021_ecr item_NN  ==  source .sav column at index ECR_IDX[NN-1]
#
# This script re-downloads the .sav, and for each of the 12 positions compares
# the source column's response-frequency vector (levels 1..7, after the script's
# own 1<=resp<=valid_max filter) against the live table's per-item frequency
# vector. All 12 source vectors are mutually distinct, so a cell-for-cell match
# on all 12 x 7 = 84 cells distinguishes EVERY item from EVERY other item -- a
# permutation of any two items would break it. It also prints the source header
# text at each position next to the shipped item_text, which is the positional
# header diff the skill requires for positional codes.
#
# What this does NOT establish: nothing about whether the .sav's own column
# headers state the wording the respondents actually saw (they are the study's
# own materials, so they do), and nothing about the option_text<->resp axis,
# which comes from the paper's stated anchors (1 = strongly disagree,
# 7 = strongly agree) and is not testable from counts.

suppressMessages(library(irw))

TABLE   <- "luo_2021_ecr"
ECR_IDX <- c(9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25)  # 0-based, as in the .py
SI_URL  <- paste0("https://journals.plos.org/plosone/article/file",
                  "?type=supplementary&id=10.1371/journal.pone.0260616.s003")

sav <- file.path(tempdir(), "luo2021_s003.sav")
if (!file.exists(sav)) download.file(SI_URL, sav, quiet = TRUE, mode = "wb")
raw <- haven::read_sav(sav)
cols <- names(raw)

items <- sprintf("item_%02d", 1:12)
src <- t(sapply(ECR_IDX, function(ix) {
    v <- suppressWarnings(as.numeric(raw[[ix + 1L]]))   # R is 1-based
    v <- v[!is.na(v) & v >= 1 & v <= 7]
    sapply(1:7, function(k) sum(v == k))
}))
dimnames(src) <- list(items, 1:7)

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = items), factor(d$resp, levels = 1:7))
live <- matrix(as.integer(live), nrow = 12, dimnames = dimnames(src))

shipped <- read.csv(file.path(dirname(sub("^--file=", "", grep("^--file=",
             commandArgs(FALSE), value = TRUE)[1])), "luo_2021_ecr__items.csv"),
             stringsAsFactors = FALSE)
shipped <- shipped[!duplicated(shipped$item), c("item", "item_text")]
shipped <- shipped[match(items, shipped$item), ]

cat("=== positional header diff: source .sav column name vs shipped item_text ===\n")
for (i in seq_along(items))
    cat(sprintf("%s  col[%2d] %-66s\n            shipped %s\n",
                items[i], ECR_IDX[i], substr(cols[ECR_IDX[i] + 1L], 1, 66),
                shipped$item_text[i]))

cat("\n=== per-item response frequency: source column vs live table (levels 1..7) ===\n")
cat(sprintf("%-9s %-28s %-28s %s\n", "item", "source", "live", "match"))
ok <- TRUE
for (i in seq_along(items)) {
    m <- all(src[i, ] == live[i, ])
    ok <- ok && m
    cat(sprintf("%-9s %-28s %-28s %s\n", items[i],
                paste(src[i, ], collapse = ","),
                paste(live[i, ], collapse = ","),
                if (m) "OK" else "MISMATCH"))
}

dist <- nrow(unique(src)) == nrow(src)
cat(sprintf("\ncells compared: %d; all matching: %s\n", length(src), ok))
cat(sprintf("source frequency vectors mutually distinct (so the match pins every item\nagainst every other, not just the set): %s\n", dist))

cat(if (ok && dist) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
