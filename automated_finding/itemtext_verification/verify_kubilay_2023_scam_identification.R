# Mapping check for kubilay_2023_scam_identification (10.1016/j.jdeveco.2023.103147,
# data 10.7910/DVN/HUYYQZ).
#
# Usage: Rscript verify_kubilay_2023_scam_identification.R [path/to/response.csv]
#        With no argument it fetches the live IRW table.
#
# WHAT IS CLAIMED. The item text ships no stem (the stimuli are phone
# screenshots, and the source publishes no wording for them). The one
# substantive field it ships is `correct_response`: the correct answer to "is
# this a scam?", taken from the article's appendix Table A1, whose `Intention`
# column marks each of the twelve vignettes Genuine or Fraudulent -- two genuine
# and four fraudulent per block.
#
# WHY IT NEEDS CHECKING. Table A1 prints six rows per block but never names them
# M1..M6, so reading its rows onto the source columns SIA_A_M1..SIA_B_M6 is
# positional, and a wrong alignment would ship a key that is backwards on four
# of twelve items. Set-comparing gates cannot see that.
#
# THE FALSIFIABLE PREDICTION. If Table A1's row order is the column order, then
# in each block the two GENUINE messages are M1 and M2, and respondents should
# call a genuine message a scam far less often than a fraudulent one. The paper
# itself reports the sample is well short of ceiling (only 12% classified all
# six of block 1 correctly), so this is a real test rather than an arithmetic
# identity: it would fail if the genuine pair sat anywhere else in the order.
#
# WHAT THIS DOES NOT ESTABLISH. It pins the Genuine/Fraudulent split and nothing
# finer. Table A1's content descriptions ("Investment opportunity", "Lottery
# win") are NOT shipped, and this route could not separate them from each other
# if they were -- all four fraudulent messages in a block are predicted to look
# alike here. That is why the item text ships the class and stops.

args <- commandArgs(trailingOnly = TRUE)

if (length(args) >= 1) {
    d <- utils::read.csv(args[1], stringsAsFactors = FALSE)
    cat("source: ", args[1], "\n\n", sep = "")
} else {
    suppressMessages(library(irw))
    d <- irw::irw_fetch("kubilay_2023_scam_identification")
    cat("source: live IRW table\n\n")
}

# Appendix Table A1, in the order the table prints them.
INTENTION <- c(sia_a_m1 = "Genuine",    sia_a_m2 = "Genuine",
               sia_a_m3 = "Fraudulent", sia_a_m4 = "Fraudulent",
               sia_a_m5 = "Fraudulent", sia_a_m6 = "Fraudulent",
               sia_b_m1 = "Genuine",    sia_b_m2 = "Genuine",
               sia_b_m3 = "Fraudulent", sia_b_m4 = "Fraudulent",
               sia_b_m5 = "Fraudulent", sia_b_m6 = "Fraudulent")

# resp 1 = "Scam", 2 = "No scam" (deposit codebook).
share_scam <- tapply(d$resp == 1, d$item, mean)
share_scam <- share_scam[names(INTENTION)]

cat(sprintf("%-10s %-11s %12s\n", "item", "Table A1", "share 'Scam'"))
for (i in seq_along(share_scam))
    cat(sprintf("%-10s %-11s %12.3f\n",
                names(share_scam)[i], INTENTION[i], share_scam[i]))

ok <- TRUE
for (blk in c("a", "b")) {
    idx <- grepl(paste0("^sia_", blk, "_"), names(share_scam))
    s <- share_scam[idx]
    g <- s[INTENTION[names(s)] == "Genuine"]
    f <- s[INTENTION[names(s)] == "Fraudulent"]
    cat(sprintf("\nblock %s: genuine max %.3f (%s) vs fraudulent min %.3f (%s)\n",
                toupper(blk), max(g), paste(names(g), collapse = ", "),
                min(f), names(f)[which.min(f)]))
    # The two lowest shares in the block must be exactly the two genuine ones.
    lowest_two <- names(sort(s))[1:2]
    if (!setequal(lowest_two, names(g))) {
        cat("  MISALIGNED: the two lowest shares are ",
            paste(lowest_two, collapse = ", "), "\n", sep = "")
        ok <- FALSE
    } else {
        cat("  the two lowest shares in the block are exactly the two genuine items\n")
    }
    if (max(g) >= min(f)) {
        cat("  MISALIGNED: genuine and fraudulent shares overlap\n")
        ok <- FALSE
    }
}

cat("\nNote: this separates the Genuine/Fraudulent classes, which is the whole of\n",
    "what correct_response claims. It cannot separate the four fraudulent\n",
    "messages within a block from one another, and no field shipped here\n",
    "distinguishes them.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
