# verify_carver_2017_puggs_pilot1_genom_know.R
#
# WHAT IS AT STAKE. The PUGGS supplements publish the first pilot's Section 3
# ("Principles of genomics") TWICE, with the SAME 18 statements under TWO
# DIFFERENT numberings:
#   * SI 3 (s003, "Initial PUGGS questionnaire, used in the first pilot study")
#   * SI 5 (s004, "Code Book used in the first pilot study")
# e.g. SI 3 numbers "Only a small proportion of the human genome ..." as 15,
# the Code Book numbers it as 20. The IRW item codes are the raw file's own
# column names Q14..Q31, so choosing the wrong document permutes item_text
# across all 18 items while every set-based gate still passes.
#
# THE CLAIM VERIFIED HERE: the data follow the CODE BOOK numbering.
#
# THE TEST. "Don't know" (code 5) was an offered option and is dropped by the
# IRW processing script, so per-item n = 207 - (don't know) - missing. Exactly
# five of the 18 statements use the jargon word "epigenetic" in the stem; those
# are the ones an undergraduate sample cannot answer. Under the Code Book
# numbering those five are items 19, 21, 23, 24, 27. The falsifiable prediction
# is that Q19/Q21/Q23/Q24/Q27 are the five LOWEST-n items of the 18 -- a 1-in-8568
# coincidence if the numbering were wrong. Under the SI 3 numbering the five
# "epigenetic" items would be 26, 27, 28, 30, 31 instead, which is what would
# show up if the mapping had been taken from the questionnaire.
#
# Live n comes from irw::irw_table_sets(per_item = TRUE): a server-side GROUP BY,
# NOT irw_fetch(), which would export the whole table (standing quota rule).

suppressMessages(library(irw))
TABLE <- "carver_2017_puggs_pilot1_genom_know"

# Items whose Code Book (SI 5) stem contains the word "epigenetic".
CODEBOOK_EPI <- c("Q19", "Q21", "Q23", "Q24", "Q27")
# The same five statements under the SI 3 questionnaire numbering -- the rival.
SI3_EPI      <- c("Q26", "Q27", "Q28", "Q30", "Q31")

s  <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
n  <- setNames(pi$n, pi$item)
n  <- n[paste0("Q", 14:31)]

cat("per-item n (rows with resp in 1..4; 'don't know' = 5 was dropped upstream)\n")
ord <- sort(n)
for (i in seq_along(ord))
    cat(sprintf("  %2d. %-5s n=%3d%s\n", i, names(ord)[i], ord[i],
                if (names(ord)[i] %in% CODEBOOK_EPI) "   <- Code Book 'epigenetic' item" else ""))

bottom5 <- names(ord)[1:5]
cat("\nfive lowest-n items      :", paste(sort(bottom5), collapse = " "), "\n")
cat("Code Book epigenetic set :", paste(sort(CODEBOOK_EPI), collapse = " "), "\n")
cat("SI 3    epigenetic set   :", paste(sort(SI3_EPI), collapse = " "), "\n")
cat(sprintf("SI 3 set's n values      : %s\n",
            paste(sprintf("%s=%d", SI3_EPI, n[SI3_EPI]), collapse = " ")))

hit_cb  <- setequal(bottom5, CODEBOOK_EPI)
hit_si3 <- setequal(bottom5, SI3_EPI)
cat(sprintf("\nbottom-5 == Code Book set: %s   bottom-5 == SI 3 set: %s\n", hit_cb, hit_si3))
cat("Chance probability of the Code Book set landing as the bottom 5: 1/choose(18,5) = 1/8568\n")

cat("\nNote: this route fixes WHICH DOCUMENT'S NUMBERING the column codes follow,\n",
    "which is the only inference in the mapping -- the IRW item code is the source\n",
    "spreadsheet's own column name, so there is no positional step to get wrong. It\n",
    "separates every item once the numbering is fixed. It does NOT check the four\n",
    "option labels against the data (they are stated outright by both documents and\n",
    "by the Code Book's primary-code column), and it does not adjudicate the minor\n",
    "wording differences between SI 3 and the Code Book, which provenance records.\n",
    sep = "")

cat(if (hit_cb && !hit_si3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
