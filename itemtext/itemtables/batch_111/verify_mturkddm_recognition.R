# verify_mturkddm_recognition.R
#
# Claim under test: every IRW `item` in mturkddm_recognition IS the literal
# stimulus word that was shown at test (column 11, `test_word_string`, of the
# study's own Experiment1.data on OSF), and `resp` is trial ACCURACY with
# 1 = correct / 0 = incorrect -- which is what option_text asserts.
#
# This is not a plumbing check. It re-runs data/mturk_ddm.R's derivation over
# the raw OSF file and compares, per item, (a) the number of scored trials and
# (b) the set of resp values observed, against server-side aggregates from the
# live table. A permuted item->word mapping, or a flipped accuracy coding,
# breaks both comparisons immediately (the flipped counterfactual is computed
# and printed below).
#
# Live side uses irw::irw_table_sets() (server-side GROUP BY), never irw_fetch(),
# so it does not touch the 200GB/30-day Redivis export cap.

suppressMessages(library(irw))

TABLE <- "mturkddm_recognition"
RAW_URL <- "https://osf.io/download/c8427/"   # OSF za9y8 / Experiment1.data
CACHE <- file.path("itemtext", ".cache", TABLE, "Experiment1.data")
if (!file.exists(CACHE)) CACHE <- file.path(".cache", TABLE, "Experiment1.data")
if (!file.exists(CACHE)) {
    CACHE <- tempfile(fileext = ".data")
    download.file(RAW_URL, CACHE, quiet = TRUE)
}

x <- read.csv(CACHE, stringsAsFactors = FALSE)
# data/mturk_ddm.R: drop practice (column_7_value == 9), task 2 = item
# recognition, key 0 = invalid keypress -> NA resp, correct iff the key matches
# the trial's studied/new status (column_8_value 1,2 = studied -> key 1).
x <- x[x$column_7_value != 9 & x$task_number == 2 & x$response_key_ID != 0, ]
z <- ifelse(x$column_8_value %in% 1:2, 1, 2)
x$resp <- ifelse(x$response_key_ID == z, 1, 0)

raw_n     <- tapply(x$resp, x$test_word_string, length)
raw_min   <- tapply(x$resp, x$test_word_string, min)
raw_max   <- tapply(x$resp, x$test_word_string, max)
# counterfactual: accuracy coding reversed (0 = correct)
flip_min  <- 1 - raw_max
flip_max  <- 1 - raw_min

s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
rownames(pi) <- pi$item

w <- sort(names(raw_n))
cat(sprintf("raw distinct stimulus words: %d | live distinct items: %d | identical sets: %s\n",
            length(raw_n), nrow(pi), identical(w, sort(pi$item))))

if (!identical(w, sort(pi$item))) { cat("VERDICT: FAIL\n"); quit(status = 0) }

n_bad     <- sum(raw_n[w] != pi[w, "n"])
range_bad <- sum(raw_min[w] != pi[w, "resp_min"] | raw_max[w] != pi[w, "resp_max"])
flip_bad  <- sum(flip_min[w] != pi[w, "resp_min"] | flip_max[w] != pi[w, "resp_max"])

cat("\nfirst 10 items, raw re-run vs live aggregate:\n")
cat(sprintf("%-14s %6s %6s %10s %10s\n", "item", "raw_n", "live_n", "raw_range", "live_range"))
for (it in head(w, 10))
    cat(sprintf("%-14s %6d %6d %10s %10s\n", it, raw_n[it], pi[it, "n"],
                sprintf("%d-%d", raw_min[it], raw_max[it]),
                sprintf("%d-%d", pi[it, "resp_min"], pi[it, "resp_max"])))

cat(sprintf("\nper-item n mismatches:                 %d / %d\n", n_bad, length(w)))
cat(sprintf("per-item resp-range mismatches:        %d / %d\n", range_bad, length(w)))
cat(sprintf("...same, with accuracy coding FLIPPED: %d / %d  (must be > 0)\n",
            flip_bad, length(w)))

cat("\nWhat this does NOT establish: nothing about which words were STUDIED vs NEW\n",
    "on any given trial -- that varies by subject and block, which is why\n",
    "correct_response is blank. It also does not test `instructions`, which is\n",
    "transcribed from the paper's instruction appendix and cannot be checked\n",
    "against the response data.\n", sep = "")

ok <- (n_bad == 0 && range_bad == 0 && flip_bad > 0)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
