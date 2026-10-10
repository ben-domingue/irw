##GP paediatric emergency-department referral vignette DCE (Ireland) from
##McDonnell, T., Nicholson, E., & McAuliffe, E. (2022). The role of contextual factors in
##decision-making by General Practitioners on paediatric referral to the Emergency Department: A
##Discrete Choice Experiment [Data set]. Zenodo. https://doi.org/10.5281/zenodo.6657412
##(no article DOI in the record; the record description gives n = 142 GPs and the 5 attributes).
##Licence: CC BY 4.0 (Zenodo record licence). Files read: "Survey Data File.xlsx" (Qualtrics export,
##one row per respondent, question ids in row 1), "Survey Questions.docx" (full instrument with every
##scenario text), "Ngene DCE design.ngd" (read as text). The 214 MB "Stata Data File Formatted for
##DCE.dta" was not downloaded (not needed: the scenario texts give every level).
##Usage: Rscript mcdonnell_2022.R <dir holding Survey Data File.xlsx> <output dir>
##
##Design: a single-profile text vignette ("A 5-year-old child presents with a temperature of 37.8 and a
##cough ...") varying 5 factors (instrument Q3.1): repeat presentation, time and day, whether the parent
##requests an ED referral, parental capacity to cope, and access to a rapid paediatric outpatient
##clinic. GPs were randomised to one of four blocks; blocks 1 and 3 (6 scenarios each, Q3.2-Q3.7 and
##Q5.2-Q5.7) belong to this study; blocks 2 and 4 (a child with intellectual disability) are a separate
##study whose answers are not in the deposit. Fixed blocked design: each block shows the same 6 vignettes
##in the instrument's order, so task = position in the block (INFERRED from the instrument order; the
##export does not record display order) and profile = 1.
##Attribute levels are coded from each scenario's text in Survey Questions.docx (table `sc` below) and
##stored as the instrument's clause, normalised across scenarios where the wording varies only
##trivially ("2pm-5pm" vs "2-5pm", "Monday" vs "Monday morning", "second visit for this complaint"
##vs "... for the same complaint", "referral to the emergency department (ED)" vs "... to the ED",
##"They do not mention a referral to the ED" vs "... the need for a referral to the emergency
##department (ED)"). The Ngene file has 24 rows x 6 attributes in 4 blocks (incl. a "competence"
##attribute and a 3-level capacity attribute); the fielded texts show 5 two/three-level factors, so the
##Ngene coding is not used.
##  choice = "Given the information provided above, would you refer the patient to the ED or not refer?"
##           Refer = 1, Not refer = 0 (single profile; opt_out = yes). Unanswered scenarios are omitted.
##150 GPs answered at least one scenario (77 in block 1, 73 in block 3); the record reports n = 142
##(probably those completing all six; flagged, not fixed). 157 exported rows with no scenario answers
##(blocks 2/4 respondents, non-starters) are not in the table.
##Covariates: cov_gender (Q2.1: Male = male, Female = female, "Other/ Prefer not to say" = NA since the
##option merges both), cov_age_group (Q2.3), cov_county (Q2.5, practice county), cov_year_qualified
##(Q2.6), cov_years_gp (Q2.7 free entry; whole numbers 0-60 kept, else NA), cov_ed_access (Q2.8,
##1 not at all .. 5 very accessible), cov_practice_size (Q2.9), cov_paed_training and
##cov_referral_pathways (Q2.4 / Q2.2 multi-select answer text), cov_rank_<attribute> (Q7.1 top-three
##ranking, 1 = most influential), cov_uncertainty_1..15 (Q8.1 physician-uncertainty items, answer text),
##cov_duration_sec (whole survey), cov_finished (1 True, 0 False). Dropped: dates, ResponseId,
##IP-status fields, all free-text comment and "other" boxes. No survey weight.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- suppressMessages(read_excel(file.path(raw, "Survey Data File.xlsx"), col_names = FALSE, col_types = "text"))
s <- as.data.table(x[-1, ]); setnames(s, unlist(x[1, ]))
stopifnot(nrow(s) == 307)
sc <- fread(text = "
q|block|task|attr_repeat|attr_time|attr_request|attr_capacity|attr_clinic
Q3.2|1|1|This is the second visit for this complaint.|It is between 9am-12pm on a Monday.|has queried the need for a referral to the emergency department (ED)|You feel they have good capacity to cope with the child being ill at home.|A rapid access paediatric outpatients' clinic is also available to you to refer the child directly.
Q3.3|1|2|This is the first visit for this complaint.|It is between 2pm-5pm on a Wednesday afternoon.|They do not mention a referral to the ED.|You feel they have good capacity to cope with the child being ill at home.|A rapid access paediatric outpatients' clinic is also available to you to refer the child directly.
Q3.4|1|3|This is the first visit for this complaint.|It is between 2pm-5pm on a Friday afternoon.|has queried the need for a referral to the emergency department (ED)|You feel they have good capacity to cope with the child being ill at home.|A rapid access paediatric outpatients' clinic is also available to you to refer the child directly.
Q3.5|1|4|This is the first visit for this complaint.|It is between 2pm-5pm on a Friday afternoon.|They do not mention a referral to the ED.|You feel they have limited capacity to cope with the child being ill at home.|A rapid access paediatric outpatients' clinic is not available to you to refer the child directly.
Q3.6|1|5|This is the second visit for this complaint.|It is between 9am-12pm on a Monday.|has requested a referral to the emergency department (ED)|You feel they have limited capacity to cope with the child being ill at home.|A rapid access paediatric outpatients' clinic is not available to you to refer the child directly.
Q3.7|1|6|This is the second visit for this complaint.|It is between 2pm-5pm on a Wednesday afternoon.|has requested a referral to the emergency department (ED)|You feel they have limited capacity to cope with the child being ill at home.|A rapid access paediatric outpatients' clinic is not available to you to refer the child directly.
Q5.2|3|1|This is the first visit for this complaint.|It is between 9am-12pm on a Monday.|has requested a referral to the emergency department (ED)|You feel they have limited capacity to cope with the child being ill at home.|A rapid access paediatric outpatients' clinic is also available to you to refer the child directly.
Q5.3|3|2|This is the second visit for this complaint.|It is between 2pm-5pm on a Wednesday afternoon.|has requested a referral to the emergency department (ED)|You feel they have good capacity to cope with the child being ill at home.|A rapid access paediatric outpatients' clinic is also available to you to refer the child directly.
Q5.4|3|3|This is the first visit for this complaint.|It is between 9am-12pm on a Monday.|They do not mention a referral to the ED.|You feel they have limited capacity to cope with the child being ill at home.|A rapid access paediatric outpatients' clinic is also available to you to refer the child directly.
Q5.5|3|4|This is the second visit for this complaint.|It is between 9am-12pm on a Monday.|has queried the need for a referral to the emergency department (ED)|You feel they have good capacity to cope with the child being ill at home.|A rapid access paediatric outpatients' clinic is not available to you to refer the child directly.
Q5.6|3|5|This is the second visit for this complaint.|It is between 2pm-5pm on a Wednesday afternoon.|They do not mention a referral to the ED.|You feel they have limited capacity to cope with the child being ill at home.|A rapid access paediatric outpatients' clinic is not available to you to refer the child directly.
Q5.7|3|6|This is the first visit for this complaint.|It is between 2pm-5pm on a Friday afternoon.|has queried the need for a referral to the emergency department (ED)|You feel they have good capacity to cope with the child being ill at home.|A rapid access paediatric outpatients' clinic is not available to you to refer the child directly.
", sep = "|")
stopifnot(nrow(unique(sc[, -(1:3)])) == 12)
s[, rid := .I]
b1 <- s[, rowSums(!is.na(.SD)) > 0, .SDcols = sc[block == 1, q]]
b3 <- s[, rowSums(!is.na(.SD)) > 0, .SDcols = sc[block == 3, q]]
stopifnot(!any(b1 & b3))
s <- s[b1 | b3]
s[, id := .I]
lg <- melt(s[, c("id", sc$q), with = FALSE], id.vars = "id", variable.name = "q", value.name = "ans",
           variable.factor = FALSE, na.rm = TRUE)
stopifnot(all(lg$ans %in% c("Refer", "Not refer")))
lg <- sc[lg, on = "q"]
d <- lg[, .(id, task, profile = 1L, choice = as.integer(ans == "Refer"), trial_block = block,
            attr_repeat, attr_time, attr_request, attr_capacity, attr_clinic)]
stopifnot(d[, uniqueN(trial_block), id][, all(V1 == 1)])
cv <- s[, .(id, cov_gender = c(Male = "male", Female = "female")[Q2.1], cov_age_group = Q2.3,
            cov_county = Q2.5, cov_year_qualified = Q2.6,
            cov_years_gp = suppressWarnings(as.numeric(Q2.7)), cov_ed_access = as.integer(Q2.8),
            cov_practice_size = Q2.9, cov_paed_training = Q2.4, cov_referral_pathways = Q2.2,
            cov_rank_repeat = as.integer(Q7.1_2), cov_rank_time = as.integer(Q7.1_6),
            cov_rank_request = as.integer(Q7.1_7), cov_rank_capacity = as.integer(Q7.1_15),
            cov_rank_clinic = as.integer(Q7.1_16),
            cov_duration_sec = as.integer(`Duration (in seconds)`), cov_finished = as.integer(Finished == "True"))]
stopifnot(all(s$Q2.1 %in% c("Male", "Female", "Other/ Prefer not to say", NA)))
cv[!(cov_years_gp %in% 0:60), cov_years_gp := NA][, cov_years_gp := as.integer(cov_years_gp)]
for (k in 1:15) cv[, paste0("cov_uncertainty_", k) := s[[paste0("Q8.1_", k)]]]
d <- cv[d, on = "id"]
setcolorder(d, c("id", "task", "profile", "choice", "trial_block"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mcdonnell_2022_gp_referral.csv"))
