##Political-leader conjoint (Afghanistan) from
##Bhatia, J., & Monroe, S. L. (2025). Candidate qualifications and out-group support: Evidence
##from Afghanistan. Comparative Political Studies. https://doi.org/10.1177/00104140241306960
##Replication data: Harvard Dataverse doi:10.7910/DVN/KE6VPA, CC0 1.0, no restricted files.
##File read: Afghan_Data_All.csv (full survey, wide). Wording, codes and design from the
##deposit's Qualifications_Codebook.xlsx; the reshaping logic checked against the authors'
##qualifications_conjoint_dataset.R (read as text). The article was not read.
##Usage: Rscript bhatia_2025.R <raw dir> <output dir>
##
##2,485 face-to-face respondents (one per household; Balkh, Kunduz, Sar-e-Pul; Aug 2016 - Jan
##2017; male enumerators interviewed men, female enumerators women). 3 rounds (task 1-3) of two
##leader profiles (Profile A = 1, Profile B = 2), 6 attributes, English level text as deposited:
##  attr_gender Male/Female; attr_education Madrassa / Educated to High School / University
##  Degree in Afghanistan / University Degree Abroad; attr_age 28/37/49/57/68; attr_ethnicity
##  Pashto (sic; the codebook says Pashtun) / Tajik / Uzbek / Hazara / Turkmen;
##  attr_professional_experience Business Owner / Donor Agency Employee / Military / Government
##  Employee / Private Sector Employee; attr_place_of_birth Balkh/Saripul/Kabul/Kandahar.
##  The survey ran in Dari (2,273), Pashto (210) or English (2) (cov_language); the Dari/Pashto
##  level text is not deposited.
##Outcomes (codebook question text):
##  choice: "Given a choice between these two profiles, which person would you prefer as a
##     leader?" (A/B, forced; every round answered).
##  rating: "On a scale of 1-5, where one indicates that you think the person is absolutely
##     unsuitable to represent you as a leader, and where five indicates that the person would
##     be an ideal leader for you, where would you rate the first profile (Profile A)?" and for B
##     "Using the same scale, how would you rate the second profile (Profile B)?"; 1 = absolutely
##     unsuitable .. 5 = absolutely suitable, as deposited.
##Before the conjoint each respondent heard one randomly assigned vignette (trial_prime, from the
##  source's Treatment): 1 control (facts about Afghanistan), 2 bribery, 3 nepotism, 4 insecurity;
##  codes 5 (2 respondents) and NA (4) are undocumented and kept as NA. The authors' main
##  analysis compares control and insecurity; all arms are kept here.
##Restrictions: none documented; level shares are clearly unequal for some attributes (Military
##  about half the share of other careers, Kandahar about a fifth of other birthplaces, age 28
##  less often), i.e. observed non-uniform weights.
##Covariates (source codes; labels from the codebook): cov_female (Res_Gender 2 -> 1, 1 -> 0),
##  cov_age (years), cov_ethnicity (1 Pashtun 2 Tajik 3 Uzbek 4 Turkmen 5 Hazara 6 Baloch 7
##  Other), cov_education (1 none 2 primary 3 secondary 4 post-secondary vocational 5 some
##  university 6 university degree 8 madrassa), cov_marital (1 single 2 married 3 divorced 4
##  widowed), cov_income (household income last year: 1 0-10,000 AFS, 4 10,000-50,000, 6
##  50,000-100,000, 7 100,000-250,000, 8 250,000+, 9 don't know), cov_province, cov_language,
##  cov_trust_provincial_gov / cov_trust_national_gov (1 a lot of confidence .. 5 none at all),
##  cov_intl_forces_remain (1 strongly agree .. 5 strongly disagree), cov_econ_change (1 a lot
##  better .. 5 much worse, 6 don't know).
##Dropped: village name, district, birth town/district/province/country (free-text place names:
##  PII), the "other ethnicity" text, consent/household-selection items, the leader-attribute
##  and behaviour rankings, service-access items, the vignette comprehension answers.
##N = 2,485 matches the codebook (the abstract says "over 2,400").
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "Afghan_Data_All.csv"))
stopifnot(uniqueN(x$ID) == nrow(x))
an <- c(Gender = "gender", Education = "education", Age = "age", Ethnicity = "ethnicity",
        Professional_Experience = "professional_experience", Place_of_Birth = "place_of_birth")
prime <- c("control", "bribery", "nepotism", "insecurity")
rows <- list()
for (t in 1:3) for (p in 1:2) {
  ch <- x[[paste0("RD", t, "_Con_Table_Choice")]]; stopifnot(all(ch %in% 1:2))
  d <- data.table(id = as.integer(x$ID), task = t, profile = p, choice = as.integer(ch == p),
                  rating = as.integer(x[[sprintf("RD_%d_%s_Rank", t, c("A", "B")[p])]]))
  for (v in names(an)) d[, paste0("attr_", an[[v]]) := as.character(x[[sprintf("Rd_%d_%s_%s", t, c("A", "B")[p], v)]])]
  d[, trial_prime := prime[match(x$Treatment, 1:4)]]
  rows[[length(rows) + 1]] <- d
}
d <- rbindlist(rows)
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_|^rating$")]), all(d$rating %in% 1:5))
cvd <- x[, .(id = as.integer(ID), cov_female = as.integer(Res_Gender == 2), cov_age = Res_Age, cov_ethnicity = Res_Ethnicity,
             cov_education = Res_Education, cov_marital = Marital_Status, cov_income = Income, cov_province = Province,
             cov_language = conjoint_language, cov_trust_provincial_gov = TrustProvGov, cov_trust_national_gov = TrustCentGov,
             cov_intl_forces_remain = IntForces, cov_econ_change = Econ_Change)]
d <- merge(d, cvd, by = "id")
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], nrow(d) == 14910L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bhatia_2025_afghan_leaders.csv"))
