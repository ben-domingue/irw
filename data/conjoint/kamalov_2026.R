##Russian-emigrant aid conjoint from
##Kamalov, E., & Sergeeva, I. (2026). Helping emigrants flee a political crisis: How antiwar
##alignment shapes the aid preferences of wartime Russian migrants. Perspectives on Politics.
##https://doi.org/10.1017/S1537592725104143 (Stanford CDDRL lists it March 2026; volume/pages not
##checked)
##Replication data: Harvard Dataverse doi:10.7910/DVN/NFQHIM, CC0 1.0, no restricted files.
##File read: input_data.sav (SPSS, value labels used). README.txt and conjoint_main_amce.R read as
##text. No codebook or questionnaire is deposited.
##Usage: Rscript kamalov_2026.R <raw dir> <output dir>
##
##2,036 Russian migrants who left Russia in 2022 after the invasion of Ukraine (convenience
##sample, more than 60 countries; article). Each did 2 forced-choice tasks of 2 profiles of
##hypothetical Russian individuals (6 attributes, "attribute levels were independently
##randomized", article). The source `profile` column is "<task>.<profile>" (verified equal to
##`task`); task and profile are recorded.
##Outcome: choice (source `choice`, 0/1): respondents were asked "to choose which profiles of
##hypothetical Russian individuals" they would help / "select their preferred option" (article
##paraphrase; the verbatim item is not deposited). Forced choice, no opt-out (exactly one chosen
##per task, checked).
##Attribute text: the authors' ENGLISH labels from the SPSS value labels (also their plot
##labels). The survey labels in the file are Russian, so respondents almost certainly saw Russian
##text, which is not deposited: age "30 y/o"/"50 y/o"; gender Man/Woman; children "No children"/
##"Two kids under 18"; profession Office worker/Journalist/Health worker; ethnicity Russian/
##Ukrainian/Buryat origin; motivation "Poor economic prospects"/"Can't accept Russian politics"/
##"Can't accept Russian politics + Was arrested in rallies" (the label's line break is replaced by
##a space). Attribute display order is not in the data.
##The deposit is already restricted to the authors' analysis sample (all rows: living outside
##Russia, left in 2022); those two constant columns are dropped.
##Covariates (from the second survey wave, as deposited): cov_female (sex: 1 = female), cov_age
##(years), cov_country (country of residence, English), cov_left_after_mobilization (1 = left
##after 21 Sept 2022, 0 = before), cov_has_children (1/0), cov_education (1 = incomplete
##secondary (9 grades or less), 2 = complete secondary, 3 = vocational, 4 = incomplete higher,
##5 = higher, 6 = academic degree), cov_politics_interest (interest in Russian politics,
##1 = very interested .. 4 = not at all), cov_income (authors' 1 = poorest .. 6 = richest),
##cov_guilt ("guilt for Russia's actions in Ukraine", 1 = do not feel at all .. 5 = feel strongly),
##cov_responsibility (responsibility for the consequences of Russia's actions towards Ukraine,
##same scale), cov_repression_count (authors' count of experiences of political pressure in
##Russia), cov_protest_permitted / cov_protest_unpermitted / cov_help_ukrainian_refugees /
##cov_help_russian_emigrants / cov_help_russian_ngos (0/1, merged across the two waves).
##Dropped: the authors' binary/indexed versions (*_bin, *_eng, polit_civic_index, country_top/
##cis/neighbours, identity_second, ukrainians, discrimination_soc), Russian-text country and
##locality fields, the remaining activity items.
##ResponseId (already 1..2,036) is re-keyed to integers as given. No PII found.
##N = 2,036 matches the article.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_sav(file.path(raw, "input_data.sav")))
stopifnot(nrow(s) == 8144, all(as_factor(s$location) == "Да"), all(as_factor(s$when_left) == "Да"))
lab <- function(x) { y <- as.character(as_factor(x)); stopifnot(!anyNA(y)); gsub("\\s*\\n\\s*", " ", y) }
d <- data.table(id = as.integer(s$ResponseId), task = as.integer(s$task), profile = as.integer(sub("^\\d+\\.", "", s$profile)),
                choice = as.integer(s$choice))
stopifnot(all(as.integer(sub("\\..*$", "", s$profile)) == d$task))
for (v in c("Age", "Gender", "Children", "Profession", "Ethnicity", "Motivation")) d[, paste0("attr_", tolower(v)) := lab(s[[v]])]
z <- function(x) as.integer(zap_labels(x))
d[, `:=`(cov_female = z(s$sex) - 1L, cov_age = as.integer(s$age_respondent), cov_country = s$country_english,
         cov_left_after_mobilization = z(s$when_left_mobiliz) - 1L, cov_has_children = 2L - z(s$child_bin),
         cov_education = z(s$education), cov_politics_interest = z(s$politics_interest_ru), cov_income = z(s$income_consum_num),
         cov_guilt = z(s$guilt), cov_responsibility = z(s$responsiblity), cov_repression_count = z(s$repress_total),
         cov_protest_permitted = z(s$polit_merged_meet_safe), cov_protest_unpermitted = z(s$polit_merged_meet_unsafe),
         cov_help_ukrainian_refugees = z(s$polit_merged_help_ukr), cov_help_russian_emigrants = z(s$polit_merged_help_rus),
         cov_help_russian_ngos = z(s$polit_merged_help_ngo))]
d[cov_country == "", cov_country := NA]
stopifnot(d[, .(s = sum(choice), n = .N), .(id, task)][, all(s == 1 & n == 2)], uniqueN(d$id) == 2036)
stopifnot(all(d$cov_female %in% c(NA, 0:1)), all(d$cov_has_children %in% c(NA, 0:1)), all(d$cov_left_after_mobilization %in% c(NA, 0:1)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kamalov_2026_emigrant_aid.csv"))
