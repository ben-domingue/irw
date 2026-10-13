##Online dating-profile experiment (Study 1) from
##Huber, G. A., & Malhotra, N. (2017). Political homophily in social relationships: Evidence from
##online dating behavior. Journal of Politics, 79(1), 269-283. https://doi.org/10.1086/687533
##Data are the "huber malhotra replication" files re-deposited with Easton & Holbein (2020), The
##democracy of dating: How political affiliations shape relationship formation (Journal of
##Experimental Political Science, 8(3), 260-272; doi 10.1017/XPS.2020.21), Harvard Dataverse doi:10.7910/DVN/24CXA7,
##CC0 1.0. Files read: d_surveyprofileevals.tab (profile evaluations, with the profile level ids),
##d_surveydemos.tab (respondent survey), plus the label tables age.csv, height.csv, ideo.csv, religion.csv,
##educ.csv, screenname.csv, picture.csv, profile.csv (";"-separated, id -> displayed level) and the authors'
##01_Prepare_Recode_DatingLabExperimentData.do (recode of respondent answers, outcome labels).
##Usage: Rscript huber_2017.R <dir with the files> <output dir>
##Files renamed on download: d_surveyprofileevals.tab -> evals.tab, d_surveydemos.tab -> demos.tab,
##01_Prepare_Recode_DatingLabExperimentData.do -> prep.do (the names are unchanged in the table of levels).
##
##Study 1: a lab-style online experiment. Each respondent saw 10 fictitious online-dating profiles, ONE
##PER TASK, in sequence (task = profilenumber, the order shown; profile = 1), and rated each on six
##questions. Profiles were of the sex the respondent is interested in (all evaluators of male profiles in
##the deposit are female and vice versa: the authors' data show it), and each profile combines 8 randomly
##assigned elements: screen name (60 names), picture (62 photos, file names), profile text (51 bios,
##text as shown), age, height, religion, education, political ideology. The Easton-Holbein Studies 1-5
##in the same deposit (one profile with a randomized same-party label; clean_dating2.tab,
##experiment1-5.tab) have a single manipulated factor and are NOT built.
##Outcomes (ratings, 5 or 4 point; the numeric prefix of the stored answer text; HIGHER = more favourable;
##question wordings are not in the deposit, labels are the authors' variable labels in prep.do):
##  rating_interested  "Interest in dating"  1 not at all .. 5 extremely interested
##  rating_attractive  "Attractiveness"  1 not at all .. 5 extremely attractive
##  rating_longterm    "Interest in LT Dating"  1 not at all .. 5 extremely well
##  rating_respond     "Would you respond to person?"  1 definitely not .. 4 definitely
##  rating_values      "Do they share your values?"  1 strongly disagree .. 4 strongly agree
##  rating_friends     "Would you like to be friends?"  1 not at all .. 5 extremely likely
##Rows with no answer to any of the six are omitted (profiles displayed but never evaluated: 858 of 11,250
##displayed; 71-139 individual answers are missing and left NA).
##Attribute text. Levels are the label-table entries. Age and height levels differ by profile sex (age 25,
##28, 31 for men; 22, 25, 28 for women; four heights), so attribute combinations are restricted by profile
##sex (restrictions = yes). The ideology level "--" (id 5) is the lookup-table entry; the authors call it
##"Blank"/"No ideo." (a profile that lists no politics); it is stored as "--" and not as "(not shown)"
##because the site field was apparently displayed with a dash (not verifiable). Level shares are unequal
##(level_weights observed). Attribute order not documented.
##Heights are stored as e.g. 5'9" (the lookup file writes the inch mark as \" and the backslash is removed).
##Covariates: cov_gender (0 Female / 1 Male in the authors' recode), cov_birth_year, cov_education (text of
##the authors' education recode), cov_ideology (Liberal/Moderate/Conservative, authors' recode), cov_race,
##cov_religion (answer text in the authors' recode). Three evaluators have no survey record: NA.
##The authors' analysis keeps respondents who rated all 10 profiles, report an ideology and a birth year, and
##are <= 35 (their paper's N is not checked here); this table keeps every respondent with an evaluation, 1,092
##of whom 1,018 rated all 10 profiles. Respondent ids are the study's internal userid, re-keyed to integers.
##Dropped: free text (postWhyConduct, postLearnFromProfile, activity answers), timestamps, derived dummies.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rd <- function(f) fread(file.path(raw, f), sep = ";", encoding = "UTF-8")
e <- fread(file.path(raw, "evals.tab"), sep = "\t"); dm <- fread(file.path(raw, "demos.tab"), sep = "\t")
lv <- function(f, col) { x <- rd(f); setNames(as.character(x[[col]]), x$id) }
age <- lv("age.csv", "age"); hgt <- lv("height.csv", "height"); hgt[] <- gsub("\\", "", hgt, fixed = TRUE); ideo <- lv("ideo.csv", "ideo")
rel <- lv("religion.csv", "religion"); edu <- lv("educ.csv", "educ")
sn <- lv("screenname.csv", "screenname"); pic <- lv("picture.csv", "picture"); prof <- lv("profile.csv", "profile")
num <- function(x) as.integer(substr(x, 1, 1))
e <- e[!(is.na(O_Interested) & is.na(O_Attractive) & is.na(O_LongTerm) & is.na(O_Respond) & is.na(O_Values) & is.na(O_Friends))]
stopifnot(!anyNA(e[, .(screennameid, pictureid, profileid, ageid, heightid, religionid, educid, ideoid)]))
d <- e[, .(id = userid, task = as.integer(profilenumber), profile = 1L,
  rating_interested = num(O_Interested), rating_attractive = num(O_Attractive), rating_longterm = num(O_LongTerm),
  rating_respond = num(O_Respond), rating_values = num(O_Values), rating_friends = num(O_Friends),
  attr_screenname = sn[as.character(screennameid)], attr_picture = pic[as.character(pictureid)],
  attr_profile_text = prof[as.character(profileid)], attr_age = age[as.character(ageid)],
  attr_height = hgt[as.character(heightid)], attr_religion = rel[as.character(religionid)],
  attr_education = edu[as.character(educid)], attr_ideology = ideo[as.character(ideoid)])]
stopifnot(!anyNA(d[, .(attr_screenname, attr_picture, attr_profile_text, attr_age, attr_height, attr_religion, attr_education, attr_ideology)]))
edlab <- c("high school", "some college", "college", "some grad school", "grad school")
rlab <- c("Buddhist", "Catholic", "Hindu", "Jewish", "Muslim", "None", "Other", "Protestant")
racelab <- c("AsianPI", "Black", "Hispanic", "NativeAmerican", "Other", "White")
ilab <- c("Liberal", "Moderate", "Conservative")
cv <- dm[, .(id = userid, cov_gender = c("female", "male")[gender + 1L], cov_birth_year = as.integer(preYearOfBirth),
  cov_education = edlab[education + 1L], cov_ideology = ilab[ideology + 1L], cov_race = racelab[race + 1L],
  cov_religion = rlab[religion + 1L])]
d <- merge(d, cv, by = "id", all.x = TRUE)
d[, id := as.integer(factor(id))]
setorder(d, id, task, profile)
stopifnot(!anyDuplicated(d[, .(id, task)]), uniqueN(d$id) == 1092)
fwrite(d, file.path(out, "huber_2017_dating_profiles.csv"))
