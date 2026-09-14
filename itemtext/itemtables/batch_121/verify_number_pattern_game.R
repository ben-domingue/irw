# verify_number_pattern_game.R
#
# CLAIM UNDER TEST
# ----------------
# `number_pattern_game`'s item codes are bare integers 1..255 that the IRW
# processing script (data/number_pattern_game.R) INVENTS:
#
#     items <- as.data.frame(unique(df$set)); items <- mutate(items, item = row_number())
#
# i.e. item i is the i-th DISTINCT VALUE OF `set`, in the row order of the raw
# Dataverse file numbergame_data.csv. The shipped item_text for item i is that
# set's numbers. Nothing in the live table records which set an integer came
# from, so the claim is only checkable by re-running the derivation over the raw
# file and showing the result reproduces the live table item by item.
#
# WHAT IS COMPARED (this is the mapping, not the plumbing)
# --------------------------------------------------------
# For each of the 255 items, a fingerprint built from columns the itemtext file
# does NOT contain: response count, mean response, and the respondent-id
# footprint (n distinct id, min, max, sum). The raw file's `id` is shifted by +1
# by the processing script, so that shift is applied here too.
#
# If the set->integer assignment were permuted in ANY way, the raw-derived
# fingerprint for at least one item would land on a different live item. The
# script also reports how many of the 255 fingerprints are mutually distinct: a
# fingerprint that is unique per item is what makes this a per-item check rather
# than a distributional one.
#
# Source of raw data: Harvard Dataverse doi:10.7910/DVN/A8ZWLF (CC0 1.0),
# file numbergame_data.csv (datafile id 2696204), fetched in original format.

suppressMessages({
    library(irw)
})

TABLE <- "number_pattern_game"
RAW_URL <- "https://dataverse.harvard.edu/api/access/datafile/2696204?format=original"
CACHE <- file.path(".cache", TABLE, "numbergame_data.csv")

if (!file.exists(CACHE)) {
    dir.create(dirname(CACHE), recursive = TRUE, showWarnings = FALSE)
    cat("downloading raw file from Dataverse ...\n")
    utils::download.file(RAW_URL, CACHE, quiet = TRUE, mode = "wb")
}

raw <- utils::read.csv(CACHE, colClasses = c(set = "character"), stringsAsFactors = FALSE)
cat(sprintf("raw rows: %d | distinct sets: %d\n", nrow(raw), length(unique(raw$set))))

# --- re-run the processing script's derivation ---------------------------
raw$id <- raw$id + 1L                       # data/number_pattern_game.R
sets <- unique(raw$set)                     # file order == row_number() order
raw$item <- match(raw$set, sets)

fp <- function(item, resp, id) {
    o <- order(item)
    item <- item[o]; resp <- resp[o]; id <- id[o]
    data.frame(
        item   = as.integer(names(tapply(resp, item, length))),
        n      = as.integer(tapply(resp, item, length)),
        mean   = as.numeric(tapply(resp, item, mean)),
        n_id   = as.integer(tapply(id, item, function(v) length(unique(v)))),
        min_id = as.integer(tapply(id, item, min)),
        max_id = as.integer(tapply(id, item, max)),
        sum_id = as.numeric(tapply(id, item, sum)),
        stringsAsFactors = FALSE
    )
}

R <- fp(raw$item, raw$rating, raw$id)

# --- live IRW table ------------------------------------------------------
d <- irw::irw_fetch(TABLE)
d$item <- as.integer(as.character(d$item))
d$resp <- as.numeric(d$resp)
d$id   <- as.integer(as.character(d$id))
L <- fp(d$item, d$resp, d$id)

m <- merge(R, L, by = "item", suffixes = c("_raw", "_live"))
stopifnot(nrow(m) == 255)

ok_n    <- sum(m$n_raw == m$n_live)
ok_mean <- sum(abs(m$mean_raw - m$mean_live) < 1e-9)
ok_nid  <- sum(m$n_id_raw == m$n_id_live)
ok_min  <- sum(m$min_id_raw == m$min_id_live)
ok_max  <- sum(m$max_id_raw == m$max_id_live)
ok_sum  <- sum(m$sum_id_raw == m$sum_id_live)

