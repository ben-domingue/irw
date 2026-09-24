# verify_trivia_fastrich_2017.R
#
# CLAIM: each bare-integer `item` code carries the trivia question that the
# study's own data file pairs with that QuestionID.
#
# The check does NOT re-count items (validate_items.R did that). It compares the
# shipped `item_text` against the question wording stored ROW-BY-ROW in the live
# IRW table's own `cov_question` covariate, which the processing script
# (data/trivia_fastrich_2017.py) carried over unchanged from the OSF source file
# (osf.io/kjahf, TriviaQuestionData.csv) alongside `item = QuestionID`. If
# item_text for two items were swapped, every pair would disagree.
#
# A server-side GROUP BY is used, not irw_fetch(): 142,490 rows are not exported
# to compare 249 strings.

suppressMessages(library(irw))

TABLE <- "trivia_fastrich_2017"
args  <- commandArgs(trailingOnly = TRUE)
here  <- dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1]))
csv   <- if (length(args)) args[1] else file.path(here, paste0(TABLE, "__items.csv"))

ship <- read.csv(csv, colClasses = "character")
ship <- unique(ship[, c("item", "item_text")])

tbl <- irw:::.fetch_redivis_table(TABLE, source = "core")
ref <- tbl$qualified_reference
q <- sprintf(paste("SELECT CAST(item AS STRING) AS item, cov_question, COUNT(*) AS n",
                   "FROM `%s` GROUP BY item, cov_question"), ref)
live <- as.data.frame(irw:::.irw_query_tibble(q))

cat(sprintf("live item x cov_question pairs: %d over %d item codes\n",
            nrow(live), length(unique(live$item))))

# Five item codes were administered under two wordings (the study corrected
# typos part way through collection); the shipped text is the later wording.
agree <- 0; disagree <- character(0)
for (i in seq_len(nrow(ship))) {
    it <- ship$item[i]; txt <- ship$item_text[i]
    cand <- live$cov_question[live$item == it]
    if (txt %in% cand) agree <- agree + 1 else disagree <- c(disagree, it)
}
cat(sprintf("shipped item_text found in that item's own cov_question values: %d/%d\n",
            agree, nrow(ship)))
if (length(disagree)) cat("disagreeing items:", paste(disagree, collapse = ", "), "\n")

# Cross-check the other direction: no shipped wording may belong to a DIFFERENT
# item code. This is what a swap would break.
cross <- 0
for (i in seq_len(nrow(ship))) {
    other <- live$cov_question[live$item != ship$item[i]]
    if (ship$item_text[i] %in% other) cross <- cross + 1
}
cat(sprintf("shipped wordings that also appear under another item code: %d (expected 0)\n", cross))

# Multi-wording codes, printed so the disclosure is visible in the evidence.
multi <- names(which(table(live$item) > 1))
cat("item codes with two administered wordings:", paste(sort(as.integer(multi)), collapse = ", "), "\n")
for (m in sort(as.integer(multi))) {
    sub <- live[live$item == as.character(m), ]
    for (j in seq_len(nrow(sub)))
        cat(sprintf("   %s  n=%5s  %s%s\n", m, sub$n[j], sub$cov_question[j],
                    if (identical(sub$cov_question[j], ship$item_text[ship$item == as.character(m)])) "   <- shipped" else ""))
}

ok <- (agree == nrow(ship)) && (cross == 0)
cat("\nThis establishes item_text <-> item for all 244 codes from the table's own\n",
    "row-level covariate. It says nothing about option_text <-> resp, which is the\n",
    "0/1 scoring of recall accuracy taken from the deposit's Documentation.txt.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
