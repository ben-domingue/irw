##New-housing factorial experiment, text version (one table) from
##Becker, C. (2026). "We need the right kind of people in this neighborhood": Racial motivation in
##opposition to new housing construction. Political Science Research and Methods, 1-21.
##https://doi.org/10.1017/psrm.2026.10131
##Replication data: Harvard Dataverse doi:10.7910/DVN/PZVRZT, CC0 1.0, no restricted files, no terms.
##File read: housing_data.xlsx (Qualtrics export: row 1 names, row 2 question text). Read as text
##only: README.md, replication.R (authors' exclusions and coding) and the article (Table 1 factors,
##Figures 1-3 stimuli, outcome wording, randomization, N).
##Usage: Rscript becker_2026.R <raw dir> <output dir>
##
##Cint panel, White US adults, Qualtrics, October 2024. 4,335 responses; kept the authors' analysis
##sample of 3,496 (README/replication.R: reCAPTCHA score >= 0.5, duration > 120 s, attention check
##answered "Strongly Agree" or "Strongly Disagree" -- the authors' rule, kept as is). Those with no
##factorial answer in their mode are dropped: 1,706 + 1,785 = 3,491, as in the article's models.
##One profile per respondent (task = profile = 1): a hypothetical development "in your
##neighborhood". Three attributes "randomly and independently varied" so that all 12 combinations are
##equally likely (article): housing type (single-family homes / apartments), expected racial makeup
##(mostly Black / mostly White), estimated monthly cost ($1,500 / $3,000 / $4,500). Respondents were
##randomly assigned to one of two presentation modes; the authors pool them (Table 4 col. 1) and also
##report each mode, and the attribute display differs between modes. Only the text mode is built:
##  becker_2026_housing_text (n = 1,706): a text profile; attr_ = the displayed lines as stored by
##    Qualtrics (text_attr_1-3): "Single Family Homes" / "Apartments", "Expected Racial Makeup: Mostly
##    Black" / "... Mostly White", "Estimated Monthly Housing Cost: $1500" / "$3000" / "$4500".
##  The image mode (n = 1,785; a mock-up flyer whose house and family race are shown only in photos)
##    is HELD (batch 6, image-conjoint rule): the deposit stores only the authors' codes for what the
##    photos showed, not displayed text. Its builder is kept in oneoff/conjoint-scouting/batch6/held_scripts.
##Outcome: choice = 1 for "Yes" to "Based just on the above information about this development, if it
##were put to a public vote, would you support it being built in your neighborhood?" (Yes/No; source
##text_treatment_1 / image_treatment_1). Single-profile vote, so opt_out = yes.
##Covariates (answer text as in the export): cov_gender (Female/Male -> female/male, Non-binary/Other
##-> other), cov_birth_year (typed year; values outside 1900-2006 set NA), cov_income, cov_education,
##cov_state, cov_neighborhood_type, cov_years_in_neighborhood (typed number; non-integers or > 100 set
##NA), cov_renter, cov_housing_crisis, cov_crisis_view (selected choice), cov_infill_support,
##cov_importance_<topic> and cov_impact_<topic> (crime, schools, property values, traffic, character,
##affordability), cov_party_id (PID1 selected choice), cov_pid_strength_rep / _dem, cov_pid_lean
##(PID1.R / PID1.D / PID1.I), cov_ideology (ideo5), cov_voted_2020, cov_vote_2020 and cov_vote_2020_hyp
##(selected choice), cov_duration_sec (whole survey), cov_recaptcha_score.
##PII in the source (dropped): ZIP code (zip5), Cint respondent id (rid), Qualtrics ResponseId; also
##dropped all free text (*_TEXT, bot-check colour), dates, Qualtrics quality fields, the list experiment
##(list_1, list_2: a separate design) and ProfileIdentifier (duplicates the attributes).
##Spot check (printed): raw difference in support, Black minus White family, per mode.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_excel(file.path(raw, "housing_data.xlsx"), col_types = "text"))[-1]
stopifnot(nrow(x) == 4335)
x[, rec := as.numeric(Q_RecaptchaScore)][, dur := as.integer(`Duration (in seconds)`)]
x <- x[!is.na(rec) & rec >= 0.5 & dur > 120 & attn_check %in% c("Strongly Agree", "Strongly Disagree")]
stopifnot(nrow(x) == 3496)
x[, id := .I]
yr <- suppressWarnings(as.numeric(x$age)); yrs <- suppressWarnings(as.numeric(x$res_stability))
topics <- c("crime", "schools", "property_values", "traffic", "character", "affordability")
cv <- x[, .(id, cov_gender = fcase(gender == "Female", "female", gender == "Male", "male",
                                   gender %in% c("Non-binary", "Other"), "other"),
            cov_birth_year = as.integer(ifelse(!is.na(yr) & yr >= 1900 & yr <= 2006 & yr == round(yr), yr, NA)),
            cov_income = income, cov_education = education, cov_state = state,
            cov_neighborhood_type = neighborhood_type,
            cov_years_in_neighborhood = as.integer(ifelse(!is.na(yrs) & yrs == round(yrs) & yrs <= 100, yrs, NA)),
            cov_renter = renter, cov_housing_crisis = housing_crisis, cov_crisis_view = crisis_skeptic,
            cov_infill_support = dev_sup_reword, cov_party_id = PID1, cov_pid_strength_rep = PID1.R,
            cov_pid_strength_dem = PID1.D, cov_pid_lean = PID1.I, cov_ideology = ideo5,
            cov_voted_2020 = voted_2020, cov_vote_2020 = candidate_select_20, cov_vote_2020_hyp = candidate_hyp_20,
            cov_duration_sec = dur, cov_recaptcha_score = rec)]
for (k in 1:6) {
  cv[, (paste0("cov_importance_", topics[k])) := x[[paste0("impacts_importance_", k)]]]
  cv[, (paste0("cov_impact_", topics[k])) := x[[paste0("impacts_eval_", k)]]]
}
build <- function(mode, ycol, attrs, n) {
  s <- x[image_treatment == mode & !is.na(get(ycol))]
  stopifnot(nrow(s) == n, all(s[[ycol]] %in% c("Yes", "No")))
  d <- s[, .(id, task = 1L, profile = 1L, choice = as.integer(get(ycol) == "Yes"))]
  for (v in names(attrs)) d[, (attrs[[v]]) := s[[v]]]
  stopifnot(!anyNA(d))
  d <- merge(d, cv, by = "id")
  d[, id := match(id, sort(unique(id)))]
  setorder(d, id, task, profile)
  d
}
tx <- build("0", "text_treatment_1", list(text_attr_1 = "attr_housing_type", text_attr_2 = "attr_racial_makeup",
                                          text_attr_3 = "attr_monthly_cost"), 1706)
fwrite(tx, file.path(out, "becker_2026_housing_text.csv"))
message("text: n ", nrow(tx), ", Black - White support ",
        round(tx[grepl("Black", attr_racial_makeup), mean(choice)] - tx[grepl("White", attr_racial_makeup), mean(choice)], 3))
