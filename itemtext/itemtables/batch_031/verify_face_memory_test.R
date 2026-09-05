# verify_face_memory_test.R
#
# face_memory_test ships NO item text (blocked: see notes_face_memory_test.csv).
# What this script verifies is the CODE->SOURCE-COLUMN mapping that any future
# extraction would have to rely on, so the block can be lifted later without
# redoing the analysis.
#
# The claim: data/face_memory_test.R assigns integer item codes by
# row_number() over unique(item) after pivoting the columns it kept, in column
# order.  That predicts
#     item  1..75   == raw columns Q1..Q75      (Exposure Based Face Memory Test)
#     item 76..175  == raw columns PQ1..PQ100   (HEXACO-PI-R items, randomly sampled)
# The falsifiable prediction is the per-item count of non-missing responses:
# the script maps -1 and 0 to NA, so each column's own non-missing count must
# reproduce the live per-item n exactly, for all 175 items at once.
#
# Live numbers come from irw::irw_table_sets(per_item = TRUE) -- server-side
# aggregation, no table export, no quota spend.

suppressMessages(library(irw))

TABLE <- "face_memory_test"
CACHE <- file.path("..", "..", ".cache", "face_memory_test")
ZIP   <- file.path(CACHE, "EBFMT.zip")
if (!file.exists(ZIP)) {
    dir.create(CACHE, recursive = TRUE, showWarnings = FALSE)
    download.file("http://openpsychometrics.org/_rawdata/EBFMT.zip", ZIP, quiet = TRUE)
}
raw <- read.delim(unz(ZIP, "EBFMT/data.csv"), stringsAsFactors = FALSE)

cols <- c(paste0("Q", 1:75), paste0("PQ", 1:100))
stopifnot(all(cols %in% names(raw)))
pred <- vapply(cols, function(cn) {
    v <- suppressWarnings(as.numeric(raw[[cn]]))
    sum(!is.na(v) & v != -1 & v != 0)
}, numeric(1))
names(pred) <- as.character(seq_along(cols))   # item code = position

s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
live <- setNames(as.numeric(pi$n), as.character(pi$item))
live <- live[names(pred)]

cat(sprintf("%-6s %-8s %8s %8s %6s\n", "item", "column", "pred_n", "live_n", "diff"))
show <- c(1:3, 74:78, 173:175)
for (i in show)
    cat(sprintf("%-6s %-8s %8d %8d %6d\n", names(pred)[i], cols[i],
                as.integer(pred[i]), as.integer(live[i]), as.integer(live[i] - pred[i])))
cat("... (all 175 compared)\n\n")

ok <- sum(pred == live)
cat(sprintf("items whose predicted n equals live n: %d / %d\n", ok, length(pred)))

# Response-range signature: the two instruments are on different scales, so the
# 75/100 block boundary is independently visible in the live data.
rng <- paste0(pi$resp_min, "-", pi$resp_max)
names(rng) <- as.character(pi$item)
face <- rng[as.character(1:75)]; hex <- rng[as.character(76:175)]
cat(sprintf("items 1-75   resp range: %s (all %s)\n", paste(unique(face), collapse = ","),
            if (length(unique(face)) == 1) "identical" else "MIXED"))
cat(sprintf("items 76-175 resp range: %s (all %s)\n", paste(unique(hex), collapse = ","),
            if (length(unique(hex)) == 1) "identical" else "MIXED"))

uniq <- sum(table(pred)[as.character(pred)] == 1)
cat(sprintf("\nitems separated from every other item by n alone: %d / %d\n", uniq, length(pred)))
cat("Note: this reproduces the whole 175-vector of counts jointly, which pins the\n",
    "Q-block/PQ-block boundary and the within-block offsets, but it cannot separate\n",
    "two items that happen to share the same n (see the count above).\n", sep = "")

pass <- ok == length(pred) && length(unique(face)) == 1 && length(unique(hex)) == 1
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
