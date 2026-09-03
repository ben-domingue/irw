# verify_vocabulary_iq.R -- Step 5b mapping verification for `vocabulary_iq`.
#
# THE CLAIM UNDER TEST
# --------------------
# The IRW `item` codes are bare integers 1..75 invented by the processing script
# (`data/vocabulary_iq.R`): it lowercases the VIQT_data.csv header, drops the E*,
# score_*, country, introelapse, testelapse and demographic columns, pivots the
# rest long, and assigns `item_id = row_number()` over `unique(item)` -- i.e. the
# surviving column order. The shipped item_text therefore asserts
#
#     items  1..45  ==  source columns Q1..Q45   (the 45 vocabulary questions)
#     items 46..75  ==  source columns S1..S30   (the supplemental survey items)
#
# Nothing in the live table's item codes records that. So this script RE-RUNS the
# derivation over the original public source file and checks that the mapping
# reproduces the live data item by item (core model section 3: "re-run the script
# rather than reason about it").
#
# WHAT WOULD BREAK IT
# -------------------
# Four independent per-item fingerprints are compared, all computed under the
# claimed item->column assignment:
#   n   -- non-missing responses           (Q: value != -1;  S: value not in {-1,0})
#   sr  -- number of correct responses     (Q: value == the codebook's key; S: 0)
#   s1  -- sum of the respondent ids that answered the item
#   s2  -- sum of squares of those ids
# `id` in the live table is `row_number()` over the raw file, so s1/s2 fingerprint
# WHICH respondents answered, not merely how many. Any permutation of the item
# codes moves these numbers. They are also all distinct across the 75 items, so a
# full match distinguishes every item from every other one -- including the four
# groups of supplemental items (S27/S28, S14/S19, S20/S21, S7/S8/S17) that happen
# to tie on `n` alone and whose resp is uniformly 0.
#
# Fallback: if the source file cannot be downloaded, the hard-coded N_PRED/SR_PRED
# below (derived from it on 2026-09-03) still give a verdict, but without the
# id-level s1/s2 evidence.

suppressMessages(library(irw))

TABLE   <- "vocabulary_iq"
SRC_URL <- "http://openpsychometrics.org/_rawdata/VIQT_data.zip"
CACHE   <- file.path("..", "..", ".cache", "vocabulary_iq")   # from itemtables/batch_016/

# Per-item n and number-correct predicted by the re-run, 2026-09-03.
N_PRED <- c(12161, 11554, 12088, 10464, 12030, 11168, 10955, 10975, 10509, 12106,
            12080, 11433, 10563, 11891, 10787, 11878, 11734, 9015, 8007, 10006,
            8803, 12119, 11961, 10788, 10527, 11651, 6865, 9237, 10978, 11305,
            12095, 11683, 11086, 10581, 11173, 8116, 10897, 6598, 10513, 10106,
            10437, 9280, 6220, 8898, 11831, 12092, 12080, 12078, 12054, 12060,
            12067, 12061, 12061, 12057, 12055, 12068, 12053, 12052, 12049, 12058,
            12021, 12061, 12046, 12049, 12051, 12051, 12043, 12059, 12056, 12045,
            12042, 12047, 12047, 12044, 12025)
SR_PRED <- c(11956, 10686, 11837, 5207, 11791, 9617, 5655, 9473, 9057, 11637,
             11748, 10494, 10067, 11669, 9590, 11602, 11233, 6065, 6574, 8828,
             6197, 11773, 11507, 9732, 6710, 10649, 3471, 7715, 9783, 10495,
             11861, 11007, 10383, 8667, 8994, 6555, 10301, 4413, 8179, 5797,
             7824, 6227, 3271, 5471, 9145, rep(0, 30))

## ---- 1. locate the original source file, re-running the derivation if we can ----
find_raw <- function() {
    p <- file.path(CACHE, "VIQT_data", "VIQT_data.csv")
    if (file.exists(p)) return(p)
    dir.create(CACHE, recursive = TRUE, showWarnings = FALSE)
    z <- file.path(CACHE, "VIQT_data.zip")
    ok <- tryCatch({ utils::download.file(SRC_URL, z, quiet = TRUE); TRUE },
                   error = function(e) FALSE, warning = function(w) FALSE)
    if (!ok) return(NA_character_)
    tryCatch(utils::unzip(z, exdir = CACHE), error = function(e) NULL)
    if (file.exists(p)) p else NA_character_
}

