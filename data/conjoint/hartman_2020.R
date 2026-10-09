##Refugee-hosting conjoint (Liberia) from
##Hartman, A. C., & Morse, B. S. (2020). Violence, empathy and altruism: Evidence from the Ivorian
##refugee crisis in Liberia. British Journal of Political Science, 50(2).
##https://doi.org/10.1017/S0007123417000655
##Replication data: Harvard Dataverse doi:10.7910/DVN/X1TGCJ, CC0 1.0. Files read:
##conjoint_analysis.tab (one row per respondent x refugee profile), Codebook.tab, ReadMe.txt; the
##authors' Hartman&Morse2017.r was read as text. Design text from the authors' manuscript (UCL
##Discovery eprint 10059736, "Hartman_Manuscript_revision.pdf"), section "Conjoint experiment".
##Usage: Rscript hartman_2020.R <dir holding conjoint_analysis.tab> <output dir>
##
##Liberian adults in host communities in eastern Liberia (face-to-face survey; the manuscript says
##i in 1..1230, the deposit holds 1,091). Respondents imagined a new refugee crisis with more refugees
##than the community could host and, in 3 rounds, chose one of two hypothetical refugee families.
##Because about half the respondents were illiterate, attributes were shown as PICTOGRAPHS
##(presentation = image). Levels are the manuscript's Table 1 labels (the pictographs themselves are
##not deposited), mapped from the deposit's 0/1 codes (Codebook.tab labels):
##  attr_gender_hh  woman_hh 1 "Female" / 0 "Male"         (gender of household head)
##  attr_ethnicity  coethnic 1 "Co-Ethnic" / 0 "Not Co-Ethnic"  (RELATIVE to the respondent's group)
##  attr_religion   muslim   1 "Muslim" / 0 "Christian"
##  attr_occupation farmer   1 "Farmer" / 0 "Not Farmer"
##  attr_food       hunger   1 "Do not have food" / 0 "Have food"
##The authors' derived `coreligious` is dropped (derivable from attr_religion and cov_muslim).
##Restriction (manuscript): co-ethnic but not co-religious profiles were excluded for respondents
##from ethnic groups predominantly of one religion (~30% of the sample; e.g. no co-ethnic Muslim
##family for Grebo respondents).
##task/profile are NOT in the file: each respondent has 6 consecutive rows; consecutive row pairs are
##INFERRED to be the 3 rounds (exactly one family chosen in every pair of the 1,089 six-row
##respondents; stopifnot). Dropped: 2 respondents with 5 rows (their pairs do not align), and 4 tasks
##(3 respondents) with a missing attribute (blank in source): 1,089 respondents, 6,526 rows.
##choice: "chose to host" this family (paraphrase; forced choice of one of two, no opt-out).
##trial_prime: respondent's arm (source weprime): 1 = the violence-experience module came BEFORE the
##conjoint (empathetic prime), 0 = after. Covariates: cov_gender (male 1 -> "male", 0 -> "female"),
##cov_muslim (respondent Muslim, 0/1), cov_warvict (number of violent acts experienced, the
##authors' index, 0-6). respid (town-coded survey id) re-keyed to 1..N.
##Spot-check: authors' m1_cnj (no-prime arm), coreligious coefficient ~0.15 ("15 per cent").
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "conjoint_analysis.tab"))
s <- s[, .(respid, decision, coethnic, farmer, hunger, woman_hh, muslim, coreligious, weprime, male, Muslim, warvict)]
stopifnot(uniqueN(s$respid) == 1091)
s <- s[respid %in% s[, .N, respid][N == 6, respid]]
s[, r := seq_len(.N), respid][, task := (r + 1L) %/% 2L][, profile := 2L - r %% 2L]
bad <- s[, sum(decision), .(respid, task)][V1 != 1, unique(respid)]
s <- s[!respid %in% bad]
na <- s[, .(m = any(is.na(farmer) | is.na(hunger) | is.na(muslim))), .(respid, task)][m == TRUE]
s <- s[!na, on = .(respid, task)]
cat("dropped respondents:", 1091 - uniqueN(s$respid), " NA tasks:", nrow(na), "\n")
lab <- function(x, one, zero) fifelse(x == 1, one, zero)
d <- s[, .(id = as.integer(factor(respid)), task, profile, choice = as.integer(decision),
           attr_gender_hh = lab(woman_hh, "Female", "Male"), attr_ethnicity = lab(coethnic, "Co-Ethnic", "Not Co-Ethnic"),
           attr_religion = lab(muslim, "Muslim", "Christian"), attr_occupation = lab(farmer, "Farmer", "Not Farmer"),
           attr_food = lab(hunger, "Do not have food", "Have food"), trial_prime = as.integer(weprime),
           cov_gender = lab(male, "male", "female"), cov_muslim = as.integer(Muslim), cov_warvict = warvict, coreligious)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
m <- lm(choice ~ attr_gender_hh + attr_occupation + attr_food + coreligious + attr_ethnicity, d[trial_prime == 0])
print(round(coef(m), 3))
d[, coreligious := NULL]
setorder(d, id, task, profile)
cat("rows", nrow(d), "respondents", uniqueN(d$id), "\n")
fwrite(d, file.path(out, "hartman_2020_refugee_hosting.csv"))
