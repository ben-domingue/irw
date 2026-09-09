# verify_jordan_2020_pss10.R -- Step 5b, route 9 (response-frequency matching).
#
# STATUS: this table is BLOCKED on instrument rights (PSS family, irw#1955 /
# irw#1945 as extended 2026-09-07). No __items.csv was written and no wording is
# reproduced here. What this script banks is the CODE->SOURCE-COLUMN and
# LABEL->INTEGER mapping, so that if the PSS ruling is ever reversed the
# extraction is a re-run rather than a restart.
#
# Claim under test: the live table's item codes Q13_1..Q13_10 ARE the Qualtrics
# short-code column names in the study's S1 supplement (row 3 of the 3-row
# header), and the processing script's label->integer map
#   Never=0, Almost Never=1, Sometimes=2, Fairly Often=3, Very Often=4
# is the map that actually produced the live integers. Both would break if any
# item were permuted or any level shifted: the check is cell-for-cell over
# 10 items x 5 levels.

suppressMessages(library(irw))

TABLE <- "jordan_2020_pss10"
SI_URL <- paste0("https://journals.plos.org/plosone/article/file",
                 "?type=supplementary&id=10.1371/journal.pone.0240667.s001")
MAP_PSS <- c("Never" = 0, "Almost Never" = 1, "Sometimes" = 2,
             "Fairly Often" = 3, "Very Often" = 4)
ITEMS <- paste0("Q13_", 1:10)

# --- source side: raw labels, keyed by the source column name itself ---
cache <- file.path("..", "..", ".cache", TABLE, "s001.csv")
src_path <- if (file.exists(cache)) cache else SI_URL
raw <- read.csv(src_path, header = FALSE, stringsAsFactors = FALSE, check.names = FALSE)
# 3-row Qualtrics header: row 1 ImportId JSON, row 2 question text, row 3 short codes.
hdr <- as.character(unlist(raw[3, ]))
names(raw) <- hdr
raw <- raw[-(1:3), , drop = FALSE]
stopifnot(all(ITEMS %in% names(raw)))

src <- matrix(0L, nrow = length(ITEMS), ncol = length(MAP_PSS),
              dimnames = list(ITEMS, names(MAP_PSS)))
for (it in ITEMS) {
    tb <- table(trimws(raw[[it]]))
    for (lb in names(MAP_PSS)) src[it, lb] <- if (!is.na(tb[lb])) as.integer(tb[lb]) else 0L
}

# --- live side: integers ---
d <- irw::irw_fetch(TABLE)
live <- matrix(0L, nrow = length(ITEMS), ncol = length(MAP_PSS),
               dimnames = list(ITEMS, names(MAP_PSS)))
for (it in ITEMS) {
    tb <- table(d$resp[d$item == it])
    for (lb in names(MAP_PSS)) {
        k <- as.character(MAP_PSS[[lb]])
        live[it, lb] <- if (!is.na(tb[k])) as.integer(tb[k]) else 0L
    }
}

cat(sprintf("%-8s %s\n", "item",
            paste(sprintf("%18s", paste0(names(MAP_PSS), "=", MAP_PSS)), collapse = "")))
for (it in ITEMS)
    cat(sprintf("%-8s %s\n", it,
        paste(sprintf("%18s", paste0(src[it, ], "/", live[it, ])), collapse = "")))

mismatch <- sum(src != live)
cat(sprintf("\ncells compared: %d (10 items x 5 levels); mismatched cells: %d\n",
            length(src), mismatch))
cat(sprintf("source total responses: %d | live rows: %d\n", sum(src), sum(live)))

cat("Note: this establishes the resp<->label axis cell-for-cell and confirms the\n",
    "item codes are the source column names verbatim (no positional assignment).\n",
    "It does NOT establish any item_text mapping, because no item text is shipped\n",
    "for this table -- it is blocked on the PSS rights ruling.\n", sep = "")

cat(if (mismatch == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