raw_path <- find_raw()
have_raw <- !is.na(raw_path)
cols <- c(paste0("Q", 1:45), paste0("S", 1:30))

if (have_raw) {
    cb  <- readLines(file.path(dirname(raw_path), "codebook.txt"), warn = FALSE)
    ql  <- grep("^Q[0-9]+ *\t", cb, value = TRUE)
    stopifnot(length(ql) == 45)
    key <- as.integer(trimws(sapply(strsplit(ql, "\t"), `[`, 2)))
    raw <- read.delim(raw_path, check.names = FALSE)
    raw$pid <- seq_len(nrow(raw))          # == data/vocabulary_iq.R's row_number()
    pred <- do.call(rbind, lapply(seq_along(cols), function(i) {
        v    <- raw[[cols[i]]]
        keep <- if (i <= 45) v != -1 else !(v %in% c(-1, 0))
        pid  <- as.numeric(raw$pid[keep])
        r    <- if (i <= 45) as.integer(v[keep] == key[i]) else rep(0L, sum(keep))
        data.frame(item = i, src = cols[i], n = length(pid), sr = sum(r),
                   s1 = sum(pid), s2 = sum(pid^2))
    }))
    cat("source: re-ran data/vocabulary_iq.R's derivation over", raw_path, "\n")
} else {
    pred <- data.frame(item = 1:75, src = cols, n = N_PRED, sr = SR_PRED,
                       s1 = NA_real_, s2 = NA_real_)
    cat("source: OFFLINE -- using hard-coded n / n-correct only (no id fingerprints)\n")
}

## ---- 2. the live table ----
d <- irw::irw_fetch(TABLE)
d$item <- as.integer(as.character(d$item))
d$resp <- as.numeric(d$resp)
d$pid  <- as.numeric(as.character(d$id))
d <- d[!is.na(d$resp), ]
live <- data.frame(
    item = sort(unique(d$item)),
    n    = as.integer(tapply(d$pid,  d$item, length))[order(unique(sort(d$item)))],
    sr   = as.numeric(tapply(d$resp, d$item, sum)),
    s1   = as.numeric(tapply(d$pid,  d$item, sum)),
    s2   = as.numeric(tapply(d$pid,  d$item, function(x) sum(x^2))))
live <- live[order(live$item), ]

m <- merge(pred, live, by = "item", suffixes = c("_pred", "_live"))
m <- m[order(m$item), ]

## ---- 3. compare, printing the numbers ----
cat(sprintf("\n%-5s %-5s %8s %8s %8s %8s %16s %16s\n",
            "item", "col", "n_pred", "n_live", "cor_pr", "cor_lv", "sum_id_pred", "sum_id_live"))
for (i in seq_len(nrow(m)))
    cat(sprintf("%-5d %-5s %8d %8d %8.0f %8.0f %16.0f %16.0f\n",
                m$item[i], m$src[i], m$n_pred[i], m$n_live[i],
                m$sr_pred[i], m$sr_live[i],
                ifelse(is.na(m$s1_pred[i]), NA, m$s1_pred[i]), m$s1_live[i]))

ok_n  <- m$n_pred  == m$n_live
ok_sr <- m$sr_pred == m$sr_live
ok_id <- if (have_raw) (m$s1_pred == m$s1_live & m$s2_pred == m$s2_live) else rep(NA, nrow(m))

cat(sprintf("\nitems matching on n:            %d / %d\n", sum(ok_n), nrow(m)))
cat(sprintf("items matching on n correct:    %d / %d\n", sum(ok_sr), nrow(m)))
if (have_raw)
    cat(sprintf("items matching on id sum+sumsq: %d / %d\n", sum(ok_id), nrow(m)))

fk <- if (have_raw) {
    paste(m$n_pred, m$sr_pred, m$s1_pred, m$s2_pred)
} else {
    paste(m$n_pred, m$sr_pred)
}
cat(sprintf("distinct fingerprints across the 75 items: %d (a full match therefore\n",
            length(unique(fk))))
cat("  distinguishes every item from every other, not just as a set)\n")

if (!have_raw)
    cat("\nNOTE: run offline. n and n-correct alone leave the four all-zero supplemental\n",
        "groups (S27/S28, S14/S19, S20/S21, S7/S8/S17) tied; re-run with the source\n",
        "file reachable for the id-level fingerprints that separate them.\n", sep = "")

pass <- all(ok_n) && all(ok_sr) && (!have_raw || all(ok_id)) &&
        length(unique(fk)) == nrow(m)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
