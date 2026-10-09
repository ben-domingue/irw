##Journal-choice discrete choice experiment (health and medical researchers) from
##Barnett, A. (2024). agbarnett/publication_preferences: R code and data for publication preferences
##discrete choice experiment (v1.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.12814360
##(CC BY 4.0). No article is linked from the record; protocol and survey on OSF (osf.io/p9guj, not read).
##Files read (from agbarnett/publication_preferences-v1.0.zip): rdata/analysis_ready.xlsx (sheets
##"data" and the two "dictionary" sheets), readme.md, scenario.txt; the authors' scripts were read as
##text (2_make_choices_for_qualtrics.R, 5_read_qualtrics_v2.R, 6_summary_combined.Rmd,
##6_mlogit_model.R, 7_prepare_journal_data.R). The design spreadsheets those scripts read (data/*.xlsx)
##are NOT in the deposit: the attribute levels were TRANSCRIBED by hand from the Qualtrics choice-set
##images the authors made and ship (figures/qualtrics/block{1,2,3}/choice_set_{1-8}.png = first
##design, figures/qualtrics/second/block{1,2,3}/... = second design, figures/qualtrics/block99 =
##dominant set). The transcription is the `sets` table below (one code letter per attribute).
##Usage: Rscript barnett_2024.R <dir holding analysis_ready.xlsx> <output dir>
##
##Online survey (Qualtrics, 2024) of health and medical researchers (authors found via PubMed).
##Scenario text (scenario.txt): "Imagine you have written a paper and are now trying to get it
##published in a journal. ..." Each choice set shows "Journal A" and "Journal B" (profiles 1/2) in a
##table with 6 attribute rows in fixed order, and asks "Select your preferred journal"; no opt-out.
##Attributes (row text -> attr_ column; levels as displayed):
##  attr_impact_factor   "In your field the journal's impact factor is": the highest / moderate / not available
##  attr_formatting      "To fit the journal's style requirements your paper will need": major formatting / minor formatting
##  attr_decision_speed  "Colleagues say that the journal's decisions are usually": slow / fast
##  attr_reviews         "Colleagues say that the journal's reviews will often": help you improve the paper / be contradictory and unhelpful
##  attr_editor_request  "After peer review the editor has indicated the paper will be accepted if you":
##                       cut a table and an analysis to reduce the word count to 3,000 / make changes in format and wording
##  attr_promotion       "Considering your next application for promotion or a fellowship, this paper will be": useful / not useful
##In the second design both journals sometimes share a level; the image then shows one merged cell,
##stored here as the same text on both profiles.
##Design: fixed blocked Ngene efficient designs, 3 blocks x 8 choice sets, two designs (trial_design
##1 = first sample, March 2024, 96 respondents; 2 = second sample, April 2024, 520), respondents
##allocated to a block and to one of two scenarios (trial_scenario: the authors' plot labels "First
##submission" / "Desk rejected"; the second scenario's text is not in the deposit).
##Tasks, in questionnaire order (task order inferred from the Qualtrics question numbers):
##  task 1    = q3, the dominant set (Journal A better on every attribute; trial_set = "dominant")
##  tasks 2-9 = q5, q7, ..., q17, q20 = choice sets 1-8 of the respondent's block (7_prepare_journal_data.R)
##  task 10   = q22, retest of set 1 (q5) or, for design 1 block 3, of set 2 (q7) (6_summary_combined.Rmd);
##              trial_repeat_of = 2 or 3. Shown with the same Journal A/B order, inferred: 80% of
##              retest answers repeat the original A/B label.
##choice = 1 for the journal picked. Unanswered sets are omitted (rows with no outcome).
##Checks: 611 of 614 answering picked Journal A in the dominant set (the expected answer).
##Covariates: cov_gender (q26: Female -> female, Male -> male, "Non-binary / third gender" and
##"I use a different term" -> other, "Prefer not to say" -> NA), cov_research_area (q25 option
##text; free-text "other" not read), cov_years_research (q27), cov_n_papers (q28), cov_country
##(q29), cov_dce_difficulty (q24 option text), cov_duration_sec (duration_mins x 60, rounded),
##cov_progress (Qualtrics % progress). Dropped: q30/q30a/q31 (different questions in the two
##samples), comments, start date. The source id ("block.scenario.n") is re-keyed to integers.
##Count check: 616 respondents in the file (96 + 520); the readme's design figure says "Final design
##520 respondents" and "External pilot testing 96 respondents" (99_study_design.R), so design 1 may
##be the pilot (kept, flagged by trial_design). 11,128 rows.
##Spot check (LPM on tasks 2-9, SE clustered by id): impact factor the highest +0.51 (SE 0.02) and
##moderate +0.34 vs not available; slow decisions -0.17; helpful reviews +0.20; useful for promotion
##+0.17. Large, sensibly signed effects on every attribute support the transcription and the
##question-to-set mapping (a misaligned design would wash them out). No article to compare with.
library(readxl); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
sets <- fread(text = "design block set A B
0 99 1 HIFPWu NJSCXn
1 1 1 MJSPXu HIFCWn
1 1 2 HJSCXn MIFPWu
1 1 3 NIFPWu HJSCXn
1 1 4 NIFPWn MJSCXu
1 1 5 NIFPXu MJSCWn
1 1 6 HIFPXu NJSCWn
1 1 7 HISCWu MJFPXn
1 1 8 HJSPWu NIFCXn
1 2 1 MJFCXu HISPWn
1 2 2 NISCWn HJFPXu
1 2 3 MIFPXn HJSCWu
1 2 4 HIFCWn NJSPXu
1 2 5 MIFCXu NJSPWn
1 2 6 NISCXn HJFPWu
1 2 7 HJFCXn MISPWu
1 2 8 MJFCWu NISPXn
1 3 1 HISPXu MJFCWn
1 3 2 MISCWu HJFPXn
1 3 3 NJFPWu MISCXn
1 3 4 NJFCXu MISPWn
1 3 5 NJSPXn HIFCWu
1 3 6 MISPXn NJFCWu
1 3 7 MJFPWn HISCXu
1 3 8 HJSPWn NIFCXu
2 1 1 MISCXu HJFPWn
2 1 2 MIFCWu HJSPXn
2 1 3 NJSPWu MIFCXn
2 1 4 NISPXn MJFCWu
2 1 5 HJFCWn NISPXu
2 1 6 MJFPXu HISCWu
2 1 7 MJSCXu NIFPWu
2 1 8 MIFPXn NJSCWu
2 2 1 NJFCXu HISPWn
2 2 2 MIFPWn HJSCXn
2 2 3 HJFPWn NISCXu
2 2 4 HIFCWu MJSPXu
2 2 5 NISCWu HJFPXn
2 2 6 NJFPWu HISCXn
2 2 7 NISPWn MJFCXu
2 2 8 HJSPXn NIFCWn
2 3 1 NJFCXu MISPWn
2 3 2 HIFPXn MJSCWu
2 3 3 MISPXu NJFCWu
2 3 4 HISCWn NJFPXu
2 3 5 MJSPWn HIFCXn
2 3 6 MJSCWu NIFPXn
2 3 7 HIFCXn NJSPWu
2 3 8 HJSCXu MIFPWn", colClasses = list(character = c("A", "B")))
dec <- list(impact_factor = c(H = "the highest", M = "moderate", N = "not available"),
            formatting = c(J = "major formatting", I = "minor formatting"),
            decision_speed = c(S = "slow", F = "fast"),
            reviews = c(P = "help you improve the paper", C = "be contradictory and unhelpful"),
            editor_request = c(X = "cut a table and an analysis to reduce the word count to 3,000",
                               W = "make changes in format and wording"),
            promotion = c(u = "useful", n = "not useful"))
stopifnot(all(nchar(sets$A) == 6), all(nchar(sets$B) == 6))
prof <- rbind(sets[, .(design, block, set, profile = 1L, code = A)], sets[, .(design, block, set, profile = 2L, code = B)])
for (j in seq_along(dec)) {
  ch <- substr(prof$code, j, j); stopifnot(all(ch %in% names(dec[[j]])))
  prof[, paste0("attr_", names(dec)[j]) := unname(dec[[j]][ch])]
}
prof[, code := NULL]
x <- as.data.table(read_excel(file.path(raw, "analysis_ready.xlsx"), sheet = "data"))
stopifnot(!anyDuplicated(x[, .(sample, id)]), all(x$sample %in% 1:2), all(x$block %in% 1:3))
x[, rid := .I]
qs <- c("q3", "q5", "q7", "q9", "q11", "q13", "q15", "q17", "q20", "q22")
long <- melt(x[, c("rid", "sample", "block", "scenario", qs), with = FALSE], id.vars = c("rid", "sample", "block", "scenario"),
             measure.vars = qs, variable.name = "q", value.name = "ans", variable.factor = FALSE)
long <- long[!is.na(ans)]
stopifnot(all(long$ans %in% c("Journal A", "Journal B")))
long[, task := match(q, qs)]
long[, set := fifelse(task == 1L, 1L, fifelse(task <= 9L, task - 1L, fifelse(sample == 1 & block == 3, 2L, 1L)))]
long[, `:=`(design = fifelse(task == 1L, 0L, as.integer(sample)), dblock = fifelse(task == 1L, 99L, as.integer(block)))]
long[, trial_repeat_of := fifelse(task == 10L, set + 1L, NA_integer_)]
d <- merge(long, prof, by.x = c("design", "dblock", "set"), by.y = c("design", "block", "set"), allow.cartesian = TRUE)
stopifnot(nrow(d) == 2 * nrow(long))
d[, choice := as.integer((ans == "Journal A" & profile == 1L) | (ans == "Journal B" & profile == 2L))]
d[, trial_set := fifelse(task == 1L, "dominant", paste0("block ", block, " set ", set))]
d[, trial_design := as.integer(sample)]
d[, trial_scenario := c("First submission", "Desk rejected")[scenario]]
cat("dominant set picks:", d[task == 1 & profile == 1, sum(choice)], "of", d[task == 1 & profile == 1, .N], "\n")
g <- x$q26
cv <- x[, .(rid,
            cov_gender = fifelse(g == "Female", "female", fifelse(g == "Male", "male",
                         fifelse(g %in% c("Non-binary / third gender", "I use a different term (please specify)"), "other", NA_character_))),
            cov_research_area = q25, cov_years_research = suppressWarnings(as.numeric(q27)),
            cov_n_papers = suppressWarnings(as.numeric(q28)), cov_country = q29, cov_dce_difficulty = q24,
            cov_duration_sec = as.integer(round(as.numeric(duration_mins) * 60)), cov_progress = as.integer(progress))]
d <- merge(d[, .(rid, task, profile, choice, attr_impact_factor, attr_formatting, attr_decision_speed, attr_reviews,
                 attr_editor_request, attr_promotion, trial_set, trial_design, trial_scenario, trial_repeat_of)], cv, by = "rid")
stopifnot(d[, sum(choice), .(rid, task)][, all(V1 == 1)])
setnames(d, "rid", "id")
setorder(d, id, task, profile)
cat("respondents:", uniqueN(d$id), " rows:", nrow(d), "\n")
fwrite(d, file.path(out, "barnett_2024_journal_choice.csv"))
