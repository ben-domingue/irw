# verify_fukuda_2021_info_reliability.R
#
# Claim under test: item codes info_source1..8 (assigned POSITIONALLY by
# data/fukuda_2021_healthliteracy.py, `{c: f"info_source{i+1}" for i,c in
# enumerate(info_cols)}` over the S1 columns matching "Information reliability")
# carry the item_text taken from the S1 header at that same position, and
# option_text 1..5 = untrusted/somewhat unreliable/neither/somewhat
# reliable/reliable.
#
# Route 9 (response-frequency matching, decisive): the S1 Data file
# (PLOS ONE 10.1371/journal.pone.0257552.s001) stores LABEL strings; the live
# IRW table stores integers 1-5. Counting each label per source column and each
# integer per live item must match cell for cell -- a swapped pair of items, or
# a flipped/permuted response scale, breaks it immediately.
# Route 1 (per-item means, corroborating): the paper's Results prints M +/- SD
# for all 8 sources in the same order.
#
# The 8x5 label counts below were read off the S1 file directly; the script
# re-downloads it when python3/pandas/openpyxl and network are available and
# uses the live download in preference to the hard-coded copy.

suppressMessages(library(irw))
TABLE <- "fukuda_2021_info_reliability"
ITEMS <- paste0("info_source", 1:8)
OPTS  <- c("untrusted", "somewhat unreliable", "neither", "somewhat reliable", "reliable")

SRC_LABEL <- c("Government announcement",
               "Announcement of local government",
               "newspaper article",
               "TV information",
               "Information from medical personnel such as doctors and pharmacists",
               "Information from friends and acquaintances",
               "Information from the Internet and SNS",
               "Information from magazines and books")

# S1 label counts, columns 30-37 in file order, levels in OPTS order.
SRC <- matrix(c(284, 169, 298, 196,  53,
                103, 146, 364, 315,  72,
                  0,  87, 377, 471,  65,
                120, 145, 394, 301,  40,
                 13,  21, 326, 497, 143,
                 55, 152, 600, 173,  20,
                 94, 218, 545, 129,  14,
                 27,  77, 514, 339,  43),
              nrow = 8, byrow = TRUE,
              dimnames = list(SRC_LABEL, OPTS))

# Paper Results, "(6) Health and medical information sources and reliability":
# national government 2.57 +/- 1.24; local government 3.11 +/- 1.07;
# newspapers 3.33 +/- 0.95; television 3.00 +/- 1.04; family physician/pharmacy
# 3.74 +/- 0.78; friends 2.95 +/- 0.79; Internet 2.75 +/- 0.85; books and
# magazines 3.29 +/- 0.78.
PAPER_M <- c(2.57, 3.11, 3.33, 3.00, 3.74, 2.95, 2.75, 3.29)

## --- optional live re-read of the S1 file ---------------------------------
py <- suppressWarnings(system2("python3", c("-c", shQuote(paste(
  "import pandas as pd,sys",
  "u='https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0257552.s001'",
  "d=pd.read_excel(u)",
  "cols=[c for c in d.columns if 'Information reliability' in c]",
  "opts=['untrusted','somewhat unreliable','neither','somewhat reliable','reliable']",
  "[print(','.join(str(int((d[c].astype(str).str.strip()==o).sum()) ) for o in opts)) for c in cols]",
  sep="\n"))), stdout = TRUE, stderr = FALSE))
if (!is.null(attr(py, "status")) || length(py) != 8) {
    cat("S1 re-download unavailable; using the hard-coded label counts.\n\n")
} else {
    live_src <- matrix(as.integer(unlist(strsplit(py, ","))), nrow = 8, byrow = TRUE)
    cat("S1 re-downloaded; hard-coded counts agree with the file: ",
        identical(as.integer(SRC), as.integer(live_src)), "\n\n", sep = "")
    if (!identical(as.integer(SRC), as.integer(live_src))) SRC[] <- live_src
}

## --- live IRW counts -------------------------------------------------------
d <- irw::irw_fetch(TABLE)
LIVE <- matrix(0L, 8, 5, dimnames = list(ITEMS, OPTS))
tb <- table(factor(d$item, ITEMS), factor(d$resp, 1:5))
LIVE[] <- as.integer(tb)

cat("Route 9 -- S1 label counts (top) vs live integer counts (bottom), per item:\n")
cat(sprintf("%-14s %s\n", "item", paste(sprintf("%20s", OPTS), collapse = "")))
for (i in 1:8) {
    cat(sprintf("%-14s %s   <- S1 col %d: %s\n", ITEMS[i],
                paste(sprintf("%20d", SRC[i, ]), collapse = ""), i + 29, SRC_LABEL[i]))
    cat(sprintf("%-14s %s   <- live\n", "",
                paste(sprintf("%20d", LIVE[i, ]), collapse = "")))
}
cell_ok <- identical(as.integer(SRC), as.integer(LIVE))
cat(sprintf("\nall 40 item x level cells match: %s\n", cell_ok))

# Does the route separate EVERY item from EVERY other item?
dups <- FALSE
for (i in 1:7) for (j in (i + 1):8)
    if (identical(SRC[i, ], SRC[j, ])) dups <- TRUE
cat(sprintf("all 8 source count-vectors pairwise distinct (so no item pair is interchangeable under this test): %s\n", !dups))

## --- corroborating route 1 -------------------------------------------------
obs_m <- round(tapply(d$resp, factor(d$item, ITEMS), mean), 2)
cat("\nRoute 1 -- paper per-item mean vs live mean:\n")
cat(sprintf("%-14s %9s %9s %8s  %s\n", "item", "paper", "live", "diff", "source"))
for (i in 1:8)
    cat(sprintf("%-14s %9.2f %9.2f %8.2f  %s\n", ITEMS[i], PAPER_M[i], obs_m[i],
                obs_m[i] - PAPER_M[i], SRC_LABEL[i]))
n_close <- sum(abs(obs_m - PAPER_M) <= 0.02)
cat(sprintf("items within 0.02 of the published mean: %d of 8\n", n_close))
cat("Known source-internal discrepancy: info_source3 (newspaper article) reads 3.51 live\n",
    "against 3.33 published; the S1 newspaper column contains zero 'untrusted' responses,\n",
    "so the deposited column and the paper's Table 9 figure disagree in the SOURCE. This is\n",
    "a response-data caveat, not a mapping question -- route 9 already ties that column to\n",
    "its header cell for cell.\n", sep = "")

cat("\nWhat this does NOT establish: nothing about the Japanese wording respondents\n",
    "actually read (the deposit publishes English headers only), and nothing about the\n",
    "instructions text, which the study never published verbatim.\n", sep = "")

cat(if (cell_ok && !dups) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
