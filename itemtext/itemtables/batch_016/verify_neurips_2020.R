# verify_neurips_2020.R -- Step 5b evidence script for a BLOCKED table.
#
# No {table}__items.csv was written for neurips_2020, so there is no
# item_text<->item mapping to verify. What this script makes re-runnable is the
# REASON the table is blocked on the mapping axis, which is a checkable claim
# about the item codes themselves.
#
# THE CLAIM
#   data/neurlps_2020.R rbinds the Eedi task-1/2 files (train_task_1_2,
#   test_public/private_answers_task_1, test_public/private_answers_task_2) with
#   the task-3/4 files (train_task_3_4, test_public_task_4_more_splits,
#   test_private_task_4) and sets item = question_id + 1. The challenge guide
#   (arXiv:2007.12061 sec. 2, p.8) states:
#
#     "all such IDs for tasks 1 and 2 are anonymized separately from those for
#      tasks 3 and 4: IMPORTANT: Question, User and Answer IDs should not be
#      linked between the data for these pairs of tasks!"
#
#   Task 1/2 has 27613 questions, task 3/4 has 948 -- DISJOINT question sets in
#   two independent ID spaces. Merging them on the raw id means item codes
#   1..948 each carry answers to TWO different questions. Prediction: the live
#   table has exactly 27613 items (not 27613+948=28561), the codes run
#   contiguously 1..27613, and items 1..948 carry several times the responses of
#   the rest.
#
# NOTE ON QUOTA: this script deliberately does NOT call irw_fetch(). The table is
# 24,076,951 rows; exporting it would consume a large fraction of the account's
# 200GB/30-day Redivis export cap. irw_table_sets() answers all of the above with
# server-side aggregates.

suppressMessages(library(irw))

TABLE   <- "neurips_2020"
N_T12   <- 27613   # questions in the task 1/2 dataset (guide p.9)
N_T34   <- 948     # questions in the task 3/4 dataset (guide p.9)

s  <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
it <- suppressWarnings(as.integer(s$items))

cat("distinct items in live table : ", length(it), "\n", sep = "")
cat("if the two ID spaces were kept apart, expected: ", N_T12, " + ", N_T34,
    " = ", N_T12 + N_T34, "\n", sep = "")
cat("item codes are contiguous 1..", max(it), ": ", identical(sort(it), 1:max(it)),
    "\n\n", sep = "")

pi        <- as.data.frame(s$per_item)
pi$itemn  <- as.integer(as.character(pi$item))
colliding <- pi[pi$itemn <= N_T34, ]
clean     <- pi[pi$itemn >  N_T34, ]

cat(sprintf("%-22s %8s %12s %12s %14s\n", "code range", "n items", "median n", "mean n", "total resp"))
cat(sprintf("%-22s %8d %12.0f %12.0f %14s\n", paste0("1-", N_T34),
            nrow(colliding), median(colliding$n), mean(colliding$n),
            format(sum(colliding$n), big.mark = ",")))
cat(sprintf("%-22s %8d %12.0f %12.0f %14s\n", paste0(N_T34 + 1, "-", max(pi$itemn)),
            nrow(clean), median(clean$n), mean(clean$n),
            format(sum(clean$n), big.mark = ",")))
ratio <- median(colliding$n) / median(clean$n)
cat(sprintf("\nmedian-n inflation on codes 1-%d: %.2fx\n", N_T34, ratio))
cat(sprintf("excess responses on codes 1-%d over the rest of the table's median: %s\n",
            N_T34, format(round(sum(colliding$n) - nrow(colliding) * median(clean$n)),
                          big.mark = ",")))
cat("(train_task_3_4.csv alone holds 1,382,727 answers over those 948 questions,\n",
    " before the task-4 public/private test splits the script also rbinds.)\n", sep = "")

# Second, independent defect on the resp axis.
cat("\nresp set: ", paste(sort(s$resp), collapse = ","), "\n", sep = "")
cat("IsCorrect is binary (guide p.8). data/neurlps_2020.R renames AnswerValue\n",
    "(a 1-4 option choice) to IsCorrect for test_public/private_answers_task_2\n",
    "before the rbind, so resp mixes 0/1 correctness with 1-4 option identity in\n",
    "one column. Levels per item:\n", sep = "")
print(table(`resp levels` = pi$n_resp_levels))

collision <- length(it) == N_T12 && identical(sort(it), 1:N_T12) && ratio > 3

cat("\nWhat this does NOT establish: nothing here checks any item_text, because\n",
    "none was shipped -- Eedi publishes no question wording as text at all\n",
    "(guide sec. 2.2: \"The question wording is contained in the images but will\n",
    "not be made available as text\"). This only reproduces the code-collision and\n",
    "resp-conflation findings that make the table unextractable and that a data\n",
    "fix would have to address.\n", sep = "")

cat(if (collision) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
