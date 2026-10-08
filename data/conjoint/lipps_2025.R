##Border-measure conjoint (Germany) from
##Lipps, J., Sczepanski, R., & Malet, G. (2025). Understanding preferences over borders.
##International Studies Quarterly, 69(1), sqaf003. https://doi.org/10.1093/isq/sqaf003
##Replication data: Harvard Dataverse doi:10.7910/DVN/H6KD6R, CC0 1.0, no restricted files.
##Files read: survey_dat_clean_conjoint.csv (the authors' long conjoint file) and, for respondent
##gender only, survey_dat_clean.csv (columns id, sex). Design facts from the
##article (Research design; open access). The deposit has no codebook or questionnaire; the
##authors' 03_likertscale.R gives the gender coding (read as text, not run).
##Usage: Rscript lipps_2025.R <raw dir> <output dir>
##
##4,374 respondents, a Bilendi online panel of German voting-age adults with quotas (December
##2022). Four tasks, each a pair of plans for "border measures" at Germany's border with a
##neighbouring country ("Germany uses a variety of measures to regulate the flow of people and
##goods across borders"); respondents chose the plan they were more likely to support, and rated
##each plan on an 11-point scale. Outcomes:
##  choice = source `chosen` (forced choice, exactly one per pair: checked).
##  rating = source `rati`, 0-10; the article gives no wording or anchors (the authors test
##     marginal means against 5). Stored as deposited.
##Task = source `Category` (1-4). PROFILE POSITION IS NOT DEPOSITED: the file stacks each
##respondent's 4 chosen profiles, then the 4 unchosen ones. profile numbers here are arbitrary
##labels (1 = the profile whose level text sorts first by measure, country, aim), so they carry
##no screen position and are independent of the choice, except in the 247 pairs whose two profiles
##are identical (there the chosen one is profile 1). Do not use them for position effects.
##Attributes: the deposit stores short English codes; respondents saw German text, not
##deposited. Stored as the article's English descriptions (code -> text):
##  measure: Fences -> "Building border fences"; DE Border guards -> "Increasing national border
##     patrols"; EU Border guards -> "Deploying European border guards"; Surveillance ->
##     "Increasing electronic border surveillance".
##  country: Switzerland, France, Poland, Czech Republic (as deposited).
##  aim (the article's "justification"): Refugees -> "Regulating the flow of people fleeing a
##     war zone"; Illeg. immig -> "Limiting illegal migration"; Crime -> "Countering drug
##     trafficking and crime"; Disease -> "Blocking the spread of communicable diseases".
##The article says all levels were randomized at the respondent level; no restrictions stated.
##Attribute order: not documented.
##Covariates (as deposited; scales not documented in the deposit): cov_border_open_close (0-10,
##the article's open (0) .. closed (10) borders item), cov_vote_intention, cov_left_right,
##cov_immigration_general, cov_european_integration, cov_urban_rural (German text: Dorf,
##Kleinstadt, Vorstadt einer Grossstadt, Grossstadt), cov_migration_background (0/1), cov_gender
##(from the answer text `sex` in survey_dat_clean.csv, joined by id: Weiblich -> female, Maennlich
##-> male, nichtbinaer -> other, "Moechte ich nicht mitteilen" -> NA; the conjoint file's 0/1
##`gender` = 0 Maennlich / 1 everything else, 03_likertscale.R, lumps women, non-binary and
##refusals), cov_state (Land). No survey weight, attention check or duration in the deposit.
##Dropped: the authors' open_cat category (derived), the source row number, and the
##respondent-location variables: nearest border country and distances to the closest border,
##to each of four borders, to the Berlin Wall and to the Iron Curtain (together they locate
##the respondent's home; dropped as identifying).
##N = 4,374 matches the article's Methods section (its abstract says 4,700, a footnote 4,290).
##Spot check: choice marginal means fences 0.40, national patrols 0.54, European guards 0.58,
##surveillance 0.48 (mean rating 4.9 / 5.9 / 6.0 / 5.7): fences least supported, as in the article.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "survey_dat_clean_conjoint.csv"), na.strings = c("", "NA"), encoding = "UTF-8")
stopifnot(s[, .N, id][, all(N == 8)], s[, sum(chosen), .(id, Category)][, all(V1 == 1)])
r <- fread(file.path(raw, "survey_dat_clean.csv"), select = c("id", "sex"), encoding = "UTF-8")
gl <- c("Weiblich" = "female", "M\u00e4nnlich" = "male", "nichtbin\u00e4r" = "other", "M\u00f6chte ich nicht mitteilen" = NA)
stopifnot(!anyDuplicated(r$id), all(r$sex %in% names(gl)), all(s$id %in% r$id))
s[, sex := r$sex[match(id, r$id)]]
stopifnot(s[, all((sex == "M\u00e4nnlich") == (gender == 0))])
m <- c(Fences = "Building border fences", `DE Border guards` = "Increasing national border patrols",
       `EU Border guards` = "Deploying European border guards", Surveillance = "Increasing electronic border surveillance")
g <- c(Refugees = "Regulating the flow of people fleeing a war zone", `Illeg. immig` = "Limiting illegal migration",
       Crime = "Countering drug trafficking and crime", Disease = "Blocking the spread of communicable diseases")
stopifnot(all(s$border %in% names(m)), all(s$aim %in% names(g)),
          all(s$country %in% c("Switzerland", "France", "Poland", "Czech Republic")), all(s$rati %in% 0:10))
d <- data.table(id = as.integer(s$id), task = as.integer(s$Category), choice = as.integer(s$chosen), rating = as.integer(s$rati),
                attr_measure = unname(m[s$border]), attr_country = s$country, attr_aim = unname(g[s$aim]),
                cov_border_open_close = s$border_open_close_1, cov_vote_intention = s$vote_intention,
                cov_left_right = s$left_right_1, cov_immigration_general = s$immigration_general_1,
                cov_european_integration = s$european_integration_1, cov_urban_rural = s$urban_rural,
                cov_migration_background = s$migration_background, cov_gender = unname(gl[s$sex]), cov_state = s$lan_name)
setorder(d, id, task, attr_measure, attr_country, attr_aim)
d[, profile := seq_len(.N), .(id, task)]
setcolorder(d, c("id", "task", "profile"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "lipps_2025_border_measures.csv"))
