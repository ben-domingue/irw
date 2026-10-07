##Citizenship-applicant conjoint (UK) from
##Donnaloja, V. (2022). British nationals' preferences over who gets to be a citizen
##according to a choice-based conjoint experiment. European Sociological Review, 38(2),
##202-218. https://doi.org/10.1093/esr/jcab034
##Replication data: Harvard Dataverse doi:10.7910/DVN/NYXQMG, CC0 1.0, no restricted files.
##Files read: dataset.dta (Dataverse "original format" download) and Codebook.xlsx (SPSS
##variable view: value labels for every attribute and covariate code). Vignette template,
##instructions and randomization restrictions are from the article (open access, LSE
##eprint 111896).
##Usage: Rscript donnaloja_2022.R <dir holding dataset.dta> <output dir>
##
##YouGov UK Omnibus, fielded 29-30 October 2018, 1,648 adults. Each respondent saw 5 pairs
##(task 1-5; Person A = profile 1, Person B = profile 2) of naturalisation applicants
##written as a sentence vignette: "This [woman] has lived in the UK for [4 years] [and has a
##British parent]. [She] is originally from [Somalia]. [She] [is a practising Christian].
##[She] has a [good] command of spoken English and [works as a language teacher]." (the
##refugee clause attaches to the origin sentence when shown). Introduction: "The next few
##pages will show you 5 pairs of profiles of working age (18-65) people who were not born
##in the UK and could submit applications to naturalise as British citizens. On the
##assumption that there is a limited number of naturalisations that can be granted every
##year, please choose to whom you want to grant citizenship. You may choose ONE, BOTH or
##NEITHER in each pair."
##Outcome: rating = 1 "Should be granted British citizenship", 0 "Should not be granted
##British citizenship" (source Qscreen_<task>_<1|2>: 1 = grant, 2 = not). Each profile is
##judged on its own (one, both or neither), so this is a per-profile 0/1 rating, higher =
##granted; there is no choice column. No missing answers.
##Attributes (attr_*, the vignette fragments as displayed, from the codebook labels):
##gender (man/woman; the pronoun He/She always agrees and is dropped), residency (4/6/10/20
##years), ancestry ("and has a British parent" / "and has a British grandparent"; "(no ancestry
##clause)" = the article's "Neither" level; source code 3, unlabelled),
##origin (10 countries), religion, english ("a basic"/"a good"/"an excellent"), occupation
##(9 levels), refugee ("and did not enter the country as a refugee" / "and entered the
##country as a refugee"; "(no refugee clause)" = clause not shown, source code 3: by design only for
##Pakistan, Nigeria, Syria and Somalia).
##Randomization restrictions (article Table 3): refugee clause only for Pakistan, Nigeria,
##Syria, Somalia; Ireland and Australia always "an excellent" English; Poland never Muslim.
##Attribute order fixed (sentence template).
##Covariates keep the source codes; labels are in Codebook.xlsx: cov_female (1 = female;
##source Gender 2), cov_age (years), cov_region_gor (1-12), cov_social_grade (1 AB, 2 C1,
##3 C2, 4 DE), cov_vote2017 (1 Con, 2 Lab, 3 Lib Dem, 4 UKIP, 5 Green, 6 Other, 7 Don't
##know/didn't vote), cov_euref (1 Remain, 2 Leave, 3 did not vote, 4 can't remember),
##cov_citizenship (1 British only, 2 British and another, 3 another country only),
##cov_work_industry (1-21), cov_education (1-20), cov_household_income (1-17),
##cov_personal_income (1-16), cov_marital (1-8), cov_ethnicity (1-19), cov_survey_weight
##(YouGov design weight). Dropped: response date, constant columns ns/total, the authors'
##Region recode. id is the source ID (1..1648, not a platform ID).
##Counts: the deposit holds all 1,648 respondents; the article analyses the 1,597 British
##citizens (cov_citizenship 1 or 2) = 15,970 profiles. Table 1's level counts and the 73%
##grant rate are reproduced on that subset (see spot check in the processing note).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "dataset.dta"))
num <- function(x) as.numeric(zap_labels(x))
fixed <- list(gender = "genderage", residency = "residency", ancestry = "Britparentgrandparent",
              origin = "origincountry", religion = "religion", english = "English",
              occupation = "incomeoccupation", refugee = "refugee")
