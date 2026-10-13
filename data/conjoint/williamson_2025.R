##Military-aid vignette experiments (United States) from
##Williamson, S. (2025). Who gets the guns? How democratic values and security threats affect
##American attitudes toward military aid. Journal of Conflict Resolution.
##https://doi.org/10.1177/00220027251388634
##Replication data: Harvard Dataverse doi:10.7910/DVN/ARAKLD, CC0 1.0 (zip "Williamson - JCR -
##Replication.zip"). Files read: YouGov_2017_Original_Data.dta (Stata value labels),
##Bilendi_2024_Original_Data.csv; "Cleaning - Williamson - JCR.do" and README read as text.
##Usage: Rscript williamson_2025.R <dir holding the unzipped files> <output dir>
##
##The paper reports four experiments (YouGov 2016, YouGov 2017, Lucid 2019, Bilendi 2024). Two
##tables are built (different attribute sets, samples and fieldings = separate tables):
##
##(1) williamson_2025_aid_yougov2017: YouGov 2017, 1,000 respondents (the file has no
##respondent id: id = row number), ONE text vignette each (task = profile = 1, inferred),
##about a country whose military the US might aid, randomized in four attributes (level text =
##the .dta value labels of SRW101_*):
##  attr_region   Africa / the Middle East / Asia
##  attr_cost     $10 million / $100 million / $1 billion   (not used in the authors' cleaning
##                code, but randomized in the file)
##  attr_rights   government "is democratic and has a reputation for respecting human rights" /
##                "is authoritarian and has a reputation for violating human rights"
##  attr_security "There are no direct threats to US security in this country." / "The country's
##                military is currently fighting a terrorist group that has attacked the United
##                States and killed dozens of American citizens." / "... killed hundreds of
##                American citizens." The .dta labels cut the last two at 120 characters
##                ("killed dozens of", "killed hundreds o"); the endings are completed from the
##                Bilendi 2024 wording and by analogy ("hundreds of American citizens.").
##  trial_rights_security_order (SRW101_order): whether the rights or the security statement came
##                first. Recorded because the order was randomized.
##Outcome rating = SRW101 "Support for Military Aid" (variable label; the question stem is not in
##the deposit): 1 Strongly agree, 2 Agree, 3 Somewhat agree, 4 Neither, 5 Somewhat disagree,
##6 Disagree, 7 Strongly disagree. LOWER = more favourable (raw, not reversed; the authors
##reverse it as 8 - SRW101). One respondent has no answer and is dropped (999 rows).
##Other covariates (value labels): cov_gender (Male/Female), cov_birth_year, cov_education (educ),
##cov_race, cov_family_income (faminc text), cov_party_id (pid3 text, "Not sure" kept as text),
##cov_party_id7 (pid7 text), cov_ideology (ideo5), cov_political_interest (newsint),
##cov_internationalist (fp_orientation, 6-point agree/disagree with an "Internationalist Indicator",
##text), cov_dem_promotion (SRW102 "Democracy Promotion Indicator", 6-point text), cov_state.
##Dropped: race_other, employment and marital items, religion and church items, timestamps.
##No survey weight in the file. Restrictions: none documented; all combinations occur.
##
##(2) williamson_2025_aid_bilendi2024: Bilendi online panel, October 2024, 3,958 respondents
##who completed the vignette and the outcome (see sample), ONE text vignette each (id = row
##number; task = profile = 1, inferred). Three attributes:
##  attr_region   Africa / Asia / the Middle East (region_treatment)
##  attr_governance  6 statements (governance_treatment): "The country's government is
##                democratic." / "... has a reputation for respecting human rights." / "... is
##                democratic and has a reputation for respecting human rights." / "... is
##                authoritarian." / "... has a reputation for violating human rights." / "...
##                is authoritarian and has a reputation for violating human rights."
##  attr_security "There are no direct threats to US security in this country." / "The country's
##                military is currently fighting a terrorist group that has attacked the United
##                States and killed dozens of American citizens."
##Sample: the file has 14,409 rows, 4,071 of which carry the treatment (the rest are blank on all
##three treatment columns and on aid_support; no source says why, they are dropped). Of those 4,071 (all passed the attention check), the authors' cleaning code
##drops reCAPTCHA scores below 0.5 (89 rows), leaving 3,982; 24 of them have no outcome -> 3,958.
##Outcome rating = aid_support (question stem not in the deposit; options Strongly agree ..
##Strongly disagree), stored as the authors' aid_ordinal coding 1 Strongly disagree, 2 Disagree,
##3 Somewhat disagree, 4 Neither agree nor disagree, 5 Somewhat agree, 6 Agree, 7 Strongly agree.
##HIGHER = more favourable (the opposite direction from table 1; the 2024 file stores text only).
##Covariates: cov_gender (Male/Female; Non-binary -> other; "Prefer not to say" -> NA),
##cov_age (years, as typed; kept only 18-99), cov_education (text), cov_race, cov_income (text),
##cov_party_id (partisanship, text, 5 categories + Independent/Something else),
##cov_ideology (text), cov_state, cov_duration_sec (Duration (in seconds)). Dropped: dates,
##reCAPTCHA score, attention item, vote2024, gaza_follow_closely, other foreign-policy items.
##No survey weight. Restrictions: none documented; level shares near-uniform.
##
##NOT built: YouGov 2016 and Lucid 2019 (treatments stored as numeric codes with no value labels
##and no vignette text in the deposit); Lucid 2021 and 2023 (no experiment, descriptive items only).
##N: no comparison with the paper (not retrieved beyond the abstract).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
## ---- (1) YouGov 2017
k <- read_dta(file.path(raw, "YouGov_2017_Original_Data.dta"))
lab <- function(v) as.character(as_factor(k[[v]], levels = "labels"))
stopifnot(nrow(k) == 1000)
sec <- lab("SRW101_Security")
sec <- ifelse(sec == "There are no direct threats to US security in this country.", sec,
       ifelse(grepl("killed dozens of$", sec), "The country's military is currently fighting a terrorist group that has attacked the United States and killed dozens of American citizens.",
       ifelse(grepl("killed hundreds o$", sec), "The country's military is currently fighting a terrorist group that has attacked the United States and killed hundreds of American citizens.", NA)))
