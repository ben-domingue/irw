##Forest-disturbance factorial vignettes (Alberta, Saskatchewan, Manitoba) from
##Parkins, J., Andison, D., Sponarski, C., & Nock, C. (2025). Forest disturbance preferences in the
##western forest regions of Canada [Data set]. Borealis. https://doi.org/10.5683/SP3/0MHZOJ
##(no article named in the deposit).
##Data: Borealis doi:10.5683/SP3/0MHZOJ, CC0 1.0, no restricted files, no terms.
##Files read: ORD-927074-Y0P0_Final_Excel_060524 (original .xlsx; sheet A1 = data, sheet Datamap =
##codebook with question text and value labels), "Forest Disturbance Questionnaire Vignettes"
##(original .xlsx: the 54 scenario texts with choicesituation and foldoverblock),
##"Forest Disturbance Questionnaire.pdf" (pdftotext; Q6 wording and factor definitions).
##Usage: Rscript parkins_2025.R <raw dir> <output dir>
##
##2,606 residents of Alberta, Saskatchewan and Manitoba (online; 2,569 panel + 37 non-panel,
##dSample), all status 3 = qualified. Q6: each respondent rated 6 of 54 scenarios ("[Each respondent
##is given 6 scenarios, with factors that are randomly assigned]"); hQ6pickerr<k> = 1 flags the 6
##drawn, Q6r<k> holds the rating (checked: rated exactly where picked). 54 scenarios = a fractional
##design in two fold-over blocks of 27 (Vignettes file); the 6 are drawn across both blocks.
##TASK ORDER IS NOT RECORDED: task = 1..6 in scenario-number order (inferred, not display order);
##profile = 1 (single vignette per task). trial_scenario = the scenario number 1-54.
##Each scenario is one sentence: "In this forest landscape <agency>, within <area>, is managing a
##forest disturbance that involves <disturbance> that disturb(s) <size> with <severity> severity on
##the forest landscape." Attributes = the parts of that sentence as displayed (parsed from the
##Vignettes file and checked against the Datamap row text):
##  attr_agency      a government agency / a private company / an indigenous organization
##  attr_area        a provincial protected area / a federal protected area / a forest management area
##  attr_disturbance natural wildfire / managed wildfire / deliberate wildfire / natural insect and
##                   disease outbreaks / managed insect and disease outbreaks / eliminating insect and
##                   disease outbreaks / timber harvest / hybrid harvest / non-timber harvest
##  attr_size        a small area / a large area / a very large area
##  attr_severity    low / moderate / high
##The questionnaire defines the levels in a preamble (e.g. small area ~ 1,000 ha, low severity < 33%
##of the landscape impacted).
##  rating = Q6, "Please indicate how acceptable the following management scenario are to you based
##           on the combination of the (1) management agency responsible, (2) forest area type, (3)
##           disturbance types, (4) size and (5) severity given in each scenario indicate. Use the
##           scale ranging from completely acceptable (+5) to completely unacceptable (-5)."
##           Stored as the source codes 1-11 (Datamap: 1 = "Completely unacceptable -5", 6 = 0,
##           11 = "Completely acceptable +5"); higher = more acceptable; code - 6 = displayed value.
##Covariates (Datamap labels; the panel and non-panel samples answered the same questions under
##*_panel and plain names, merged): cov_sample (dSample: Panel / Non-Panel), cov_age_group (Q15),
##cov_gender (Q16: Female, Male, Non-binary = other, Prefer not to answer -> NA), cov_education
##(Q17 text), cov_community (Q11 text), cov_forest_distance (Q12 text), cov_duration_sec (LOI,
##"LOI (seconds)").
##PII in the deposit, dropped: Draw_Questionr2 (37 email addresses), Q13/Q14 (first three digits of
##home and work postal codes), uuid and psid (panel identifiers), record (re-keyed to row order),
##date/start_date, free-text "other" answers. Also dropped: Q1-Q5, Q7-Q10 attitude items, Q18/Q19.
library(readxl); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_excel(file.path(raw, "ORD-927074-Y0P0_Final_Excel_060524.xlsx"), sheet = "A1", guess_max = 3000))
v <- as.data.table(read_excel(file.path(raw, "Forest Disturbance Questionnaire Vignettes.xlsx")))
stopifnot(nrow(v) == 54, all(v$choicesituation == 1:54), all(x$status == 3))
re <- "^In this forest landscape (a government agency|a private company|an indigenous organization), within (a provincial protected area|a federal protected area|a forest management area), is managing a forest disturbance that involves (.+) that disturbs? (a small area|a large area|a very large area) with (low|moderate|high) severity on the forest landscape\\.$"
v[, vignette := trimws(vignette)]
stopifnot(all(grepl(re, v$vignette)))
v[, `:=`(attr_agency = sub(re, "\\1", vignette), attr_area = sub(re, "\\2", vignette), attr_disturbance = sub(re, "\\3", vignette),
         attr_size = sub(re, "\\4", vignette), attr_severity = sub(re, "\\5", vignette))]
stopifnot(uniqueN(v$attr_disturbance) == 9)
x[, id := seq_len(.N)]
p <- as.matrix(x[, paste0("hQ6pickerr", 1:54), with = FALSE]); r <- as.matrix(x[, paste0("Q6r", 1:54), with = FALSE])
stopifnot(all((p == 1) == !is.na(r)), all(rowSums(p) == 6), all(r %in% c(1:11, NA)))
d <- data.table(id = rep(x$id, 54), trial_scenario = rep(1:54, each = nrow(x)), rating = as.integer(r))[!is.na(rating)]
setorder(d, id, trial_scenario)
d[, `:=`(task = seq_len(.N), profile = 1L), by = id]
d <- v[, .(trial_scenario = choicesituation, trial_foldover_block = as.integer(foldoverblock), attr_agency, attr_area,
           attr_disturbance, attr_size, attr_severity)][d, on = "trial_scenario"]
co <- function(a, b) fcoalesce(as.integer(x[[a]]), as.integer(x[[b]]))
age <- co("Q15_panel", "Q15"); gen <- co("Q16_panel", "Q16"); edu <- co("Q17_panel", "Q17")
com <- co("Q11_panel", "Q11"); dis <- co("Q12_panel", "Q12")
stopifnot(all(age %in% c(1:8, NA)), all(gen %in% c(1:4, NA)), all(edu %in% c(1:7, NA)), all(com %in% c(1:4, NA)), all(dis %in% c(1:3, NA)))
cv <- data.table(id = x$id, cov_sample = c("Panel", "Non-Panel")[x$dSample],
  cov_age_group = c("Under 18", "18 to 24", "25 to 34", "35 to 44", "45 to 54", "55 to 64", "65 to 74", "75 or older")[age],
  cov_gender = c("female", "male", "other", NA)[gen],
  cov_education = c("No diploma", "High school", "College", "Trade or Vocational School", "Bachelor's Degree", "Masters Degree", "Doctorate")[edu],
  cov_community = c("Resident of an urban community", "Resident of a suburban community", "Resident of a rural community of 4999 or less",
                    "Resident of a rural community of 5,000 or more")[com],
  cov_forest_distance = c("Further than 10 kilometers", "Between 1 and 10 kilometers", "Less than 1 kilometer")[dis],
  cov_duration_sec = as.numeric(x$LOI))
d <- cv[d, on = "id"]
setcolorder(d, c("id", "task", "profile", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "parkins_2025_forest_disturbance.csv"))
