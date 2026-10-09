##Corruption-harm conjoint (Armenia, face-to-face tablet survey, January-May 2023) from
##Erlich, A., Gans-Morse, J., Nichter, S., & Holverscheid, A. (2025). What corruption is most harmful?
##Unbundling citizen perceptions. World Development, 194, 107001.
##https://doi.org/10.1016/j.worlddev.2025.107001
##Replication data: Harvard Dataverse doi:10.7910/DVN/3HHOMK, CC0 1.0, no restricted files. Files read
##(inside wd_upload_20250410.zip): data_raw/AIP_FINAL.sav (survey responses), data_raw/design1.csv
##(formr randomization: respID, qID = screen, altID = scenario A/B, Armenian level text),
##data_raw/attribute_levels_list1.csv and _transl.csv (Armenian level text with the authors' English),
##data_clean/final_data_wide_weighted.rds (only the authors' weight ps_wgt_gen_age). SurveyInstrument.docx
##(English) and scripts/01-07 read as text, not run. The article itself was not available (Elsevier).
##(erlich_2025.R is a different study: Erlich, Gans-Morse & Nichter, Selective bribery, Ukraine.)
##Usage: Rscript erlich_2025_corruption.R <dir holding data_raw/ and data_clean/> <output dir>
##
##1,497 respondents keep at least one answered task (of 1,501 interviews; the authors' analysis file
##long_data_cj1_eng.rds has 1,495 analysis_IDs; 61 task records are dropped for a screen mismatch, below). 5 screens (tasks) x 2 scenarios (A = profile 1, B = 2), 7 attributes, all shown.
##Five forced choices per screen (SurveyInstrument.docx Exp1_Screen1; the SPSS variable labels of
##X1_S*.2-.5 are left over from an earlier draft and do not match; the authors' Global_Params.R
##OUTCOMES list follows the instrument order):
##  choice_personal  X1_St.1 "which of the scenarios is likely to harm you and your family the most"
##  choice_economy   X1_St.2 "which of the scenarios will probably harm Armenia's economy more"
##  choice_trust     X1_St.3 "which of the scenarios would most likely reduce your confidence in the
##                   political system of Armenia"
##  choice_moral     X1_St.4 "in which of the following scenarios do you think the official's action
##                   is more morally wrong"
##  choice_frequent  X1_St.5 "which of these two scenarios do you think happens most often in Armenia"
##Answers 1 = Scenario A, 2 = Scenario B; 98 DK / 99 RA are set to NA for that question on both
##profiles (the authors drop the whole task). Only A and B were offered, so opt_out = no.
##Design: the tablet pulled the profiles from formr by the ID the interviewer entered (pulled_id =
##design1 respID). 244 IDs were entered for 2-3 different interviews, which therefore saw the same
##profiles; kept, as the authors do.
##id is one interview, never the formr ID: respondents are keyed by their row in AIP_FINAL.sav (one row per
##interview, distinct SubmissionDate/age/gender), so the interviews sharing a formr ID get separate ids. Before each screen the interviewer recorded the screen number the
##respondent saw (Npic_t); tasks where it is not t, or missing, are dropped (the profiles shown cannot
##be confirmed; the authors keep them). Level text is the Armenian screen text from design1.csv (the
##authors' English is in attribute_levels_list1_transl.csv). Each level also had a picture (attribute
##list column `image`). The instrument walks the respondent through the scenario table line by line
##(type, use of funds, amount, acting alone, rank, sector), so attribute order is taken as fixed.
##Check: marginal means by official rank on choice_personal (0.513 high / 0.487 low) and choice_economy
##(0.520 / 0.480) reproduce the authors' main/FIG_3_mms_margins.csv.
##Restrictions (observed in design1; the authors estimate within constrained combinations,
##05_constrained_lm.R): "gives corrupt favors to family members" and "uses public resources to
##benefit own firm" occur only with "keeps all corrupt funds" and with personal use; political use
##never occurs with "keeps all corrupt funds". Those two types are 6% of profiles each, the others
##29-30%; personal use 64%.
##Covariates (value-label text from the .sav): cov_age (D1, years), cov_gender (D2: 1 Female, 2 Male),
##cov_region (D3), cov_residence (D4), cov_education (D5; "DK" kept, 99 RA -> NA), cov_marital (D6),
##cov_children (D7), cov_family_finances (D10), cov_income (D11), and the pre-conjoint 1-7 items
##cov_harm_personal / cov_harm_economy / cov_harm_trust / cov_corruption_frequency (A7-A10 codes).
##cov_survey_weight = ps_wgt_gen_age, the authors' post-stratification weight to census age x gender
##cells (02_weight_armenia.R), matched by row.
##PII FOUND and dropped: tablet device IDs, contact dates/times, settlement (locality) codes,
##interviewer ID, free-text "other" answers; formr IDs not kept (respondents re-keyed 1..n in file order).
##The deposit also holds a second conjoint (anti-corruption agencies, design2.csv, X2_S1-S5) that the
##article does not analyse and the instrument does not document; it is not built here.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_sav(file.path(raw, "data_raw/AIP_FINAL.sav")))
w <- readRDS(file.path(raw, "data_clean/final_data_wide_weighted.rds"))
stopifnot(nrow(s) == 1501L, nrow(w) == 1501L, all(w$pulled_id == s$pulled_id), all(w$analysis_ID2 == 1:1501))
s[, rid := .I][, wt := w$ps_wgt_gen_age]
ds <- fread(file.path(raw, "data_raw/design1.csv"), encoding = "UTF-8")
stopifnot(ds[, .N, respID][, all(N == 10L)], all(s$pulled_id %in% ds$respID))
lv <- fread(file.path(raw, "data_raw/attribute_levels_list1.csv"), encoding = "UTF-8")
feat <- c("type", "sector", "official_rank", "size_corrupt", "official_use", "act_alone", "official_gender")
for (f in feat) stopifnot(all(ds[[f]] %in% lv[attribute == f, level]))
oc <- c("personal", "economy", "trust", "moral", "frequent")
rows <- list(); dropped <- 0L
for (t in 1:5) {
  x <- s[, c(list(rid = rid, pulled_id = pulled_id, npic = as.integer(zap_labels(get(paste0("Npic_", t))))),
             setNames(lapply(1:5, function(k) as.integer(zap_labels(get(sprintf("X1_S%d.%d", t, k))))), oc))]
  bad <- is.na(x$npic) | x$npic != t
  dropped <- dropped + sum(bad & rowSums(!is.na(x[, ..oc])) > 0)
  x <- x[!bad]
  for (p in 1:2) {
    y <- merge(x, ds[qID == t & altID == p, c("respID", feat), with = FALSE], by.x = "pulled_id", by.y = "respID")
    y[, `:=`(task = t, profile = p)]
    for (k in oc) y[, paste0("choice_", k) := fifelse(get(k) %in% 1:2, as.integer(get(k) == p), NA_integer_)]
    rows[[length(rows) + 1]] <- y
  }
}
message("tasks dropped for screen-number mismatch: ", dropped)
d <- rbindlist(rows)
d <- d[rowSums(!is.na(d[, paste0("choice_", oc), with = FALSE])) > 0]
setnames(d, feat, paste0("attr_", feat))
stopifnot(d[, .N, .(rid, task)][, all(N == 2L)], !anyNA(d[, paste0("attr_", feat), with = FALSE]))
for (k in paste0("choice_", oc)) stopifnot(d[!is.na(get(k)), sum(get(k)), .(rid, task)][, all(V1 == 1L)])
lab <- function(x, na = 99) { y <- as.character(as_factor(x, levels = "labels")); y[zap_labels(x) %in% na | is.na(zap_labels(x))] <- NA; y }
cv <- s[, .(rid, cov_age = as.integer(D1), cov_gender = c("female", "male")[as.integer(zap_labels(D2))],
            cov_region = lab(D3), cov_residence = lab(D4), cov_education = lab(D5), cov_marital = lab(D6),
            cov_children = lab(D7), cov_family_finances = lab(D10), cov_income = lab(D11),
            cov_harm_personal = as.integer(zap_labels(A7)), cov_harm_economy = as.integer(zap_labels(A8)),
            cov_harm_trust = as.integer(zap_labels(A9)), cov_corruption_frequency = as.integer(zap_labels(A10)),
            cov_survey_weight = wt)]
stopifnot(all(attr(s$D2, "labels") == c(Female = 1, Male = 2)), all(cv$cov_age %in% 18:100))
d <- merge(d[, c("rid", "task", "profile", paste0("choice_", oc), paste0("attr_", feat)), with = FALSE], cv, by = "rid")
d[, id := match(rid, sort(unique(rid)))][, rid := NULL]
setcolorder(d, c("id", "task", "profile"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "erlich_2025_corruption_harms.csv"))
