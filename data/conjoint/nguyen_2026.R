##Queensland households' most- and least-preferred of three sanitation options (two urine-separating sanitation
##systems and conventional toilets), from the data set
##Nguyen, T. G., Iftekhar, M. S., Koskue, V., Ratnasiri, S., Roiko, A., & Beal, C. D. (2026). Is investing in
##urine-separating sanitation systems socially optimal? Lessons from an Australian case study [Data set]. figshare.
##https://doi.org/10.6084/m9.figshare.34699905 (CC BY 4.0, figshare record licence). No article DOI located.
##Files read: "Survey data_Queensland.xls" (one sheet, 12,888 rows x 222 columns; 3 rows per choice task).
##Usage: Rscript nguyen_2026.R <dir holding the xls> <output dir>
##(Draft held in batch 13, oneoff/conjoint-scouting/batch13/build/held_scripts/nguyen_2026.R; rewritten here under the
###3474 neutral-name rule.)
##
##Design: 537 Queensland households (abstract: 537), 8 choice tasks each (choicetask_n = task, recorded order index),
##blocked fixed design (Block 1-5, one per respondent; choicetask = design task 1-40, kept as trial_design_task; levels
##constant within design task x alternative, checked). Three alternatives per task: two urine-separating options and a
##fixed third alternative whose stored levels are "Conventional toilets and/or urinals" (att1, att2), "N/A" (att4, att5)
##and 0 (att3, att6). It is shown with its own levels, so it is a profile (profile 3), not an opt-out; whether "N/A"
##and 0 were the displayed entries is not documented (kept as deposited).
##Outcomes on the same tasks: choice = selectedmostprefer (most preferred of the three) and choice_least_preferred =
##selectedleastprefer (least preferred of the three); exactly one of each per task and never the same alternative
##(checked, 4,296 tasks). Forced (opt_out = no). Question wording not deposited.
##ATTRIBUTES. The deposit names the attribute columns only att1-att6 and has no codebook; no source states which
##attribute each column is, so the columns keep the deposit's names (#3474 neutral-name rule). att1, att2, att4 and att5
##hold level TEXT (e.g. "New toilets and/or urinals", "Portable toilets + Public facilities", "Urine-derived fertilisers
##for pastures", "Low/Medium/High") and are stored as attr_att1, attr_att2, attr_att4, attr_att5. att3 (0/5/65/70/95)
##and att6 (0/25/50/75/100/125/150) are bare numbers whose displayed form, unit and currency are not documented:
##CODED as attr_att3_code and attr_att6_code. (The parameter labels of the deposit's benefit-cost workbooks suggest
##att3 = water saving for toilet flushing in %, att6 = cost; unconfirmed, not used for naming.)
##Covariates: cov_gender (Male/Female; "Prefer not to say" -> NA), cov_age_group (band text), cov_education (answer
##text), cov_income (band text as stored, period not stated; "I would rather no say" -> NA), cov_protestvoter (as
##deposited; the authors' protest-voter flag, rule undocumented). Pre_location is Queensland for everyone (dropped).
##No exclusions applied; the deposit documents none.
##Dropped: ppid (panel respondent id, re-keyed), Mostprechoice/Leastprechoice (repeat the outcomes), the derived
##dummy codings (type1-3, loc1-4, fer1-5, scale1-3), attitude/knowledge/ranking/follow-up batteries, the recoded
##covariate copies (MALE, AGE, INC, ...), every *_TEXT and _comment free-text field.
##PII FOUND: ppid is a panel respondent id (dropped, re-keyed).
suppressMessages({library(data.table); library(readxl)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- list.files(raw, pattern = "\\.xls$", full.names = TRUE); stopifnot(length(f) == 1L)
d <- as.data.table(suppressWarnings(read_excel(f, col_types = "text")))
stopifnot(nrow(d) == 12888L, uniqueN(d$ppid) == 537L, all(d$Pre_location == "Queensland"))
d[, `:=`(id = match(ppid, sort(unique(ppid))), task = as.integer(choicetask_n), profile = as.integer(alt),
         choice = as.integer(selectedmostprefer), choice_least_preferred = as.integer(selectedleastprefer))]
stopifnot(d[, .(a = sum(choice), b = sum(choice_least_preferred), c = sum(choice * choice_least_preferred), n = .N,
                p = paste(sort(profile), collapse = "")), .(id, task)][, all(a == 1 & b == 1 & c == 0 & n == 3 & p == "123")])
stopifnot(d[, uniqueN(paste(att1, att2, att3, att4, att5, att6)), .(choicetask, alt)][, all(V1 == 1L)])
stopifnot(d[alt == "3", all(att1 == "Conventional toilets and/or urinals" & att4 == "N/A" & att5 == "N/A" & att3 == "0" & att6 == "0")])
stopifnot(d[, lapply(.SD, uniqueN), id, .SDcols = c("Pre_gender", "Pre_age", "Education", "Pre_income", "protestvoter")][,
  all(as.matrix(.SD) == 1L), .SDcols = -1])
x <- d[, .(id, task, profile, choice, choice_least_preferred,
  attr_att1 = att1, attr_att2 = att2, attr_att3_code = as.integer(att3), attr_att4 = att4, attr_att5 = att5,
  attr_att6_code = as.integer(att6), trial_block = as.integer(Block), trial_design_task = as.integer(choicetask),
  cov_gender = fcase(Pre_gender == "Male", "male", Pre_gender == "Female", "female", default = NA_character_),
  cov_age_group = Pre_age, cov_education = Education,
  cov_income = fifelse(Pre_income == "I would rather no say", NA_character_, Pre_income),
  cov_protestvoter = protestvoter)]
stopifnot(!anyNA(x[, .(attr_att1, attr_att2, attr_att3_code, attr_att4, attr_att5, attr_att6_code)]))
setorder(x, id, task, profile)
fwrite(x, file.path(out, "nguyen_2026_urine_sanitation.csv"))
cat(nrow(x), uniqueN(x$id), "\n")