d <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L, rating = as.integer(k$SRW101),
  attr_region = lab("SRW101_Region"), attr_cost = lab("SRW101_Cost"), attr_rights = lab("SRW101_Rights"), attr_security = sec,
  trial_rights_security_order = lab("SRW101_order"),
  cov_gender = c("male", "female")[as.integer(k$gender)], cov_birth_year = as.integer(k$birthyr),
  cov_education = lab("educ"), cov_race = lab("race"), cov_family_income = lab("faminc"),
  cov_party_id = lab("pid3"), cov_party_id7 = lab("pid7"), cov_ideology = lab("ideo5"),
  cov_political_interest = lab("newsint"), cov_internationalist = lab("fp_orientation"),
  cov_dem_promotion = lab("SRW102"), cov_state = lab("inputstate"))
stopifnot(!anyNA(d[, .(attr_region, attr_cost, attr_rights, attr_security)]))
d <- d[!is.na(rating)]; stopifnot(nrow(d) == 999)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "williamson_2025_aid_yougov2017.csv"))
## ---- (2) Bilendi 2024
b <- fread(file.path(raw, "Bilendi_2024_Original_Data.csv"), encoding = "UTF-8")
b <- b[governance_treatment != ""]
stopifnot(nrow(b) == 4071, all(b$attention == "Trade war between US and China"))
b <- b[Q_RecaptchaScore >= 0.5]; stopifnot(nrow(b) == 3982)
rt <- c("Strongly disagree" = 1L, "Disagree" = 2L, "Somewhat disagree" = 3L, "Neither agree nor disagree" = 4L,
        "Somewhat agree" = 5L, "Agree" = 6L, "Strongly agree" = 7L)
b <- b[aid_support != ""]; stopifnot(nrow(b) == 3958, all(b$aid_support %in% names(rt)))
g <- data.table(id = seq_len(nrow(b)), task = 1L, profile = 1L, rating = unname(rt[b$aid_support]),
  attr_region = b$region_treatment, attr_governance = b$governance_treatment, attr_security = b$security_treatment,
  cov_gender = c(Male = "male", Female = "female", "Non-binary" = "other")[b$Gender],
  cov_age = ifelse(b$Age >= 18 & b$Age <= 99, as.integer(b$Age), NA_integer_),
  cov_education = b$education, cov_race = b$race, cov_income = b$Income, cov_party_id = b$partisanship,
  cov_ideology = b$ideology, cov_state = b$State, cov_duration_sec = as.integer(b[["Duration (in seconds)"]]))
for (cc in c("cov_education", "cov_race", "cov_income", "cov_party_id", "cov_ideology", "cov_state")) g[get(cc) == "", (cc) := NA]
g[, cov_gender := unname(cov_gender)]
stopifnot(!anyNA(g[, .(attr_region, attr_governance, attr_security)]), uniqueN(g$attr_governance) == 6)
cat("Bilendi table levels:", uniqueN(g$attr_region), uniqueN(g$attr_governance), uniqueN(g$attr_security), "\n")
setorder(g, id, task, profile)
fwrite(g, file.path(out, "williamson_2025_aid_bilendi2024.csv"))
