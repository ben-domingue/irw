##Spoken administrative language factorial survey (Germany) from
##Eckhard, S., & Friedrich, L. (2022). Linguistic features of public service encounters: How
##spoken administrative language affects citizen satisfaction. Journal of Public Administration
##Research and Theory, 34(1), 122-135. https://doi.org/10.1093/jopart/muac052
##Replication data: Harvard Dataverse doi:10.7910/DVN/OXWTNE, CC0 1.0. Files read:
##"Factorial survey data.xlsx" (one sheet, codes) and Codebook.pdf (question wording, codes,
##condition definitions). "R code used for analysis.txt" read as text only.
##Usage: Rscript eckhard_2022.R <dir holding the .xlsx> <output dir>
##
##1,402 German respondents, each heard ONE audio recording of a fictional public service
##encounter (task = profile = 1; between-subjects). The 8 recordings cross two randomized
##factors (codebook "Experimental treatment conditions"):
##  attr_language: the administrative language used by the public employee, 4 levels that
##    bundle 7 linguistic features (casualness, comprehensibility, empathy, executive function,
##    motivation/intention of practices, availability, support): "Control" (none),
##    "Highly informational administrative language" (comprehensibility, executive function,
##    motivation), "Highly relational administrative language" (casualness, empathy,
##    availability, support), "Highly informational and relational administrative language"
##    (all 7). It is a 2 x 2 of informational x relational language.
##  attr_service_decision: "Negative service decision" / "Positive service decision".
##Level text is the codebook's English condition names; the audio was German and its script is
##not in the deposit. The codebook prints the same feature pattern (1 0 1 0 0 1 1 0) for both
##relational conditions; the text labels (v_119 positive, v_120 negative) and the authors' code
##(relP = v_33, relN = v_38) agree, and are used.
##Outcomes (codebook; 10-point scales, 1 = lowest, 10 = highest; stored raw):
##  rating = satisfaction ("All in all, how satisfied are you with the bureaucratic encounter?"),
##  rating_comprehensibility, rating_reification, rating_emotionality, rating_complaisance.
##Each vignette flag is 1 = presented and listened completely, 0 = presented, not listened
##completely (-77 = not presented): kept as trial_listened_complete (1,272 / 124; 6 respondents
##have -99/-66 on the flag of their one presented recording -> NA). The second attention check
##("Which of the following authorities are mentioned in the audio file?", v_126-v_134, one per
##recording) is trial_imc_authority (answer text). Missing codes 0, -66, -77, -99 -> NA.
##Covariates (codebook codes -> text): cov_gender (v_1: Female -> female, Male -> male,
##Other -> other), cov_age_group (v_125), cov_education (v_99), cov_employment (v_101),
##cov_vote_intention (v_100, vote "next Sunday"; not party identification),
##cov_attention_pass (v_136 "attention check passed" box ticked: 1 = 1; -77 kept NA since the
##codebook does not define it for this item), cov_benefits (v_102 No/Yes),
##cov_months_since_contact (v_86, open numeric answer), cov_last_encounter_satisfaction (v_87,
##1-10), cov_trust_* (v_88-v_98, 1-10).
##Dropped: free text (v_103 benefit type, v_137 agencies contacted), the first attention check's
##distractor boxes (v_78-v_83, v_135).
##Every respondent has exactly one recording and at least one outcome answer (satisfaction
##missing for 1). All second-check answers are "Social office and jobcentre".
##N: 1,402 rows in the deposit; the article was not read, so its N is unchecked.
library(readxl); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_excel(file.path(raw, "Factorial survey data.xlsx")))
stopifnot(nrow(s) == 1402)
cond <- data.table(flag = c("v_106", "v_105", "v_118", "v_107", "v_120", "v_119", "v_122", "v_121"),
  language = rep(c("Control", "Highly informational administrative language", "Highly relational administrative language",
                   "Highly informational and relational administrative language"), each = 2),
  decision = rep(c("Negative service decision", "Positive service decision"), 4),
  sat = c("v_13", "v_3", "v_18", "v_8", "v_38", "v_33", "v_48", "v_43"))