## value labels copied from Codebook.xlsx (the .dta carries none); code 3 of ancestry and
## refugee is labelled "3" there, i.e. no clause shown
labs <- list(gender = c("man", "woman"), residency = c("4 years", "6 years", "10 years", "20 years"),
             ancestry = c("and has a British parent", "and has a British grandparent", "(no ancestry clause)"),
             origin = c("Poland", "Germany", "Italy", "India", "Pakistan", "Nigeria", "Ireland", "Australia", "Syria", "Somalia"),
             religion = c("is a practising Christian", "is a practising Muslim", "does not practise any religion"),
             english = c("a basic", "a good", "an excellent"),
             occupation = c("works as a corporate manager", "works as a doctor", "works as an IT professional",
                            "works as a language teacher", "works as an admin worker", "works on a farm",
                            "works as a cleaner", "is unemployed", "is a stay at home parent"),
             refugee = c("and did not enter the country as a refugee", "and entered the country as a refugee", "(no refugee clause)"))
d <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:2, function(p) {
  ab <- c("A", "B")[p]
  x <- data.table(id = as.integer(k$ID), task = t, profile = p,
                  rating = c(`1` = 1L, `2` = 0L)[as.character(num(k[[sprintf("Qscreen_%d_%d", t, p)]]))])
  for (n in names(fixed)) {
    v <- k[[sprintf("%s%s_screen%d", fixed[[n]], ab, t)]]
    stopifnot(all(num(v) %in% seq_along(labs[[n]])))
    tx <- labs[[n]][num(v)]
    x[, paste0("attr_", n) := tx]
  }
  x
}))))
stopifnot(!anyNA(d$rating), nrow(d) == 1648 * 10)
## restrictions hold
stopifnot(d[attr_refugee != "(no refugee clause)", all(attr_origin %in% c("Pakistan", "Nigeria", "Syria", "Somalia"))],
          d[attr_refugee == "(no refugee clause)", all(!attr_origin %in% c("Pakistan", "Nigeria", "Syria", "Somalia"))],
          d[attr_origin %in% c("Ireland", "Australia"), all(attr_english == "an excellent")],
          d[attr_origin == "Poland", all(attr_religion != "is a practising Muslim")])
## pronoun agrees with gender
for (t in 1:5) for (ab in c("A", "B")) stopifnot(all(num(k[[sprintf("genderage%s_screen%d", ab, t)]]) ==
                                                     num(k[[sprintf("gendernoun%s_screen%d", ab, t)]])))
cv <- data.table(id = as.integer(k$ID), cov_female = as.integer(num(k$Gender) == 2), cov_age = as.integer(num(k$Age)),
                 cov_region_gor = as.integer(num(k$Region_GOR)), cov_social_grade = as.integer(num(k$Socialgrade)),
                 cov_vote2017 = as.integer(num(k$Vote2017)), cov_euref = as.integer(num(k$Pastvote_EURef)),
                 cov_citizenship = as.integer(num(k$Citizenship)), cov_work_industry = as.integer(num(k$Work_industry)),
                 cov_education = as.integer(num(k$Education_level)),
                 cov_household_income = as.integer(num(k$Gross_household_income)),
                 cov_personal_income = as.integer(num(k$Gross_personal_income)),
                 cov_marital = as.integer(num(k$Marital)), cov_ethnicity = as.integer(num(k$Ethnicity)),
                 cov_survey_weight = num(k$Weight))
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "donnaloja_2022_citizenship.csv"))
