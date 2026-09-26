# verify_onah_2021_covid_knowledge.R -- re-runnable Step 5b check (batch_453).
#
# ITEM axis: mapping_basis=data_labels. The IRW item code IS the .sav column name
# (COVID_1..COVID_25, data/onah_2021_covid_literacy.py melts the columns without
# renaming), and each column's SPSS variable label reproduces the questionnaire
# stem (25/25; differences are trailing "?", "......", "." and one double space).
# Nothing to infer there, so nothing here re-checks it.
#
# RESP axis (route 9): this is the axis that carried a decision. The .sav stores
# 1/2 with value labels 'correct'/'incorrect', and the polarity is NOT constant:
# COVID_11, 12, 15, 21, 22, 23 label 2='correct' (COVID_11 spells it 'icorrect'
# for 1), the other 19 label 1='correct'. The shipped rows say resp 1='correct',
# resp 0='incorrect'. Prediction: for every item, the live count of resp==1
# equals the .sav count of whichever raw code that item's value labels call
# 'correct'. A blanket 1->1 recode would miss on all six flipped items.
#
# SAV_CORRECT below was counted from SPSS-DATA-COVID-19.sav (Mendeley Data
# 10.17632/cf3s3v8wb3, file 61f7a311-78ae-468f-9b84-a965b23a901b), N=7,890,
# reading each item's own value labels.

suppressMessages(library(irw))

TABLE <- "onah_2021_covid_knowledge"
SAV_N <- 7890
SAV_CORRECT <- c(4528, 3331, 4101, 4456, 4270, 3555, 3887, 4242, 4425, 3578,
                 2668, 4066, 4029, 5869, 5979, 5292, 2389, 1951, 5205, 3694,
                 3755, 4832, 5295, 5201, 3175)
names(SAV_CORRECT) <- paste0("COVID_", 1:25)
FLIPPED <- paste0("COVID_", c(11, 12, 15, 21, 22, 23))

d <- irw::irw_fetch(TABLE)
live1 <- tapply(d$resp == 1, d$item, sum)[names(SAV_CORRECT)]
liven <- tapply(!is.na(d$resp), d$item, sum)[names(SAV_CORRECT)]

cat(sprintf("%-9s %8s %10s %10s %6s %s\n", "item", "live_n", "sav_correct",
            "live_resp1", "diff", ""))
for (it in names(SAV_CORRECT))
    cat(sprintf("%-9s %8d %10d %10d %6d %s\n", it, liven[it], SAV_CORRECT[it],
                live1[it], live1[it] - SAV_CORRECT[it],
                if (it %in% FLIPPED) "(2=correct in .sav)" else ""))

# Counter-check: under a naive 1->1 recode the flipped items would read
# SAV_N - SAV_CORRECT. Show that this is NOT what the live data holds.
naive_miss <- sum(live1[FLIPPED] == (SAV_N - SAV_CORRECT[FLIPPED]))
cat(sprintf("\nexact matches: %d/25; flipped items matching the naive reading: %d/6\n",
            sum(live1 == SAV_CORRECT), naive_miss))
cat("Note: this pins resp 1='correct' / 0='incorrect' per item. It does not test the\n",
    "item_text <-> item tie (that is the .sav's own variable labels), and there is no\n",
    "published answer key, so correct_response is left blank and not checked.\n", sep = "")

ok <- all(liven == SAV_N) && all(live1 == SAV_CORRECT) && naive_miss == 0
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
