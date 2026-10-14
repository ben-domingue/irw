##2x2 vignette on political newcomers joining a party (South Korea) from
##(Script name han_2026_party_newcomers.R: han_2026.R belongs to another Han 2026 deposit.)
##Han, S. (2026). Beyond the gate: Political incorporation and representative authority. (Replication data, Kyonggi
##University; unpublished manuscript, no article DOI in the deposit.)
##Replication data: Harvard Dataverse doi:10.7910/DVN/KHUZ0R, CC0 1.0. Files read: df_pooled.xlsx (readxl; general public
##n = 2,000 + party members n = 1,000), Codebook_detailed.xlsx, survey.pdf (Korean instrument, Table A1) as text. The
##single-sample files df_1_only_public.xlsx and df_2_only_party_members.xlsx are subsets of the pooled file and are not read.
##Usage: Rscript han_2026_party_newcomers.R <dir holding df_pooled.xlsx> <output dir>
##
##3,000 Korean adults: 2,000 general public and 1,000 party members (500 Democratic Party, 500 People Power Party members,
##column party_member_type). The authors pool them in df_pooled; they are kept in ONE table with cov_sample (the
##attribute text and design are identical).
##One vignette per respondent (task = profile = 1; id = re-keyed from the file's id, which runs 1-3,000). Setting: three fictional
##parties; A and B belong to the same bloc, C to the opposing bloc; A is considering what role to give a new member
##(survey.pdf, Table A1: "한 정치인은 ... A정당에 합류했습니다"). Respondents were randomly assigned to one of four cells
##(cells are exactly balanced within sample: 500 per cell among the public, 125 per cell per party in the member samples,
##so the design is a balanced assignment, not simple randomization):
##  attr_previous_party (political_distance): 과거 B정당에서 활동 (same bloc as A) / 과거 C정당에서 활동 (opposing bloc to A)
##  attr_party_contribution (organizational_commitment): 최근 A정당에 합류 (recent entry) / A정당에 합류한 이후 상당 기간
##      조직 활동과 선거운동에 꾸준히 참여 (sustained organizational contribution)
##Level text is the displayed Korean clause of survey.pdf conditions 1-4, shortened (the full sentence is
##"한 정치인은 과거 B정당에서 활동했지만 최근 A정당에 합류했습니다" and so on).
##Outcomes (7-point ratings, raw, 1 = strongly disagree/not at all fair ... 7 = strongly agree/very fair; Korean
##wording in survey.pdf, English paraphrase in the codebook):
##  rating_member_acceptance q1_member_acceptance "이 정치인은 A정당의 일원으로 받아들여져야 한다."
##  rating_campaign_participation "... A정당의 선거운동에 참여할 수 있어야 한다."
##  rating_party_office "... A정당의 일반 당직을 맡을 수 있어야 한다."
##  rating_local_nomination "... A정당의 지방선거 후보로 공천될 수 있어야 한다."
##  rating_national_nomination "... A정당의 국회의원 후보로 공천될 수 있어야 한다."
##  rating_party_leadership "... A정당의 지도부가 될 수 있어야 한다."
##  rating_fair_to_existing_members q2 "귀하는 이 정치인에게 이러한 역할을 부여하는 것이 오랫동안 A정당에서 활동해 온 기존
##      구성원들에게 얼마나 공정하다고 생각하십니까?" 1 not at all fair ... 7 very fair
##Covariates (codebook text as stored, English): cov_gender (Male/Female/Other), cov_age (years), cov_age_group, cov_region,
##cov_education, cov_income (monthly household income band), cov_marital_status, cov_union_membership,
##cov_employment, cov_housing_tenure, cov_ideology_1_7 (1 very liberal ... 7 very conservative), cov_political_interest_1_7
##(1 not at all ... 7 very interested), cov_sample (General public / Democratic Party member / People Power Party member).
##Dropped: the authors' derived authority_gap index (mean of Q1-Q3 minus mean of Q4-Q6; not in the pooled file's columns).
##Respondent n = 3,000, as described by the authors. No survey weight in the deposit.
suppressMessages({library(readxl); library(data.table)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_excel(file.path(raw, "df_pooled.xlsx")))
stopifnot(nrow(k) == 3000, uniqueN(k$id) == 3000)
pd <- c("Same bloc" = "과거 B정당에서 활동 (A정당과 같은 정치 진영)", "Opposing bloc" = "과거 C정당에서 활동 (A정당과 반대되는 정치 진영)")
oc <- c("Recent entry" = "최근 A정당에 합류", "Organizational commitment" = "A정당에 합류한 이후 상당 기간 조직 활동과 선거운동에 꾸준히 참여")
stopifnot(all(k$political_distance %in% names(pd)), all(k$organizational_commitment %in% names(oc)))
d <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L)
rn <- c(q1_member_acceptance = "member_acceptance", q1_campaign_participation = "campaign_participation", q1_party_office = "party_office",
        q1_local_nomination = "local_nomination", q1_national_nomination = "national_nomination", q1_party_leadership = "party_leadership",
        q2_fairness_existing_members = "fair_to_existing_members")
for (v in names(rn)) d[, paste0("rating_", rn[v]) := as.integer(k[[v]])]
d[, attr_previous_party := pd[k$political_distance]][, attr_party_contribution := oc[k$organizational_commitment]]
d[, cov_gender := c(Male = "male", Female = "female", Other = "other")[k$gender]]
d[, cov_age := as.integer(k$age)][, cov_age_group := k$age_group][, cov_region := k$region][, cov_education := k$education]
d[, cov_income := k$monthly_household_income][, cov_marital_status := k$marital_status][, cov_union_membership := k$union_membership]
d[, cov_employment := k$employment_type][, cov_housing_tenure := k$housing_tenure]
d[, cov_ideology_1_7 := as.integer(k$political_ideology_1_7)][, cov_political_interest_1_7 := as.integer(k$political_interest_1_7)]
d[, cov_sample := ifelse(k$party_member_type == "General public", "General public", k$party_member_type)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "han_2026_party_newcomers.csv"))
cat("rows", nrow(d), "\n")
print(d[, .(m_nat = round(mean(rating_national_nomination), 2), m_member = round(mean(rating_member_acceptance), 2), n = .N), by = .(attr_previous_party, attr_party_contribution)])
