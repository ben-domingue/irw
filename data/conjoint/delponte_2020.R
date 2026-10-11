##Sovereign-debt moral-dilemma vignette experiment (MTurk, Study 1) from
##Del Ponte, A., & DeScioli, P. (2020). Pay your debts: Moral dilemmas of international debt.
##Political Behavior. https://doi.org/10.1007/s11109-020-09675-6
##Replication data: Harvard Dataverse doi:10.7910/DVN/XJ2BDK, CC0 1.0. File read: "Study1_MTurk.tab" (Dataverse
##original-format Stata download, saved here as s1.dta) and the authors' "Study1_Replication.do" (read as text, not run).
##Not built: Study 2 (Study2_SSI.tab, 1,046 respondents): a single manipulated factor (the loss ratio 2x vs 20x),
##so not a conjoint; the "Comments" tab files (free text) are not used.
##Usage: Rscript delponte_2020.R <dir holding s1.dta> <output dir>
##
##648 MTurk workers, one vignette each (Avalon owes a loan to Freedonia; the question is what Avalon's government
##should do), 4 x 2 between-subject (do-file header: Condition 1-4 = 6,000 / 10,000 / 25,000 / 100,000 jobs, "Full
##Default"; 5-8 the same with "Partial Default"; verified against the variables Loss and partial):
##  attr_jobs_lost: the variable Loss, "6,000 lost jobs" / "10,000 lost jobs" / "25,000 lost jobs" / "100,000 lost jobs";
##  attr_default_type: "Full default" / "Partial default" (the do-file's condition labels). The vignette paragraphs are not in
##    the deposit, so the level text is the authors' condition labels, not the displayed sentences.
##Presentation text; task = 1, profile = 1; id = row number (the MTurk ResponseId is dropped).
##Outcomes (do-file comments; single-profile judgements):
##  choice = whatDo, binary decision of the respondent for the government (opt_out = yes: single-profile accept/reject).
##    CODING INFERRED: 1 = repay, 0 = default. The Study 1 code does not say; the Study 2 code header says "Should Avalon default (0)
##    or Repay (1)?" for the same variable name, but its Table 4 comment says the opposite; the data decrease with jobs lost
##    (72% at 6,000 jobs, full default, down to 26% at 100,000 partial), like StopRepay, which supports 1 = repay.
##  rating_stop_repay_wrong (StopRepay, 0/1 "Would it be morally wrong to stop repaying? No (0) or Yes (1)"),
##  rating_stop_wrong (StopWrong_1, "How morally wrong to stop repaying?" 0-10), rating_stop_punish (StopPunish_1,
##  "How strong of a punishment for stop repaying?" 0-10), rating_cuts_wrong_binary (Cuts, "Would it be morally wrong to make
##  cuts? No (0) or Yes (1)"), rating_cuts_wrong (CutWrong_1, 0-10), rating_cuts_punish (CutPunish_1, 0-10).
##Covariates: cov_gender (the authors' `Female` 0/1; gender 1 = male, 0 = female in the data), cov_age (years).
##Dropped: ResponseId, free text (Q55, Q52, FinalComments, race, religion, PID_6_TEXT), income, education (0-1 rescale with
##unknown levels), party identification and ideology batteries, authors' derived variables (ratio*, full, partial, ...).
##Count check: 97+71+81+80+81+78+80+80 = 648 respondents = the file; the paper's N not looked up (the triage note says 648).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- as.data.table(read_dta(file.path(raw, "s1.dta")))
stopifnot(nrow(r) == 648, all(r$Condition %in% 1:8), all(r$whatDo %in% 0:1), all(r$StopRepay %in% 0:1), all(r$Cuts %in% 0:1))
stopifnot(all(r$partial == as.integer(r$Condition >= 5)), all(r$Loss == c("6,000 lost jobs", "10,000 lost jobs", "25,000 lost jobs", "100,000 lost jobs")[(r$Condition - 1) %% 4 + 1]))
stopifnot(all(r$StopWrong_1 >= 0 & r$StopWrong_1 <= 10), all(r$CutWrong_1 >= 0 & r$CutWrong_1 <= 10), all(r$StopPunish_1 <= 10), all(r$CutPunish_1 <= 10))
d <- data.table(id = seq_len(nrow(r)), task = 1L, profile = 1L, choice = as.integer(r$whatDo),
                rating_stop_repay_wrong = as.integer(r$StopRepay), rating_stop_wrong = r$StopWrong_1, rating_stop_punish = r$StopPunish_1,
                rating_cuts_wrong_binary = as.integer(r$Cuts), rating_cuts_wrong = r$CutWrong_1, rating_cuts_punish = r$CutPunish_1,
                attr_jobs_lost = r$Loss, attr_default_type = c("Full default", "Partial default")[r$partial + 1L],
                cov_gender = c("male", "female")[r$Female + 1L], cov_age = ifelse(r$age >= 18 & r$age <= 100, as.integer(r$age), NA_integer_))
stopifnot(r[, all(gender == 1 - Female)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "delponte_2020_debt_dilemmas.csv"))
