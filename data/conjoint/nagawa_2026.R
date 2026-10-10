##Project and department conjoints with Ugandan civil servants from
##Nagawa, M. (2026). Foreign aid and the performance of bureaucrats. International Organization.
##https://doi.org/10.1017/S0020818326101489 (DOI from the triage sheet; not resolved here)
##Replication data: Harvard Dataverse doi:10.7910/DVN/G2KIZY, CC0 1.0, no restricted files.
##Files read: ForeignAidandBureaucrats_ReplicationData (original .csv); the authors'
##ForeignAidandBureaucrats_ReplicationCode.Rmd read as text (not run) for outcome and covariate
##codes. Design and wording from the working-paper version (PEIO 2026 submission_6.pdf,
##Jan 8 2026, sec. 4, Tables 1-2 and the quoted introductions).
##Usage: Rscript nagawa_2026.R <raw dir> <output dir>
##
##562 mid-level bureaucrats in six Ugandan ministries (in-person survey, 2023); 3 rows have no
##conjoint data ("three incomplete surveys", Rmd) and are dropped, leaving 559 (matches the paper).
##TWO TABLES, one per experiment (different attribute sets, separate analyses in the paper):
##  nagawa_2026_aid_projects: 3 forced-choice tasks of Project A (profile 1) vs Project B (2),
##    4 attributes (funder, monetary benefits, ownership, discretion). Intro: "Now I am going to
##    ask you your opinion about certain aspects of donor funded projects. I will show you two
##    pairs of three hypothetical projects that have a funding period of three years. ..."
##    choice = pair<t>_project (1 = A, 2 = B), which project the respondent prefers.
##  nagawa_2026_aid_departments: 3 forced-choice tasks of Department A vs B, 3 attributes (donor
##    exposure, inequity, coordination). choice = conj2_pair<t>_dept, which department the
##    respondent would prefer to work in.
##Choices are forced (no opt-out; exactly one chosen per task, checked). Level text is the
##displayed text as stored in the *_att*_txt columns (monetary amounts in UGX, as the paper says
##respondents saw them; the paper's Table 1 shows USD conversions).
##NOT KEPT: the follow-up effort questions asked only about the chosen profile (additional hours
##per day on the project/department, hours taken off routine government work): stored as codes
##1-6 / 1-9 with no deposited labels (the paper says "up to four hours" / "up to eight hours").
##Covariates (codes -> text from the Rmd's recode, `general` chunk): cov_gender (gender 1 Female,
##0 Male; codes 4 and 5, 3 respondents, unlabelled -> NA), cov_ministry, cov_region, cov_education
##(educ; 6 is unlabelled -> NA), cov_contract, cov_rank (0 unlabelled -> NA), "No response" -> NA,
##"Other" kept; cov_dfp_ever (ever worked with development partners 1/0; 900 -> NA, Rmd);
##cov_dfp_org_freq_code (how frequently the organisation works with development partners; codes,
##no labels deposited). The ODK instanceID is re-keyed. No survey weight.
##N: 559 respondents per table, as in the paper.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "data.csv"), na.strings = c("NA", ""))
s <- s[!is.na(pair1_project)]
stopifnot(nrow(s) == 559, !anyDuplicated(s$instanceID))
s[, idn := seq_len(.N)]
rc <- function(x, map) { y <- unname(map[as.character(x)]); y }
cov <- data.table(id = s$idn,
  cov_gender = rc(s$gender, c("1" = "female", "0" = "male")),
  cov_ministry = rc(s$ministry, c("1" = "Ministry of Finance, Planning and Economic Development",
    "2" = "Ministry of Trade, Industry and Cooperatives", "3" = "Ministry of Agriculture, Animal Industry and Fisheries",
    "4" = "Ministry of Health", "5" = "Ministry of Education and Sports", "6" = "Ministry of Works and Transport")),
  cov_region = rc(s$region, c("1" = "Northern", "2" = "Southern", "3" = "Eastern", "4" = "Western", "5" = "Central", "700" = "Other")),
  cov_education = rc(s$educ, c("1" = "Vocational/post-high school diploma", "2" = "Undergraduate degree",
    "3" = "Post-graduate diploma", "4" = "Masters degree", "5" = "PhD/Doctorate", "700" = "Other")),
  cov_contract = rc(s$contract, c("1" = "Permanent contract/pensionable", "2" = "Short-term/Temporary/Contractor")),
  cov_rank = rc(s$rank, c("1" = "Management, direction and supervision", "2" = "Technical and/or professional responsibilities",
    "3" = "Administrative support and assistance", "700" = "Other")),
  cov_dfp_ever = fifelse(s$dfp_ever %in% 0:1, s$dfp_ever, NA_integer_),
  cov_dfp_org_freq_code = s$dfp_org_freq)
build <- function(stem, chosen, natt, nm) {
  d <- rbindlist(lapply(1:3, function(t) rbindlist(lapply(1:2, function(p) {
    x <- data.table(id = s$idn, task = t, profile = p, choice = as.integer(s[[sprintf(chosen, t)]] == p))
    for (k in seq_len(natt)) x[, paste0("attr_", nm[k]) := trimws(s[[sprintf(stem, t, c("a", "b")[p], k)]])]
    x
  }))))
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d))
  d <- merge(d, cov, by = "id")
  setorder(d, id, task, profile)
  d
}
p <- build("pair%d%s_att%d_txt", "pair%d_project", 4, c("funder", "monetary_benefits", "ownership", "discretion"))
stopifnot(uniqueN(p$attr_funder) == 4, uniqueN(p$attr_monetary_benefits) == 4, uniqueN(p$attr_ownership) == 3, uniqueN(p$attr_discretion) == 3)
fwrite(p, file.path(out, "nagawa_2026_aid_projects.csv"))
d <- build("pair%d%s_conj2_att%d_txt", "conj2_pair%d_dept", 3, c("donor_exposure", "inequity", "coordination"))
stopifnot(uniqueN(d$attr_donor_exposure) == 4, uniqueN(d$attr_inequity) == 3, uniqueN(d$attr_coordination) == 3)
fwrite(d, file.path(out, "nagawa_2026_aid_departments.csv"))
