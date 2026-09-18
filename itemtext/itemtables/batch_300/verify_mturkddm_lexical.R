# Verification for mturkddm_lexical (#2228, batch_300).
# See verify_mturkddm_common.R for the source and the shared routes.
#
# THE ITEM CODE IS THE STIMULUS STRING. data/mturk_ddm.R sets
#     item <- x$test_word_string
# which its header documents as "the character string presented at test". So
# item_text is a transcription of the code, and the code cannot drift from it.
#
# THE KEY COMES FROM THE DEPOSIT, NOT FROM INFERENCE. column_7_value is 1 for
# "valid word" and 2 for "nonword", and the script scores resp as
# response_key_ID == column_7_value. Route 2 re-reads Experiment1.data and
# checks the shipped correct_response against that column for all 4,588 strings.
TB <- "mturkddm_lexical"
SRC <- ".cache/batch_300/Experiment1.data"
CHECK_KEY <- function(items) {
    if (!file.exists(SRC)) { cat("  missing cached deposit file:", SRC, "\n"); return(FALSE) }
    x <- read.csv(SRC, stringsAsFactors = FALSE)
    x <- x[x$column_7_value != 9 & x$task_number == 1, ]   # drop practice, lexical task only
    m <- unique(x[, c("test_word_string", "column_7_value")])
    amb <- sum(duplicated(m$test_word_string))
    cat(sprintf("  deposit strings %d, with a conflicting word/nonword flag: %d\n",
                length(unique(m$test_word_string)), amb))
    key <- setNames(ifelse(m$column_7_value == 1, "valid word", "nonword"), m$test_word_string)
    u <- unique(items[, c("item", "correct_response")])
    ok <- sum(u$correct_response == key[u$item], na.rm = TRUE)
    cat(sprintf("  %d of %d items: correct_response agrees with the deposit's own flag\n", ok, nrow(u)))
    cat(sprintf("  split: %d valid words / %d nonwords\n",
                sum(key == "valid word"), sum(key == "nonword")))
    amb == 0 && ok == nrow(u)
}
NOT_ESTABLISHED <- paste0(
"  Nothing about the wording, because there is nothing to transcribe -- the\n",
"  item IS the string. section_prompt carries the frequency pool the deposit\n",
"  records in column_8_value (high, low, very low); the script's header notes\n",
"  that for nonwords this is 'the word pool from which each was derived', so it\n",
"  describes provenance of the string rather than a property of a real word.\n")
source("itemtables/batch_300/verify_mturkddm_common.R")
