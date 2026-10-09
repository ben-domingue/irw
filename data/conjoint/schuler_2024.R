##National Assembly candidate conjoint (Vietnam, PAPI 2022) from
##Schuler, P. (2024). Gender and clientelism: Do expectations of patronage penalize women
##candidates in legislative elections? Comparative Political Studies, 57(14), 2348-2375.
##https://doi.org/10.1177/00104140231204248
##Replication data: Harvard Dataverse doi:10.7910/DVN/MX6976, CC0 1.0, no restricted files,
##no terms. File read: Schuler_GenderAndClientelism_Replication3.dta (Dataverse "original
##format" download). Schuler_GenderAndClientelism_Replication2_Public.do read as text (arm
##coding, attribute coding). Replication1/2 (.tab; PAPI 2020/2021) hold a single randomized
##trait question (prefer a man or a woman), not a conjoint, and are not used.
##Usage: Rscript schuler_2024.R <raw dir> <output dir>
##
##PAPI 2022 face-to-face survey, Vietnam, in Vietnamese. The deposited file keeps only the form
##that asked about National Assembly delegates without the sexual-orientation variant (do-file
##note; leader_group == 1 and gay_treatment == 0 throughout). 6,429 respondents with a profile
##(3 rows with no id and no profile dropped; 2 respondents with a missing level (age "." or
##party missing) dropped). One task: "[Interviewer read]: Now imagine two
##candidates for the National Assembly ..." (Stata label, truncated in the source), Candidate 1 =
##profile 1, Candidate 2 = profile 2.
##6 attributes per candidate; level text = the survey's own Vietnamese level names stored in
##d102_<attr><k>_lb ([D102_..._NAME]), which match the numeric codes one-to-one (checked):
##  attr_age     29 / 39 / 49 / 59 (the displayed text may have carried a unit; only the number
##               is stored in the NAME field)
##  attr_sex     Nam (man) / Nữ (woman)
##  attr_education Hết cấp 3 (high school) / Đại học (bachelor's) / Thạc sĩ (master's) / Tiến sĩ (doctorate)
##  attr_party   Đảng viên (party member) / Người ngoài Đảng (non-member)
##  attr_benefits  who the candidate's work benefits (do-file: ben_*): Công dân (citizens) /
##               Doanh nghiệp (business) / Lãnh đạo chính quyền (government leaders) / Tổ chức xã
##               hội (social organizations) / Cộng đồng (community)
##  attr_kinship Người trong dòng tộc (inside the [respondent's] clan) / Người ngoài dòng tộc
##               (outside the clan). NOTE: the authors' do-file sets inclan = 1 for code 2,
##               whose NAME is "outside the clan"; the stored text follows the NAME field.
##Randomization: per-attribute uniform draws (d102_*_random variables, not kept); the level
##shares are near-equal. No restriction documented.
##  choice = d102a, which candidate the respondent would vote for (do-file `vote`): 1 Candidate 1,
##           2 Candidate 2; [DK]/[RA] or missing for 540 respondents (dropped: no outcome).
##           No opt-out offered beyond DK/RA.
##trial_prime = the preceding prime (authors' client_group from d101e_random: < 1/3 Control,
##1/3-2/3 Honesty prime, > 2/3 Clientelism prime; the paper's main contrast is Control vs
##Clientelism).
##Covariates: cov_gender (a001 "Gender": Male/Female), cov_age (a002 "How old are you?"),
##cov_education (a006 value-label text; [DK]/[RA] -> NA), cov_ethnicity (a005 text: Kinh /
##Other; [DK] kept as "[DK]"), cov_area (khuvuc: Urban / Rural, label text shortened to the first
##word). No survey weight in this file (the 2020/2021 files carry PAPI weights; the 2022 models
##in the do-file are unweighted). Dropped: the *_random draws, a016 memberships, d101*/d602aa,
##income (d611ai), leader_group, gay_treatment.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "Schuler_GenderAndClientelism_Replication3.dta"))
z <- as.data.table(zap_labels(k))
txt <- function(v) { x <- as.character(as_factor(k[[v]], levels = "labels")); x[is.na(k[[v]])] <- NA; x }
z[, `:=`(edu_t = txt("a006"), eth_t = txt("a005"))]
z <- z[!is.na(id)]
cc <- paste0("d102_", rep(c("age", "sex", "edu", "party", "ben", "rel"), each = 2), 1:2)
cat("respondents dropped for a missing attribute:", sum(!complete.cases(z[, ..cc])), "\n")
z <- z[complete.cases(z[, ..cc])]
stopifnot(!anyDuplicated(z$id), all(z$leader_group == 1), all(z$gay_treatment == 0))
at <- c(age = "age", sex = "sex", education = "edu", party = "party", benefits = "ben", kinship = "rel")
rows <- list()
for (p in 1:2) {
  r <- data.table(id = as.integer(z$id), task = 1L, profile = p,
                  choice = fifelse(z$d102a %in% 1:2, as.integer(z$d102a == p), NA_integer_))
  for (n in names(at)) {
    cd <- z[[sprintf("d102_%s%d", at[[n]], p)]]; lb <- z[[sprintf("d102_%s%d_lb", at[[n]], p)]]
    stopifnot(!anyNA(cd), all(lb != ""), data.table(cd, lb)[, uniqueN(lb), by = cd][, all(V1 == 1)])
    r[, paste0("attr_", n) := lb]
  }
  rows[[p]] <- r
}
d <- rbindlist(rows)
stopifnot(all(z[d102_rel1 == 1, d102_rel1_lb] == "Người trong dòng tộc"))
grp <- fcase(z$d101e_random < .333, "Control", z$d101e_random > .333 & z$d101e_random < .666, "Honesty prime",
             z$d101e_random > .666, "Clientelism prime")
stopifnot(!anyNA(grp), all(z$a001 %in% 1:2))
cv <- data.table(id = as.integer(z$id), trial_prime = grp, cov_gender = c("male", "female")[z$a001],
                 cov_age = as.integer(z$a002),
                 cov_education = fifelse(z$a006 %in% 1:10, z$edu_t, NA_character_),
                 cov_ethnicity = fifelse(z$a005 %in% c(1, 7, 888), z$eth_t, NA_character_),
                 cov_area = c("Urban", "Rural")[z$khuvuc])
d <- cv[d, on = "id"]
setcolorder(d, c("id", "task", "profile", "choice"))
d <- d[!is.na(choice)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "schuler_2024_gender_clientelism.csv"))