sig <- paste(m$n_raw, sprintf("%.12f", m$mean_raw), m$n_id_raw,
             m$min_id_raw, m$max_id_raw, m$sum_id_raw, sep = "|")
n_distinct_fp <- length(unique(sig))

cat("\n-- first 8 items: shipped set, then raw-derived vs live fingerprint --\n")
cat(sprintf("%-5s %-18s %7s %7s %9s %9s %6s %6s %9s %9s\n",
            "item", "set (item_text)", "n_raw", "n_live", "mean_raw", "mean_live",
            "nid_r", "nid_l", "sumid_r", "sumid_l"))
for (i in 1:8) {
    j <- which(m$item == i)
    cat(sprintf("%-5d %-18s %7d %7d %9.5f %9.5f %6d %6d %9.0f %9.0f\n",
                i, gsub("_ ", ", ", sets[i]),
                m$n_raw[j], m$n_live[j], m$mean_raw[j], m$mean_live[j],
                m$n_id_raw[j], m$n_id_live[j], m$sum_id_raw[j], m$sum_id_live[j]))
}

cat(sprintf("\nagreement over all 255 items: n %d/255 | mean(<1e-9) %d/255 | n_id %d/255 | min_id %d/255 | max_id %d/255 | sum_id %d/255\n",
            ok_n, ok_mean, ok_nid, ok_min, ok_max, ok_sum))
cat(sprintf("largest |mean_raw - mean_live|: %.3g\n", max(abs(m$mean_raw - m$mean_live))))
cat(sprintf("distinct fingerprints among the 255 items: %d/255\n", n_distinct_fp))

cat("\nEstablishes: each integer item code is tied to one specific stimulus set,\n",
    "individually (fingerprints are unique per item), so no permutation of the\n",
    "255 set->integer assignments is consistent with the live data.\n",
    "Does NOT establish: which of the 30 targets a given response referred to --\n",
    "the raw `target` column is dropped by the IRW processing script and is not\n",
    "recoverable from the live table. That is a property of the response data,\n",
    "not of the item->text mapping.\n", sep = "")


# --- second axis: option_text <-> resp (does 1 mean 'yes'?) --------------
# README.txt: "binary (1 or 0) rating, corresponding to whether the response was
# 'yes' or 'no'". Figure 1: "Press y for 'yes' or n for 'no'." Neither states
# which integer is which, so check it against content: `target` (raw only, and
# dropped by the IRW script) says what each response was about. The per-item
# mean agreement above proves raw `rating` IS live `resp`, so a content check on
# `rating` transfers.
cat("\n-- resp direction: mean rating for concept-consistent vs other targets --\n")
probe <- list(
    "10_ 50_ 100"  = function(t) t %% 10 == 0,
    "16_ 32_ 2_ 8" = function(t) t %in% c(1, 2, 4, 8, 16, 32, 64),
    "3_ 33_ 99"    = function(t) t %% 3 == 0
)
dir_ok <- TRUE
for (s in names(probe)) {
    sub <- raw[raw$set == s, ]
    inn <- probe[[s]](sub$target)
    mi <- mean(sub$rating[inn]); mo <- mean(sub$rating[!inn])
    cat(sprintf("  set {%s}: consistent targets mean=%.3f (n=%d) | others mean=%.3f (n=%d)\n",
                gsub("_ ", ", ", s), mi, sum(inn), mo, sum(!inn)))
    if (!(mi > mo)) dir_ok <- FALSE
}
cat(sprintf("  => 1 = 'yes', 0 = 'no': %s\n", if (dir_ok) "confirmed" else "CONTRADICTED"))

pass <- dir_ok && ok_n == 255 && ok_mean == 255 && ok_nid == 255 && ok_min == 255 &&
        ok_max == 255 && ok_sum == 255 && n_distinct_fp == 255
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
