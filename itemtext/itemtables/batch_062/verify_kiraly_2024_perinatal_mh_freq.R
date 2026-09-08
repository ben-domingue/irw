# verify_kiraly_2024_perinatal_mh_freq.R
#
# Step 5b re-runnable evidence. mapping_basis = data_labels: the IRW `item` codes
# ARE the column names of the study's S2 Data workbook (see
# data/kiraly_2024_perinatal_mh_providers.py, FREQ_COLS), and each column name is
# a snake_case rendering of the question wording. The shipped item_text, however,
# comes from a SECOND source -- the study's two live Qualtrics forms (S1 File) --
# so the code->column tie and the column->wording tie are checked separately here.
#
# CHECK 1 (code <-> source column): per-item non-missing counts in the S2 workbook
#   must reproduce the live per-item n exactly. A shifted or permuted column
#   assignment breaks this immediately, because the 16 items split 96/95/94/81/80/15/14
#   by which of the two survey forms carried them.
# CHECK 2 (column <-> shipped wording): every shipped item_text, normalised to
#   snake_case tokens, must have its OWN item code as its single best token-overlap
#   match among all 16 codes. If item_text for two items were swapped, the best-match
#   assignment stops being the identity permutation and this fails.
#
# What this does NOT establish: which of the two forms' phrasings is "the" wording
# for the 7 items asked on both. Four of those differ slightly between the
# obstetrician and pediatrician/NP forms; the shipped wording is the one the
# workbook's own column name reproduces, and the variants are recorded in
# notes_kiraly_2024_perinatal_mh_freq.csv. That is a wording choice, not a mapping.

suppressMessages(library(irw))

TABLE <- "kiraly_2024_perinatal_mh_freq"
XLSX  <- paste0("https://journals.plos.org/plosone/article/file",
                "?type=supplementary&id=10.1371/journal.pone.0306265.s002")

items_csv <- file.path(dirname(sub("^--file=", "",
    commandArgs(FALSE)[grep("^--file=", commandArgs(FALSE))][1])),
    paste0(TABLE, "__items.csv"))
shipped <- read.csv(items_csv, colClasses = "character")
shipped <- unique(shipped[, c("item", "item_text")])

## ---- CHECK 1 --------------------------------------------------------------
tmp <- tempfile(fileext = ".xlsx")
utils::download.file(XLSX, tmp, quiet = TRUE, mode = "wb")
raw <- as.data.frame(readxl::read_excel(tmp))

live <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)$per_item
live <- live[order(live$item), c("item", "n")]
# blank cells are stored as the literal string "NA" in this workbook
src_n <- sapply(live$item, function(x) sum(!(is.na(raw[[x]]) | trimws(raw[[x]]) %in% c("", "NA"))))

cat(sprintf("%-95s %6s %6s\n", "item (= S2 workbook column name)", "live n", "xlsx n"))
for (i in seq_len(nrow(live)))
    cat(sprintf("%-95s %6d %6d\n", substr(live$item[i], 1, 95), live$n[i], src_n[i]))
ok1 <- all(live$n == src_n)
cat(sprintf("\nCHECK 1 code<->column: %d/%d per-item counts reproduce exactly\n",
            sum(live$n == src_n), nrow(live)))

## ---- CHECK 2 --------------------------------------------------------------
toks <- function(x) {
    x <- tolower(x)
    x <- gsub("[^a-z0-9]+", " ", x)
    setdiff(strsplit(trimws(x), " +")[[1]],
            c("i", "a", "the", "my", "of", "and", "to", "in", "their", "with",
              "her", "his", "you", "do", "about", "it", "for", "on", "s", "am",
              "is", "are", "at", "an", "or", "if", "will", "that", "they", "have"))
}
code_t <- lapply(shipped$item, toks)
text_t <- lapply(shipped$item_text, toks)
n <- nrow(shipped)
J <- matrix(0, n, n)
for (i in seq_len(n)) for (j in seq_len(n)) {
    a <- text_t[[i]]; b <- code_t[[j]]
    J[i, j] <- length(intersect(a, b)) / length(union(a, b))
}
best <- apply(J, 1, which.max)
self <- diag(J)
runner <- sapply(seq_len(n), function(i) max(J[i, -i]))
cat(sprintf("\n%-60s %6s %6s %s\n", "shipped item_text (truncated)", "self J", "next J", "best match is own code"))
for (i in seq_len(n))
    cat(sprintf("%-60s %6.2f %6.2f %s\n", substr(shipped$item_text[i], 1, 60),
                self[i], runner[i], ifelse(best[i] == i, "yes", "NO")))
ok2 <- all(best == seq_len(n))
cat(sprintf("\nCHECK 2 column<->wording: %d/%d item_texts match their own code best (min self-J %.2f, max rival J %.2f)\n",
            sum(best == seq_len(n)), n, min(self), max(runner)))

## ---- CHECK 3 (option_text <-> resp) ---------------------------------------
# The workbook stores frequency LABELS; the live table stores 1-5. Applying the
# shipped option_text->resp mapping to the source labels must reproduce each
# item's live resp_min / resp_max / n_resp_levels. Items whose respondents never
# used an end category (e.g. one item runs 4-5, another 2-5) are what makes this
# decisive about the direction: a flipped scale mismatches immediately.
MAP <- c("never" = 1, "sometimes" = 2, "about half of the time" = 3,
         "most of the time" = 4, "always" = 5)
liv3 <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)$per_item
liv3 <- liv3[order(liv3$item), ]
cat(sprintf("\n%-60s %-18s %-18s\n", "item", "live min/max/lev", "source min/max/lev"))
ok3 <- TRUE
for (i in seq_len(nrow(liv3))) {
    v <- raw[[liv3$item[i]]]
    v <- v[!(is.na(v) | trimws(v) %in% c("", "NA"))]
    r <- unname(MAP[tolower(trimws(v))])
    a <- c(min(liv3$resp_min[i]), liv3$resp_max[i], liv3$n_resp_levels[i])
    b <- c(min(r), max(r), length(unique(r)))
    if (!all(a == b)) ok3 <- FALSE
    cat(sprintf("%-60s %-18s %-18s %s\n", substr(liv3$item[i], 1, 60),
                paste(a, collapse = "/"), paste(b, collapse = "/"),
                ifelse(all(a == b), "", "MISMATCH")))
}
cat(sprintf("\nCHECK 3 option_text<->resp: %s\n",
            ifelse(ok3, "all 16 items reproduce live resp min/max/level-count", "FAILED")))

cat(if (ok1 && ok2 && ok3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
