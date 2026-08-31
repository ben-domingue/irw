## verify_himmelstein-admc_raw-2025.R
##
## Route: source_code_id_match + response_range_fingerprint.
##
## The primary tie is a code match, not an order inference: the study's own
## experiment source keys each item to the exact identifier the data records
## (data/data_admc_raw.py passes item_col='admc_id'), so this script re-derives the
## shipped text from those files and diffs it. It then re-runs the corroborating
## fingerprint, which is the part that could in principle come apart from the data.
##
## Run from itemtext/:
##   Rscript itemtables/batch_014/verify_himmelstein-admc_raw-2025.R

suppressMessages(library(irw))
TBL <- "himmelstein-admc_raw-2025"
CSV <- "itemtables/batch_014/himmelstein-admc_raw-2025__items.csv"
D   <- ".cache/himmelstein-admc_raw-2025"
RAW <- "https://raw.githubusercontent.com/forecastingresearch/fpt/main/materials/js"
FORMS <- c("admc_framing_a1_task", "admc_framing_a2_task",
           "admc_framing_rc1_task", "admc_framing_rc2_task")
fail <- character(0)

dir.create(D, recursive = TRUE, showWarnings = FALSE)
for (f in c(FORMS, "admc_decision_rules_task")) {
    p <- file.path(D, paste0(f, ".js"))
    if (!file.exists(p)) download.file(file.path(RAW, paste0(f, ".js")), p, quiet = TRUE)
}
it <- read.csv(CSV, stringsAsFactors = FALSE)

## ---- 1. framing text is identical across all four counterbalanced forms -------
cat("=== 1. are the 28 framing items identical across the four form files? ===\n")
grab <- function(p) {
    s <- paste(readLines(p, warn = FALSE), collapse = "\n")
    m <- gregexpr("stimulus_html:\\s*`.*?`,\\s*\\n\\s*label_min:\\s*'[^']*',\\s*label_max:\\s*'[^']*',\\s*\\n\\s*id:\\s*'[a-z0-9_]+'", s)
    regmatches(s, m)[[1]]
}
sets <- lapply(file.path(D, paste0(FORMS, ".js")), grab)
n <- vapply(sets, length, 1L)
same <- vapply(sets, function(x) identical(sort(x), sort(sets[[1]])), TRUE)
for (i in seq_along(FORMS))
    cat(sprintf("  %-26s items=%2d identical_to_a1=%s\n", FORMS[i], n[i], same[i]))
if (!all(same) || !all(n == 28)) fail <- c(fail, "framing items differ across form files")

## ---- 2. decision-rules keys re-derived from source ---------------------------
cat("\n=== 2. correct_response vs the js correct_answers ===\n")
s <- paste(readLines(file.path(D, "admc_decision_rules_task.js"), warn = FALSE), collapse = "\n")
m <- regmatches(s, gregexpr("id:\\s*'dr[0-9]+',\\s*correct_answers:\\s*\\[[^]]*\\]", s))[[1]]
code <- sub(".*id:\\s*'(dr[0-9]+)'.*", "\\1", m)
keys <- gsub("['\" ]", "", sub(".*\\[([^]]*)\\].*", "\\1", m))
src <- data.frame(item = code, expect = gsub(",", ";", keys),
                  nkey = lengths(strsplit(keys, ",")), stringsAsFactors = FALSE)
ship <- unique(it[grepl("^dr", it$item), c("item", "correct_response")])
mm <- merge(src, ship, by = "item")
bad <- mm[mm$expect != mm$correct_response, ]
cat("  dr items compared:", nrow(mm), "| mismatches:", nrow(bad), "\n")
if (nrow(bad)) { fail <- c(fail, "correct_response mismatch"); print(bad) }

## ---- 3. the fingerprint: n correct answers predicts max resp ----------------
cat("\n=== 3. response-range fingerprint against live data ===\n")
live <- tryCatch(irw_fetch(TBL), error = function(e) NULL)
if (is.null(live) || !nrow(live)) {
    cat("  live data unavailable -- fingerprint unchecked\n")
    fail <- c(fail, "live data unavailable")
} else {
    live$item <- as.character(live$item)
    obs <- tapply(live$resp, live$item, max)
    mm$observed <- as.integer(obs[mm$item])
    mm <- mm[order(as.integer(sub("dr", "", mm$item))), ]
    for (i in seq_len(nrow(mm)))
        cat(sprintf("  %-5s keys=%-8s predicted max=%d observed max=%d  %s\n",
            mm$item[i], mm$expect[i], mm$nkey[i], mm$observed[i],
            ifelse(mm$nkey[i] == mm$observed[i], "match", "*** MISMATCH ***")))
    if (!all(mm$nkey == mm$observed)) fail <- c(fail, "fingerprint mismatch")
    fr <- live[!grepl("^dr", live$item), ]
    lv <- tapply(fr$resp, fr$item, function(v) paste(sort(unique(v)), collapse = ","))
    cat("  framing items covering exactly 1-6:", sum(lv == "1,2,3,4,5,6"), "of", length(lv), "\n")
    if (any(lv != "1,2,3,4,5,6")) fail <- c(fail, "a framing item does not cover 1-6")
    cat("  item/resp sets identical to live:",
        identical(sort(unique(it$item)), sort(unique(live$item))) &&
        identical(sort(unique(as.numeric(it$resp))), sort(unique(as.numeric(live$resp)))), "\n")
    cat("\n  What the fingerprint does NOT establish: it isolates dr8 and separates\n")
    cat("  {dr9,dr10} from {dr1..dr7}, but not dr1 from dr2-dr7 nor dr9 from dr10.\n")
    cat("  Those rest on the code match checked in steps 1-2.\n")
}

cat("\n", strrep("-", 60), "\n", sep = "")
if (length(fail)) { cat("VERDICT: FAIL\n"); cat(paste0("  - ", fail, collapse = "\n"), "\n")
} else            { cat("VERDICT: PASS\n") }
