##Afghan-refugee conjoint (Pakistan) from
##Malik, M., Siddiqui, N., & Zhou, Y.-Y. (2025). How does coethnicity with refugees shape
##their reception? Evidence from Afghan refugees in Pakistan. SocArXiv preprint
##(https://doi.org/10.31235/osf.io/56drf_v1); forthcoming, The Journal of Politics.
##Replication data: Harvard Dataverse doi:10.7910/DVN/CWGNZR, CC0 1.0, no restricted files.
##File read: "Full Survey Data Set N 3500 aug 31.dta", from
##MalikSiddiquiZhou_JOP_ReplicationPackage.zip. Level labels and question numbers from the
##package's Codebook.pdf; question wording and design from the preprint (Table 1). The
##authors' .Rmd was read as text (not run).
##Usage: Rscript malik_2025.R <dir holding the .dta> <output dir>
##
##Face-to-face survey (Gallup Pakistan, May-Aug 2024) of 3,500 Pakistani citizens in the 15
##largest Afghan-refugee-hosting districts; interviews in Urdu or Pashto, profiles shown on a
##screen and read aloud. 3 rounds (task 1-3) of 2 profiles (profile 1 = Profile_1).
##Outcome, forced choice: "Now I will show you two profiles of Afghan refugees. These two
##Afghan refugees are not registered in Pakistan, but they both want to stay here. After I
##tell you some details about each of these two Afghan refugees, I want you to pick which one
##you would prefer to stay in Pakistan." choice = 1 for the profile picked. No opt-out was
##offered, but respondents could refuse/say don't know (source conj<r> = 0 "Skip/DK/NR"):
##those tasks have no outcome and are omitted (841, 935, 986 tasks in rounds 1-3); 714
##respondents skipped all three and are absent, leaving 2,786 respondents (the article
##reports 714 = 20.4% skipping; the authors also drop skipped tasks).
##Attributes (4; row order randomized per the preprint, not recorded):
##  attr_ethnicity Pashtun (p = .5) / Tajik / Uzbek (.25 each; source label "Uzbik",
##    spelled Uzbek as the authors do);
##  attr_gender Male / Female;
##  attr_household_head_occupation: "Daily Wage Laborer", "Small Business Owner/Trader",
##    "Agricultural Farm Worker", or the RESPONDENT'S OWN household head's occupation piped
##    in (source codes 1-13, 997 = the respondent's hh_occupation answer, verified equal to it
##    in all but 3 of 4,988 such profiles). Text is the codebook's English answer label (e.g.
##    "Small Business Owners", "Skilled labor"); the authors recode all piped levels to
##    "Household Head Occupation" and "Small Business Owners" to "Small Business
##    Owner/Trader". 997 is "Others Specify:____" (the actual answer text is not deposited).
##  attr_years_in_pakistan "3 years" / "15 years" / "40 years" (time the family has resided
##    in Pakistan).
##Labels are the English codebook labels; respondents heard Urdu or Pashto.
##Covariates (codebook codes; 998/999 refused/don't know set missing): cov_female (1 =
##female), cov_age, cov_ethnicity (e1: 1 Urdu Speaking Muhajir 2 Punjabi 3 Sindhi 4 Balochi
##5 Pashtun 6 Others 7 Hindkon/Hazarewal 8 Hazarewal 9 Siraiki), cov_province and
##cov_district (names), cov_urban (1 = urban), cov_interview_pashto (1 = Pashto),
##cov_hh_occupation (S12q8 code), cov_income (1-7 monthly bands), cov_education (edu_years
##1-9 code), cov_religion (1 Islam 2 Christianity 3 Hindu 4 Others), cov_sect (1 Shia 2 Sunni
##3 Aga Khani 4 Deobandi 5 Barelvi 6 Other), cov_radio_arm (lab_exp, the separate radio-
##message experiment arm; the two experiments' order was randomized). No survey weight.
##Dropped: GPS latitude/longitude, interview duration, Gallup id_no (re-keyed to 1..n in
##file order), enumerator guess of ethnicity, all attitude/policy outcomes.
##Spot check vs the authors' Figure 1 marginal means (knitted .html): Pashtun - Uzbek =
##0.096 reproduces exactly (Pashtun respondents, e1 = 5: 0.128, exact); Pashtun - Tajik is
##0.090 here vs 0.092 reported (Pashtun respondents 0.109 vs 0.111). Not reconciled.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "Full Survey Data Set N 3500 aug 31.dta"))
stopifnot(nrow(k) == 3500, !anyDuplicated(k$id_no))
lab <- function(x) { y <- as.character(as_factor(x, levels = "labels")); stopifnot(!anyNA(y)); y }
num <- function(x) { y <- as.integer(zap_labels(x)); y[y %in% c(997L, 998L, 999L)] <- NA; y }
k$rid <- seq_len(nrow(k))
cv <- data.table(id = k$rid, cov_female = as.integer(k$gender == 2), cov_age = as.integer(k$age),
                 cov_ethnicity = num(k$e1), cov_province = as.character(k$province), cov_district = as.character(k$district),
                 cov_urban = as.integer(k$urban_rural == 1), cov_interview_pashto = as.integer(k$interview_lang == 1),
                 cov_hh_occupation = num(k$hh_occupation), cov_income = num(k$income), cov_education = num(k$edu_years),
                 cov_religion = num(k$religion), cov_sect = num(k$sect), cov_radio_arm = as.character(k$lab_exp))
d <- rbindlist(lapply(1:3, function(r) rbindlist(lapply(1:2, function(p) {
  g <- function(v) k[[sprintf("%s_%d_p%d", v, r, p)]]
  data.table(id = k$rid, task = r, profile = p, sel = as.integer(k[[paste0("conj", r)]]),
             attr_ethnicity = sub("^Uzbik$", "Uzbek", lab(g("ethnicity"))), attr_gender = lab(g("gender")),
             attr_household_head_occupation = lab(g("occup")), attr_years_in_pakistan = lab(g("reside")))
}))))
d <- d[sel %in% 1:2][, choice := as.integer(sel == profile)][, sel := NULL]
d <- cv[d, on = "id"]
setcolorder(d, c("id", "task", "profile", "choice", grep("^attr_", names(d), value = TRUE)))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)],
          uniqueN(d$id) == 3500 - 714)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "malik_2025_afghan_refugees.csv"))
