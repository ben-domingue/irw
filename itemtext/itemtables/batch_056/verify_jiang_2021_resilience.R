# verify_jiang_2021_resilience.R
#
# Claim under test (Step 5b): each live item code C1..C17 carries the wording
# Table 4 of Jiang et al. 2021 (PLOS ONE 10.1371/journal.pone.0245662) prints
# next to that very code, and resp 5 = "完全符合 / Extremely match" ...
# resp 1 = "完全不符合 / Extremely not match".
#
# Three checks, none of which is a re-run of validate_items.R:
#
#  A. The deposit column <-> live item tie. S5 File (the study's raw .xlsx) has
#     C1..C17 written in its own header row 1 and one dimension label per block
#     in row 0. Its per-item non-missing counts (0s dropped, as data/
#     jiang_2021_resilience.py does) are compared item-by-item against the live
#     table's per-item n from irw::irw_table_sets(). The counts are NOT uniform
#     -- 950/951/952 -- so this is a fingerprint, not a formality.
#
#  B. The wording <-> code tie. The shipped item_text_translated stems are
#     compared string-for-string against Table 4's own "C<n> <text>" rows,
#     hard-coded below from the table image. If item_text for two items were
#     swapped this fails outright.
#
#  C. The option direction. Observed per-item means (computed from S5 with
#     5 = "Extremely match") are compared against Table 5's published per-item
#     means, and against the reversed reading (6 - mean). One of the two is a
#     near match and the other is off by ~1.6 on every item.
#
# What this does NOT establish: nothing about within-block ordering is left to
# inference, because Table 4 labels every item with its code -- but the
# published means in Table 5 are close enough between C4..C8 that check C on
# its own could not separate them. Check B is what pins them.
#
# Requires network (PLOS S5 File + irw_table_sets). No full-table export.

suppressMessages(library(irw))

TABLE  <- "jiang_2021_resilience"
ITEMS  <- paste0("C", 1:17)
SI_URL <- paste0("https://journals.plos.org/plosone/article/file",
                 "?type=supplementary&id=10.1371/journal.pone.0245662.s005")

# Jiang et al. 2021, Table 5 ("Item discrete trend and correlation coefficient")
PUB_MEAN <- c(4.04, 4.48, 4.50, 4.16, 4.19, 4.15, 4.19, 4.15, 4.27,
              4.24, 4.14, 4.33, 3.91, 3.65, 3.68, 3.65, 3.36)

# Jiang et al. 2021, Table 4 ("Weights of the individual earthquake resilience
# questionnaire"), which prints each item prefixed with its own code.
TAB4 <- c(
 "I am generally in good health.",
 "I can move freely and easily.",
 "I can think clearly and communicate with others.",
 "I believe I can control my emotions when an earthquake strikes.",
 "I always have a positive view when suffering difficulties.",
 "I do not give up easily when suffering difficulties.",
 "I can recover from setbacks quickly.",
 "I believe that difficulties make me stronger.",
 paste("I can play my roles in daily life well, such as studying hard as a",
       "student, doing my own job well as a worker, taking care of my family",
       "as a parent, etc."),
 "I can cope with problems well.",
 "I can adapt quickly when the environment changes.",
 "I can get along with others well.",
 paste("I am good at finding and using social resource (staff, funds,",
       "supplies, skills, social relations and so on)."),
 "I have basic earthquake disaster assessment ability.",
 "I know how to escape after shocks.",
 "I have basic survival skills needed after an earthquake.",
 "I can administer first aid.")

ok <- TRUE

## ---- read the study's raw S5 File --------------------------------------
tmp <- tempfile(fileext = ".xlsx")
utils::download.file(SI_URL, tmp, quiet = TRUE, mode = "wb")
raw <- as.data.frame(readxl::read_excel(tmp, col_names = FALSE))
hdr_dim  <- as.character(raw[1, -1])
hdr_code <- as.character(raw[2, -1])
dat <- raw[-(1:2), -1]
dat <- as.data.frame(lapply(dat, function(x) suppressWarnings(as.numeric(x))))
names(dat) <- hdr_code
dat[dat == 0] <- NA   # matches data/jiang_2021_resilience.py

cat("S5 File header row 1 (item codes):", paste(hdr_code, collapse = " "), "\n")
if (!identical(hdr_code, ITEMS)) { cat("  !! header codes are not C1..C17\n"); ok <- FALSE }

## ---- A. per-item n, deposit vs live ------------------------------------
s   <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi  <- as.data.frame(s$per_item)
liven <- setNames(as.integer(pi$n), as.character(pi$item))[ITEMS]
depn  <- sapply(ITEMS, function(c) sum(!is.na(dat[[c]])))

cat("\n-- A. per-item n: S5 File (0s dropped) vs live table --\n")
cat(sprintf("%-5s %8s %8s %6s\n", "item", "deposit", "live", "diff"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-5s %8d %8d %6d\n", ITEMS[i], depn[i], liven[i], liven[i] - depn[i]))
nA <- sum(depn == liven)
cat(sprintf("matched: %d/17 (n is not constant: %s)\n",
            nA, paste(sort(unique(depn)), collapse = "/")))
if (nA != 17) ok <- FALSE

## ---- B. shipped wording vs Table 4 -------------------------------------
csv <- read.csv(file.path(dirname(sub("^--file=", "", grep("^--file=",
        commandArgs(FALSE), value = TRUE)[1])),
        paste0(TABLE, "__items.csv")), encoding = "UTF-8", stringsAsFactors = FALSE)
ship <- sapply(ITEMS, function(c)
    unique(csv$item_text_translated[csv$item == c])[1])
ship <- sub(" Index illumination:.*$", "", ship)   # Table 4 puts these in footnotes
cat("\n-- B. shipped item_text_translated vs paper Table 4 (code-prefixed) --\n")
nB <- 0
for (i in seq_along(ITEMS)) {
    m <- identical(trimws(as.character(ship[i])), trimws(TAB4[i]))
    nB <- nB + m
    cat(sprintf("%-5s %-5s %s\n", ITEMS[i], if (m) "OK" else "MISMATCH",
                substr(ship[i], 1, 68)))
}
cat(sprintf("matched: %d/17\n", nB))
if (nB != 17) ok <- FALSE

## ---- C. option direction ------------------------------------------------
obs <- sapply(ITEMS, function(c) mean(dat[[c]], na.rm = TRUE))
cat("\n-- C. per-item mean vs Table 5, as shipped and reversed --\n")
cat(sprintf("%-5s %9s %9s %7s %9s %7s\n",
            "item", "published", "as-shipped", "diff", "reversed", "diff"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-5s %9.2f %9.2f %7.2f %9.2f %7.2f\n", ITEMS[i], PUB_MEAN[i],
                obs[i], obs[i] - PUB_MEAN[i], 6 - obs[i], 6 - obs[i] - PUB_MEAN[i]))
wS <- max(abs(obs - PUB_MEAN)); wR <- max(abs((6 - obs) - PUB_MEAN))
cat(sprintf("largest deviation -- as shipped: %.3f | reversed: %.3f\n", wS, wR))
if (!(wS < 0.20 && wR > 1.0)) ok <- FALSE

cat("\nNote: check C fixes only the direction of the 1-5 coding; C4..C8 sit within\n",
    "0.04 of each other and C would not separate them. Check B is what pins every\n",
    "item, because Table 4 prints the code beside the wording.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
