# Verification for mturkddm_by (#2228, batch_300).
# See verify_mturkddm_common.R for the source and the shared routes.
#
# THE ITEM CODE IS THE STIMULUS, ARITHMETICALLY. Experiment 2's dot-difference
# task pastes the two dot counts together -- data/mturk_ddm.R does
#     x1$item <- paste(x1$column_7_value, x1$column_8_value)
# where column_7_value is the number of YELLOW dots and column_8_value the number
# of BLUE dots. So "10 15" is ten yellow and fifteen blue, and which colour is
# more numerous -- i.e. the correct answer -- follows from the code itself with
# no external file. That is what Route 2 checks.
TB <- "mturkddm_by"
CHECK_KEY <- function(items) {
    u <- unique(items[, c("item", "correct_response")])
    n <- nrow(u); ok <- 0
    for (i in seq_len(n)) {
        p <- as.integer(strsplit(u$item[i], " ")[[1]])
        want <- if (p[1] > p[2]) "more yellow dots" else "more blue dots"
        if (identical(u$correct_response[i], want)) ok <- ok + 1
        else cat(sprintf("  MISMATCH %s: shipped %s, arithmetic says %s\n",
                         u$item[i], u$correct_response[i], want))
    }
    cat(sprintf("  %d of %d items: correct_response agrees with the dot counts in the code\n", ok, n))
    cat("  (yellow > blue -> 'more yellow dots', else 'more blue dots')\n")
    ok == n
}
NOT_ESTABLISHED <- paste0(
"  The visual stimulus itself. item_text describes the trial from the counts\n",
"  the code carries ('[stimulus: 10 yellow dots and 15 blue dots]') and is this\n",
"  project's rendering, not administered wording -- the participant saw dots,\n",
"  not a sentence. Dot AREA was also manipulated (columns 9-11 of the source)\n",
"  and is not part of the item code, so two trials with the same counts but\n",
"  different area conditions share one item here.\n")
source("itemtables/batch_300/verify_mturkddm_common.R")
