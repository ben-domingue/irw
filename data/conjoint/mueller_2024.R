##COVID-19 decision-making conjoint in six countries from
##Mueller, S., & Bundi, P. (2024). Multilingual federalism in times of crisis. Regional & Federal
##Studies, 35(4), 631-665. https://doi.org/10.1080/13597566.2024.2314081 (open access, CC BY;
##read from the Serval repository copy).
##Replication data: Harvard Dataverse doi:10.7910/DVN/2QS1TA, CC0 1.0. Files read: RFSdata.rds (one
##data.frame, 60,792 rows), RFSreplication.R (as text).
##Usage: Rscript mueller_2024.R <dir holding RFSdata.rds> <output dir>
##
##7,599 respondents (Qualtrics online panels, winter 2020/21, quotas on age, gender, residence,
##education) in Australia, Belgium, Canada, France, Switzerland and the USA; Table 2 gives 7,599
##(matches). "Each respondent was presented four times with two scenarios of how COVID-19
##responses should be taken ... respondents had to indicate which of the two scenarios they
##preferred" (forced choice, no opt-out; no rating asked, note 6). Each scenario was "a random
##combination of characteristics; the order of the five dimensions remained constant".
##The deposit has NO task or profile column: every respondent has exactly 8 rows and each
##consecutive row pair has exactly one chosen scenario (checked), so task = pair index and
##profile = position within the pair are INFERRED from row order (which scenario was shown first
##on screen is not recorded).
##One table: the authors run the same experiment in all countries and compare groups (cregg by
##country / mother tongue); cov_country and cov_mother_tongue identify the samples.
##Attribute text: the article's Table 1 English wording (the survey ran in Dutch, English, French,
##German; translations not deposited), mapped from the authors' short labels in the .rds:
##  attr_level (govt): central -> "Decision made at the {federal|national} level";
##    central+regional -> "... level, but each {X} can be more restrictive"; regions together ->
##    "{Xs} coordinate with each other and decide together"; regions alone -> "Each {X} decides for
##    itself"; local govt -> "Each {municipality|county or city} decides for itself", with the
##    country words of the Table 1 note: national (France) / federal (others); X = State (USA,
##    Australia), province (Canada), community and region (Belgium), canton (Switzerland), region
##    (France); county or city (USA) / municipality (others). The bracketed order in Table 1 is read
##    as USA-Australia / Canada / Belgium / Switzerland / France, following the note.
##  attr_scientists (experts): No / Some / Strong influence.
##  attr_citizens: "No influence" / "Some influence (consultative citizens' forums)".
##  attr_stakeholders (employers, trade unions, etc.): No / Some / Strong influence.
##  attr_transparency: "None" / "Some (decision is explained)" / "Full (decision is explained and
##    all data publicly available)".
##Attribute order fixed (article: "We refrained from randomizing the order of dimensions"; Table 1
##lists level, scientists, citizens, stakeholders, transparency; on-screen order per Figure A1, not
##read). Randomization restrictions and level probabilities not documented.
##Covariates (the authors' recoded labels as stored, English): cov_country, cov_mother_tongue
##(Language), cov_language_group (group), cov_region (Region), cov_age_group (Age), cov_gender
##(Gender female/male; 79 respondents NA), cov_education_level (Education, 3 harmonized levels; not the source
##question's own categories), cov_place, cov_life (subjective income), cov_religion,
##cov_leftright_band (LeftRight2, 3 bands of a 0-10 scale), cov_attention_pass (CovidTest: pass = 1,
##fail = 0; "correctly indicated that to contain the Covid-19 virus, one should avoid crowded places";
##the article's main results keep failers). Dropped: the Qualtrics ResponseId (re-keyed),
##Affected1-8_rec (undocumented 0/1 recodes), matching (authors' derived grouping). No weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
m <- as.data.table(readRDS(file.path(raw, "RFSdata.rds")))
for (v in names(m)) if (is.factor(m[[v]])) m[, (v) := as.character(get(v))]
stopifnot(nrow(m) == 60792L, uniqueN(m$id) == 7599L, m[, .N, id][, all(N == 8)], !anyNA(m$Y))
m[, r := seq_len(.N), id][, task := (r + 1L) %/% 2L][, profile := 2L - r %% 2L]
stopifnot(m[, .(sum(Y), .N), .(id, task)][, all(V1 == 1 & N == 2)], m[, uniqueN(Country), id][, all(V1 == 1)])
cw <- data.table(Country = c("USA", "Australia", "Canada", "Belgium", "Switzerland", "France"),
                 lev = c("federal", "federal", "federal", "federal", "federal", "national"),
                 X = c("State", "State", "province", "community and region", "canton", "region"),
                 Xs = c("States", "States", "Provinces", "Communities and regions", "Cantons", "Regions"),
                 loc = c("county or city", "municipality", "municipality", "municipality", "municipality", "municipality"))
m <- merge(m, cw, by = "Country", sort = FALSE)
m[, attr_level := fcase(govt == "central", paste0("Decision made at the ", lev, " level"),
                        govt == "central+regional", paste0("Decision made at the ", lev, " level, but each ", X, " can be more restrictive"),
                        govt == "regions together", paste0(Xs, " coordinate with each other and decide together"),
                        govt == "regions alone", paste0("Each ", X, " decides for itself"),
                        govt == "local govt", paste0("Each ", loc, " decides for itself"))]
inf <- c(no = "No influence", some = "Some influence", strong = "Strong influence")
m[, attr_scientists := inf[sub(" .*", "", experts)]][, attr_stakeholders := inf[sub(" .*", "", stakeholders)]]
m[, attr_citizens := c("no citizen influence" = "No influence", "some citizen influence" = "Some influence (consultative citizens' forums)")[citizens]]
m[, attr_transparency := c("no transparency" = "None", "partial transparency" = "Some (decision is explained)",
                           "total transparency" = "Full (decision is explained and all data publicly available)")[transparency]]
for (v in grep("^attr_", names(m), value = TRUE)) stopifnot(!anyNA(m[[v]]))
d <- m[, .(id = match(id, sort(unique(id))), task, profile, choice = as.integer(Y),
           attr_level, attr_scientists, attr_citizens, attr_stakeholders, attr_transparency,
           cov_country = Country, cov_mother_tongue = Language, cov_language_group = group, cov_region = Region,
           cov_age_group = Age, cov_gender = Gender, cov_education_level = Education, cov_place = Place, cov_life = Life,
           cov_religion = Religion, cov_leftright_band = LeftRight2,
           cov_attention_pass = fifelse(trimws(CovidTest) == "pass", 1L, fifelse(trimws(CovidTest) == "fail", 0L, NA_integer_)))]
stopifnot(all(d$cov_gender %in% c("female", "male", NA)), !anyNA(d$cov_attention_pass))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mueller_2024_covid_governance.csv"))
