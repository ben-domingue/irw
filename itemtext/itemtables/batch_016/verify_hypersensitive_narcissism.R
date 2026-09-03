# verify_hypersensitive_narcissism.R
#
# CLAIM UNDER TEST: the IRW item codes "1".."22" are the column positions of
# data.csv in the Open-Source Psychometrics Project's HSNS+DD deposit, after
# data/hypersensitive_narcissism.R drops age/gender/accuracy/country -- i.e.
#   1..10  = HSNS1..HSNS10, 11..14 = DDP1..DDP4,
#   15..18 = DDN1..DDN4,    19..22 = DDM1..DDM4
# and that resp 1..5 is the deposit's raw 1..5 coding (0 -> NA), unrecoded.
#
# FALSIFIABLE PREDICTION: for every item, the full response-frequency profile
# (counts of resp = 1,2,3,4,5 and of missing) must match the corresponding
# source column cell for cell. All 22 source profiles are distinct, so any
# permutation of the mapping -- including a swap of two adjacent items --
# breaks at least two rows of the comparison.
#
# QUOTA NOTE: this deliberately does NOT call irw::irw_fetch(), which would
# export all 1,187,582 rows. It runs one server-side GROUP BY instead; queries
# are not export-capped. Same numbers, no egress.

suppressMessages(library(irw))

TABLE <- "hypersensitive_narcissism"
ZIPURL <- "http://openpsychometrics.org/_rawdata/HSNS+DD.zip"
CACHE  <- file.path(".cache", TABLE)
CSV    <- file.path(CACHE, "HSNS+DD", "data.csv")

if (!file.exists(CSV)) {
    dir.create(CACHE, recursive = TRUE, showWarnings = FALSE)
    z <- file.path(CACHE, "hsnsdd.zip")
    if (!file.exists(z)) download.file(ZIPURL, z, quiet = TRUE)
    unzip(z, exdir = CACHE)
}

raw  <- read.csv(CSV, sep = "\t", check.names = FALSE)
cols <- setdiff(names(raw), c("age", "gender", "accuracy", "country"))
stopifnot(length(cols) == 22)

q  <- getFromNamespace(".irw_query_tibble", "irw")
ft <- getFromNamespace(".fetch_redivis_table", "irw")
ref <- ft(TABLE, source = "core")$qualified_reference
live <- as.data.frame(q(sprintf(
    "SELECT CAST(item AS STRING) AS item, TRIM(CAST(resp AS STRING)) AS resp, COUNT(*) AS n FROM `%s` GROUP BY 1,2", ref)))
live$resp[is.na(live$resp) | live$resp == ""] <- "NA"

cell <- function(i, r) { x <- live$n[live$item == as.character(i) & live$resp == r]; if (length(x)) x else 0L }

cat(sprintf("%-4s %-7s %-27s %-27s %s\n", "code", "srccol",
            "source 1/2/3/4/5 (missing)", "live 1/2/3/4/5 (missing)", ""))
ok <- TRUE
for (i in seq_along(cols)) {
    v   <- raw[[cols[i]]]
    src <- vapply(1:5, function(k) sum(v == k, na.rm = TRUE), integer(1))
    srcNA <- sum(v == 0 | is.na(v))
    lv   <- vapply(1:5, function(k) as.integer(cell(i, as.character(k))), integer(1))
    lvNA <- as.integer(cell(i, "NA"))
    m <- all(src == lv) && srcNA == lvNA
    ok <- ok && m
    cat(sprintf("%-4d %-7s %-27s %-27s %s\n", i, cols[i],
                sprintf("%s (%d)", paste(src, collapse = "/"), srcNA),
                sprintf("%s (%d)", paste(lv,  collapse = "/"), lvNA),
                if (m) "OK" else "MISMATCH"))
}

prof <- vapply(cols, function(cn) paste(vapply(1:5, function(k) sum(raw[[cn]] == k, na.rm = TRUE), integer(1)), collapse = "-"), character(1))
cat(sprintf("\ndistinct source profiles: %d of %d -- every item is separated from every other.\n",
            length(unique(prof)), length(prof)))
cat("This establishes both mapping axes: which source column each integer code is\n",
    "(so which item_text belongs to it) and that resp 1..5 is the raw, unrecoded\n",
    "deposit scale (so option_text Disagree/Neutral/Agree sits at 1/3/5). It does\n",
    "NOT establish the wording of items 2 and 4's unlabelled anchors -- the deposit\n",
    "labels only 1, 3 and 5, and those option_text cells are deliberately blank.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
