##Visual (AI-face) conjoint on school-curriculum reform proposals, Netherlands and Germany, from
##López Ortega, A., & Turnbull-Dugarte, S. J. (2025). Selectively (il)liberal: Theory and
##evidence on nativist disidentification. Political Science Research and Methods, 14(3), 789-815
##(online 19 December 2025). https://doi.org/10.1017/psrm.2025.10066
##Replication data: Harvard Dataverse doi:10.7910/DVN/GJWWEE, CC0 1.0, no restricted files.
##File read (from replicationfiles_LopezOrtega_TurnbullDugarte_PSRM.zip):
##data/conjoint_choice.Rdata (tibble `conjoint_choice`, one row per respondent x task x profile,
##loaded into its own environment). Design facts from the article; the authors' scripts were
##read as text (not run). No codebook or questionnaire is deposited.
##Usage: Rscript lopezortega_2025.R <raw dir holding replicationfiles_.../> <output dir>
##
##Kieskompas quota panels: Netherlands August 2022, Germany April 2023. TWO TABLES, one per
##country: the authors pool the countries (with by-country estimates), but the displayed level
##text is Dutch in one and German in the other, so it cannot be shared:
##  lopezortega_2025_curriculum_nl 1,140 respondents; lopezortega_2025_curriculum_de 1,263.
##The article reports N = 1,169 (NL) and 1,358 (DE), 2,527 in all; the deposit has 2,403
##respondents (all complete, 10 rows each); the difference is not explained (the authors'
##descriptives drop respondents with no post-stratification weight; those may be absent here).
##Design: respondents were told policy-makers were considering reforms to the national school
##curriculum and saw, in a hypothetical public consultation, 5 pairs (task = `round` 1-5,
##profile = `candidate` A/B -> 1/2) of proposals from civic actors. Outcome: choice = which
##proposal the respondent supports (exact wording NOT in the deposit or the article text read;
##forced choice: exactly one profile chosen in every task).
##Attributes:
##  attr_group_name   group name as displayed, with its emoji (nameRec; 25 per language; a
##                    stray trailing tab in one German name stripped)
##  attr_proposal     proposed curriculum addition/protection (proposRec; 12 per language)
##  attr_reasoning    justification (reasonRec; 6 per language)
##  attr_national_support  share of national support, "20%" .. "80%"
##  attr_country      a foreign country named in the profile (worldRec, in the display
##                    language); the article calls it international opposition/endorsement;
##                    the framing words around it are not deposited
##  attr_face         AI-generated face, stored as the Google Drive file id of the image (40
##                    faces); attr_photo_gender (Man/Woman), attr_photo_age (Junior/Senior) and
##                    attr_photo_ethnicity (White/Non-White) are the authors' coding of the face
##                    (5 faces per combination), not displayed text
##  attr_lgbt_marker  authors' code (No marker / LGBT+ marker / Trans marker); shown as a visual
##                    emoji cue per the article; display form not deposited
##Restrictions (article): across the five tasks no picture, group name, country, reasoning or
##proposal appears more than once for a respondent (in the data this holds for ~97-99% of
##respondents for faces, names and countries, not for reasoning or proposals, which have fewer
##levels than the 10 profiles shown).
##Covariates: cov_gender from respondent_gender (conjoint_choice.Rdata value labels 1 = Man,
##2 = Woman -> male/female); cov_birth_year (respondent_age holds years of birth, 1927..; the
##authors' scripts call it Birthyear); cov_education from respondent_edu, as its value-label text
##"Low education" / "Middle education" / "High education" (the only education variable in the
##file, already banded; script1_primary_analysis.R L42-44 relabels the same codes "Primary/
##Secondary/Tertiary studies"); cov_left_right 0-10; cov_sexuality (Heterosexual/LGB); cov_immigration_economy,
##cov_immigration_culture, cov_immigration_placetolive (ESS-style 0-10 items, direction as
##deposited); cov_attention_check (0-10 item; correct answer not documented, so it is not
##recoded to cov_attention_pass);
##cov_survey_weight (`weight`, used in the authors' cj() calls).
##Spot check: pooled weighted share chosen for Muslim group names (the ☪ emoji) = 0.46, the
##article's "only 46% of the time".
##Dropped: Qualtrics ResponseId (re-keyed 1..N per table), respondent ethnicity (missing for
##over half), sexual-role item (sexrole), the many attitude/affect/ptv batteries (no wording
##deposited; country-specific), and all derived groupings/bins (group, proposal codes,
##proposal_grouped*, reasoning_grouped, muslim, LGBT bins, international_rejection*, etc.).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "replicationfiles_LopezOrtega_TurnbullDugarte_PSRM", "data", "conjoint_choice.Rdata"), envir = e)
s <- as.data.table(e$conjoint_choice)
stopifnot(identical(unname(attr(s$respondent_gender, "labels")), c(1, 2)), identical(names(attr(s$respondent_gender, "labels")), c("Man", "Woman")),
          identical(names(attr(s$respondent_edu, "labels")), c("Low education", "Middle education", "High education")),
          identical(unname(attr(s$respondent_edu, "labels")), c(1, 2, 3)), all(s$respondent_gender %in% c(NA, 1, 2)), all(s$respondent_edu %in% c(NA, 1:3)))
ch <- function(x) trimws(as.character(x))
for (cc in c("The Netherlands", "Germany")) {
  x <- s[country == cc]
  x[, rid := match(as.character(ResponseId), unique(sort(as.character(ResponseId))))]
  d <- data.table(id = x$rid, task = as.integer(as.character(x$round)), profile = match(ch(x$candidate), c("A", "B")),
                  choice = as.integer(x$choice),
                  attr_group_name = ch(x$nameRec), attr_proposal = ch(x$proposRec), attr_reasoning = ch(x$reasonRec),
                  attr_national_support = ch(x$national_support), attr_country = ch(x$worldRec),
                  attr_face = sub(".*[?&]id=", "", ch(x$face)), attr_photo_gender = ch(x$gender), attr_photo_age = ch(x$age),
                  attr_photo_ethnicity = ch(x$ethinicity), attr_lgbt_marker = ch(x$LGBT),
                  cov_gender = c("male", "female")[as.integer(x$respondent_gender)], cov_birth_year = as.integer(x$respondent_age),
                  cov_education = c("Low education", "Middle education", "High education")[as.integer(x$respondent_edu)], cov_left_right = as.integer(x$respondent_leri),
                  cov_sexuality = ch(x$respondent_sexuality), cov_immigration_economy = x$immigration_economy,
                  cov_immigration_culture = x$immigration_culture, cov_immigration_placetolive = x$immigration_placetolive,
                  cov_attention_check = x$attention_check, cov_survey_weight = x$weight)
  ac <- grep("^attr_", names(d), value = TRUE)
  stopifnot(!anyNA(d[, ..ac]), d[, all(sapply(.SD, function(v) all(v != ""))), .SDcols = ac], !anyNA(d$profile),
            !anyDuplicated(d[, .(id, task, profile)]), d[, sum(choice), .(id, task)][, all(V1 == 1)],
            all(x$choice == (x$value == match(ch(x$candidate), c("A", "B")))))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("lopezortega_2025_curriculum_", ifelse(cc == "Germany", "de", "nl"), ".csv")))
}
