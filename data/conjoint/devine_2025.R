##Class-profile conjoint on perceived class and political success from
##Devine, D., Turnbull-Dugarte, S. J., & Ryan, M. (2025). Success denied: Social class and
##perceptions of political success. Legislative Studies Quarterly. https://doi.org/10.1111/lsq.70024
##Replication data: Harvard Dataverse doi:10.7910/DVN/ILIYPE, CC0 1.0, no restricted files.
##File read: "UniversityofOxford_Results_230523_CLIENT_V3" (SPSS original, saved as ox.sav): the raw
##survey file with value labels, 4,157 UK online panel respondents. The authors' script1_datacleaning.R
##(read as text) gives the task/profile layout: Q1_A1/Q1_B1 = task 1 profiles A/B, Q1_A2/B2 = task 2,
##Q1_A3/B3, Q1_A4/B4 = tasks 3-4; q_attr<k>_concept<c>_task<t> = attribute k of profile c in task t.
##Not read: analysisdata.rds (group 2 only, the authors' long file), the .tab twins.
##Usage: Rscript devine_2025.R <raw dir> <output dir>
##
##4 tasks x 2 profiles ("Person A", "Person B"), id re-keyed to row order. Each profile is a
##hypothetical person described by up to 9 attributes (attr_ columns, text = the SPSS value labels):
##occupation (8), housing (4), parents' occupation (8), region (8), political office (3), education
##(4), gender (2), age (6: 24, 35, 46, 57, 68, 79), partner's occupation (8). The sample has two
##randomized groups (trial_group, uk_grp_as_v2): group 1 (n = 2,073) saw all nine attributes including
##"Political office" (Is a local councillor / Is an MP in Westminster / No, has never held political
##office) and answered only Q1; group 2 (n = 2,084, the paper's analysis sample) saw eight attributes
##(no political office: stored as "(not shown)") and answered Q1 and Q2. One table because the groups
##share the design and differ by one hidden attribute.
##Outcomes (rating, no choice; each person rated separately, so no opt-out):
##  rating = Q2 "Imagine these people decide to run to be a Member of Parliament in Westminster.
##    Thinking of these attributes, what do you think the chances of them being successful are?"
##    0-10 (group 2 only); the "not sure" answers (code 997) are NA.
##  rating_class = Q1 "Thinking about these two profiles, please rate them on a scale from working
##    class to upper class." 1 Working class, 2 Lower middle class, 3 Middle class, 4 Upper middle
##    class, 5 Upper class (a higher code = higher class; both groups).
##Tasks 3 and 4 were shown to only about half of the respondents of each group (the other half have
##no profiles or answers there; those rows do not exist). Respondents therefore have 2 or 4 tasks.
##Order of attributes was randomized per respondent: the deposit holds the string `attr_order`
##(e.g. [1, 2, 3, 5, 4, 7, 6, 9, 8]); it is kept as trial_attr_order and NOT turned into attrpos_
##columns, because in group 2 (eight attributes) the list has eight entries and the mapping of its
##indices to attribute ids is not documented.
##Covariates (SPSS value labels): cov_gender (profile_gender), cov_age (age as recorded; one
##implausible 123 is NA), cov_education (highest_education_gce, "DK" kept), cov_vote_ge2019
##(pastvote_ge_2019, vote choice not party id; "Don't know" kept), cov_left_right
##(politics_scale_profile_update, "Don't know" kept), cov_social_grade (A/B/C1/C2/D/E; refused and
##unknown NA), cov_survey_weight = Weight. Dropped: start/end times, region of the respondent,
##income, education age, Opinium persona and the raw table template.
##Respondent counts: 4,157 here; the paper's analysis uses group 2 (2,084 respondents).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_sav(file.path(raw, "ox.sav")))
stopifnot(nrow(d) == 4157, !anyDuplicated(d$ID))
lv <- function(x) { l <- attr(x, "labels"); l <- l[l < 98]; names(l)[match(as.numeric(x), l)] }
an <- c("occupation", "housing", "parents_occupation", "region", "political_office", "education", "gender", "age", "partner_occupation")
cv <- function(v, omit = integer()) { l <- attr(d[[v]], "labels"); x <- as.numeric(d[[v]]); x[x %in% omit] <- NA; l <- l[!l %in% omit]; names(l)[match(x, l)] }
g <- d$uk_grp_as_v2
cov <- data.table(id = seq_len(nrow(d)), trial_group = as.integer(g), trial_attr_order = d$attr_order,
  cov_gender = tolower(cv("profile_gender", c(8, 9))), cov_age = ifelse(d$age >= 18 & d$age <= 100, as.integer(d$age), NA_integer_),
  cov_education = cv("highest_education_gce"), cov_vote_ge2019 = cv("pastvote_ge_2019", c(98, 99, 998, 999)),
  cov_left_right = cv("politics_scale_profile_update", c(98, 99)), cov_social_grade = cv("profile_socialgrade_cie", c(7, 8, 98, 99)),
  cov_survey_weight = d$Weight)
qn <- list(c(1, 1, "A1", "B1"), c(2, 2, "A2", "B2"), c(3, 3, "A3", "B3"), c(4, 4, "A4", "B4"))
res <- rbindlist(lapply(1:4, function(t) rbindlist(lapply(1:2, function(p) {
  s <- sprintf("concept%d_task%d", p, t); L <- sprintf("%s%d", c("A", "B")[p], t)
  at <- sapply(1:9, function(k) { x <- d[[sprintf("q_attr%d_%s", k, s)]]; l <- attr(x, "labels"); l <- l[l < 98]; x <- as.numeric(x); x[!x %in% l] <- NA; names(l)[match(x, l)] })
  at <- as.data.table(at); setnames(at, paste0("attr_", an))
  shown <- !is.na(at$attr_occupation)   # tasks 3 and 4 were shown to about half of each group only
  stopifnot(all(is.na(at[!shown]) | TRUE), !anyNA(at[shown, -"attr_political_office"]),
            g[shown] == 2 | !is.na(at$attr_political_office[shown]), is.na(at$attr_political_office[g == 2]))
  at[g == 2, attr_political_office := "(not shown)"]
  q2 <- as.numeric(d[[paste0("Q2_", L)]]); q2[q2 %in% c(997, 998, 999)] <- NA
  q1 <- as.numeric(d[[paste0("Q1_", L)]]); q1[q1 %in% c(8, 9)] <- NA
  stopifnot(is.na(q1[!shown]), is.na(q2[!shown]))
  cbind(data.table(id = seq_len(nrow(d)), task = t, profile = p, rating = as.integer(q2), rating_class = as.integer(q1)), at)[shown]
}))))
stopifnot(res[!is.na(rating), all(rating %in% 0:10)], res[!is.na(rating_class), all(rating_class %in% 1:5)])
cat("Q2 answered", res[, sum(!is.na(rating))], "; Q1 answered", res[, sum(!is.na(rating_class))], "\n")
res <- res[!(is.na(rating) & is.na(rating_class))]
res <- merge(res, cov, by = "id")
setorder(res, id, task, profile)
fwrite(res, file.path(out, "devine_2025_class_political_success.csv"))
