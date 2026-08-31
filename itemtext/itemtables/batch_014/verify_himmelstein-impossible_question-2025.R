## verify_himmelstein-impossible_question-2025.R
##
## Route: exact_reproduction. The mapping is not inferred here, so this script does
## not argue for it -- it rebuilds it. The study's own response file carries
## question_text on every row keyed to id, the IRW `item` IS that id
## (data/data_impossible_question.py passes item_col='id', resp_col='correct'), and
## aggregating the source's `correct` by `id` must reproduce the live table.
##
## Also re-checks the two things that were NOT obvious and had to be settled against
## the data: which option each item keys to, and how opting out is scored.
##
## Run from itemtext/:
##   Rscript itemtables/batch_014/verify_himmelstein-impossible_question-2025.R

suppressMessages(library(irw))
TBL <- "himmelstein-impossible_question-2025"
CSV <- "itemtables/batch_014/himmelstein-impossible_question-2025__items.csv"
SRC <- ".cache/himmelstein-impossible_question-2025/data_impossible_question.csv"
URL <- paste0("https://raw.githubusercontent.com/forecastingresearch/fpt/main/",
              "data_cognitive_tasks/task_datasets/data_impossible_question.csv")
fail <- character(0)

if (!file.exists(SRC)) { dir.create(dirname(SRC), recursive = TRUE, showWarnings = FALSE)
                         download.file(URL, SRC, quiet = TRUE) }
src <- read.csv(SRC, stringsAsFactors = FALSE)
it  <- read.csv(CSV, stringsAsFactors = FALSE)

## ---- 1. id -> question_text is one-to-one, and matches what we shipped --------
cat("=== 1. shipped item_text vs the source's question_text, per id ===\n")
u <- unique(src[, c("id", "question_text")])
cat("distinct ids:", length(unique(src$id)), "| distinct (id,text) pairs:", nrow(u),
    "| any id with >1 text:", any(table(u$id) > 1), "\n")
if (any(table(u$id) > 1)) fail <- c(fail, "id -> question_text is not one-to-one")
ship <- unique(it[, c("item", "item_text")])
m <- merge(u, ship, by.x = "id", by.y = "item", all = TRUE)
bad <- m[is.na(m$question_text) | is.na(m$item_text) | m$question_text != m$item_text, ]
cat("items compared:", nrow(m), "| mismatches:", nrow(bad), "\n")
if (nrow(bad)) { fail <- c(fail, "item_text mismatch"); print(head(bad, 5)) }

## ---- 2. correct_response vs the file's own key -------------------------------
cat("\n=== 2. correct_response vs correct_answer (1=answer_1, 2=answer_2, 3=Opt-out) ===\n")
k <- unique(src[, c("id", "answer_1", "answer_2", "correct_answer")])
k$expect <- ifelse(k$correct_answer == 1, k$answer_1,
            ifelse(k$correct_answer == 2, k$answer_2, "Opt-out"))
sk <- unique(it[, c("item", "correct_response")])
mk <- merge(k[, c("id", "correct_answer", "expect")], sk, by.x = "id", by.y = "item")
badk <- mk[mk$expect != mk$correct_response, ]
cat("mismatches:", nrow(badk), "\n")
print(table(correct_answer = mk$correct_answer,
            shipped = ifelse(mk$correct_response == "Opt-out", "Opt-out", "an alternative")))
if (nrow(badk)) fail <- c(fail, "correct_response mismatch")

## ---- 3. exact reproduction of the live table --------------------------------
cat("\n=== 3. does the source reproduce the live table, per item? ===\n")
live <- tryCatch(irw_fetch(TBL), error = function(e) NULL)
if (is.null(live) || !nrow(live)) {
    cat("live data unavailable -- reproduction unchecked\n")
    fail <- c(fail, "live data unavailable")
} else {
    live$item <- as.character(live$item)
    s <- do.call(data.frame, aggregate(correct ~ id, src[src$id %in% unique(live$item), ],
                                       function(x) c(n = length(x), m = mean(x))))
    names(s) <- c("item", "src_n", "src_mean")
    l <- do.call(data.frame, aggregate(resp ~ item, live, function(x) c(n = length(x), m = mean(x))))
    names(l) <- c("item", "live_n", "live_mean")
    mm <- merge(s, l, by = "item")
    okn <- all(mm$src_n == mm$live_n); okm <- all(abs(mm$src_mean - mm$live_mean) < 1e-12)
    cat("items:", nrow(mm), "| per-item n identical:", okn,
        "| per-item mean identical to 1e-12:", okm, "\n")
    if (!okn || !okm) fail <- c(fail, "source does not reproduce the live table")
    cat("item/resp sets identical:",
        identical(sort(unique(it$item)), sort(unique(live$item))) &&
        identical(sort(unique(as.numeric(it$resp))), sort(unique(as.numeric(live$resp)))), "\n")
}

## ---- 4. the opt-out scoring rule, which the instructions get wrong -----------
cat("\n=== 4. how opting out is actually scored (instructions say it is not scored) ===\n")
src$kind <- ifelse(src$question_type == "IQ", "IQ", "GK")
print(table(kind = src$kind, choice = src$response_choice, correct = src$correct))
gk3 <- src[src$kind == "GK" & src$response_choice == 3 & !is.na(src$correct), "correct"]
iq3 <- src[src$kind == "IQ" & src$response_choice == 3 & !is.na(src$correct), "correct"]
cat(sprintf("GK + opt-out: %d rows, all scored incorrect: %s\n", length(gk3), all(gk3 == 0)))
cat(sprintf("IQ + opt-out: %d rows, all scored correct  : %s\n", length(iq3), all(iq3 == 1)))
if (!all(gk3 == 0) || !all(iq3 == 1)) fail <- c(fail, "opt-out scoring rule does not hold")

cat("\n", strrep("-", 60), "\n", sep = "")
if (length(fail)) { cat("VERDICT: FAIL\n"); cat(paste0("  - ", fail, collapse = "\n"), "\n")
} else            { cat("VERDICT: PASS\n") }