nm <- names(s)
cond[, imc := sapply(flag, function(f) nm[match(f, nm) + 1L])]
cond[, `:=`(comp = paste0("v_", as.integer(sub("v_", "", sat)) + 1L), emo = paste0("v_", as.integer(sub("v_", "", sat)) + 2L),
            reif = paste0("v_", as.integer(sub("v_", "", sat)) + 3L), compl = paste0("v_", as.integer(sub("v_", "", sat)) + 4L))]
stopifnot(all(grepl("^v_1(2[6-9]|3[0-4])$", cond$imc)), uniqueN(cond$imc) == 8)
fl <- as.matrix(s[, cond$flag, with = FALSE]); shown <- fl != -77
stopifnot(all(rowSums(shown) == 1))
k <- max.col(shown)
miss <- function(x) { x <- as.integer(x); x[x %in% c(0L, -66L, -77L, -99L)] <- NA; x }
pick <- function(col) sapply(seq_len(nrow(s)), function(i) s[[cond[[col]][k[i]]]][i])
imc_lab <- c("Fire brigade and police", "School and university", "Social office and jobcentre",
             "Federal Ministry for Economic Affairs and Energy and Federal Office of Administration")
d <- data.table(id = seq_len(nrow(s)), task = 1L, profile = 1L,
  rating = miss(pick("sat")), rating_comprehensibility = miss(pick("comp")), rating_reification = miss(pick("reif")),
  rating_emotionality = miss(pick("emo")), rating_complaisance = miss(pick("compl")),
  attr_language = cond$language[k], attr_service_decision = cond$decision[k],
  trial_listened_complete = { x <- as.integer(fl[cbind(seq_len(nrow(s)), k)]); x[x < 0] <- NA; x },
  trial_imc_authority = imc_lab[miss(pick("imc"))])
stopifnot(all(d[, .(rating, rating_comprehensibility, rating_reification, rating_emotionality, rating_complaisance)][, unlist(.SD)] %in% c(1:10, NA)))
lab <- function(x, l) l[miss(x)]
d[, cov_gender := lab(s$v_1, c("female", "male", "other"))]
d[, cov_age_group := lab(s$v_125, c("Between 18 and 29 years", "Between 30 and 39 years", "Between 40 and 49 years", "Between 50 and 59 years", "Between 60 and 80 years"))]
d[, cov_education := lab(s$v_99, c("I am currently completing my education (study, school, vocational training)", "Completed vocational training or apprenticeship",
                                     "University or college degree", "None beyond school", "Other"))]
d[, cov_employment := lab(s$v_101, c("Education (study, school, vocational training)", "Employee in the private sector",
                                       "Civil servant or employee in the public sector", "Self-employed or freelancer", "Currently unemployed", "Other"))]
d[, cov_vote_intention := lab(s$v_100, c("CDU", "SPD", "AfD", "FDP", "Die Linke", "Die Grünen", "Other"))]
d[, cov_attention_pass := fifelse(s$v_136 == 1, 1L, NA_integer_)]
d[, cov_benefits := lab(s$v_102, c("No", "Yes"))]
d[, cov_months_since_contact := suppressWarnings(as.numeric(s$v_86))][cov_months_since_contact < 0, cov_months_since_contact := NA]
d[, cov_last_encounter_satisfaction := miss(s$v_87)]
tr <- c(v_88 = "bundestag", v_89 = "constitutional_court", v_90 = "justice", v_91 = "federal_government", v_92 = "state_government",
        v_93 = "armed_forces", v_94 = "parties", v_95 = "local_administration", v_96 = "police", v_97 = "state_administration", v_98 = "federal_administration")
for (v in names(tr)) d[, (paste0("cov_trust_", tr[[v]])) := miss(s[[v]])]
d <- d[!(is.na(rating) & is.na(rating_comprehensibility) & is.na(rating_reification) & is.na(rating_emotionality) & is.na(rating_complaisance))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "eckhard_2022_administrative_language.csv"))
