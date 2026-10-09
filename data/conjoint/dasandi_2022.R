##Climate-message framing conjoint (China, Germany, India, UK, USA; Deltapoll) from
##Dasandi, N., Graham, H., Hudson, D., Jankin, S., vanHeerde-Hudson, J., & Watts, N. (2022). Positive,
##global, and health or environment framing bolsters public support for climate policies.
##Communications Earth & Environment, 3, 239. https://doi.org/10.1038/s43247-022-00571-x
##Replication data: Harvard Dataverse doi:10.7910/DVN/XJ4VEH, CC0 1.0. Files read:
##CEE_ClimateFrames_df_cj_profiles.rds (main study) and CEE_ClimateFrames_August_pilot.rds (pilot).
##CEE_ClimateChangeConjoint_analysis.R read as text, not run. Wording, languages and design from the
##article (Methods, Fig. 1 caption, Fig. 4).
##Usage: Rscript dasandi_2022.R <dir holding the two .rds> <output dir>
##
##Two tables, one per fielding (same design, same statements):
##  dasandi_2022_climate_frames        main study, October 2020, 7,512 respondents (China 1,502,
##                                     Germany 1,501, India 1,506, UK 1,500, USA 1,503 = the article).
##  dasandi_2022_climate_frames_pilot  "earlier pilots ... in the five countries" (article; shown in
##                                     Supplementary Figs. S24-S25), 4,935 respondents; the file name says
##                                     August (2020 presumably; not stated).
##The authors pool the five countries (Fig. 2, n = 7,512) and the statement text is one English master,
##so each fielding is one table with cov_country.
##Each respondent saw 5 pairs of statements (task = xLoopConcepts r<task>, profile = c<1/2>, recorded).
##Outcome:
##  choice = Chosen, "Indicate which of the two statements would make you more likely to support policies
##           to tackle climate change." Forced choice, exactly one per task (checked).
##Not kept: the deposit's `rating` (a monthly willingness-to-pay amount per statement, article Methods:
##"how much they would be willing to pay each month"; not analysed in the paper). Its wording, currency
##and slider range are not documented and differ by country (max 20 UK, 26 US, 23 DE, 180 CN, 1,844 IN),
##so it is dropped; rating_pref/Chosen_rat/rating_z/rating_norm are derived from it. `shown` (index of
##the 96 statements) and `text` (the UK-English statement) are dropped.
##Attributes (text vignette; article Fig. 4 + Table S2): each statement opens with the valence ("Climate
##change is the greatest threat we face" / "Tackling climate change is the greatest opportunity we
##have"), names the theme with a fixed example for each valence x theme, and ends "This will make things
##better/worse for <scale> <time>". attr_ keep the authors' level names (as in Fig. 4): valence
##Opportunity/Threat; theme Economic/Environmental/Health/Migration; scale World/Country/Community/
##Personal (displayed as "the world", the survey country's name, "your community", "you"); time
##Now/2030/2050 ("right now", "by 2030", "by 2050"). Randomized "without any constraints" (article,
##Statistical analysis), 96 statements. English in UK/USA/India; professionally translated into Chinese
##and German (article, Survey translations); translations not deposited.
##Covariates: cov_country; cov_gender from gender_fac_bin (Male/Female; the 13 main-study respondents who
##answered "In another way" are NA in that column, so NA here); cov_age_group (agecat4_fac, the authors'
##bands); cov_university_degree (educ_uni_fac, the only education variable deposited, already collapsed);
##cov_party_id (QDP18, country-specific party lists pid_DE/UK/US/IN_fac, text; not asked in China);
##cov_concern (concern_fac_r, Q2 "How concerned, if at all, are you personally about climate change?");
##cov_care_<issue> (Q1 multi-select, Selected/Not selected); cov_children (children_bin);
##cov_work_status (work_status_fac2); cov_survey_weight = w8 ("Standard Weight Variable"; the authors
##weight every analysis). Derived age/generation/income/party recodes are dropped. The Deltapoll
##"Unique ID" is re-keyed to integers.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
build <- function(file, name) {
  x <- as.data.table(as.data.frame(readRDS(file.path(raw, file))))
  x[, task := as.integer(sub("^xLoopConceptsr([1-5])c[12]$", "\\1", statement))]
  x[, profile := as.integer(sub("^xLoopConceptsr[1-5]c([12])$", "\\1", statement))]
  stopifnot(!anyNA(x$task), !anyNA(x$profile), x$contest_no == paste0("Q3_CHOICE_", x$task))
  ids <- sort(unique(x$id))
  d <- x[, .(id = match(id, ids), task, profile, choice = as.integer(Chosen),
             attr_valence = as.character(Valence), attr_theme = as.character(Theme),
             attr_scale = as.character(Scale), attr_time = as.character(Time),
             cov_country = as.character(country_fac),
             cov_gender = c(Male = "male", Female = "female")[as.character(gender_fac_bin)],
             cov_age_group = as.character(agecat4_fac),
             cov_university_degree = as.character(educ_uni_fac),
             cov_party_id = fcoalesce(as.character(pid_DE_fac), as.character(pid_UK_fac),
                                      as.character(pid_US_fac), as.character(pid_IN_fac)),
             cov_concern = as.character(concern_fac_r))]
  for (v in grep("^care_.*_fac$", names(x), value = TRUE))
    d[, paste0("cov_", sub("_fac$", "", v)) := as.character(x[[v]])]
  d[, `:=`(cov_children = as.character(x$children_bin), cov_work_status = as.character(x$work_status_fac2),
           cov_survey_weight = as.numeric(x$w8))]
  stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)],
            d[, uniqueN(id)] == length(ids), !anyNA(d[, .(attr_valence, attr_theme, attr_scale, attr_time)]))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv")))
  cat(name, nrow(d), "rows,", uniqueN(d$id), "respondents\n")
}
build("CEE_ClimateFrames_df_cj_profiles.rds", "dasandi_2022_climate_frames")
build("CEE_ClimateFrames_August_pilot.rds", "dasandi_2022_climate_frames_pilot")
